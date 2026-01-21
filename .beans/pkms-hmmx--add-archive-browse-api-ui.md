---
# pkms-hmmx
title: Add archive browse API + UI
status: completed
type: feature
priority: normal
created_at: 2026-01-21T06:41:47Z
updated_at: 2026-01-21T06:48:46Z
---

Expose archived inbox notes via a safe browse API and add UI support to view them. Prefer explicit /api/archive and /archive routes; ensure auth applies and archive stays read-only.

## Checklist
- [x] Inspect existing browse endpoints + UI flow
- [x] Add archive browse endpoint in Gardener
- [x] Add Scribe proxy + UI route for archive browsing
- [x] Update docs/AGENTS if needed
- [x] Run targeted tests/builds
