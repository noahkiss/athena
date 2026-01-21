"""Automated gardener processing via file watching or polling."""

import asyncio
import logging

from watchfiles import Change, awatch

from config import (
    GARDENER_AUTO,
    GARDENER_DEBOUNCE,
    GARDENER_MODE,
    GARDENER_POLL_INTERVAL,
    INBOX_DIR,
)

logger = logging.getLogger(__name__)

# Track if processing is currently running to avoid overlapping runs
_processing_lock = asyncio.Lock()


async def _run_gardener() -> None:
    """Run the gardener processor (called from async context)."""
    from workers.gardener import process_inbox

    async with _processing_lock:
        logger.info("Running gardener processor...")
        try:
            # Run sync function in thread pool
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(None, process_inbox)

            success = sum(1 for r in results if r.get("success"))
            failed = sum(1 for r in results if not r.get("success"))

            if results:
                logger.info(f"Gardener completed: {success} processed, {failed} failed")
            else:
                logger.debug("Gardener: inbox empty")
        except Exception as e:
            logger.error(f"Gardener processing failed: {e}")


async def watch_inbox() -> None:
    """Watch inbox directory for changes and trigger processing."""
    logger.info(f"Starting inbox watcher (debounce: {GARDENER_DEBOUNCE}s)")

    # Ensure inbox exists
    INBOX_DIR.mkdir(parents=True, exist_ok=True)

    pending_process: asyncio.Task | None = None

    async def debounced_process():
        """Wait for debounce period then process."""
        await asyncio.sleep(GARDENER_DEBOUNCE)
        await _run_gardener()

    try:
        async for changes in awatch(INBOX_DIR, recursive=False):
            # Filter for markdown file additions
            md_changes = [
                (change, path)
                for change, path in changes
                if path.endswith(".md") and change in (Change.added, Change.modified)
            ]

            if not md_changes:
                continue

            logger.debug(f"Detected changes: {md_changes}")

            # Cancel pending process and restart debounce timer
            if pending_process and not pending_process.done():
                pending_process.cancel()
                try:
                    await pending_process
                except asyncio.CancelledError:
                    pass

            # Start new debounced process
            pending_process = asyncio.create_task(debounced_process())

    except asyncio.CancelledError:
        logger.info("Inbox watcher stopped")
        if pending_process and not pending_process.done():
            pending_process.cancel()
        raise


async def poll_inbox() -> None:
    """Poll inbox directory at intervals and trigger processing."""
    logger.info(f"Starting inbox poller (interval: {GARDENER_POLL_INTERVAL}s)")

    try:
        while True:
            # Check if inbox has files
            INBOX_DIR.mkdir(parents=True, exist_ok=True)
            md_files = list(INBOX_DIR.glob("*.md"))

            if md_files:
                logger.debug(f"Poll found {len(md_files)} files in inbox")
                await _run_gardener()

            await asyncio.sleep(GARDENER_POLL_INTERVAL)

    except asyncio.CancelledError:
        logger.info("Inbox poller stopped")
        raise


async def start_automation() -> None:
    """Start the appropriate automation mode based on config."""
    if not GARDENER_AUTO:
        logger.info("Gardener automation disabled (set GARDENER_AUTO=true to enable)")
        return

    if GARDENER_MODE == "poll":
        await poll_inbox()
    else:
        await watch_inbox()


def get_automation_status() -> dict:
    """Get current automation configuration status."""
    return {
        "enabled": GARDENER_AUTO,
        "mode": GARDENER_MODE if GARDENER_AUTO else None,
        "poll_interval": GARDENER_POLL_INTERVAL if GARDENER_MODE == "poll" else None,
        "debounce": GARDENER_DEBOUNCE if GARDENER_MODE == "watch" else None,
    }
