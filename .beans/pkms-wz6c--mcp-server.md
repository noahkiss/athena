---
# pkms-wz6c
title: MCP server
status: completed
type: feature
priority: normal
created_at: 2026-01-19T08:02:20Z
updated_at: 2026-01-19T08:40:45Z
parent: pkms-38nj
---

Model Context Protocol server for external AI access.

## Tools to expose
- `read_notes(path?, query?)` - Read content from /data
- `add_note(content)` - Write to /data/inbox

## Requirements
- Use mcp Python library
- Expose via stdio or SSE
- Update docker-compose to run/expose the server

## Use case
Connect desktop Claude app or other AI tools to query/add notes.