# Athena PKMS

**Athena** is an AI-native Personal Knowledge Management System. It combines the speed of "Grug Brain" capture (text dumps) with the intelligence of a "Gardener" agent that organizes, links, and refines your thoughts into a structured Second Brain.

## 🏛 System Architecture

The project is divided into three distinct components. Each component contains its own `AGENTS.md` file, serving as a "Live Context" document for any LLM (Claude, ChatGPT, etc.) assisting with development.

### 1. `athena/` (The Data Skeleton)
The source of truth. This directory is a **template** for the volume bind-mounted to the Docker container.
*   **Role:** Storage, Context, Philosophy.
*   **Tech:** Markdown, Git, YAML Frontmatter.
*   **Key Files:**
    *   `AGENTS.md`: The "System Prompt" defining the user's persona and life categories.
    *   `GARDNER.md`: The rulebook for how the AI should organize files.

### 2. `gardner/` (The Brain)
The backend service and worker nodes.
*   **Role:** API endpoints, File Watchers, Cron Jobs, LLM Processing.
*   **Tech:** Python, FastAPI, Anthropic SDK, APScheduler.
*   **Function:** Watches the `inbox`, reads `GARDNER.md` instructions, and moves files into the `athena` structure.

### 3. `scribe/` (The Interface)
The lightweight frontend.
*   **Role:** Capture and Retrieval.
*   **Tech:** Astro (SSR), HTMX, TailwindCSS.
*   **Philosophy:** Mobile-first capture. "Refine" vs "Submit" workflows.

---

## 🚀 Quick Start

### Prerequisites
*   Docker & Docker Compose
*   An Anthropic API Key (for the Gardener)

### Installation

1.  **Clone the Repo:**
    ```bash
    git clone https://github.com/yourusername/pkms.git
    cd pkms
    ```

2.  **Configure Environment:**
    ```bash
    cp .env.example .env
    # Edit .env and add your ANTHROPIC_API_KEY
    ```

3.  **Initialize the Brain:**
    The `athena` folder in this repo is just a skeleton. When running locally, you might want to map this to a real data directory on your machine, or use the skeleton as a starting point.
    *(See `docker-compose.yml` for volume mapping details)*.

4.  **Launch:**
    ```bash
    docker-compose up -d --build
    ```

5.  **Access:**
    *   **Scribe (Frontend):** `http://localhost:3000`
    *   **Gardner (API):** `http://localhost:8000/docs`

---

## 🤖 Working with Agents

This project is designed to be built *by* and *with* AI agents (Claude Code, Cursor, etc.).

**The `AGENTS.md` Protocol:**
Every sub-directory contains an `AGENTS.md` file. These are **Live Documents**. They are not just documentation; they are prompts.

*   **When coding `scribe`:** Point your AI to `scribe/AGENTS.md`. It contains the tech stack rules (Astro/HTMX) and design philosophy.
*   **When coding `gardner`:** Point your AI to `gardner/AGENTS.md`. It contains the logic for how files should be handled.
*   **When organizing data:** The system automatically reads `athena/AGENTS.md` to understand *who you are* (The User Context).

**Example Workflow:**
> "I want to add a new feature to the frontend."

1.  Open `scribe/AGENTS.md`.
2.  Update the file with the new requirement or architectural change.
3.  Prompt your AI: *"Read scribe/AGENTS.md and implement the new 'Refine' button logic."*

---

## 📂 Directory Structure

```text
pkms/
├── docker-compose.yml   # Orchestration
├── .env.example         # Config template
├── README.md            # This file
├── AGENTS.md            # Root agent instructions (uv, beans)
├── pyproject.toml       # Python project config (uv)
├── gardner/             # Backend Service
│   └── AGENTS.md        # "You are a Python FastAPI expert..."
├── scribe/              # Frontend Service
│   └── AGENTS.md        # "You are a Frontend Architect using Astro..."
└── athena/              # Data Template (The "Volume")
    ├── AGENTS.md        # "You are managing the PKMS for [User]..."
    ├── GARDNER.md       # Classification rules for the Gardener
    ├── tasks.md         # The Ambiguity Log
    ├── inbox/           # Raw capture landing zone
    ├── meta/            # Machine-generated indexes
    └── atlas/           # The Permanent Library (living structure)
        ├── projects/    # Business ideas, coding projects
        ├── people/      # CRM/PRM data
        ├── home/        # DIY, maintenance, vehicles
        ├── wellness/    # Health, fitness, diet
        ├── tech/        # Homelab, configs, reference
        ├── journal/     # Philosophy, parenting, brain dumps
        └── reading/     # Books, articles, media notes
```

> **Note:** The `atlas/` structure is living and may be modified by the Gardener agent as new categories emerge.

## 🛠 Features

- [x] **Capture:** Fast mobile-friendly text dump to Markdown.
- [x] **Gardener:** Manual trigger to auto-sort inbox files using Claude Sonnet.
- [x] **Refine:** AI-assisted context injection *before* saving a note (Claude Haiku).
- [x] **Browse:** Read-only view of the `atlas` directory with markdown rendering.
- [x] **MCP Server:** Expose notes to external AI tools via Model Context Protocol.

---

## 🔌 API Endpoints

**Gardner (Port 8000):**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/inbox` | Submit a note to the inbox |
| `GET` | `/api/status` | Health check |
| `POST` | `/api/trigger-gardener` | Manually trigger inbox processing |
| `POST` | `/api/refine` | Get AI suggestions for a note |
| `GET` | `/api/browse/{path}` | Browse atlas directory/files |

**MCP Server (stdio):**

| Tool | Description |
|------|-------------|
| `read_notes` | Read/search notes from atlas |
| `add_note` | Add a note to the inbox |

To use with Claude Desktop, add to your config:
```json
{
  "athena": {
    "command": "uv",
    "args": ["run", "python", "mcp_server.py"],
    "cwd": "/path/to/pkms/gardner",
    "env": { "DATA_DIR": "/path/to/pkms/athena" }
  }
}
```
