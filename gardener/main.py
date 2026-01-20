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


class GitState(BaseModel):
    """Git repository state."""
    available: bool
    current_head: str | None = None
    current_branch: str | None = None
    last_processed_sha: str | None = None
    last_seen_sha: str | None = None
    dirty_files: int = 0
    dirty_by_location: dict[str, int] | None = None
    dirty_files_preview: list[str] | None = None  # First N dirty files (truncated)
    repo_identity_valid: bool = True


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
    git: GitState | None = None


class GardenerTriggerResponse(BaseModel):
    """Response model for gardener trigger."""
    message: str
    status: str


class BootstrapResponse(BaseModel):
    """Response model for bootstrap endpoint."""
    created: list[str]
    skipped: list[str]
    exists: list[str]
    baseline_commit: bool | None = None


class SnapshotRequest(BaseModel):
    """Request model for snapshot endpoint."""
    message: str | None = None


class SnapshotResponse(BaseModel):
    """Response model for snapshot endpoint."""
    committed: bool
    message: str
    files_changed: int | None = None


class ChangedFileInfo(BaseModel):
    """Info about a changed file."""
    path: str
    location: str
    status: str
    old_path: str | None = None


class ReconcileResponse(BaseModel):
    """Response model for reconcile endpoint."""
    run_id: int
    run_at: str
    from_sha: str | None
    to_sha: str | None
    files_changed: int
    changes_by_location: dict[str, int]
    tasks: list[str]
    changes: list[ChangedFileInfo] | None = None  # Optional detailed list
    # Uncommitted changes (working tree)
    uncommitted_files: int = 0
    uncommitted_by_location: dict[str, int] | None = None
    uncommitted_warning: str | None = None
    # Repo identity
    repo_identity_valid: bool = True


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

def get_git_state() -> GitState | None:
    """Get the current git repository state."""
    try:
        from state import (
            get_current_head, get_current_branch, get_repo_state,
            get_dirty_files, get_dirty_summary, check_repo_identity, init_db,
            update_last_seen_sha
        )

        # Ensure state DB is initialized
        init_db()

        # Check if git is available
        import subprocess
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return GitState(available=False)

        # Check if DATA_DIR is a git repo
        git_dir = DATA_DIR / ".git"
        if not git_dir.exists():
            return GitState(available=False)

        # Get current HEAD and update last_seen_sha if it differs
        current_head = get_current_head()
        repo_state = get_repo_state()

        # Update last_seen_sha when we observe a new HEAD (external commits)
        if current_head and current_head != repo_state.get("last_seen_sha"):
            update_last_seen_sha(current_head)
            repo_state = get_repo_state()  # Refresh after update

        identity_valid, _ = check_repo_identity()
        dirty = get_dirty_files()
        dirty_summary = get_dirty_summary()

        # Truncate dirty files list for preview (max 10)
        dirty_preview = dirty[:10] if dirty else None

        return GitState(
            available=True,
            current_head=current_head,
            current_branch=get_current_branch(),
            last_processed_sha=repo_state.get("last_processed_sha"),
            last_seen_sha=repo_state.get("last_seen_sha"),
            dirty_files=len(dirty),
            dirty_by_location=dirty_summary if dirty else None,
            dirty_files_preview=dirty_preview,
            repo_identity_valid=identity_valid,
        )
    except Exception:
        return None


@app.get("/api/status", response_model=StatusResponse)
async def get_status() -> StatusResponse:
    """Health check endpoint."""
    agents_file = DATA_DIR / "AGENTS.md"
    backend_type, config = get_backend_config()
    auto_status = get_automation_status()
    git_state = get_git_state()

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
        git=git_state,
    )


@app.post("/api/bootstrap", response_model=BootstrapResponse)
async def bootstrap_knowledge_base(force: bool = False) -> BootstrapResponse:
    """Initialize the knowledge base directory structure."""
    from bootstrap import bootstrap
    results = bootstrap(force=force)
    return BootstrapResponse(**results)


@app.post("/api/snapshot", response_model=SnapshotResponse)
async def snapshot_changes(request: SnapshotRequest = SnapshotRequest()) -> SnapshotResponse:
    """Commit any uncommitted changes in the data directory.

    This is for manually snapshotting changes made outside of Gardener
    (e.g., manual edits, external tools). Does not auto-commit by default;
    must be explicitly called.
    """
    import subprocess

    # Check if git is available
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return SnapshotResponse(
            committed=False,
            message="Git is not available",
        )

    # Check if DATA_DIR is a git repo
    git_dir = DATA_DIR / ".git"
    if not git_dir.exists():
        return SnapshotResponse(
            committed=False,
            message="Data directory is not a git repository",
        )

    # Check for uncommitted changes using -z for NUL-separated output
    # This handles paths with spaces, tabs, and Unicode correctly
    result = subprocess.run(
        ["git", "status", "--porcelain", "-z"],
        cwd=DATA_DIR,
        capture_output=True,
    )
    if not result.stdout.strip():
        return SnapshotResponse(
            committed=False,
            message="No changes to commit",
            files_changed=0,
        )

    # Stage all changes
    subprocess.run(["git", "add", "-A"], cwd=DATA_DIR, check=True, capture_output=True)

    # Parse git status -z output for proper handling of paths
    # Format with -z: entries are NUL-separated
    # - Regular: "XY path\x00"
    # - Rename/Copy: "XY new_path\x00old_path\x00"
    parsed_changes: list[dict] = []
    entries = result.stdout.split(b'\x00')
    i = 0
    while i < len(entries):
        entry = entries[i]
        if not entry:
            i += 1
            continue

        status = entry[:2].decode('utf-8', errors='replace')
        path = entry[3:].decode('utf-8', errors='replace')

        if status[0] == 'R' or status[1] == 'R':
            # Rename: next entry is the old path (old file no longer exists)
            old_path = entries[i + 1].decode('utf-8', errors='replace') if i + 1 < len(entries) else None
            parsed_changes.append({'status': 'rename', 'path': path, 'old_path': old_path})
            i += 2  # Skip both entries
        elif status[0] == 'C' or status[1] == 'C':
            # Copy: next entry is the source path (source file still exists)
            old_path = entries[i + 1].decode('utf-8', errors='replace') if i + 1 < len(entries) else None
            parsed_changes.append({'status': 'copy', 'path': path, 'old_path': old_path})
            i += 2  # Skip both entries
        elif status[0] == 'D' or status[1] == 'D':
            parsed_changes.append({'status': 'delete', 'path': path, 'old_path': None})
            i += 1
        else:
            parsed_changes.append({'status': 'modify', 'path': path, 'old_path': None})
            i += 1

    changed_files = len(parsed_changes)

    # Commit with provided message or default
    commit_message = request.message or "Manual: Snapshot uncommitted changes"
    try:
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=DATA_DIR,
            check=True,
            capture_output=True,
        )

        # Update state DB after successful commit
        try:
            from state import (
                get_current_head, get_current_branch, record_processed_commit,
                update_file_state, record_provenance, remove_file_state,
                PROVENANCE_MANUAL
            )
            head = get_current_head()
            if head:
                branch = get_current_branch()
                record_processed_commit(head, branch, commit_message)

                # Update file state and provenance based on change type
                for change in parsed_changes:
                    file_path = change['path']
                    full_path = DATA_DIR / file_path

                    if change['status'] == 'delete':
                        # Remove deleted files from state
                        remove_file_state(full_path)
                        record_provenance(file_path, PROVENANCE_MANUAL, head,
                                          {'action': 'delete'})
                    elif change['status'] == 'rename':
                        # Remove old path, add new path
                        if change['old_path']:
                            remove_file_state(DATA_DIR / change['old_path'])
                        if full_path.exists():
                            update_file_state(full_path)
                        record_provenance(file_path, PROVENANCE_MANUAL, head,
                                          {'action': 'rename', 'from': change['old_path']})
                    elif change['status'] == 'copy':
                        # Keep source in state, add new path
                        if full_path.exists():
                            update_file_state(full_path)
                        record_provenance(file_path, PROVENANCE_MANUAL, head,
                                          {'action': 'copy', 'from': change['old_path']})
                    else:
                        # Add/modify
                        if full_path.exists():
                            update_file_state(full_path)
                            record_provenance(file_path, PROVENANCE_MANUAL, head)
        except Exception:
            pass  # State tracking is optional

        return SnapshotResponse(
            committed=True,
            message=f"Committed {changed_files} file(s)",
            files_changed=changed_files,
        )
    except subprocess.CalledProcessError as e:
        return SnapshotResponse(
            committed=False,
            message=f"Commit failed: {e.stderr.decode() if e.stderr else str(e)}",
        )


@app.post("/api/reconcile", response_model=ReconcileResponse)
async def reconcile_changes(include_details: bool = False) -> ReconcileResponse:
    """Detect and reconcile manual/external changes to the knowledge base.

    This operation:
    1. Checks repo identity (detects history rewrites)
    2. Detects committed changes since last reconcile
    3. Reports uncommitted changes (requires snapshot first)
    4. Classifies changes by location (inbox/atlas/meta)
    5. Generates maintenance task recommendations
    6. Records the reconcile run

    Source-of-truth rules:
    - Atlas notes are never auto-rewritten (manual edits preserved)
    - Inbox changes trigger normal gardener processing
    - Meta changes flag for reindexing

    Args:
        include_details: If True, include full list of changed files
    """
    try:
        from state import (
            run_reconcile, get_changes_since_sha, init_db,
            check_repo_identity, get_dirty_files, get_dirty_summary
        )

        init_db()

        # Check repo identity first
        identity_valid, _ = check_repo_identity()

        # Get uncommitted changes
        dirty_files = get_dirty_files()
        dirty_summary = get_dirty_summary() if dirty_files else None
        uncommitted_warning = None
        if dirty_files:
            uncommitted_warning = (
                f"{len(dirty_files)} uncommitted file(s) not included in reconcile. "
                "Run /api/snapshot first to include them."
            )

        # Run reconciliation (on committed changes)
        result = run_reconcile()

        # Get detailed changes if requested (use result's from_sha to match the actual scan)
        changes_detail = None
        if include_details:
            changes = get_changes_since_sha(result["from_sha"])
            changes_detail = [
                ChangedFileInfo(
                    path=c["path"],
                    location=c["location"],
                    status=c["status"],
                    old_path=c.get("old_path"),
                )
                for c in changes
            ]

        return ReconcileResponse(
            run_id=result["id"],
            run_at=result["run_at"],
            from_sha=result["from_sha"],
            to_sha=result["to_sha"],
            files_changed=result["files_changed"],
            changes_by_location={
                "inbox": result["inbox_changes"],
                "atlas": result["atlas_changes"],
                "meta": result["meta_changes"],
            },
            tasks=result["tasks_generated"],
            changes=changes_detail,
            uncommitted_files=len(dirty_files),
            uncommitted_by_location=dirty_summary,
            uncommitted_warning=uncommitted_warning,
            repo_identity_valid=identity_valid,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reconciliation failed: {e}")


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
