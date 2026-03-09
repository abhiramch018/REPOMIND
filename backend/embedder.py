"""
RepoMind — Code embedding generator using sentence-transformers.
"""

import numpy as np
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP

# Lazy-loaded singleton
_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def chunk_code(content: str, file_path: str = "",
               chunk_size: int = CHUNK_SIZE,
               overlap: int = CHUNK_OVERLAP) -> list[dict]:
    """
    Split file content into overlapping text chunks.

    Each chunk is annotated with its source file path so we can
    trace results back to the original file.

    Returns:
        List of dicts: {"text": ..., "file_path": ...}
    """
    chunks: list[dict] = []
    lines = content.split("\n")
    current_chunk: list[str] = []
    current_length = 0

    for line in lines:
        line_len = len(line) + 1  # +1 for newline
        current_chunk.append(line)
        current_length += line_len

        if current_length >= chunk_size:
            chunk_text = "\n".join(current_chunk)
            # Prepend file path context for better retrieval
            header = f"# File: {file_path}\n" if file_path else ""
            chunks.append({
                "text": header + chunk_text,
                "file_path": file_path,
            })

            # Keep last few lines for overlap
            overlap_lines: list[str] = []
            overlap_len = 0
            for ol in reversed(current_chunk):
                overlap_len += len(ol) + 1
                overlap_lines.insert(0, ol)
                if overlap_len >= overlap:
                    break
            current_chunk = overlap_lines
            current_length = overlap_len

    # Don't forget the last chunk
    if current_chunk:
        chunk_text = "\n".join(current_chunk)
        header = f"# File: {file_path}\n" if file_path else ""
        chunks.append({
            "text": header + chunk_text,
            "file_path": file_path,
        })

    return chunks


def generate_embeddings(texts: list[str]) -> np.ndarray:
    """
    Generate dense vector embeddings for a list of text strings.

    Args:
        texts: List of text chunks.

    Returns:
        numpy array of shape (n, embedding_dim).
    """
    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=True,
                              batch_size=64, normalize_embeddings=True)
    return np.array(embeddings, dtype="float32")
