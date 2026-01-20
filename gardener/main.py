"""The Gardener - FastAPI backend for Project Athena."""

import asyncio
import contextlib
import logging
from datetime import datetime
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from automation import start_automation, get_automation_status
from backends import get_backend, get_backend_config
from config import DATA_DIR, INBOX_DIR, ATLAS_DIR
from mcp_tools import mcp

logger = logging.getLogger(__name__)


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage MCP session and automation lifecycle."""
    # Start automation task
    automation_task = asyncio.create_task(start_automation())

    async with mcp.session_manager.run():
        yield

    # Cleanup automation on shutdown
    automation_task.cancel()
    try:
        await automation_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Gardener",
    description="Backend API for Project Athena PKMS",
    lifespan=lifespan,
)

# Mount MCP server at /mcp (FastMCP app configured to serve at "/")
app.mount("/mcp", mcp.streamable_http_app())


# --- Request/Response Models ---

class InboxRequest(BaseModel):
    """Request model for submitting a note to the inbox."""
    content: str


class InboxResponse(BaseModel):
    """Response model for inbox submission."""
    filename: str
    message: str


class AutomationStatus(BaseModel):
    """Automation configuration status."""
    enabled: bool
    mode: str | None
    poll_interval: int | None
    debounce: float | None


class StatusResponse(BaseModel):
    """Response model for health check."""
    status: str
    inbox_path: str
    inbox_exists: bool
    atlas_exists: bool
    bootstrapped: bool
    gardener_backend: str
    gardener_model: str
    gardener_model_fast: str | None = None
    automation: AutomationStatus


class GardenerTriggerResponse(BaseModel):
    """Response model for gardener trigger."""
    message: str
    status: str


class BootstrapResponse(BaseModel):
    """Response model for bootstrap endpoint."""
    created: list[str]
    skipped: list[str]
    exists: list[str]


class RefineRequest(BaseModel):
    """Request model for content refinement."""
    content: str


class AskRequest(BaseModel):
    """Request model for knowledge retrieval."""
    question: str


class BrowseItem(BaseModel):
    """Item in a directory listing."""
    name: str
    type: str  # "file" or "directory"
    path: str


class BrowseResponse(BaseModel):
    """Response model for browse endpoint."""
    path: str
    items: list[BrowseItem]
    content: str | None = None
    is_file: bool = False


# --- Endpoints ---

@app.get("/api/status", response_model=StatusResponse)
async def get_status() -> StatusResponse:
    """Health check endpoint."""
    agents_file = DATA_DIR / "AGENTS.md"
    backend_type, config = get_backend_config()
    auto_status = get_automation_status()
    return StatusResponse(
        status="ok",
        inbox_path=str(INBOX_DIR),
        inbox_exists=INBOX_DIR.exists(),
        atlas_exists=ATLAS_DIR.exists(),
        bootstrapped=agents_file.exists(),
        gardener_backend=backend_type,
        gardener_model=config.model_thinking,
        gardener_model_fast=config.model_fast,
        automation=AutomationStatus(**auto_status),
    )


@app.post("/api/bootstrap", response_model=BootstrapResponse)
async def bootstrap_knowledge_base(force: bool = False) -> BootstrapResponse:
    """Initialize the knowledge base directory structure."""
    from bootstrap import bootstrap
    results = bootstrap(force=force)
    return BootstrapResponse(**results)


@app.post("/api/inbox", response_model=InboxResponse)
async def submit_to_inbox(request: InboxRequest) -> InboxResponse:
    """Accept note content and save to inbox as timestamped markdown."""
    INBOX_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    short_uuid = uuid4().hex[:8]
    filename = f"{now.strftime('%Y-%m-%d_%H%M')}-{short_uuid}.md"
    filepath = INBOX_DIR / filename

    try:
        filepath.write_text(request.content)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Failed to write file: {e}")

    return InboxResponse(filename=filename, message="Note saved to inbox")


def run_gardener() -> None:
    """Run the gardener worker in the background."""
    from workers.gardener import process_inbox
    process_inbox()


@app.post("/api/trigger-gardener", response_model=GardenerTriggerResponse)
async def trigger_gardener(background_tasks: BackgroundTasks) -> GardenerTriggerResponse:
    """Manually trigger the gardener to process the inbox."""
    background_tasks.add_task(run_gardener)
    return GardenerTriggerResponse(
        message="Gardener processing started in background",
        status="started",
    )


# --- Refine Endpoint ---

def search_atlas(keywords: list[str], max_files: int = 5) -> list[dict]:
    """Search atlas for files containing keywords."""
    if not ATLAS_DIR.exists():
        return []

    matches = []
    for md_file in ATLAS_DIR.rglob("*.md"):
        try:
            content = md_file.read_text().lower()
            score = sum(1 for kw in keywords if kw.lower() in content)
            if score > 0:
                preview = md_file.read_text()[:200].replace("\n", " ")
                matches.append({
                    "path": str(md_file.relative_to(ATLAS_DIR)),
                    "score": score,
                    "preview": preview,
                })
        except Exception:
            continue

    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches[:max_files]


def extract_keywords(content: str) -> list[str]:
    """Extract potential keywords from content."""
    stopwords = {
        "this", "that", "with", "from", "have", "been", "will", "would",
        "could", "should", "about", "what", "when", "where", "which",
        "their", "there", "these", "those", "some", "other"
    }
    words = content.lower().split()
    keywords = [
        w.strip(".,!?\"'()[]{}")
        for w in words
        if len(w) > 3 and w.lower() not in stopwords
    ]
    return list(set(keywords))[:20]


def format_refine_html(result: str) -> str:
    """Format refinement result as HTML."""
    html_parts = ['<div class="space-y-2 text-sm">']

    for line in result.strip().split("\n"):
        if line.startswith("TAGS:"):
            tags = line.replace("TAGS:", "").strip()
            html_parts.append(f'<p><span class="text-gray-400">Tags:</span> <span class="text-blue-400">{tags}</span></p>')
        elif line.startswith("CATEGORY:"):
            category = line.replace("CATEGORY:", "").strip()
            html_parts.append(f'<p><span class="text-gray-400">Category:</span> <span class="text-green-400">{category}</span></p>')
        elif line.startswith("RELATED:"):
            related_text = line.replace("RELATED:", "").strip()
            if related_text and related_text.lower() != "none":
                html_parts.append(f'<p><span class="text-gray-400">Related:</span> <span class="text-purple-400">{related_text}</span></p>')
        elif line.startswith("MISSING:"):
            missing = line.replace("MISSING:", "").strip()
            if missing and missing.lower() != "none":
                html_parts.append(f'<p><span class="text-gray-400">Consider adding:</span> <span class="text-yellow-400">{missing}</span></p>')

    html_parts.append("</div>")
    return "\n".join(html_parts)


def format_ask_html(answer: str, related: list[dict]) -> str:
    """Format ask result as HTML."""
    import html

    escaped = html.escape(answer.strip())
    html_parts = ['<div class="space-y-3 text-sm">']
    if escaped:
        html_parts.append(f'<div class="whitespace-pre-wrap text-gray-200">{escaped}</div>')
    else:
        html_parts.append('<p class="text-gray-500">No answer returned.</p>')

    if related:
        html_parts.append('<div class="text-xs text-gray-400">Related files:</div>')
        html_parts.append('<ul class="list-disc list-inside text-xs text-gray-400">')
        for item in related:
            html_parts.append(f'<li>{html.escape(item["path"])}</li>')
        html_parts.append('</ul>')

    html_parts.append("</div>")
    return "\n".join(html_parts)


@app.post("/api/refine")
async def refine_content(request: RefineRequest):
    """Analyze content and suggest context, tags, and related notes."""
    content = (request.content or "").strip()
    if not content:
        return HTMLResponse('<p class="text-gray-500">Enter some content to get suggestions.</p>')

    # Search for related content
    keywords = extract_keywords(content)
    related = search_atlas(keywords)

    related_context = ""
    if related:
        for r in related:
            related_context += f"- {r['path']}: {r['preview']}...\n"

    try:
        with get_backend() as backend:
            result = backend.refine(content, related_context)
            return HTMLResponse(format_refine_html(result))
    except ValueError as e:
        return HTMLResponse(f'<p class="text-yellow-500">AI not configured: {e}</p>')
    except Exception as e:
        return HTMLResponse(f'<p class="text-red-500">Refinement failed: {e}</p>')


@app.post("/api/ask")
async def ask_question(request: AskRequest):
    """Answer a question using the knowledge base as context."""
    question = (request.question or "").strip()
    if not question:
        return HTMLResponse('<p class="text-gray-500">Enter a question to explore your notes.</p>')

    keywords = extract_keywords(question)
    related = search_atlas(keywords, max_files=8)

    related_context = ""
    if related:
        for r in related:
            related_context += f"- {r['path']}: {r['preview']}...\n"

    try:
        with get_backend() as backend:
            result = backend.ask(question, related_context)
            return HTMLResponse(format_ask_html(result, related))
    except ValueError as e:
        return HTMLResponse(f'<p class="text-yellow-500">AI not configured: {e}</p>')
    except Exception as e:
        return HTMLResponse(f'<p class="text-red-500">Ask failed: {e}</p>')


# --- Browse Endpoint ---

@app.get("/api/browse/{path:path}", response_model=BrowseResponse)
@app.get("/api/browse", response_model=BrowseResponse)
async def browse_atlas(path: str = "") -> BrowseResponse:
    """Browse the atlas directory structure."""
    target = ATLAS_DIR / path if path else ATLAS_DIR

    if not target.exists():
        raise HTTPException(status_code=404, detail="Path not found")

    # Security check: ensure path is within ATLAS_DIR
    try:
        target.resolve().relative_to(ATLAS_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")

    if target.is_file():
        content = target.read_text()
        return BrowseResponse(
            path=path,
            items=[],
            content=content,
            is_file=True,
        )

    # List directory contents
    items = []
    for item in sorted(target.iterdir()):
        if item.name.startswith("."):
            continue
        item_path = str(item.relative_to(ATLAS_DIR))
        items.append(BrowseItem(
            name=item.name,
            type="directory" if item.is_dir() else "file",
            path=item_path,
        ))

    # Sort: directories first, then files
    items.sort(key=lambda x: (0 if x.type == "directory" else 1, x.name.lower()))

    return BrowseResponse(path=path, items=items, is_file=False)
