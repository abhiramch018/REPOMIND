"""
RepoMind — GitHub repository cloner using GitPython.
"""

import re
import shutil
from pathlib import Path

from git import Repo, GitCommandError

from config import REPOS_DIR


def _extract_repo_name(repo_url: str) -> str:
    """Extract 'owner_repo' slug from a GitHub URL."""
    # Handle both https and git@ URLs
    pattern = r"(?:github\.com[/:])([\w.\-]+)/([\w.\-]+?)(?:\.git)?$"
    match = re.search(pattern, repo_url.strip().rstrip("/"))
    if not match:
        raise ValueError(f"Invalid GitHub URL: {repo_url}")
    owner, name = match.group(1), match.group(2)
    return f"{owner}_{name}"


def clone_repo(repo_url: str, force: bool = False) -> dict:
    """
    Clone a GitHub repository into the local data directory.

    Args:
        repo_url: Full GitHub repository URL.
        force: If True, re-clone even if the repo already exists.

    Returns:
        dict with "repo_name", "local_path", and "status".
    """
    repo_name = _extract_repo_name(repo_url)
    local_path = REPOS_DIR / repo_name

    if local_path.exists():
        if force:
            shutil.rmtree(local_path)
        else:
            return {
                "repo_name": repo_name,
                "local_path": str(local_path),
                "status": "already_cloned",
            }

    try:
        Repo.clone_from(repo_url, str(local_path), depth=1)  # shallow clone
        return {
            "repo_name": repo_name,
            "local_path": str(local_path),
            "status": "cloned",
        }
    except GitCommandError as exc:
        raise RuntimeError(f"Failed to clone {repo_url}: {exc}") from exc
