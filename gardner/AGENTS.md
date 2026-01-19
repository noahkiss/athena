# GARDNER DEVELOPMENT CONTEXT (Live Document)

**Role:** You are a Senior Python Backend Engineer.
**Project:** "The Gardener" - A background service and API for Project Athena.

**Tech Stack:**
- **Runtime:** Python 3.12+
- **Package Manager:** uv
- **API Framework:** FastAPI
- **AI Integration:** Anthropic Python SDK (Claude Sonnet for classification, Haiku for refine)
- **MCP:** Model Context Protocol server for external AI access

## Project Structure

```
gardner/
├── main.py              # FastAPI application
├── mcp_server.py        # MCP server for external AI tools
├── workers/
│   └── gardener.py      # Inbox processing worker
├── pyproject.toml       # Dependencies (uv)
└── Dockerfile
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/inbox` | POST | Accept note content, save to inbox |
| `/api/status` | GET | Health check |
| `/api/trigger-gardener` | POST | Manually trigger inbox processing |
| `/api/refine` | POST | AI-assisted suggestions (Haiku) |
| `/api/browse/{path}` | GET | Browse atlas directory/files |

## Worker Logic

The gardener worker (`workers/gardener.py`):
1. Scans `/data/inbox` for `.md` files
2. Reads `/data/AGENTS.md` + `/data/GARDNER.md` for context
3. Sends each note to Claude Sonnet for classification
4. Executes file operation (create/append/task)
5. Commits changes to Git
6. Deletes processed inbox file

**Coding Standards:**
- Type hinting is mandatory
- Use `pydantic` for data validation
- Keep the logic "Headless": The API should not know about the Frontend implementation
- All file operations target `/data` (Docker volume mount)
