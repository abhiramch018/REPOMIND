"""
RepoMind — FastAPI application entry point.

Endpoints:
    POST /analyze  — Clone & index a GitHub repository.
    POST /ask      — Ask a question about an analyzed repository.
    GET  /health   — Health check.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from config import FRONTEND_DIR, TOP_K
from cloner import clone_repo, _extract_repo_name
from scanner import scan_repository
from embedder import chunk_code, generate_embeddings
from vector_store import build_index, save_index, load_index, search
from llm import ask_llm

# ── FastAPI app ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="RepoMind",
    description="AI-powered GitHub repository analyzer",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request / response models ───────────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    repo_url: str
    force: bool = False

class AnalyzeResponse(BaseModel):
    status: str
    repo_name: str
    files_scanned: int
    chunks_created: int
    message: str

class AskRequest(BaseModel):
    repo_url: str
    question: str

class AskResponse(BaseModel):
    answer: str
    sources: list[str]


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "service": "RepoMind"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    """Clone a GitHub repo, scan files, generate embeddings, build FAISS index."""
    try:
        # 1. Clone
        clone_result = clone_repo(req.repo_url, force=req.force)
        repo_name = clone_result["repo_name"]
        local_path = clone_result["local_path"]

        # 2. Scan
        files = scan_repository(local_path)
        if not files:
            raise HTTPException(
                status_code=400,
                detail="No supported code files found in the repository.",
            )

        # 3. Chunk
        all_chunks: list[dict] = []
        for f in files:
            file_chunks = chunk_code(f["content"], file_path=f["file_path"])
            all_chunks.extend(file_chunks)

        if not all_chunks:
            raise HTTPException(
                status_code=400,
                detail="Could not create any text chunks from the repository files.",
            )

        # 4. Embed
        texts = [c["text"] for c in all_chunks]
        embeddings = generate_embeddings(texts)

        # 5. Index & save
        index = build_index(embeddings)
        metadata = [{"text": c["text"], "file_path": c["file_path"]} for c in all_chunks]
        save_index(index, metadata, repo_name)

        return AnalyzeResponse(
            status="success",
            repo_name=repo_name,
            files_scanned=len(files),
            chunks_created=len(all_chunks),
            message=f"Repository analyzed successfully! {len(files)} files scanned, "
                    f"{len(all_chunks)} chunks indexed.",
        )

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")


@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    """Answer a question about an analyzed repository using RAG."""
    try:
        repo_name = _extract_repo_name(req.repo_url)

        # 1. Load index
        try:
            index, metadata = load_index(repo_name)
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail="Repository not yet analyzed. Please run /analyze first.",
            )

        # 2. Embed the question
        question_embedding = generate_embeddings([req.question])

        # 3. Search for relevant chunks
        results = search(index, question_embedding, top_k=TOP_K)

        # 4. Gather context snippets
        snippets: list[dict] = []
        source_files: set[str] = set()
        for chunk_idx, score in results:
            if chunk_idx < len(metadata):
                snippets.append(metadata[chunk_idx])
                source_files.add(metadata[chunk_idx].get("file_path", "unknown"))

        if not snippets:
            return AskResponse(
                answer="I couldn't find relevant code snippets to answer your question.",
                sources=[],
            )

        # 5. Ask the LLM
        answer = ask_llm(req.question, snippets)

        return AskResponse(
            answer=answer,
            sources=sorted(source_files),
        )

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Query failed: {exc}")


# ── Serve frontend ──────────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/")
async def serve_frontend():
    return FileResponse(str(FRONTEND_DIR / "index.html"))
