---
# pkms-hsh6
title: Clean up unused import and fix git status path parsing
status: completed
type: bug
created_at: 2026-01-20T21:01:16Z
updated_at: 2026-01-20T21:05:00Z
---

Final cleanup from code review:

## Checklist
- [x] Low: Remove unused get_repo_state import in reconcile_changes (gardener/main.py:409)
- [x] Low: Use git status --porcelain -z with NUL-split parsing for proper handling of quoted/escaped paths (spaces, tabs, Unicode) in gardener/main.py:304-351
  - Changed to `git status --porcelain -z` for NUL-separated output
  - Parse bytes with proper decoding (utf-8 with replace for invalid chars)
  - Handle rename/copy format where old path is in next NUL-separated entry