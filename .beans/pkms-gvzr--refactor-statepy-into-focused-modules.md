---
# pkms-gvzr
title: Refactor state.py into focused modules
status: completed
type: task
priority: low
created_at: 2026-01-21T00:15:45Z
updated_at: 2026-01-21T05:12:18Z
---

The `gardener/state.py` file is 30KB and handles too many responsibilities, making it difficult to test and maintain.

## Current Responsibilities
- Git commit tracking
- File state management  
- Change reconciliation
- Edit provenance tracking
- SQLite database operations

## Suggested Split

### `git_state.py`
- `get_current_head()`, `get_current_branch()`
- `get_commit_info()`, `get_commits_since()`
- Git subprocess operations

### `file_state.py`
- `get_file_state()`, `get_all_file_states()`
- File hash calculations
- Reconciliation logic

### `provenance.py`
- Edit tracking and attribution
- Provenance queries

### `db.py` (shared)
- Database connection management
- Schema definitions
- Common query utilities

## Benefits
- Easier to test individual modules
- Clearer separation of concerns
- Reduced cognitive load when debugging

## Checklist
- [x] Create new module files
- [x] Move functions to appropriate modules
- [x] Update imports throughout gardener/
- [x] Ensure existing E2E tests still pass
- [x] Add module-level docstrings explaining purpose
