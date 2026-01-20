---
# pkms-k2bg
title: Distinguish copy vs rename in snapshot state handling
status: completed
type: bug
created_at: 2026-01-20T21:22:21Z
updated_at: 2026-01-20T21:25:00Z
---

Copy status (C) incorrectly treated as rename, removing old path from state.

## Checklist
- [x] Distinguish R (rename) vs C (copy) status codes in snapshot parsing
  - Separate branches for 'R' and 'C' status codes
- [x] For renames: remove old path from state (file moved)
  - Calls `remove_file_state()` on old path
- [x] For copies: keep old path in state (file still exists)
  - Only adds new path, source file state preserved
- [x] Record provenance with 'copy' vs 'rename' action for audit trail
  - `{'action': 'rename', 'from': old_path}` vs `{'action': 'copy', 'from': old_path}`