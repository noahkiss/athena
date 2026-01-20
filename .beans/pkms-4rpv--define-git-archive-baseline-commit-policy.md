---
# pkms-4rpv
title: Define git archive baseline + commit policy
status: todo
type: feature
priority: normal
created_at: 2026-01-20T05:50:01Z
updated_at: 2026-01-20T15:12:28Z
parent: pkms-wsuj
---

Clarify how the knowledge base becomes a git archive: initial repo setup, baseline commit, commit message conventions, and optional auto-commit for manual edits (manual edits are source of truth).\n\n## Checklist\n- [ ] Decide whether bootstrap should make a baseline commit\n- [ ] Add/confirm .gitignore policy for data dir (logs, tmp, cache)\n- [ ] Define commit message format for gardener vs manual vs external tools\n- [ ] Ensure gardener commits only touched files (avoid staging manual edits)\n- [ ] Decide policy for auto-committing manual edits (default off) and how to record in SQLite\n- [ ] Add optional snapshot command/endpoint to commit dirty changes on demand