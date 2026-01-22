"""The Gardener - FastAPI backend for Project Athena."""

import asyncio
import contextlib
import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    File,
    Header,
    HTTPException,
    UploadFile,
)
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

from api_usage import get_usage_stats
from automation import get_automation_status, start_automation
from backends import get_backend, get_backend_config
from branding import (
    ICON_NAMES,
    MAX_ICON_BYTES,
    generate_icons,
    get_icon_path,
    has_custom_icon,
    load_settings,
    save_uploaded_icon,
    update_settings,
)
from config import (
    ARCHIVE_DIR,
    ATLAS_DIR,
    AUTH_ENABLED,
    AUTH_TOKEN,
    DATA_DIR,
    INBOX_DIR,
    MAX_CONTENT_SIZE,
    setup_logging,
)
from mcp_tools import mcp

# Configure logging before anything else
setup_logging()
logger = logging.getLogger(__name__)


class FileContentCache:
    """Simple in-memory cache for file contents with mtime validation."""

    def __init__(self, max_entries: int = 500, ttl_seconds: float = 60.0):
        self._cache: dict[
            Path, tuple[float, float, str]
        ] = {}  # path -> (mtime, cached_at, content)
        self._max_entries = max_entries
        self._ttl = ttl_seconds

    def get(self, path: Path) -> str | None:
        """Get cached content if valid, or None if stale/missing."""
        if path not in self._cache:
            return None
        mtime, cached_at, content = self._cache[path]
        now = time.time()
        # Check TTL
        if now - cached_at > self._ttl:
            del self._cache[path]
            return None
        # Check mtime hasn't changed
        try:
            current_mtime = path.stat().st_mtime
            if current_mtime != mtime:
                del self._cache[path]
                return None
        except OSError:
            del self._cache[path]
            return None
        return content

    def put(self, path: Path, content: str) -> None:
        """Cache file content."""
        if len(self._cache) >= self._max_entries:
            # Evict oldest entry
            oldest = min(self._cache.items(), key=lambda x: x[1][1])
            del self._cache[oldest[0]]
        try:
            mtime = path.stat().st_mtime
            self._cache[path] = (mtime, time.time(), content)
        except OSError:
            pass

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()


_atlas_content_cache = FileContentCache()


# --- Authentication ---


async def verify_auth_token(
    authorization: str | None = Header(None),
    x_auth_token: str | None = Header(None),
) -> None:
    """Verify authentication token if auth is enabled.

    Accepts token via:
    - Authorization: Bearer <token>
    - X-Auth-Token: <token>

    If AUTH_ENABLED is False, this is a no-op (always passes).
    """
    if not AUTH_ENABLED:
        return

    token = None

    # Check Authorization header (Bearer token)
    if authorization:
        parts = authorization.split(" ", 1)
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]

    # Fall back to X-Auth-Token header
    if not token and x_auth_token:
        token = x_auth_token

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Provide token via 'Authorization: Bearer <token>' or 'X-Auth-Token' header.",
        )

    if token != AUTH_TOKEN:
        raise HTTPException(
            status_code=403,
            detail="Invalid authentication token.",
        )


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage MCP session and automation lifecycle."""
    logger.info("Gardener starting up...")

    # Start automation task
    automation_task = asyncio.create_task(start_automation())

    async with mcp.session_manager.run():
        logger.info("Gardener ready to accept requests")
        yield

    # Cleanup automation on shutdown
    logger.info("Gardener shutting down...")
    automation_task.cancel()
    try:
        await automation_task
    except asyncio.CancelledError:
        pass
    logger.info("Gardener shutdown complete")


app = FastAPI(
    title="Gardener",
    description="Backend API for Project Athena PKMS",
    lifespan=lifespan,
)


@app.middleware("http")
async def auth_middleware(request, call_next):
    """Check authentication for MCP endpoints when auth is enabled.

    API endpoints use the verify_auth_token dependency directly.
    This middleware handles auth for the mounted MCP app.
    """
    if AUTH_ENABLED and request.url.path.startswith("/mcp"):
        token = None

        # Check Authorization header (Bearer token)
        auth_header = request.headers.get("authorization")
        if auth_header:
            parts = auth_header.split(" ", 1)
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]

        # Fall back to X-Auth-Token header
        if not token:
            token = request.headers.get("x-auth-token")

        if not token:
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Authentication required. Provide token via 'Authorization: Bearer <token>' or 'X-Auth-Token' header."
                },
            )

        if token != AUTH_TOKEN:
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=403,
                content={"detail": "Invalid authentication token."},
            )

    return await call_next(request)


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


class ApiUsageStats(BaseModel):
    """API usage statistics."""

    total_calls: int
    calls_last_hour: int
    calls_last_day: int
    hourly_limit: int
    daily_limit: int
    hourly_usage_percent: float
    daily_usage_percent: float
    is_near_hourly_limit: bool
    is_near_daily_limit: bool


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
    api_usage: ApiUsageStats


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


class BrandingUpdateRequest(BaseModel):
    """Request model for updating branding settings."""

    app_name: str | None = None
    theme: str | None = None


class BrandingSettingsResponse(BaseModel):
    """Response model for branding settings."""

    app_name: str
    theme: str
    icon_version: str
    has_icon: bool


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
        from db import init_db
        from file_state import get_dirty_summary
        from git_state import (
            check_repo_identity,
            get_current_branch,
            get_current_head,
            get_dirty_files,
            get_repo_state,
            update_last_seen_sha,
        )

        # Ensure state DB is initialized
        init_db()

        # Check if git is available
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
    except (ImportError, OSError, subprocess.CalledProcessError) as e:
        logger.warning(f"Could not get git state: {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error getting git state: {e}")
        return None


@app.get(
    "/api/status",
    response_model=StatusResponse,
    dependencies=[Depends(verify_auth_token)],
)
async def get_status() -> StatusResponse:
    """Health check endpoint."""
    agents_file = DATA_DIR / "AGENTS.md"
    backend_type, config = get_backend_config()
    auto_status = get_automation_status()
    git_state = get_git_state()
    usage_stats = get_usage_stats()

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
        api_usage=ApiUsageStats(
            total_calls=usage_stats.total_calls,
            calls_last_hour=usage_stats.calls_last_hour,
            calls_last_day=usage_stats.calls_last_day,
            hourly_limit=usage_stats.hourly_limit,
            daily_limit=usage_stats.daily_limit,
            hourly_usage_percent=usage_stats.hourly_usage_percent,
            daily_usage_percent=usage_stats.daily_usage_percent,
            is_near_hourly_limit=usage_stats.is_near_hourly_limit,
            is_near_daily_limit=usage_stats.is_near_daily_limit,
        ),
    )


@app.get(
    "/api/branding",
    response_model=BrandingSettingsResponse,
    dependencies=[Depends(verify_auth_token)],
)
async def get_branding_settings() -> BrandingSettingsResponse:
    """Return branding settings for the UI."""
    settings = load_settings()
    return BrandingSettingsResponse(
        app_name=settings.app_name,
        theme=settings.theme,
        icon_version=settings.icon_version,
        has_icon=has_custom_icon(settings),
    )


@app.post(
    "/api/branding",
    response_model=BrandingSettingsResponse,
    dependencies=[Depends(verify_auth_token)],
)
async def update_branding_settings(
    payload: BrandingUpdateRequest,
) -> BrandingSettingsResponse:
    """Update branding settings (name/theme)."""
    try:
        settings = update_settings(
            app_name=payload.app_name,
            theme=payload.theme,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return BrandingSettingsResponse(
        app_name=settings.app_name,
        theme=settings.theme,
        icon_version=settings.icon_version,
        has_icon=has_custom_icon(settings),
    )


@app.post(
    "/api/branding/icon",
    response_model=BrandingSettingsResponse,
    dependencies=[Depends(verify_auth_token)],
)
async def upload_branding_icon(
    file: UploadFile = File(...),
) -> BrandingSettingsResponse:
    """Upload a base icon and generate required sizes."""
    allowed_types = {"image/png", "image/jpeg", "image/webp"}
    if file.content_type and file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Unsupported image type")

    try:
        content = await file.read()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Failed to read upload") from exc

    if not content:
        raise HTTPException(status_code=400, detail="Empty file upload")
    if len(content) > MAX_ICON_BYTES:
        raise HTTPException(status_code=413, detail="Icon file is too large")

    try:
        settings = save_uploaded_icon(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Icon processing failed")
        raise HTTPException(status_code=500, detail="Failed to process icon") from exc

    return BrandingSettingsResponse(
        app_name=settings.app_name,
        theme=settings.theme,
        icon_version=settings.icon_version,
        has_icon=has_custom_icon(settings),
    )


@app.get(
    "/api/branding/icon/{icon_name}",
    response_class=FileResponse,
    dependencies=[Depends(verify_auth_token)],
)
async def get_branding_icon(icon_name: str) -> FileResponse:
    """Serve generated branding icons."""
    if icon_name not in ICON_NAMES:
        raise HTTPException(status_code=404, detail="Icon not found")

    generate_icons()
    icon_path = get_icon_path(icon_name)
    if not icon_path.exists():
        raise HTTPException(status_code=404, detail="Icon not found")

    media_type = "image/x-icon" if icon_name.endswith(".ico") else "image/png"
    return FileResponse(icon_path, media_type=media_type)


@app.post(
    "/api/bootstrap",
    response_model=BootstrapResponse,
    dependencies=[Depends(verify_auth_token)],
)
async def bootstrap_knowledge_base(force: bool = False) -> BootstrapResponse:
    """Initialize the knowledge base directory structure."""
    from bootstrap import bootstrap

    results = bootstrap(force=force)
    return BootstrapResponse(**results)


@app.post(
    "/api/snapshot",
    response_model=SnapshotResponse,
    dependencies=[Depends(verify_auth_token)],
)
async def snapshot_changes(
    request: SnapshotRequest = SnapshotRequest(),
) -> SnapshotResponse:
    """Commit any uncommitted changes in the data directory.

    This is for manually snapshotting changes made outside of Gardener
    (e.g., manual edits, external tools). Does not auto-commit by default;
    must be explicitly called.
    """

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
    entries = result.stdout.split(b"\x00")
    i = 0
    while i < len(entries):
        entry = entries[i]
        if not entry:
            i += 1
            continue

        status = entry[:2].decode("utf-8", errors="replace")
        path = entry[3:].decode("utf-8", errors="replace")

        if status[0] == "R" or status[1] == "R":
            # Rename: next entry is the old path (old file no longer exists)
            old_path = (
                entries[i + 1].decode("utf-8", errors="replace")
                if i + 1 < len(entries)
                else None
            )
            parsed_changes.append(
                {"status": "rename", "path": path, "old_path": old_path}
            )
            i += 2  # Skip both entries
        elif status[0] == "C" or status[1] == "C":
            # Copy: next entry is the source path (source file still exists)
            old_path = (
                entries[i + 1].decode("utf-8", errors="replace")
                if i + 1 < len(entries)
                else None
            )
            parsed_changes.append(
                {"status": "copy", "path": path, "old_path": old_path}
            )
            i += 2  # Skip both entries
        elif status[0] == "D" or status[1] == "D":
            parsed_changes.append({"status": "delete", "path": path, "old_path": None})
            i += 1
        else:
            parsed_changes.append({"status": "modify", "path": path, "old_path": None})
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
            from file_state import remove_file_state, update_file_state
            from git_state import (
                get_current_branch,
                get_current_head,
                record_processed_commit,
            )
            from provenance import PROVENANCE_MANUAL, record_provenance

            head = get_current_head()
            if head:
                branch = get_current_branch()
                record_processed_commit(head, branch, commit_message)

                # Update file state and provenance based on change type
                for change in parsed_changes:
                    file_path = change["path"]
                    full_path = DATA_DIR / file_path

                    if change["status"] == "delete":
                        # Remove deleted files from state
                        remove_file_state(full_path)
                        record_provenance(
                            file_path, PROVENANCE_MANUAL, head, {"action": "delete"}
                        )
                    elif change["status"] == "rename":
                        # Remove old path, add new path
                        if change["old_path"]:
                            remove_file_state(DATA_DIR / change["old_path"])
                        if full_path.exists():
                            update_file_state(full_path)
                        record_provenance(
                            file_path,
                            PROVENANCE_MANUAL,
                            head,
                            {"action": "rename", "from": change["old_path"]},
                        )
                    elif change["status"] == "copy":
                        # Keep source in state, add new path
                        if full_path.exists():
                            update_file_state(full_path)
                        record_provenance(
                            file_path,
                            PROVENANCE_MANUAL,
                            head,
                            {"action": "copy", "from": change["old_path"]},
                        )
                    else:
                        # Add/modify
                        if full_path.exists():
                            update_file_state(full_path)
                            record_provenance(file_path, PROVENANCE_MANUAL, head)
        except (ImportError, OSError) as e:
            logger.debug(f"State tracking unavailable: {e}")
        except Exception as e:
            logger.warning(f"State tracking failed: {e}")

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


@app.post(
    "/api/reconcile",
    response_model=ReconcileResponse,
    dependencies=[Depends(verify_auth_token)],
)
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
        from db import init_db
        from file_state import get_changes_since_sha, get_dirty_summary, run_reconcile
        from git_state import check_repo_identity, get_dirty_files

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


@app.post(
    "/api/inbox",
    response_model=InboxResponse,
    dependencies=[Depends(verify_auth_token)],
)
async def submit_to_inbox(request: InboxRequest) -> InboxResponse:
    """Accept note content and save to inbox as timestamped markdown."""
    # Validate content
    content = request.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Content cannot be empty")

    if len(content) > MAX_CONTENT_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Content too large (max {MAX_CONTENT_SIZE // 1024}KB)",
        )

    INBOX_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    short_uuid = uuid4().hex[:8]
    filename = f"{now.strftime('%Y-%m-%d_%H%M')}-{short_uuid}.md"
    filepath = INBOX_DIR / filename

    try:
        filepath.write_text(content)
        logger.info(f"Saved note to inbox: {filename}")
    except OSError as e:
        logger.error(f"Failed to write inbox file {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to write file: {e}")

    return InboxResponse(filename=filename, message="Note saved to inbox")


def run_gardener() -> None:
    """Run the gardener worker in the background."""
    from workers.gardener import process_inbox

    process_inbox()


@app.post(
    "/api/trigger-gardener",
    response_model=GardenerTriggerResponse,
    dependencies=[Depends(verify_auth_token)],
)
async def trigger_gardener(
    background_tasks: BackgroundTasks,
) -> GardenerTriggerResponse:
    """Manually trigger the gardener to process the inbox."""
    background_tasks.add_task(run_gardener)
    return GardenerTriggerResponse(
        message="Gardener processing started in background",
        status="started",
    )


# --- Refine Endpoint ---


def search_atlas(keywords: list[str], max_files: int = 5) -> list[dict]:
    """Search atlas for files containing keywords.

    Uses an in-memory cache for file contents to avoid repeated disk reads.
    """
    if not ATLAS_DIR.exists():
        return []

    matches = []
    keywords_lower = [kw.lower() for kw in keywords if kw]
    for md_file in ATLAS_DIR.rglob("*.md"):
        try:
            # Try cache first, fall back to disk read
            content = _atlas_content_cache.get(md_file)
            if content is None:
                content = md_file.read_text()
                _atlas_content_cache.put(md_file, content)

            content_lower = content.lower()
            content_score = sum(1 for kw in keywords_lower if kw in content_lower)
            if content_score > 0:
                rel_path = str(md_file.relative_to(ATLAS_DIR))
                path_lower = rel_path.lower()
                filename_score = sum(1 for kw in keywords_lower if kw in path_lower)
                score = content_score * 10 + filename_score
                preview = content[:200].replace("\n", " ")
                matches.append(
                    {
                        "path": rel_path,
                        "score": score,
                        "preview": preview,
                    }
                )
        except (OSError, UnicodeDecodeError) as e:
            logger.debug(f"Could not read {md_file}: {e}")
            continue

    matches.sort(key=lambda x: (-x["score"], x["path"]))
    return matches[:max_files]


def extract_keywords(content: str) -> list[str]:
    """Extract potential keywords from content."""
    stopwords = {
        "this",
        "that",
        "with",
        "from",
        "have",
        "been",
        "will",
        "would",
        "could",
        "should",
        "about",
        "what",
        "when",
        "where",
        "which",
        "their",
        "there",
        "these",
        "those",
        "some",
        "other",
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
    import html

    html_parts = ['<div class="space-y-2 text-sm">']

    for line in result.strip().split("\n"):
        if line.startswith("TAGS:"):
            tags = html.escape(line.replace("TAGS:", "").strip())
            html_parts.append(
                f'<p><span class="text-gray-400">Tags:</span> <span class="text-blue-400">{tags}</span></p>'
            )
        elif line.startswith("CATEGORY:"):
            category = html.escape(line.replace("CATEGORY:", "").strip())
            html_parts.append(
                f'<p><span class="text-gray-400">Category:</span> <span class="text-green-400">{category}</span></p>'
            )
        elif line.startswith("RELATED:"):
            related_text = line.replace("RELATED:", "").strip()
            if related_text and related_text.lower() != "none":
                html_parts.append(
                    f'<p><span class="text-gray-400">Related:</span> <span class="text-purple-400">{html.escape(related_text)}</span></p>'
                )
        elif line.startswith("MISSING:"):
            missing = line.replace("MISSING:", "").strip()
            if missing and missing.lower() != "none":
                html_parts.append(
                    f'<p><span class="text-gray-400">Consider adding:</span> <span class="text-yellow-400">{html.escape(missing)}</span></p>'
                )

    html_parts.append("</div>")
    return "\n".join(html_parts)


def format_ask_html(answer: str, related: list[dict]) -> str:
    """Format ask result as HTML."""
    import html

    escaped = html.escape(answer.strip())
    html_parts = ['<div class="space-y-3 text-sm">']
    if escaped:
        html_parts.append(
            f'<div class="whitespace-pre-wrap text-gray-200">{escaped}</div>'
        )
    else:
        html_parts.append('<p class="text-gray-500">No answer returned.</p>')

    if related:
        html_parts.append('<div class="text-xs text-gray-400">Related files:</div>')
        html_parts.append('<ul class="list-disc list-inside text-xs text-gray-400">')
        for item in related:
            html_parts.append(f"<li>{html.escape(item['path'])}</li>")
        html_parts.append("</ul>")

    html_parts.append("</div>")
    return "\n".join(html_parts)


@app.post("/api/refine", dependencies=[Depends(verify_auth_token)])
async def refine_content(request: RefineRequest):
    """Analyze content and suggest context, tags, and related notes."""
    content = (request.content or "").strip()
    if not content:
        return HTMLResponse(
            '<p class="text-gray-500">Enter some content to get suggestions.</p>'
        )

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
        import html

        return HTMLResponse(
            f'<p class="text-yellow-500">AI not configured: {html.escape(str(e))}</p>'
        )
    except Exception as e:
        import html

        return HTMLResponse(
            f'<p class="text-red-500">Refinement failed: {html.escape(str(e))}</p>'
        )


@app.post("/api/ask", dependencies=[Depends(verify_auth_token)])
async def ask_question(request: AskRequest):
    """Answer a question using the knowledge base as context."""
    question = (request.question or "").strip()
    if not question:
        return HTMLResponse(
            '<p class="text-gray-500">Enter a question to explore your notes.</p>'
        )

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
        import html

        return HTMLResponse(
            f'<p class="text-yellow-500">AI not configured: {html.escape(str(e))}</p>'
        )
    except Exception as e:
        import html

        return HTMLResponse(
            f'<p class="text-red-500">Ask failed: {html.escape(str(e))}</p>'
        )


# --- Browse Endpoints ---


def browse_directory(root: Path, path: str) -> BrowseResponse:
    """Browse a directory tree rooted at the provided path."""
    target = root / path if path else root

    if not target.exists():
        raise HTTPException(status_code=404, detail="Path not found")

    # Security check: ensure path is within root
    try:
        target.resolve().relative_to(root.resolve())
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
        item_path = str(item.relative_to(root))
        items.append(
            BrowseItem(
                name=item.name,
                type="directory" if item.is_dir() else "file",
                path=item_path,
            )
        )

    # Sort: directories first, then files
    items.sort(key=lambda x: (0 if x.type == "directory" else 1, x.name.lower()))

    return BrowseResponse(path=path, items=items, is_file=False)


@app.get(
    "/api/browse/{path:path}",
    response_model=BrowseResponse,
    dependencies=[Depends(verify_auth_token)],
)
@app.get(
    "/api/browse",
    response_model=BrowseResponse,
    dependencies=[Depends(verify_auth_token)],
)
async def browse_atlas(path: str = "") -> BrowseResponse:
    """Browse the atlas directory structure."""
    return browse_directory(ATLAS_DIR, path)


@app.get(
    "/api/archive/{path:path}",
    response_model=BrowseResponse,
    dependencies=[Depends(verify_auth_token)],
)
@app.get(
    "/api/archive",
    response_model=BrowseResponse,
    dependencies=[Depends(verify_auth_token)],
)
async def browse_archive(path: str = "") -> BrowseResponse:
    """Browse archived inbox notes."""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    return browse_directory(ARCHIVE_DIR, path)


@app.get(
    "/api/random",
    dependencies=[Depends(verify_auth_token)],
)
async def get_random_note():
    """Get a random note from the atlas for serendipitous discovery."""
    import random
    import secrets

    # Get all markdown files from atlas
    atlas_files = []
    if ATLAS_DIR.exists():
        for md_file in ATLAS_DIR.rglob("*.md"):
            try:
                rel_path = str(md_file.relative_to(ATLAS_DIR))
                atlas_files.append(rel_path)
            except (OSError, ValueError):
                continue

    if not atlas_files:
        raise HTTPException(status_code=404, detail="No notes found in atlas")

    # Use secrets for cryptographically secure randomness
    random_note = secrets.choice(atlas_files)

    return {"path": random_note}


@app.get(
    "/api/recent",
    dependencies=[Depends(verify_auth_token)],
)
async def get_recent_activity(limit: int = 10):
    """Get recently modified notes from atlas for quick access."""
    import subprocess
    from datetime import datetime, timezone

    if not ATLAS_DIR.exists():
        return {"recent": []}

    try:
        # Use git log to get recently committed files
        # Format: commit_time|file_path (one per line)
        result = subprocess.run(
            [
                "git",
                "log",
                "--name-only",
                "--pretty=format:%ct",
                "--diff-filter=AM",  # Added or Modified files only
                f"-{limit * 3}",  # Get more than needed to account for duplicates
            ],
            cwd=ATLAS_DIR,
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode != 0:
            logger.warning(f"Git log failed: {result.stderr}")
            return {"recent": []}

        # Parse git log output
        lines = result.stdout.strip().split("\n")
        seen_files = set()
        recent_notes = []
        current_timestamp = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Lines with only digits are timestamps
            if line.isdigit():
                current_timestamp = int(line)
            elif line.endswith(".md") and current_timestamp:
                # This is a file path
                if line not in seen_files:
                    seen_files.add(line)
                    # Extract category from path (first directory)
                    parts = line.split("/")
                    category = parts[0] if len(parts) > 1 else None

                    recent_notes.append(
                        {
                            "path": line,
                            "timestamp": current_timestamp,
                            "category": category,
                        }
                    )

                    if len(recent_notes) >= limit:
                        break

        return {"recent": recent_notes}

    except subprocess.TimeoutExpired:
        logger.error("Git log timeout")
        return {"recent": []}
    except Exception as e:
        logger.error(f"Error getting recent activity: {e}")
        return {"recent": []}
