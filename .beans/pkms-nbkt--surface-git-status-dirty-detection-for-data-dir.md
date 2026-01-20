---
# pkms-nbkt
title: Surface git status + dirty detection for data dir
status: completed
type: feature
priority: normal
created_at: 2026-01-20T05:49:54Z
updated_at: 2026-01-20T17:29:22Z
parent: pkms-wsuj
---

Expose data-repo state (current HEAD, last-seen commit from Gardener, dirty flag, changed files summary, /inbox vs /atlas vs /meta counts) via /api/status and optionally in Scribe UI. This supports manual edit awareness without auto-committing changes.

## Checklist
- [x] Add git status/HEAD info to Gardener status response (guarded by git availability)
  - `GitState` model in main.py with: available, current_head, current_branch
  - Guarded: returns `available=false` if git not installed or not a repo
- [x] Include last-seen commit info from SQLite/state
  - `last_processed_sha` and `last_seen_sha` from state.py
  - `repo_identity_valid` flag for detecting history rewrites
- [x] Add summary counts by area (/inbox vs /atlas vs /meta) plus truncated file list
  - `dirty_by_location`: {"inbox": N, "atlas": N, "meta": N, "root": N}
  - `dirty_files_preview`: first 10 dirty file paths
  - `dirty_files`: total count
- [ ] Decide how to display in Scribe (banner, status panel, etc.)
  - API ready; Scribe UI deferred (separate frontend task)
  - Suggested: status indicator in header, expandable panel showing dirty files
- [x] Document env flags or config knobs
  - No new env flags needed; git detection is automatic
  - `.gardener/` state directory is gitignored
  - State tracking is optional (graceful fallback if unavailable)