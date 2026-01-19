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

Athena works with any OpenAI-compatible API (OpenAI, LiteLLM, Ollama, etc.):

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_BASE_URL` | `https://api.openai.com/v1` | API endpoint |
| `AI_API_KEY` | - | API key |
| `AI_MODEL_FAST` | `gpt-4o-mini` | Quick tasks (suggestions) |
| `AI_MODEL_THINKING` | `gpt-4o` | Complex tasks (classification) |

**LiteLLM example:**
```env
AI_BASE_URL=http://localhost:4000/v1
AI_API_KEY=your-key
AI_MODEL_FAST=claude-3-haiku-20240307
AI_MODEL_THINKING=claude-3-5-sonnet-20241022
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
