---
# pkms-ifzz
title: 'Clean up beans: fix statuses, add blocking, adjust priorities'
status: completed
type: task
priority: normal
created_at: 2026-01-20T17:03:24Z
updated_at: 2026-01-20T17:04:48Z
---

Analysis revealed issues with bean metadata:
- 5 beans have invalid 'done' status (should be 'completed')
- No blocking relationships despite clear dependencies
- Foundation beans not prioritized

## Checklist
- [x] Fix 5 invalid statuses (done → completed)
- [x] Add 4 blocking relationships for dependency chain
- [x] Set high priority on foundation beans (4rpv, pcbh)