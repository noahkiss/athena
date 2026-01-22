"""Database utilities for Gardener state tracking."""

import sqlite3

import config

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
    location TEXT NOT NULL,  -- 'archive', 'inbox', 'atlas', 'meta', 'root'
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

-- Track individual API calls for usage monitoring and rate limiting
CREATE TABLE IF NOT EXISTS api_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    backend TEXT NOT NULL,
    operation TEXT NOT NULL,  -- 'classify', 'refine', 'ask'
    timestamp TEXT DEFAULT (datetime('now')),
    success INTEGER DEFAULT 1,  -- 1 for success, 0 for failure
    error TEXT
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
CREATE INDEX IF NOT EXISTS idx_api_calls_timestamp ON api_calls(timestamp);
CREATE INDEX IF NOT EXISTS idx_api_calls_backend ON api_calls(backend);
CREATE INDEX IF NOT EXISTS idx_api_calls_operation ON api_calls(operation);
"""


def get_db_connection() -> sqlite3.Connection:
    """Get a connection to the state database."""
    config.STATE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.STATE_DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize the database schema."""
    conn = get_db_connection()
    try:
        conn.executescript(SCHEMA)
        # Initialize singleton repo_state row if not exists
        conn.execute("INSERT OR IGNORE INTO repo_state (id) VALUES (1)")
        # Set schema version
        conn.execute(
            "INSERT OR REPLACE INTO schema_version (version) VALUES (?)",
            (SCHEMA_VERSION,),
        )
        conn.commit()
    finally:
        conn.close()
