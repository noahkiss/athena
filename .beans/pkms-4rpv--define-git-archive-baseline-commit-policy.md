---
# pkms-4rpv
title: Define git archive baseline + commit policy
status: completed
type: feature
priority: high
created_at: 2026-01-20T05:50:01Z
updated_at: 2026-01-20T17:15:17Z
parent: pkms-wsuj
blocking:
    - pkms-pcbh
---

Clarify how the knowledge base becomes a git archive: initial repo setup, baseline commit, commit message conventions, and optional auto-commit for manual edits (manual edits are source of truth).

## Checklist
- [x] Decide whether bootstrap should make a baseline commit
  - YES: Bootstrap now makes baseline commit "Athena: Initialize knowledge base" after git init
- [x] Add/confirm .gitignore policy for data dir (logs, tmp, cache)
  - Added `.gitignore` to bootstrap with: logs/, tmp/, cache/, *.log, .DS_Store, editor artifacts, __pycache__
- [x] Define commit message format for gardener vs manual vs external tools
  - `Athena: <action>` - system/bootstrap commits
  - `Gardener: <action>` - automated processing (already implemented)
  - `Manual: <action>` - snapshot/manual commits
  - `External[source]: <action>` - future: external tool commits (pkms-ty7n)
- [x] Ensure gardener commits only touched files (avoid staging manual edits)
  - Already implemented: `git_commit()` in gardener.py stages single file only
- [x] Decide policy for auto-committing manual edits (default off) and how to record in SQLite
  - Policy: OFF by default (manual edits are source of truth, user controls when to commit)
  - SQLite tracking deferred to pkms-pcbh
- [x] Add optional snapshot command/endpoint to commit dirty changes on demand
  - Added `POST /api/snapshot` endpoint with optional custom message