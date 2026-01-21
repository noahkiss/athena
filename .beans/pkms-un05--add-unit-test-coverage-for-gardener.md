---
# pkms-un05
title: Add unit test coverage for gardener
status: completed
type: task
priority: normal
created_at: 2026-01-21T00:15:42Z
updated_at: 2026-01-21T01:52:04Z
---

No unit tests currently exist for the gardener backend. Only an E2E bash script exists (`scripts/test_e2e_full.sh`).

## Priority Areas

### High Priority
- `workers/gardener.py`: `classify_note()` - Core AI classification logic
- `workers/gardener.py`: `execute_action()`, `validate_action_path()` - Path validation and file operations
- `state.py`: SQLite operations for commit/file state tracking

### Medium Priority  
- `backends/openai.py`, `backends/anthropic.py`: AI backend implementations
- `main.py`: API endpoint handlers
- `bootstrap.py`: Knowledge base initialization

### Test Infrastructure Needed
- Add pytest to pyproject.toml dev dependencies
- Create `tests/` directory structure
- Add fixtures for FastAPI test client
- Add mock AI backends for deterministic testing

## Checklist
- [x] Add pytest and pytest-asyncio to dev dependencies
- [x] Create tests/ directory with conftest.py
- [x] Add unit tests for `classify_note()` with mock backends
- [x] Add unit tests for path validation (`validate_action_path`, `execute_action`)
- [x] Add unit tests for state.py SQLite operations
- [ ] Add API endpoint tests with FastAPI TestClient
- [x] Integrate with CI (see pkms-byys)

## Test Coverage Summary

**52 tests total across 4 test files:**

### test_xss_sanitization.py (10 tests)
- XSS protection for `format_refine_html()` and `format_ask_html()`

### test_json_parsing.py (13 tests)
- JSON extraction from LLM responses
- GardenerAction validation
- ParseError handling

### test_gardener_worker.py (12 tests)
- Path validation security (absolute paths, traversal, null bytes)
- File operations (create, append, task actions)
- classify_note with mock backend

### test_state.py (17 tests)
- Database initialization
- Repo state operations (SHA tracking)
- File state operations (hash, location)
- Provenance tracking
- Commit message formatting/parsing