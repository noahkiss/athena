# Athena

An AI-native Personal Knowledge Management System. Capture thoughts quickly, let AI organize them into a structured knowledge base.

> **Note:** Athena is designed for **single-user, self-hosted** deployments. It's your personal knowledge base running on your own hardware. Features like rate limiting and multi-tenancy are intentionally omitted to keep the system simple and focused.

## Overview

Athena follows a simple philosophy: **capture fast, organize later**. Drop raw notes into an inbox, and the Gardener agent classifies, formats, and files them into your personal atlas.

**Components:**

| Directory | Role | Tech |
|-----------|------|------|
| `gardener/` | Backend API + AI worker | Python, FastAPI |
| `scribe/` | Capture frontend | Astro, HTMX, Tailwind |
| `athena/` | Knowledge base template | Markdown, Git |

## Quick Start (All-in-one)

**Prerequisites:** Docker, an OpenAI-compatible API key

```bash
git clone https://github.com/noahkiss/athena.git
cd athena
cp .env.example .env
# Edit .env with your AI provider settings
docker-compose -f docker-compose.allinone.yml up -d --build
curl -X POST http://localhost:8000/api/bootstrap
```

**Access:**
- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

## Quick Start (Split services)

```bash
git clone https://github.com/noahkiss/athena.git
cd athena
cp .env.example .env
# Edit .env with your AI provider settings
docker-compose up -d --build
curl -X POST http://localhost:8000/api/bootstrap
```

**Access:**
- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

## Configuration

### AI Backend

Athena supports multiple AI backends:

| Variable | Default | Description |
|----------|---------|-------------|
| `GARDENER_BACKEND` | `openai` | Backend type: `openai` or `anthropic` |
| `AI_API_KEY` | - | API key (falls back to `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`) |
| `AI_MODEL_THINKING` | `gpt-4o` / `claude-sonnet-4-20250514` | Model for classification |
| `AI_MODEL_FAST` | `AI_MODEL_THINKING` | Model for refinement/quick tasks |
| `AI_MODEL` | - | Legacy fallback for both models if `AI_MODEL_THINKING` is unset |
| `AI_BASE_URL` | `https://api.openai.com/v1` | API endpoint (OpenAI backend only) |
| `AI_TIMEOUT` | `120` | Request timeout in seconds |

**OpenAI example:**
```env
GARDENER_BACKEND=openai
AI_API_KEY=sk-...
AI_MODEL_THINKING=gpt-4o
AI_MODEL_FAST=gpt-4o-mini
```

**Anthropic example:**
```env
GARDENER_BACKEND=anthropic
ANTHROPIC_API_KEY=sk-ant-...
AI_MODEL_THINKING=claude-sonnet-4-20250514
AI_MODEL_FAST=claude-3-haiku-20240307
```

**LiteLLM example** (use OpenAI backend):
```env
GARDENER_BACKEND=openai
AI_BASE_URL=http://localhost:4000/v1
AI_API_KEY=your-key
AI_MODEL_THINKING=claude-3-5-sonnet-20241022
AI_MODEL_FAST=claude-3-haiku-20240307
```

### Automation

By default, the gardener must be triggered manually. Enable automatic processing:

| Variable | Default | Description |
|----------|---------|-------------|
| `GARDENER_AUTO` | `false` | Enable automatic inbox processing |
| `GARDENER_MODE` | `watch` | Detection mode: `watch` (file watcher) or `poll` |
| `GARDENER_DEBOUNCE` | `5.0` | Seconds to wait after last file change (watch mode) |
| `GARDENER_POLL_INTERVAL` | `300` | Seconds between polls (poll mode) |

**Enable automation:**
```env
GARDENER_AUTO=true
GARDENER_MODE=watch
GARDENER_DEBOUNCE=5.0
```

### Logging

Control log verbosity with:

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `LOG_FORMAT` | `%(asctime)s - %(name)s - %(levelname)s - %(message)s` | Python logging format string |

**Examples:**
```env
# Verbose debugging
LOG_LEVEL=DEBUG

# Only warnings and errors
LOG_LEVEL=WARNING
```

### Authentication (Optional)

By default, the API and MCP server are open on localhost. To require a shared token, set:

| Variable | Default | Description |
|----------|---------|-------------|
| `ATHENA_AUTH_TOKEN` | - | Shared token that enables auth for `/api/*` and `/mcp` |

**Example:**
```env
ATHENA_AUTH_TOKEN=your-secret-token
```

**Send the token via:**
- `Authorization: Bearer <token>`
- `X-Auth-Token: <token>`

## Knowledge Base Structure

The `athena/` directory serves as a template. On first run, bootstrap creates:

```
athena/
├── AGENTS.md      # User context and preferences
├── GARDENER.md     # Classification rules
├── tasks.md       # Ambiguity log (uncertain classifications)
├── inbox/         # Landing zone for new notes
│   └── archive/   # Raw backup of processed notes (ignored by agents)
└── atlas/         # Organized knowledge
    ├── projects/
    ├── people/
    ├── home/
    ├── wellness/
    ├── tech/
    ├── journal/
    └── reading/
```

The atlas structure evolves as the Gardener encounters new content types.

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/status` | Health check |
| `POST` | `/api/bootstrap` | Initialize knowledge base |
| `POST` | `/api/inbox` | Submit a note |
| `POST` | `/api/trigger-gardener` | Process inbox |
| `POST` | `/api/refine` | Get AI suggestions for a note |
| `POST` | `/api/ask` | Ask a question using your knowledge base |
| `GET` | `/api/browse/{path}` | Browse atlas |
| `GET` | `/api/archive/{path}` | Browse archived inbox notes |

**Notes:**
- `/api/refine` HTML output is sanitized server-side to strip unsafe tags/attributes.

## MCP Server

Expose your knowledge base to external AI tools via Model Context Protocol. The MCP server runs as part of the FastAPI app using streamable-http transport.

**Configure Claude Code:**
```bash
claude mcp add --transport http athena-pkms http://localhost:8000/mcp
```

**Or add to `.mcp.json`:**
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

**Tools:** `read_notes`, `add_note`

## Testing & CI

- Gardener unit tests: `cd gardener && uv run pytest`
- Gardener formatting + lint: `cd gardener && uv run ruff format --check .` then `uv run ruff check .`
- Scribe build: `cd scribe && npm run build`
- Full E2E flow: `./scripts/test_e2e_full.sh` (see `TESTS.md` for options)

CI runs the Gardener tests + ruff checks and the Scribe build on PRs.

## Development

Each component has an `AGENTS.md` file with context for AI-assisted development. Point your coding assistant to the relevant file when working on that component.
