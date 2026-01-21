---
# pkms-eti7
title: Optional auth for Gardener/MCP endpoints
status: completed
type: feature
priority: normal
created_at: 2026-01-21T00:10:34Z
updated_at: 2026-01-21T05:04:59Z
---

Add optional access control for the HTTP API and MCP tool endpoints so self-hosted deployments can lock down access when exposed beyond localhost. Include a minimal shared-token option that is opt-in and disabled by default.

Refs: gardener/main.py (API routes), gardener/mcp_tools.py (MCP tools), docker-compose.yml (port exposure)

## Checklist
- [x] Define the default-off token scheme (e.g., ATHENA_AUTH_TOKEN) and accepted header(s)
- [x] Add auth dependency and middleware/route guard
- [x] Apply guards to /api/* and /mcp when configured
- [x] Return clear 401/403 responses on missing/invalid token
- [x] Document configuration in README/.env.example
- [x] Add tests or update E2E script to cover enabled/disabled modes
