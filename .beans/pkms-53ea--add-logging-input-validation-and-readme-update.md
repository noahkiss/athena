---
# pkms-53ea
title: Add logging, input validation, and README update
status: completed
type: task
priority: normal
created_at: 2026-01-21T06:58:05Z
updated_at: 2026-01-21T07:04:04Z
---

Final polish before release:

## Checklist
- [x] Add structured logging with configurable levels to gardener
- [x] Add input validation to inbox endpoint (reject empty, cap size)
- [x] Update README to note single-user self-hosted design

## Changes Made

### Logging (`config.py`, `main.py`)
- Added `setup_logging()` function in config.py
- Configurable via `LOG_LEVEL` env var (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Configurable format via `LOG_FORMAT` env var
- Quiets noisy libraries (httpx, watchfiles, uvicorn.access) unless DEBUG
- Added startup/shutdown logging in main.py lifespan
- Added info/error logging for inbox operations

### Input Validation (`main.py`)
- Inbox endpoint now rejects empty/whitespace-only content (400)
- Inbox endpoint now rejects content > MAX_CONTENT_SIZE (default 100KB)
- `MAX_CONTENT_SIZE` configurable via env var

### README Updates
- Added note at top: "designed for single-user, self-hosted deployments"
- Added Logging section with `LOG_LEVEL` and `LOG_FORMAT` documentation

### .env.example
- Added `LOG_LEVEL=INFO`
- Added `MAX_CONTENT_SIZE=102400` (commented)

### Tests
- Updated inbox tests: now expects 400 for empty/whitespace
- Added test for oversized content rejection
- All 142 tests pass