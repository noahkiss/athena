---
# pkms-ecuc
title: Fix MCP mount path/order to avoid API shadowing
status: completed
type: bug
priority: normal
created_at: 2026-01-20T00:31:41Z
updated_at: 2026-01-20T03:42:57Z
---

FastAPI mounts FastMCP app at '/' before API routes, which likely intercepts /api endpoints. Adjust mount path to /mcp or move mount after API routes (verify FastMCP expectations) and update tests/docs as needed.\n\n## Checklist\n- [x] Confirm routing behavior with current mount\n- [x] Update FastAPI mount path/order\n- [x] Verify /api endpoints and /mcp both work\n- [x] Update docs if mount path changes
