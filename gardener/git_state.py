"""Git and commit state tracking for Gardener."""

import hashlib
import subprocess
from typing import TypedDict

import config
from db import get_db_connection


class CommitInfo(TypedDict):
    sha: str
    branch: str
    processed_at: str
    note: str | None


class RepoState(TypedDict):
    last_seen_sha: str | None
    last_processed_sha: str | None
    last_reconcile_sha: str | None
    repo_root_hash: str | None
    last_updated: str | None


def get_repo_root_hash() -> str | None:
    """Get a hash identifying the repo (for detecting history rewrites)."""
    try:
        # Use the initial commit SHA as repo identity
        result = subprocess.run(
            ["git", "rev-list", "--max-parents=0", "HEAD"],
            cwd=config.DATA_DIR,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            return hashlib.sha256(result.stdout.strip().encode()).hexdigest()[:16]
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return None


def get_current_head() -> str | None:
    """Get the current HEAD SHA."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=config.DATA_DIR,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return None


def get_current_branch() -> str:
    """Get the current branch name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=config.DATA_DIR,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return "unknown"


def get_repo_state() -> RepoState:
    """Get the current repo state from the database."""
    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT last_seen_sha, last_processed_sha, last_reconcile_sha, repo_root_hash, last_updated FROM repo_state WHERE id = 1"
        ).fetchone()
        if row:
            return RepoState(
                last_seen_sha=row["last_seen_sha"],
                last_processed_sha=row["last_processed_sha"],
                last_reconcile_sha=row["last_reconcile_sha"],
                repo_root_hash=row["repo_root_hash"],
                last_updated=row["last_updated"],
            )
        return RepoState(
            last_seen_sha=None,
            last_processed_sha=None,
            last_reconcile_sha=None,
            repo_root_hash=None,
            last_updated=None,
        )
    finally:
        conn.close()


def update_last_seen_sha(sha: str) -> None:
    """Update the last seen commit SHA."""
    conn = get_db_connection()
    try:
        conn.execute(
            "UPDATE repo_state SET last_seen_sha = ?, last_updated = datetime('now') WHERE id = 1",
            (sha,),
        )
        conn.commit()
    finally:
        conn.close()


def update_last_processed_sha(sha: str) -> None:
    """Update the last processed commit SHA."""
    conn = get_db_connection()
    try:
        conn.execute(
            "UPDATE repo_state SET last_processed_sha = ?, last_updated = datetime('now') WHERE id = 1",
            (sha,),
        )
        conn.commit()
    finally:
        conn.close()


def update_repo_root_hash(hash_value: str) -> None:
    """Update the repo root hash (for detecting history rewrites)."""
    conn = get_db_connection()
    try:
        conn.execute(
            "UPDATE repo_state SET repo_root_hash = ?, last_updated = datetime('now') WHERE id = 1",
            (hash_value,),
        )
        conn.commit()
    finally:
        conn.close()


def record_processed_commit(sha: str, branch: str, note: str | None = None) -> None:
    """Record a processed commit and update last_seen_sha."""
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO processed_commits (sha, branch, note, processed_at) VALUES (?, ?, ?, datetime('now'))",
            (sha, branch, note),
        )
        # Update both last_processed_sha and last_seen_sha
        conn.execute(
            "UPDATE repo_state SET last_processed_sha = ?, last_seen_sha = ?, last_updated = datetime('now') WHERE id = 1",
            (sha, sha),
        )
        conn.commit()
    finally:
        conn.close()


def get_processed_commits(limit: int = 10) -> list[CommitInfo]:
    """Get recent processed commits."""
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT sha, branch, processed_at, note FROM processed_commits ORDER BY processed_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [
            CommitInfo(
                sha=row["sha"],
                branch=row["branch"],
                processed_at=row["processed_at"],
                note=row["note"],
            )
            for row in rows
        ]
    finally:
        conn.close()


def check_repo_identity() -> tuple[bool, str | None]:
    """Check if the repo identity matches what we've seen before.

    Returns:
        (matches, current_hash): matches is True if identity is same or first check,
                                  current_hash is the computed identity hash
    """
    current_hash = get_repo_root_hash()
    if current_hash is None:
        return True, None  # Git not available or no commits

    state = get_repo_state()
    if state["repo_root_hash"] is None:
        # First time seeing this repo
        update_repo_root_hash(current_hash)
        return True, current_hash

    return state["repo_root_hash"] == current_hash, current_hash


def get_dirty_files() -> list[str]:
    """Get list of uncommitted files in the data directory."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=config.DATA_DIR,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            return [line[3:] for line in result.stdout.strip().split("\n") if line]
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return []


def cleanup_old_commits(keep_count: int = 100) -> int:
    """Remove old processed commit records, keeping the most recent ones.

    Returns the number of records deleted.
    """
    conn = get_db_connection()
    try:
        # Get IDs to keep
        rows = conn.execute(
            "SELECT id FROM processed_commits ORDER BY processed_at DESC LIMIT ?",
            (keep_count,),
        ).fetchall()
        keep_ids = [row["id"] for row in rows]

        if not keep_ids:
            return 0

        # Delete older records
        placeholders = ",".join("?" * len(keep_ids))
        cursor = conn.execute(
            f"DELETE FROM processed_commits WHERE id NOT IN ({placeholders})", keep_ids
        )
        deleted = cursor.rowcount
        conn.commit()
        return deleted
    finally:
        conn.close()
