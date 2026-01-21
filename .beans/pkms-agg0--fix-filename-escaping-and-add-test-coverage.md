---
# pkms-agg0
title: Fix filename escaping and add test coverage
status: completed
type: task
priority: normal
created_at: 2026-01-21T06:40:56Z
updated_at: 2026-01-21T06:51:17Z
---

Address findings from codebase review:

## Checklist
- [x] Fix filename escaping in scribe/src/pages/api/inbox.ts
- [x] Add endpoint integration tests for /api/inbox, /api/ask, /api/refine
- [x] Add mock-based backend tests for LLM integration
- [x] Add MCP tool tests

## Changes Made

### XSS Fix
- Added `escapeHtml()` function to `scribe/src/pages/api/inbox.ts`
- Applied escaping to `data.filename` in response HTML

### New Test Files (59 tests total)

**test_endpoints.py** - API endpoint integration tests:
- Inbox: save, empty content, filename format
- Browse: root listing, directory, file content, 404, path traversal
- Archive: listing, file content, 404, path traversal
- Refine: empty content message, no backend, mocked backend
- Ask: empty question message, no backend, mocked backend
- Trigger-gardener: success, processes inbox

**test_backends.py** - LLM backend tests:
- OpenAI: initialization, classify (success, markdown JSON, invalid JSON), refine, ask
- Anthropic: initialization, classify (success, retries, max retries), refine, ask
- Factory: config without key, selects openai, selects anthropic
- GardenerAction validation: valid actions, invalid type, missing fields, extra fields

**test_mcp_tools.py** - MCP tool tests:
- read_notes: root listing, directory, file content, nonexistent, path traversal, search, hidden files
- add_note: creates file, filename format, rejects empty, creates inbox dir, preserves markdown, special chars
- Registration: server created, tools registered

All 140 tests pass (81 original + 59 new).