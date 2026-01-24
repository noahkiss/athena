---
# pkms-iexi
title: Rename project directory from pkms to athena
status: completed
type: task
created_at: 2026-01-24T18:10:19Z
updated_at: 2026-01-24T18:18:00Z
---

Rename the project root directory from pkms to athena and update all Claude config files that reference the old path.

## Completed

- [x] Updated `AGENTS.md` - project structure diagram
- [x] Updated `README.md` - MCP config examples
- [x] Updated `docker-compose.yml` - commented example paths
- [x] Updated `pyproject.toml` - project name from `athena-pkms` to `athena`
- [x] Updated `gardener/AGENTS.md` - MCP config example
- [x] Updated `gardener/mcp_server.py` - docstring and server name
- [x] Updated `gardener/mcp_tools.py` - docstring and FastMCP name
- [x] Merged Claude config directories (`~/.claude/projects/-home-flight-develop-pkms` → `-home-flight-develop-athena`)