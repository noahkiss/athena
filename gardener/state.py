"""State tracking for Gardener using SQLite.

Tracks:
- Processed commits (SHA, timestamp, branch)
- File state (hash, mtime, location)
- Repo identity (detect history rewrites)
"""

import hashlib
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from typing import TypedDict

from config import DATA_DIR, STATE_DIR, STATE_DB, INBOX_DIR, ATLAS_DIR, META_DIR

# Schema version for migrations
SCHEMA_VERSION = 1

SCHEMA = """
-- Track processed commits
CREATE TABLE IF NOT EXISTS processed_commits (
    id INTEGER PRIMARY KEY,
    sha TEXT UNIQUE NOT NULL,
    branch TEXT NOT NULL,
    processed_at TEXT DEFAULT (datetime('now')),
    note TEXT
);

-- Track the last seen commit (may differ from last processed)
CREATE TABLE IF NOT EXISTS repo_state (
    id INTEGER PRIMARY KEY CHECK (id = 1),  -- Singleton row
    last_seen_sha TEXT,
    last_processed_sha TEXT,
    last_reconcile_sha TEXT,  -- SHA when last reconcile was run
    repo_root_hash TEXT,  -- Hash of repo identity for detecting history rewrites
    last_updated TEXT DEFAULT (datetime('now'))
);

-- Track file state for change detection
CREATE TABLE IF NOT EXISTS file_state (
    id INTEGER PRIMARY KEY,
    file_path TEXT UNIQUE NOT NULL,
    location TEXT NOT NULL,  -- 'inbox', 'atlas', 'meta', 'root'
    content_hash TEXT NOT NULL,
    mtime REAL NOT NULL,
    size INTEGER NOT NULL,
    last_checked TEXT DEFAULT (datetime('now'))
);

-- Track reconciliation runs
CREATE TABLE IF NOT EXISTS reconcile_runs (
    id INTEGER PRIMARY KEY,
    run_at TEXT DEFAULT (datetime('now')),
    from_sha TEXT,
    to_sha TEXT,
    files_changed INTEGER DEFAULT 0,
    inbox_changes INTEGER DEFAULT 0,
    atlas_changes INTEGER DEFAULT 0,
    meta_changes INTEGER DEFAULT 0,
    tasks_generated TEXT  -- JSON array of task descriptions
);

-- Track edit provenance (who/what made changes)
CREATE TABLE IF NOT EXISTS edit_provenance (
    id INTEGER PRIMARY KEY,
    file_path TEXT NOT NULL,
    commit_sha TEXT,
    source TEXT NOT NULL,  -- 'gardener', 'manual', 'external:claude-code', 'external:mcp', etc.
    recorded_at TEXT DEFAULT (datetime('now')),
    metadata TEXT  -- Optional JSON for additional context
);

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_file_state_location ON file_state(location);
CREATE INDEX IF NOT EXISTS idx_processed_commits_sha ON processed_commits(sha);
CREATE INDEX IF NOT EXISTS idx_reconcile_runs_run_at ON reconcile_runs(run_at);
CREATE INDEX IF NOT EXISTS idx_edit_provenance_file ON edit_provenance(file_path);
CREATE INDEX IF NOT EXISTS idx_edit_provenance_source ON edit_provenance(source);
"""


class CommitInfo(TypedDict):
    sha: str
    branch: str
    processed_at: str
    note: str | None


class FileInfo(TypedDict):
    file_path: str
    location: str
    content_hash: str
    mtime: float
    size: int
    last_checked: str


class RepoState(TypedDict):
    last_seen_sha: str | None
    last_processed_sha: str | None
    last_reconcile_sha: str | None
    repo_root_hash: str | None
    last_updated: str | None


class ReconcileRun(TypedDict):
    id: int
    run_at: str
    from_sha: str | None
    to_sha: str | None
    files_changed: int
    inbox_changes: int
    atlas_changes: int
    meta_changes: int
    tasks_generated: list[str]


class ChangedFile(TypedDict):
    path: str
    location: str
    status: str  # 'added', 'modified', 'deleted', 'renamed'
    old_path: str | None  # For renames


class EditProvenance(TypedDict):
    id: int
    file_path: str
    commit_sha: str | None
    source: str
    recorded_at: str
    metadata: dict | None


# Standard source identifiers for provenance
PROVENANCE_GARDENER = "gardener"
PROVENANCE_MANUAL = "manual"
PROVENANCE_EXTERNAL_CLAUDE = "external:claude-code"
PROVENANCE_EXTERNAL_MCP = "external:mcp"
PROVENANCE_EXTERNAL_SCRIPT = "external:script"


def get_db_connection() -> sqlite3.Connection:
    """Get a connection to the state database."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(STATE_DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize the database schema."""
    conn = get_db_connection()
    try:
        conn.executescript(SCHEMA)
        # Initialize singleton repo_state row if not exists
        conn.execute(
            "INSERT OR IGNORE INTO repo_state (id) VALUES (1)"
        )
        # Set schema version
        conn.execute(
            "INSERT OR REPLACE INTO schema_version (version) VALUES (?)",
            (SCHEMA_VERSION,)
        )
        conn.commit()
    finally:
        conn.close()


def get_repo_root_hash() -> str | None:
    """Get a hash identifying the repo (for detecting history rewrites)."""
    try:
        # Use the initial commit SHA as repo identity
        result = subprocess.run(
            ["git", "rev-list", "--max-parents=0", "HEAD"],
            cwd=DATA_DIR,
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
            cwd=DATA_DIR,
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
            cwd=DATA_DIR,
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
            (sha,)
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
            (sha,)
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
            (hash_value,)
        )
        conn.commit()
    finally:
        conn.close()


def record_processed_commit(sha: str, branch: str, note: str | None = None) -> None:
    """Record a processed commit."""
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO processed_commits (sha, branch, note, processed_at) VALUES (?, ?, ?, datetime('now'))",
            (sha, branch, note)
        )
        conn.execute(
            "UPDATE repo_state SET last_processed_sha = ?, last_updated = datetime('now') WHERE id = 1",
            (sha,)
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
            (limit,)
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


def classify_location(file_path: Path) -> str:
    """Classify a file's location (inbox, atlas, meta, or root)."""
    try:
        file_path = file_path.resolve()
        if file_path.is_relative_to(INBOX_DIR.resolve()):
            return "inbox"
        if file_path.is_relative_to(ATLAS_DIR.resolve()):
            return "atlas"
        if file_path.is_relative_to(META_DIR.resolve()):
            return "meta"
    except (ValueError, RuntimeError):
        pass
    return "root"


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of file contents."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def update_file_state(file_path: Path) -> FileInfo:
    """Update the state tracking for a file."""
    abs_path = file_path.resolve()
    rel_path = str(abs_path.relative_to(DATA_DIR.resolve()))
    stat = abs_path.stat()
    content_hash = compute_file_hash(abs_path)
    location = classify_location(abs_path)

    conn = get_db_connection()
    try:
        conn.execute(
            """INSERT OR REPLACE INTO file_state
               (file_path, location, content_hash, mtime, size, last_checked)
               VALUES (?, ?, ?, ?, ?, datetime('now'))""",
            (rel_path, location, content_hash, stat.st_mtime, stat.st_size)
        )
        conn.commit()

        return FileInfo(
            file_path=rel_path,
            location=location,
            content_hash=content_hash,
            mtime=stat.st_mtime,
            size=stat.st_size,
            last_checked=datetime.now().isoformat(),
        )
    finally:
        conn.close()


def get_file_state(file_path: Path) -> FileInfo | None:
    """Get the tracked state for a file."""
    abs_path = file_path.resolve()
    try:
        rel_path = str(abs_path.relative_to(DATA_DIR.resolve()))
    except ValueError:
        return None

    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT file_path, location, content_hash, mtime, size, last_checked FROM file_state WHERE file_path = ?",
            (rel_path,)
        ).fetchone()
        if row:
            return FileInfo(
                file_path=row["file_path"],
                location=row["location"],
                content_hash=row["content_hash"],
                mtime=row["mtime"],
                size=row["size"],
                last_checked=row["last_checked"],
            )
        return None
    finally:
        conn.close()


def remove_file_state(file_path: Path) -> None:
    """Remove tracking for a deleted file."""
    abs_path = file_path.resolve()
    try:
        rel_path = str(abs_path.relative_to(DATA_DIR.resolve()))
    except ValueError:
        return

    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM file_state WHERE file_path = ?", (rel_path,))
        conn.commit()
    finally:
        conn.close()


def get_files_by_location(location: str) -> list[FileInfo]:
    """Get all tracked files in a location."""
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT file_path, location, content_hash, mtime, size, last_checked FROM file_state WHERE location = ?",
            (location,)
        ).fetchall()
        return [
            FileInfo(
                file_path=row["file_path"],
                location=row["location"],
                content_hash=row["content_hash"],
                mtime=row["mtime"],
                size=row["size"],
                last_checked=row["last_checked"],
            )
            for row in rows
        ]
    finally:
        conn.close()


def get_file_counts_by_location() -> dict[str, int]:
    """Get count of tracked files by location."""
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT location, COUNT(*) as count FROM file_state GROUP BY location"
        ).fetchall()
        return {row["location"]: row["count"] for row in rows}
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
            cwd=DATA_DIR,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            return [line[3:] for line in result.stdout.strip().split("\n") if line]
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return []


def get_dirty_summary() -> dict[str, int]:
    """Get summary of dirty files by location."""
    dirty = get_dirty_files()
    summary: dict[str, int] = {"inbox": 0, "atlas": 0, "meta": 0, "root": 0}

    for file_path in dirty:
        path = DATA_DIR / file_path
        location = classify_location(path)
        summary[location] = summary.get(location, 0) + 1

    return summary


def cleanup_old_commits(keep_count: int = 100) -> int:
    """Remove old processed commit records, keeping the most recent ones.

    Returns the number of records deleted.
    """
    conn = get_db_connection()
    try:
        # Get IDs to keep
        rows = conn.execute(
            "SELECT id FROM processed_commits ORDER BY processed_at DESC LIMIT ?",
            (keep_count,)
        ).fetchall()
        keep_ids = [row["id"] for row in rows]

        if not keep_ids:
            return 0

        # Delete older records
        placeholders = ",".join("?" * len(keep_ids))
        cursor = conn.execute(
            f"DELETE FROM processed_commits WHERE id NOT IN ({placeholders})",
            keep_ids
        )
        deleted = cursor.rowcount
        conn.commit()
        return deleted
    finally:
        conn.close()


def cleanup_stale_files() -> int:
    """Remove file state entries for files that no longer exist.

    Returns the number of records deleted.
    """
    conn = get_db_connection()
    try:
        rows = conn.execute("SELECT id, file_path FROM file_state").fetchall()
        to_delete = []

        for row in rows:
            full_path = DATA_DIR / row["file_path"]
            if not full_path.exists():
                to_delete.append(row["id"])

        if to_delete:
            placeholders = ",".join("?" * len(to_delete))
            conn.execute(
                f"DELETE FROM file_state WHERE id IN ({placeholders})",
                to_delete
            )
            conn.commit()

        return len(to_delete)
    finally:
        conn.close()


# --- Reconciliation functions ---


def get_changes_since_sha(from_sha: str | None) -> list[ChangedFile]:
    """Get list of changed files since a given SHA.

    Uses git diff to detect additions, modifications, deletions, and renames.
    """
    if from_sha is None:
        # No previous SHA, return all tracked files
        return get_all_current_files()

    try:
        # Use git diff with rename detection
        result = subprocess.run(
            ["git", "diff", "--name-status", "-M", from_sha, "HEAD"],
            cwd=DATA_DIR,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return []

        changes: list[ChangedFile] = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue

            parts = line.split("\t")
            status_code = parts[0]

            if status_code.startswith("R"):  # Rename
                old_path = parts[1]
                new_path = parts[2]
                changes.append(ChangedFile(
                    path=new_path,
                    location=classify_location(DATA_DIR / new_path),
                    status="renamed",
                    old_path=old_path,
                ))
            elif status_code == "A":  # Added
                file_path = parts[1]
                changes.append(ChangedFile(
                    path=file_path,
                    location=classify_location(DATA_DIR / file_path),
                    status="added",
                    old_path=None,
                ))
            elif status_code == "M":  # Modified
                file_path = parts[1]
                changes.append(ChangedFile(
                    path=file_path,
                    location=classify_location(DATA_DIR / file_path),
                    status="modified",
                    old_path=None,
                ))
            elif status_code == "D":  # Deleted
                file_path = parts[1]
                changes.append(ChangedFile(
                    path=file_path,
                    location=classify_location(DATA_DIR / file_path),
                    status="deleted",
                    old_path=None,
                ))

        return changes
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def get_all_current_files() -> list[ChangedFile]:
    """Get all tracked files in the repo as 'added' changes."""
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=DATA_DIR,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return []

        return [
            ChangedFile(
                path=f,
                location=classify_location(DATA_DIR / f),
                status="added",
                old_path=None,
            )
            for f in result.stdout.strip().split("\n")
            if f
        ]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def generate_maintenance_tasks(changes: list[ChangedFile]) -> list[str]:
    """Generate maintenance task descriptions based on detected changes.

    Source-of-truth rules:
    - Inbox changes: process as normal ingestion
    - Atlas changes: never auto-rewrite; generate review tasks
    - Meta changes: can be regenerated; flag for reindex
    """
    tasks: list[str] = []

    inbox_changes = [c for c in changes if c["location"] == "inbox"]
    atlas_changes = [c for c in changes if c["location"] == "atlas"]
    meta_changes = [c for c in changes if c["location"] == "meta"]

    # Inbox: trigger gardener processing
    if inbox_changes:
        added = [c for c in inbox_changes if c["status"] == "added"]
        if added:
            tasks.append(f"Process {len(added)} new inbox file(s)")

    # Atlas: manual edits are source of truth - generate review tasks only
    if atlas_changes:
        modified = [c for c in atlas_changes if c["status"] == "modified"]
        added = [c for c in atlas_changes if c["status"] == "added"]
        deleted = [c for c in atlas_changes if c["status"] == "deleted"]
        renamed = [c for c in atlas_changes if c["status"] == "renamed"]

        if modified:
            tasks.append(f"Review {len(modified)} modified note(s) in atlas (manual edits preserved)")
        if added:
            tasks.append(f"Index {len(added)} new note(s) added to atlas")
        if deleted:
            tasks.append(f"Clean up references to {len(deleted)} deleted note(s)")
        if renamed:
            tasks.append(f"Update links for {len(renamed)} renamed note(s)")

    # Meta: derived artifacts can be regenerated
    if meta_changes:
        tasks.append("Regenerate meta indexes (derived artifacts may be stale)")

    # Cross-cutting tasks
    if any(c["status"] in ("renamed", "deleted") for c in changes):
        tasks.append("Refresh backlinks and cross-references")

    if atlas_changes or meta_changes:
        tasks.append("Run consistency check on knowledge base")

    return tasks


def record_reconcile_run(
    from_sha: str | None,
    to_sha: str | None,
    changes: list[ChangedFile],
    tasks: list[str],
) -> int:
    """Record a reconciliation run in the database.

    Returns the run ID.
    """
    import json

    inbox_changes = len([c for c in changes if c["location"] == "inbox"])
    atlas_changes = len([c for c in changes if c["location"] == "atlas"])
    meta_changes = len([c for c in changes if c["location"] == "meta"])

    conn = get_db_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO reconcile_runs
               (from_sha, to_sha, files_changed, inbox_changes, atlas_changes, meta_changes, tasks_generated)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (from_sha, to_sha, len(changes), inbox_changes, atlas_changes, meta_changes, json.dumps(tasks))
        )
        run_id = cursor.lastrowid

        # Update last reconcile SHA
        if to_sha:
            conn.execute(
                "UPDATE repo_state SET last_reconcile_sha = ?, last_updated = datetime('now') WHERE id = 1",
                (to_sha,)
            )

        conn.commit()
        return run_id
    finally:
        conn.close()


def get_last_reconcile_run() -> ReconcileRun | None:
    """Get the most recent reconciliation run."""
    import json

    conn = get_db_connection()
    try:
        row = conn.execute(
            """SELECT id, run_at, from_sha, to_sha, files_changed,
                      inbox_changes, atlas_changes, meta_changes, tasks_generated
               FROM reconcile_runs ORDER BY run_at DESC LIMIT 1"""
        ).fetchone()

        if row:
            return ReconcileRun(
                id=row["id"],
                run_at=row["run_at"],
                from_sha=row["from_sha"],
                to_sha=row["to_sha"],
                files_changed=row["files_changed"],
                inbox_changes=row["inbox_changes"],
                atlas_changes=row["atlas_changes"],
                meta_changes=row["meta_changes"],
                tasks_generated=json.loads(row["tasks_generated"]) if row["tasks_generated"] else [],
            )
        return None
    finally:
        conn.close()


def run_reconcile() -> ReconcileRun:
    """Run reconciliation: detect changes, generate tasks, record run.

    This is the main entry point for the reconcile operation.
    """
    init_db()

    # Get current state
    repo_state = get_repo_state()
    from_sha = repo_state["last_reconcile_sha"] or repo_state["last_processed_sha"]
    to_sha = get_current_head()

    # Detect changes
    changes = get_changes_since_sha(from_sha)

    # Generate maintenance tasks
    tasks = generate_maintenance_tasks(changes)

    # Record the run
    run_id = record_reconcile_run(from_sha, to_sha, changes, tasks)

    return ReconcileRun(
        id=run_id,
        run_at=datetime.now().isoformat(),
        from_sha=from_sha,
        to_sha=to_sha,
        files_changed=len(changes),
        inbox_changes=len([c for c in changes if c["location"] == "inbox"]),
        atlas_changes=len([c for c in changes if c["location"] == "atlas"]),
        meta_changes=len([c for c in changes if c["location"] == "meta"]),
        tasks_generated=tasks,
    )


# --- Edit provenance tracking ---


def record_provenance(
    file_path: str | Path,
    source: str,
    commit_sha: str | None = None,
    metadata: dict | None = None,
) -> int:
    """Record edit provenance for a file.

    Args:
        file_path: Path to the file (relative to DATA_DIR)
        source: Source identifier (use PROVENANCE_* constants)
        commit_sha: Optional commit SHA associated with this edit
        metadata: Optional additional context as dict

    Returns:
        The provenance record ID
    """
    import json

    if isinstance(file_path, Path):
        try:
            file_path = str(file_path.resolve().relative_to(DATA_DIR.resolve()))
        except ValueError:
            file_path = str(file_path)

    conn = get_db_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO edit_provenance (file_path, commit_sha, source, metadata)
               VALUES (?, ?, ?, ?)""",
            (file_path, commit_sha, source, json.dumps(metadata) if metadata else None)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_file_provenance(file_path: str | Path, limit: int = 10) -> list[EditProvenance]:
    """Get provenance history for a file.

    Args:
        file_path: Path to the file (relative to DATA_DIR)
        limit: Maximum number of records to return

    Returns:
        List of provenance records, most recent first
    """
    import json

    if isinstance(file_path, Path):
        try:
            file_path = str(file_path.resolve().relative_to(DATA_DIR.resolve()))
        except ValueError:
            file_path = str(file_path)

    conn = get_db_connection()
    try:
        rows = conn.execute(
            """SELECT id, file_path, commit_sha, source, recorded_at, metadata
               FROM edit_provenance
               WHERE file_path = ?
               ORDER BY recorded_at DESC
               LIMIT ?""",
            (file_path, limit)
        ).fetchall()

        return [
            EditProvenance(
                id=row["id"],
                file_path=row["file_path"],
                commit_sha=row["commit_sha"],
                source=row["source"],
                recorded_at=row["recorded_at"],
                metadata=json.loads(row["metadata"]) if row["metadata"] else None,
            )
            for row in rows
        ]
    finally:
        conn.close()


def get_provenance_by_source(source: str, limit: int = 50) -> list[EditProvenance]:
    """Get all provenance records for a given source.

    Args:
        source: Source identifier to filter by
        limit: Maximum number of records to return

    Returns:
        List of provenance records, most recent first
    """
    import json

    conn = get_db_connection()
    try:
        rows = conn.execute(
            """SELECT id, file_path, commit_sha, source, recorded_at, metadata
               FROM edit_provenance
               WHERE source = ?
               ORDER BY recorded_at DESC
               LIMIT ?""",
            (source, limit)
        ).fetchall()

        return [
            EditProvenance(
                id=row["id"],
                file_path=row["file_path"],
                commit_sha=row["commit_sha"],
                source=row["source"],
                recorded_at=row["recorded_at"],
                metadata=json.loads(row["metadata"]) if row["metadata"] else None,
            )
            for row in rows
        ]
    finally:
        conn.close()


def format_commit_message(source: str, action: str) -> str:
    """Format a commit message with proper source attribution.

    Standard commit message formats:
    - Gardener: "Gardener: <action>"
    - Manual: "Manual: <action>"
    - External: "External[<tool>]: <action>"

    Args:
        source: Source identifier (use PROVENANCE_* constants)
        action: Description of the action taken

    Returns:
        Formatted commit message
    """
    if source == PROVENANCE_GARDENER:
        return f"Gardener: {action}"
    elif source == PROVENANCE_MANUAL:
        return f"Manual: {action}"
    elif source.startswith("external:"):
        tool = source.split(":", 1)[1]
        return f"External[{tool}]: {action}"
    else:
        return f"{source}: {action}"


def parse_commit_source(message: str) -> str:
    """Parse source from a commit message.

    Args:
        message: Git commit message

    Returns:
        Source identifier
    """
    if message.startswith("Gardener:"):
        return PROVENANCE_GARDENER
    elif message.startswith("Manual:"):
        return PROVENANCE_MANUAL
    elif message.startswith("External["):
        # Extract tool name from "External[tool]: action"
        end = message.find("]:")
        if end > 9:
            tool = message[9:end]
            return f"external:{tool}"
    elif message.startswith("Athena:"):
        return "athena"
    return "unknown"
