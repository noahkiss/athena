---
# pkms-mf4j
title: Update local LiteLLM env and run smoke tests
status: completed
type: task
priority: normal
created_at: 2026-01-20T04:31:08Z
updated_at: 2026-01-20T04:34:31Z
---

Use provided LiteLLM base URL/key/models, choose a non-conflicting DATA_DIR, and run local backend smoke tests.

## Checklist
- [x] Update local .env with LiteLLM settings and DATA_DIR
- [x] Create local data directory
- [x] Run local backend smoke tests (/api/status, /api/refine, /api/ask, /mcp)
