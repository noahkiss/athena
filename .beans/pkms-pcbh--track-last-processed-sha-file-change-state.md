---
# pkms-pcbh
title: Track last processed SHA + file change state
status: completed
type: feature
priority: high
created_at: 2026-01-20T05:50:18Z
updated_at: 2026-01-20T17:27:17Z
parent: pkms-wsuj
blocking:
    - pkms-nbkt
    - pkms-3bv5
---

Persist last-known git SHAs and file fingerprints in SQLite (preferred) or a state file to detect edits since last gardener run and avoid missing manual changes.

## Checklist
- [x] Add SQLite table for processed commits (sha, timestamp, branch, note)
  - Created `state.py` with `processed_commits` table
  - Added `aiosqlite` dependency to pyproject.toml
- [x] Store last seen vs last processed commit SHAs (db or state file fallback)
  - `repo_state` table with `last_seen_sha` and `last_processed_sha` columns
  - Bootstrap records baseline commit
  - Gardener records each commit after processing
- [x] Track per-file hash/mtime and classify changes by location (inbox vs atlas vs meta)
  - `file_state` table with hash, mtime, size, location
  - `classify_location()` function categorizes files
  - `update_file_state()` and `get_file_state()` for tracking
- [x] Track repo identity/history rewrites; force rescan if HEAD diverges from last seen
  - `repo_state.repo_root_hash` stores hash of initial commit
  - `check_repo_identity()` detects history rewrites
  - Exposed via `git.repo_identity_valid` in status
- [x] Expose state via /api/status for visibility and automation
  - Added `GitState` model with: current_head, current_branch, last_processed_sha, last_seen_sha, dirty_files, dirty_by_location, repo_identity_valid
  - `/api/status` now includes `git` field
- [x] Decide retention/cleanup policy for state data
  - `cleanup_old_commits(keep_count=100)` keeps last 100 commits
  - `cleanup_stale_files()` removes entries for deleted files
  - `.gardener/` directory added to .gitignore (not version controlled)