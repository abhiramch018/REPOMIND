"""
RepoMind — Shared configuration and constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPOS_DIR = DATA_DIR / "repos"
INDEX_DIR = DATA_DIR / "indexes"
FRONTEND_DIR = BASE_DIR / "frontend"

# Ensure runtime directories exist
REPOS_DIR.mkdir(parents=True, exist_ok=True)
INDEX_DIR.mkdir(parents=True, exist_ok=True)

# ── Supported code file extensions ───────────────────────────────────────────
SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".java", ".cpp", ".c", ".h", ".hpp",
    ".go", ".rs", ".rb", ".php",
    ".html", ".css", ".scss",
    ".swift", ".kt", ".scala",
    ".sh", ".bash", ".zsh",
    ".sql", ".r", ".m",
    ".json", ".yaml", ".yml", ".toml",
    ".md", ".txt",
}

# Directories to skip during scanning
SKIP_DIRS = {
    ".git", "__pycache__", "node_modules", "vendor",
    "dist", "build", ".venv", "venv", "env",
    ".idea", ".vscode", ".next", "target",
    "coverage", ".tox", "eggs", "*.egg-info",
}

# ── Embedding / chunking settings ────────────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 500        # characters per chunk
CHUNK_OVERLAP = 50      # overlap between consecutive chunks
MAX_FILE_SIZE = 100_000  # skip files larger than 100 KB

# ── Retrieval settings ───────────────────────────────────────────────────────
TOP_K = 5               # number of chunks to retrieve per query

# ── LLM settings ─────────────────────────────────────────────────────────────
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash"
