---
# pkms-3bv5
title: Manual change reconciliation workflow
status: todo
type: feature
priority: normal
created_at: 2026-01-20T05:50:06Z
updated_at: 2026-01-20T05:50:31Z
parent: pkms-wsuj
---

Provide a safe workflow when notes are edited manually or by external tools (diff awareness, optional reprocessing, and maintenance tasks without clobbering user edits).\n\n## Checklist\n- [ ] Define detection rules (git diff vs hash/mtime tracking)\n- [ ] Add reconcile operation (CLI or API) that summarizes changed files\n- [ ] Optional: generate maintenance tasks or suggestions instead of rewriting files\n- [ ] Ensure gardener avoids overwriting locally-edited files without warning