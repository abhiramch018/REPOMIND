"""
RepoMind — Recursive code file scanner and extractor.
"""

from pathlib import Path

from config import SUPPORTED_EXTENSIONS, SKIP_DIRS, MAX_FILE_SIZE


def scan_repository(repo_path: str) -> list[dict]:
    """
    Recursively walk a repository directory and extract all relevant code files.

    Args:
        repo_path: Absolute path to the cloned repository.

    Returns:
        List of dicts with "file_path" (relative) and "content".
    """
    root = Path(repo_path)
    if not root.is_dir():
        raise FileNotFoundError(f"Repository path not found: {repo_path}")

    files: list[dict] = []

    for path in root.rglob("*"):
        # Skip directories themselves
        if path.is_dir():
            continue

        # Skip hidden/ignored directories
        parts = path.relative_to(root).parts
        if any(part in SKIP_DIRS or part.startswith(".") for part in parts[:-1]):
            continue

        # Only include supported extensions
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        # Skip very large files
        if path.stat().st_size > MAX_FILE_SIZE:
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            if content.strip():  # skip empty files
                files.append({
                    "file_path": str(path.relative_to(root)),
                    "content": content,
                })
        except Exception:
            # Skip files that can't be read
            continue

    return files
