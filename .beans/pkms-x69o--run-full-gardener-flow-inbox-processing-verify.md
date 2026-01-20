---
# pkms-x69o
title: Run full gardener flow (inbox -> processing -> verify)
status: completed
type: task
priority: normal
created_at: 2026-01-20T04:38:47Z
updated_at: 2026-01-20T04:44:02Z
---

Run end-to-end test: submit note to inbox, trigger gardener, verify atlas change and retrieval endpoints, using LiteLLM settings.

## Checklist
- [x] Submit note to /api/inbox
- [x] Trigger gardener and wait for processing
- [x] Verify atlas file created/updated
- [x] Verify browse/ask/refine with real data
