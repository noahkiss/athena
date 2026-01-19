---
# pkms-mgel
title: Integrate MCP server with FastAPI using streamable-http transport
status: completed
type: feature
priority: normal
created_at: 2026-01-19T16:10:49Z
updated_at: 2026-01-19T16:28:21Z
---

Refactor the MCP server to use FastMCP with streamable-http transport and mount it to the existing FastAPI app. This allows Claude Code to connect via HTTP instead of stdio, making the server more extensible.

## Checklist
- [x] Add FastMCP integration to main.py
- [x] Implement read_notes tool using existing browse logic
- [x] Implement add_note tool using existing inbox logic
- [x] Add lifespan handler for MCP session manager
- [x] Update pyproject.toml if needed (not needed - mcp already installed)
- [x] Test the MCP server endpoint
- [x] Document how to configure Claude Code to use it

## Configuration

To configure Claude Code to use this MCP server:

```bash
claude mcp add --transport http athena-pkms http://localhost:8000/mcp
```

Or add to `.mcp.json` in project root:

```json
{
  "mcpServers": {
    "athena-pkms": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## Tools Exposed

- **read_notes**: Browse/read from the atlas knowledge base
- **add_note**: Add notes to the inbox for processing