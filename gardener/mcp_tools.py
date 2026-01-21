"""MCP Tools for Athena PKMS - FastMCP integration."""

import logging
from datetime import datetime
from uuid import uuid4

from mcp.server.fastmcp import FastMCP

from config import ATLAS_DIR, INBOX_DIR

logger = logging.getLogger(__name__)

# Create MCP server with stateless HTTP mode.
# Set streamable_http_path="/" so mounting at /mcp exposes /mcp (no double /mcp/mcp).
mcp = FastMCP(
    "athena-pkms",
    stateless_http=True,
    json_response=True,
    streamable_http_path="/",
)


@mcp.tool()
def read_notes(path: str = "", query: str | None = None) -> str:
    """Read notes from the Athena knowledge base.

    Can browse directories or read specific files. Optionally search by content.

    Args:
        path: Path relative to atlas (e.g., 'projects/my-project.md'). Empty for root listing.
        query: Search query to filter files by content (optional).
    """
    target = ATLAS_DIR / path if path else ATLAS_DIR

    if not target.exists():
        return f"Path not found: {path}"

    # Security check: ensure path is within ATLAS_DIR
    try:
        target.resolve().relative_to(ATLAS_DIR.resolve())
    except ValueError:
        return "Access denied"

    if target.is_file():
        content = target.read_text()
        return f"# {target.name}\n\n{content}"

    # Directory listing with optional search
    results = []
    items = sorted(target.rglob("*.md") if query else target.iterdir())

    for item in items:
        if item.name.startswith("."):
            continue

        if item.is_dir():
            results.append(f"📁 {item.name}/")
        else:
            # If query provided, search content
            if query:
                try:
                    content = item.read_text()
                    if query.lower() in content.lower():
                        rel_path = item.relative_to(ATLAS_DIR)
                        preview = content[:200].replace("\n", " ")
                        results.append(f"📄 {rel_path}: {preview}...")
                except (OSError, UnicodeDecodeError) as e:
                    logger.debug(f"Could not read {item}: {e}")
                    continue
            else:
                results.append(f"📄 {item.name}")

    if not results:
        msg = "No files found"
        if query:
            msg += f" matching '{query}'"
        return msg

    header = f"Contents of atlas/{path}" if path else "Atlas root"
    if query:
        header += f" (search: {query})"

    return f"{header}:\n\n" + "\n".join(results)


@mcp.tool()
def add_note(content: str) -> str:
    """Add a new note to the Athena inbox for later processing by the Gardener.

    Args:
        content: The note content (markdown supported).
    """
    if not content.strip():
        return "Error: Content cannot be empty"

    INBOX_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    short_uuid = uuid4().hex[:8]
    filename = f"{now.strftime('%Y-%m-%d_%H%M')}-{short_uuid}.md"
    filepath = INBOX_DIR / filename

    try:
        filepath.write_text(content)
        return f"Note saved to inbox: {filename}"
    except OSError as e:
        logger.warning(f"Failed to save note to {filepath}: {e}")
        return f"Error saving note: {e}"
