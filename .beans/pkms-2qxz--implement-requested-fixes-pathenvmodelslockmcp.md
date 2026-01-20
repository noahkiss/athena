---
# pkms-2qxz
title: Implement requested fixes (path/env/models/lock/MCP)
status: completed
type: task
priority: normal
created_at: 2026-01-20T03:37:53Z
updated_at: 2026-01-20T03:41:07Z
---

Implement requested fixes: validate Gardener action paths, use runtime GARDNER_URL in Scribe, add fast/thinking model config, add cross-run lock, and adjust MCP mount to avoid API shadowing.\n\n## Checklist\n- [x] Validate action.path and safe fallback\n- [x] Update Scribe to read GARDNER_URL at runtime\n- [x] Implement fast/thinking model config in backends and docs\n- [x] Add shared processing lock to avoid overlap\n- [x] Fix MCP mount path configuration
