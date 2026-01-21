---
# pkms-2d51
title: Archive processed inbox notes
status: completed
type: feature
priority: normal
created_at: 2026-01-21T06:33:46Z
updated_at: 2026-01-21T06:40:10Z
---

Add an archive for raw inbox notes that should be ignored by AI agents. After successful processing, move the original inbox file into /inbox/archive instead of deleting it, update state tracking and docs.

## Checklist
- [x] Decide archive behavior and location
- [x] Update gardener worker to move inbox files into archive
- [x] Adjust state tracking + git commit for archived files
- [x] Update documentation/AGENTS/bootstrap to mention archive
- [x] Run relevant tests/builds
