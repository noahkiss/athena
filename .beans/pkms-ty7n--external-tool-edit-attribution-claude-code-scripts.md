---
# pkms-ty7n
title: External tool edit attribution (Claude Code, scripts, MCP)
status: completed
type: feature
priority: normal
created_at: 2026-01-20T05:50:12Z
updated_at: 2026-01-20T17:38:43Z
parent: pkms-wsuj
---

Treat edits from Claude Code or other tooling like manual edits while preserving attribution/source metadata, and record optional provenance in SQLite when possible.

## Checklist
- [x] Define how to record source attribution (commit author, frontmatter, or sidecar metadata)
  - Decision: Use commit message prefix + SQLite provenance table
  - Commit messages: `External[tool-name]: action description`
  - Avoids modifying note content or frontmatter
- [x] Decide default provenance location to avoid touching curated notes (prefer sidecar/DB)
  - Provenance stored in SQLite `edit_provenance` table
  - Columns: file_path, commit_sha, source, recorded_at, metadata (JSON)
  - Never touches the note files themselves
- [x] Add a standard tag for external-tool edits in git commit messages
  - Format: `External[tool-name]: action`
  - Predefined constants: PROVENANCE_EXTERNAL_CLAUDE, PROVENANCE_EXTERNAL_MCP, PROVENANCE_EXTERNAL_SCRIPT
  - `format_commit_message()` and `parse_commit_source()` helpers
- [x] Record external tool provenance in SQLite state when enabled
  - `record_provenance(file_path, source, commit_sha, metadata)` function
  - `get_file_provenance(file_path)` returns history
  - `get_provenance_by_source(source)` for auditing
- [x] Ensure reconciliation workflow treats external edits identically to manual ones
  - Already handled: reconciliation uses git diff, not source tracking
  - External commits parsed same as manual (atlas = source of truth)
  - No distinction in maintenance task generation
- [x] Document recommended practices for external tooling
  - Use `External[tool-name]:` commit message prefix
  - Call `record_provenance()` after edits for audit trail
  - Never auto-modify atlas notes (same as manual edit policy)
  - Inbox submissions are fine (processed normally by gardener)