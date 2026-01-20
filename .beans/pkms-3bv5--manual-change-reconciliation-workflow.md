---
# pkms-3bv5
title: Manual change reconciliation workflow
status: todo
type: feature
priority: normal
created_at: 2026-01-20T05:50:06Z
updated_at: 2026-01-20T15:12:17Z
parent: pkms-wsuj
---

Provide a safe workflow when notes are edited manually or by external tools (diff awareness, automatic maintenance tasks, and optional reprocessing) without clobbering user edits. Prefer automated handling over user prompts; treat inbox edits as normal ingestion while curated note edits trigger reconciliation tasks.\n\n## Checklist\n- [ ] Define detection rules (git diff vs hash/mtime tracking) and classification by location (/inbox vs /atlas vs /meta)\n- [ ] Define source-of-truth rules (never auto-rewrite curated notes; only update derived artifacts)\n- [ ] Add reconcile operation (CLI or API) that summarizes changed files, including rename/delete detection\n- [ ] Generate maintenance tasks: reindex, refresh backlinks, consistency checks, update derived artifacts (without rewriting originals)\n- [ ] Avoid reprocessing loops (ignore derived outputs; record last reconcile run)\n- [ ] Document default auto-policy and optional override config