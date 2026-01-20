---
# pkms-nbkt
title: Surface git status + dirty detection for data dir
status: todo
type: feature
priority: normal
created_at: 2026-01-20T05:49:54Z
updated_at: 2026-01-20T15:12:40Z
parent: pkms-wsuj
---

Expose data-repo state (current HEAD, last-seen commit from Gardener, dirty flag, changed files summary, /inbox vs /atlas vs /meta counts) via /api/status and optionally in Scribe UI. This supports manual edit awareness without auto-committing changes.\n\n## Checklist\n- [ ] Add git status/HEAD info to Gardener status response (guarded by git availability)\n- [ ] Include last-seen commit info from SQLite/state\n- [ ] Add summary counts by area (/inbox vs /atlas vs /meta) plus truncated file list\n- [ ] Decide how to display in Scribe (banner, status panel, etc.)\n- [ ] Document env flags or config knobs