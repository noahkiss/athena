---
# pkms-edeg
title: Automated Gardener Processing
status: in-progress
type: feature
priority: normal
created_at: 2026-01-19T21:11:29Z
updated_at: 2026-01-19T21:11:29Z
parent: pkms-y140
---

Trigger gardener automatically instead of requiring manual API calls.

## Approaches Considered

### 1. File Watcher (Recommended)
Watch inbox directory for new files, trigger processing after a debounce period.
- **Pros**: Immediate processing, no external dependencies
- **Cons**: Requires inotify/fswatch, Docker volume considerations

### 2. Scheduled Polling
Run gardener on a fixed interval (e.g., every 5 minutes).
- **Pros**: Simple, works everywhere
- **Cons**: Delayed processing, unnecessary work if inbox empty

### 3. Webhook from Scribe
Scribe triggers gardener after successful inbox submission.
- **Pros**: Immediate, explicit
- **Cons**: Coupling between services, harder to add other ingest sources

## Recommended Design

**Hybrid approach**: File watcher with configurable fallback to polling.

```python
# Configuration
GARDENER_AUTO=true|false          # Enable automation
GARDENER_MODE=watch|poll          # How to detect new notes
GARDENER_POLL_INTERVAL=300        # Seconds between polls (if polling)
GARDENER_DEBOUNCE=5               # Seconds to wait after last file change
```

### Implementation

1. **Background task** that runs during FastAPI lifespan
2. **Watchfiles library** for cross-platform file watching (pure Python)
3. **Debounce logic** to batch rapid submissions
4. **Graceful handling** when inbox is empty

```python
# Pseudocode
async def gardener_watcher():
    async for changes in awatch(INBOX_DIR):
        await asyncio.sleep(DEBOUNCE_SECONDS)
        process_inbox()
```

## Checklist
- [x] Add watchfiles to dependencies
- [x] Create gardener automation config options
- [x] Implement file watcher with debounce
- [x] Implement polling fallback
- [x] Add lifespan task to start watcher
- [x] Add automation status to /api/status endpoint
- [x] Handle errors gracefully (don't crash watcher on failures)
- [ ] Document configuration in README/AGENTS.md
- [ ] Test with rapid file submissions
- [ ] Test with Docker volume mounts