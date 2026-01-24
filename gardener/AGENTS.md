# GARDENER DEVELOPMENT CONTEXT (Live Document)

**Role:** You are a Senior Python Backend Engineer.
**Project:** "The Gardener" - A background service and API for Project Athena.

**Tech Stack:**
- **Runtime:** Python 3.12+
- **Package Manager:** uv
- **API Framework:** FastAPI
- **AI Integration:** Configurable backends (OpenAI-compatible, Anthropic native)
- **MCP:** Model Context Protocol server for external AI access

## Project Structure

```
gardener/
├── main.py              # FastAPI application + MCP server mount
├── config.py            # Centralized configuration
├── automation.py        # File watcher and polling for auto-processing
├── mcp_tools.py         # MCP tools (FastMCP with streamable-http)
├── backends/
│   ├── base.py          # GardenerBackend abstract base class
│   ├── openai.py        # OpenAI-compatible backend
│   ├── anthropic.py     # Native Anthropic Claude backend
│   └── __init__.py      # Factory function
├── workers/
│   └── gardener.py      # Inbox processing worker
├── pyproject.toml       # Dependencies (uv)
└── Dockerfile
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | Health check (includes backend & automation info) |
| `/api/bootstrap` | POST | Initialize knowledge base |
| `/api/inbox` | POST | Accept note content, save to inbox |
| `/api/trigger-gardener` | POST | Manually trigger inbox processing |
| `/api/refine` | POST | AI-assisted suggestions |
| `/api/ask` | POST | Ask questions over the knowledge base |
| `/api/browse/{path}` | GET | Browse atlas directory/files |
| `/api/archive/{path}` | GET | Browse archived inbox notes |
| `/mcp` | POST | MCP server endpoint (JSON-RPC) |

## Configuration

### AI Backend
```bash
GARDENER_BACKEND=openai|anthropic  # Default: openai
AI_API_KEY=...                      # Or OPENAI_API_KEY / ANTHROPIC_API_KEY
AI_MODEL_THINKING=gpt-4o            # Model for classification
AI_MODEL_FAST=gpt-4o-mini           # Model for refinement/quick tasks
AI_MODEL=gpt-4o                     # Legacy fallback for both models
AI_BASE_URL=...                     # OpenAI backend only
AI_TIMEOUT=120                      # Request timeout in seconds
```

### Automation
```bash
GARDENER_AUTO=true|false            # Enable auto-processing (default: false)
GARDENER_MODE=watch|poll            # Detection mode (default: watch)
GARDENER_DEBOUNCE=5.0               # Seconds after last change (watch mode)
GARDENER_POLL_INTERVAL=300          # Seconds between polls (poll mode)
```

### Authentication (Optional)
```bash
# Enable shared-token auth for /api/* and /mcp endpoints
ATHENA_AUTH_TOKEN=...               # When set, auth is required
```

Send the token via:
- `Authorization: Bearer <token>`
- `X-Auth-Token: <token>`

## Backend Architecture

The gardener uses a pluggable backend system:

```
GardenerBackend (ABC)
├── classify(note_content, filename, context) -> GardenerAction
├── refine(content, related_context) -> str
└── close()

Implementations:
├── OpenAIBackend  - OpenAI-compatible APIs (LiteLLM, Azure, Ollama)
└── AnthropicBackend - Native Claude SDK
```

Use `get_backend()` to get a configured instance based on environment.

## MCP Server

The MCP server is integrated into the FastAPI app using FastMCP with streamable-http transport.

**Tools exposed:**
- `read_notes` - Browse/read from the atlas knowledge base
- `add_note` - Add notes to the inbox

**Configure Claude Code to use it:**
```bash
claude mcp add --transport http athena http://localhost:8000/mcp
```

## Worker Logic

The gardener worker (`workers/gardener.py`):
1. Scans `/data/inbox` for `.md` files
2. Reads `/data/AGENTS.md` + `/data/GARDENER.md` for context
3. Sends each note to the configured backend for classification
4. Executes file operation (create/append/task)
5. Commits changes to Git
6. Archives processed inbox file to `/data/inbox/archive`

**Automation** (`automation.py`):
- Watch mode: Uses `watchfiles` to detect new inbox files, debounces, then processes
- Poll mode: Checks inbox at intervals, processes if files exist
- Runs as background task during FastAPI lifespan

**Coding Standards:**
- Type hinting is mandatory
- Use `pydantic` for data validation
- Keep the logic "Headless": The API should not know about the Frontend implementation
- All file operations target `/data` (Docker volume mount)
