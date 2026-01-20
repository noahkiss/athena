---
# pkms-nbkt
title: Surface git status + dirty detection for data dir
status: todo
type: feature
priority: normal
created_at: 2026-01-20T05:49:54Z
updated_at: 2026-01-20T05:50:23Z
parent: pkms-wsuj
---

Expose data-repo state (last commit sha/time, dirty flag, changed files summary) via /api/status and optionally in Scribe UI. This supports manual edit awareness without auto-committing changes.\n\n## Checklist\n- [ ] Add git status/HEAD info to Gardener status response (guarded by git availability)\n- [ ] Add optional list/summary of modified/untracked files with truncation\n- [ ] Decide how to display in Scribe (banner, status panel, etc.)\n- [ ] Document env flags or config knobs