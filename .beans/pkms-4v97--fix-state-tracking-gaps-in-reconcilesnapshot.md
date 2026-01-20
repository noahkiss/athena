---
# pkms-4v97
title: Fix state tracking gaps in reconcile/snapshot
status: completed
type: bug
priority: normal
created_at: 2026-01-20T18:15:53Z
updated_at: 2026-01-20T18:21:24Z
---

Issues found in review:

## Checklist
- [x] High: reconcile should report uncommitted changes (currently only sees committed history)
  - Added `uncommitted_files`, `uncommitted_by_location`, `uncommitted_warning` to ReconcileResponse
  - Clear message: "Run /api/snapshot first to include them"
- [x] Medium: last_seen_sha never updated - update it when commits are recorded
  - `record_processed_commit()` now updates both last_processed_sha and last_seen_sha
- [x] Medium: /api/snapshot should update state DB, file_state, and provenance
  - Snapshot now calls `record_processed_commit()`, `update_file_state()`, `record_provenance()`
- [x] Low: reconcile should check repo identity and force full scan if history rewritten
  - `run_reconcile()` checks identity, forces full scan if invalid, updates repo hash