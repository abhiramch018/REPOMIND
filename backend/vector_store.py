"""
RepoMind — FAISS vector store manager.
"""

import json
from pathlib import Path

import faiss
import numpy as np

from config import INDEX_DIR


def build_index(embeddings: np.ndarray) -> faiss.Index:
    """
    Build a FAISS flat L2 index from embeddings.

    Args:
        embeddings: numpy array of shape (n, dim).

    Returns:
        A FAISS index ready for search.
    """
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # Inner product (cosine sim with normalized vecs)
    index.add(embeddings)
    return index


def save_index(index: faiss.Index, metadata: list[dict], repo_name: str) -> None:
    """
    Persist a FAISS index and its chunk metadata to disk.

    Args:
        index: The FAISS index object.
        metadata: List of chunk metadata dicts (text, file_path).
        repo_name: Repository slug used as the directory name.
    """
    store_dir = INDEX_DIR / repo_name
    store_dir.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(store_dir / "index.faiss"))

    with open(store_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False)


def load_index(repo_name: str) -> tuple[faiss.Index, list[dict]]:
    """
    Load a previously saved FAISS index and its metadata.

    Returns:
        Tuple of (FAISS index, list of metadata dicts).

    Raises:
        FileNotFoundError if the index doesn't exist.
    """
    store_dir = INDEX_DIR / repo_name
    index_path = store_dir / "index.faiss"
    meta_path = store_dir / "metadata.json"

    if not index_path.exists():
        raise FileNotFoundError(
            f"No index found for repo '{repo_name}'. Run /analyze first."
        )

    index = faiss.read_index(str(index_path))

    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    return index, metadata


def search(index: faiss.Index, query_embedding: np.ndarray,
           top_k: int = 5) -> list[tuple[int, float]]:
    """
    Search the FAISS index for the nearest chunks.

    Args:
        index: FAISS index.
        query_embedding: 1-D or 2-D numpy array of the query vector.
        top_k: Number of results to return.

    Returns:
        List of (chunk_index, distance_score) tuples.
    """
    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(1, -1)

    distances, indices = index.search(query_embedding, top_k)

    results = []
    for idx, dist in zip(indices[0], distances[0]):
        if idx != -1:  # FAISS returns -1 for empty slots
            results.append((int(idx), float(dist)))

    return results
