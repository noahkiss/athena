# Athena

An AI-native Personal Knowledge Management System. Capture thoughts quickly, let AI organize them into a structured knowledge base.

## Overview

Athena follows a simple philosophy: **capture fast, organize later**. Drop raw notes into an inbox, and the Gardener agent classifies, formats, and files them into your personal atlas.

**Components:**

| Directory | Role | Tech |
|-----------|------|------|
| `gardner/` | Backend API + AI worker | Python, FastAPI |
| `scribe/` | Capture frontend | Astro, HTMX, Tailwind |
| `athena/` | Knowledge base template | Markdown, Git |

## Quick Start

**Prerequisites:** Docker, an OpenAI-compatible API key

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
| `AI_MODEL` | `gpt-4o` / `claude-sonnet-4-20250514` | Model for classification |
| `AI_BASE_URL` | `https://api.openai.com/v1` | API endpoint (OpenAI backend only) |

**OpenAI example:**
```env
GARDENER_BACKEND=openai
AI_API_KEY=sk-...
AI_MODEL=gpt-4o
```

**Anthropic example:**
```env
GARDENER_BACKEND=anthropic
ANTHROPIC_API_KEY=sk-ant-...
AI_MODEL=claude-sonnet-4-20250514
```

**LiteLLM example** (use OpenAI backend):
```env
GARDENER_BACKEND=openai
AI_BASE_URL=http://localhost:4000/v1
AI_API_KEY=your-key
AI_MODEL=claude-3-5-sonnet-20241022
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

## Knowledge Base Structure

The `athena/` directory serves as a template. On first run, bootstrap creates:

```
athena/
├── AGENTS.md      # User context and preferences
├── GARDNER.md     # Classification rules
├── tasks.md       # Ambiguity log (uncertain classifications)
├── inbox/         # Landing zone for new notes
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
| `GET` | `/api/browse/{path}` | Browse atlas |

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

## Development

Each component has an `AGENTS.md` file with context for AI-assisted development. Point your coding assistant to the relevant file when working on that component.
