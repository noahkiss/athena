---
# pkms-zit7
title: Replace broad exception handling with specific types
status: completed
type: bug
priority: normal
created_at: 2026-01-21T00:15:47Z
updated_at: 2026-01-21T01:23:13Z
---

Multiple `except Exception:` blocks throughout the codebase silently swallow errors, making debugging difficult and potentially hiding issues.

## Locations

### gardener/main.py
- **Line 226**: `except Exception:` returns None silently in `get_git_state()`
- **Line 390**: `except Exception:` swallows all errors when updating state
- **Line 538**: `except Exception: continue` in loop silently ignores file read failures
- **Line 629**: `except Exception:` in refine endpoint
- **Line 654**: `except Exception:` in ask endpoint

### gardener/workers/gardener.py
- **Line 217**: `except Exception:` silently passes state tracking failures

### gardener/mcp_tools.py
- **Line 64**: `except Exception: continue` in loop
- **Line 102**: `except Exception:` in search

## Fix Approach
1. Identify specific exceptions that can occur (OSError, IOError, subprocess.CalledProcessError, etc.)
2. Catch specific types and handle appropriately
3. Log unexpected exceptions with context before re-raising or returning error
4. Add structured logging with file/function context

## Checklist
- [x] Audit all `except Exception:` blocks
- [x] Replace with specific exception types where possible
- [x] Add logging for caught exceptions with context
- [x] Ensure errors propagate appropriately (don't silently fail)
- [x] Test error paths work correctly

## Changes Made

### gardener/main.py
- `get_git_state()`: Now catches `(ImportError, OSError, subprocess.CalledProcessError)` with warning log, plus fallback `Exception` with exception log
- State tracking (snapshot): Now catches `(ImportError, OSError)` with debug log, plus fallback `Exception` with warning log
- `search_atlas()`: Now catches `(OSError, UnicodeDecodeError)` with debug log
- `/api/refine` and `/api/ask` endpoints: Already fixed in pkms-7e63 (XSS bug) - exceptions are now escaped with `html.escape()`

### gardener/workers/gardener.py
- `remove_file_state`: Now catches `(ImportError, OSError)` with debug log, plus fallback `Exception` with warning log

### gardener/mcp_tools.py
- Added logging setup (`import logging`, `logger = getLogger(__name__)`)
- Content search: Now catches `(OSError, UnicodeDecodeError)` with debug log
- `add_note()`: Now catches `OSError` specifically with warning log