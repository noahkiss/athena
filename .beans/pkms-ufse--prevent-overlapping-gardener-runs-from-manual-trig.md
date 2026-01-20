---
# pkms-ufse
title: Prevent overlapping Gardener runs from manual trigger vs automation
status: completed
type: task
priority: normal
created_at: 2026-01-20T00:32:01Z
updated_at: 2026-01-20T03:42:37Z
---

Manual /api/trigger-gardener runs process_inbox without the automation lock, so it can overlap with watcher/poller runs. Consider reusing the same lock or centralizing processing to avoid double-processing.\n\n## Checklist\n- [x] Decide on single processing gate\n- [x] Update trigger_gardener to use shared lock\n- [x] Add basic test or log to confirm serialization
