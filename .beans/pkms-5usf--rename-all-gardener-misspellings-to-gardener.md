---
# pkms-5usf
title: Rename misspelled service name to gardener
status: completed
type: task
priority: normal
created_at: 2026-01-20T15:37:36Z
updated_at: 2026-01-20T16:34:15Z
---

Replace all misspellings of the service name with the correct 'gardener' spelling (including env vars, docs, beans, and gitignored files) and verify no remaining occurrences.\n\nNotes: After user recreated venv, remaining matches are only binary __pycache__ files.\n\n## Checklist\n- [x] Scan repo (including gitignored files) for misspelled occurrences\n- [x] Rename env vars, files, docs, and code references to 'gardener'\n- [x] Update beans titles/paths/text for spelling\n- [x] Re-scan to confirm no remaining misspellings\n- [x] Summarize changes