---
# pkms-es7g
title: Fix edge cases in reconcile details and snapshot parsing
status: completed
type: bug
created_at: 2026-01-20T19:53:15Z
updated_at: 2026-01-20T20:15:00Z
---

Follow-up issues:

## Checklist
- [x] Medium: include_details uses stale from_sha when identity invalid - use result["from_sha"] instead
  - Now uses `result["from_sha"]` which reflects actual scan start (including full scan on identity mismatch)
- [x] Medium: snapshot doesn't parse git status codes - deletes/renames mishandled
  - Parse git status --porcelain output for D (delete) and R (rename) codes
  - Deletes call `remove_file_state()`, renames track old_path
- [x] Low: last_seen_sha only updated on processed commits - update when HEAD observed
  - `get_git_state()` now calls `update_last_seen_sha()` when HEAD differs from stored value