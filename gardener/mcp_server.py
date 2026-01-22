"""MCP Server for Athena PKMS - External AI access to notes."""

import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
INBOX_DIR = DATA_DIR / "inbox"
ATLAS_DIR = DATA_DIR / "atlas"

server = Server("athena-pkms")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="read_notes",
            description="Read notes from the Athena knowledge base. Can browse directories or read specific files.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path relative to atlas (e.g., 'projects/my-project.md'). Empty for root listing.",
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query to filter files by content (optional).",
                    },
                },
            },
        ),
        Tool(
            name="add_note",
            description="Add a new note to the Athena inbox for later processing by the Gardener.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The note content (markdown supported).",
                    },
                },
                "required": ["content"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name == "read_notes":
        return await read_notes(arguments.get("path", ""), arguments.get("query"))
    elif name == "add_note":
        return await add_note(arguments.get("content", ""))
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def read_notes(path: str, query: str | None) -> list[TextContent]:
    """Read notes from the atlas."""
    target = ATLAS_DIR / path if path else ATLAS_DIR

    if not target.exists():
        return [TextContent(type="text", text=f"Path not found: {path}")]

    # Security check
    try:
        target.resolve().relative_to(ATLAS_DIR.resolve())
    except ValueError:
        return [TextContent(type="text", text="Access denied")]

    if target.is_file():
        content = target.read_text()
        return [TextContent(type="text", text=f"# {target.name}\n\n{content}")]

    # Directory listing with optional search
    results = []
    for item in sorted(target.rglob("*.md") if query else target.iterdir()):
        if item.name.startswith("."):
            continue

        if item.is_dir():
            results.append(f"[DIR] {item.name}/")
        else:
            # If query provided, search content
            if query:
                try:
                    content = item.read_text()
                    if query.lower() in content.lower():
                        rel_path = item.relative_to(ATLAS_DIR)
                        preview = content[:200].replace("\n", " ")
                        results.append(f"[FILE] {rel_path}: {preview}...")
                except Exception:
                    continue
            else:
                results.append(f"[FILE] {item.name}")

    if not results:
        return [
            TextContent(
                type="text",
                text="No files found" + (f" matching '{query}'" if query else ""),
            )
        ]

    header = f"Contents of atlas/{path}" if path else "Atlas root"
    if query:
        header += f" (search: {query})"

    return [TextContent(type="text", text=f"{header}:\n\n" + "\n".join(results))]


async def add_note(content: str) -> list[TextContent]:
    """Add a note to the inbox."""
    if not content.strip():
        return [TextContent(type="text", text="Error: Content cannot be empty")]

    INBOX_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    short_uuid = uuid4().hex[:8]
    filename = f"{now.strftime('%Y-%m-%d_%H%M')}-{short_uuid}.md"
    filepath = INBOX_DIR / filename

    try:
        filepath.write_text(content)
        return [TextContent(type="text", text=f"Note saved to inbox: {filename}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error saving note: {e}")]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
