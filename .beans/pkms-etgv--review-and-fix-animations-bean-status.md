---
# pkms-etgv
title: Review and fix animations bean status
status: completed
type: task
priority: normal
created_at: 2026-01-22T13:31:10Z
updated_at: 2026-01-22T13:31:28Z
---

Bean pkms-pcbt is marked completed but has 3 unchecked items. Need to either:
1. Remove unchecked items that can't be done (dropdowns/toasts don't exist, local testing required)
2. Or mark bean as scrapped/blocked if those items are required

## Context
- Dropdown animations: No dropdowns exist yet
- Toast animations: No toasts implemented
- Performance testing: Requires local device testing

## Decision
Remove the 3 items that can't currently be completed and update the bean body to note what's missing for future work.