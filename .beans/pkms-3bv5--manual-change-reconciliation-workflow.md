---
# pkms-3bv5
title: Manual change reconciliation workflow
status: completed
type: feature
priority: normal
created_at: 2026-01-20T05:50:06Z
updated_at: 2026-01-20T17:34:16Z
parent: pkms-wsuj
blocking:
    - pkms-ty7n
---

Provide a safe workflow when notes are edited manually or by external tools (diff awareness, automatic maintenance tasks, and optional reprocessing) without clobbering user edits. Prefer automated handling over user prompts; treat inbox edits as normal ingestion while curated note edits trigger reconciliation tasks.

## Checklist
- [x] Define detection rules (git diff vs hash/mtime tracking) and classification by location (/inbox vs /atlas vs /meta)
  - Uses `git diff --name-status -M` for change detection with rename support
  - `classify_location()` categorizes files into inbox/atlas/meta/root
  - Tracks from last reconcile SHA or last processed SHA
- [x] Define source-of-truth rules (never auto-rewrite curated notes; only update derived artifacts)
  - Atlas: generate review tasks only, never auto-modify ("manual edits preserved")
  - Inbox: trigger normal gardener processing
  - Meta: flag for reindexing (derived artifacts can be regenerated)
- [x] Add reconcile operation (CLI or API) that summarizes changed files, including rename/delete detection
  - `POST /api/reconcile` endpoint with optional `?include_details=true`
  - Detects: added, modified, deleted, renamed files
  - Returns: files_changed, changes_by_location, tasks, optional detailed changes list
- [x] Generate maintenance tasks: reindex, refresh backlinks, consistency checks, update derived artifacts (without rewriting originals)
  - `generate_maintenance_tasks()` creates task list based on change types
  - Tasks include: process inbox, index atlas, clean references, update links, regenerate meta, refresh backlinks, consistency check
- [x] Avoid reprocessing loops (ignore derived outputs; record last reconcile run)
  - `reconcile_runs` table tracks each run with SHA range
  - `last_reconcile_sha` in repo_state prevents re-processing same changes
  - Meta directory flagged for regeneration, not re-reconciled
- [x] Document default auto-policy and optional override config
  - Default: manual reconcile via API call (no auto-reconcile)
  - Reconcile is idempotent; running twice on same state yields no new tasks
  - No override config needed yet (can be added if auto-reconcile requested)