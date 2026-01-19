"""The Gardener - FastAPI backend for Project Athena."""

import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Gardner", description="Backend API for Project Athena PKMS")

DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
INBOX_DIR = DATA_DIR / "inbox"


class InboxRequest(BaseModel):
    """Request model for submitting a note to the inbox."""

    content: str


class InboxResponse(BaseModel):
    """Response model for inbox submission."""

    filename: str
    message: str


class StatusResponse(BaseModel):
    """Response model for health check."""

    status: str
    inbox_path: str
    inbox_exists: bool


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


@app.get("/api/status", response_model=StatusResponse)
async def get_status() -> StatusResponse:
    """Health check endpoint."""
    return StatusResponse(
        status="ok",
        inbox_path=str(INBOX_DIR),
        inbox_exists=INBOX_DIR.exists(),
    )


class GardenerTriggerResponse(BaseModel):
    """Response model for gardener trigger."""

    message: str
    status: str


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


ATLAS_DIR = DATA_DIR / "atlas"


class RefineRequest(BaseModel):
    """Request model for content refinement."""

    content: str


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
                # Get first 200 chars as preview
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
    # Simple extraction: words longer than 3 chars, excluding common words
    stopwords = {"this", "that", "with", "from", "have", "been", "will", "would", "could", "should", "about", "what", "when", "where", "which", "their", "there", "these", "those", "some", "other"}
    words = content.lower().split()
    keywords = [w.strip(".,!?\"'()[]{}") for w in words if len(w) > 3 and w.lower() not in stopwords]
    return list(set(keywords))[:20]  # Limit to 20 unique keywords


@app.post("/api/refine")
async def refine_content(request: RefineRequest):
    """Analyze content and suggest context, tags, and related notes."""
    from fastapi.responses import HTMLResponse

    content = request.content.strip()
    if not content:
        return HTMLResponse('<p class="text-gray-500">Enter some content to get suggestions.</p>')

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return HTMLResponse('<p class="text-yellow-500">AI suggestions unavailable (API key not configured).</p>')

    # Search for related content
    keywords = extract_keywords(content)
    related = search_atlas(keywords)

    related_context = ""
    if related:
        related_context = "\n\nRelated files in knowledge base:\n"
        for r in related:
            related_context += f"- {r['path']}: {r['preview']}...\n"

    try:
        from anthropic import Anthropic

        client = Anthropic(api_key=api_key)

        response = client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"""Analyze this note and provide brief suggestions.

Note content:
{content}
{related_context}

Respond in this exact format (keep it brief):
TAGS: tag1, tag2, tag3
CATEGORY: suggested category (projects/people/home/wellness/tech/journal/reading)
RELATED: any related topics or files mentioned above
MISSING: what context might improve this note (1 sentence)"""
            }],
        )

        result = response.content[0].text

        # Parse and format as HTML
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
        return HTMLResponse("\n".join(html_parts))

    except Exception as e:
        return HTMLResponse(f'<p class="text-red-500">Refinement failed: {e}</p>')


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
        # Return file content
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
