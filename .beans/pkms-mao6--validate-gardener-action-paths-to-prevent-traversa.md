---
# pkms-mao6
title: Validate Gardener action paths to prevent traversal
status: completed
type: bug
priority: normal
created_at: 2026-01-20T00:31:46Z
updated_at: 2026-01-20T03:41:30Z
---

AI-generated action.path is concatenated directly with ATLAS_DIR. Add normalization/validation to ensure writes stay within atlas (reject '..', absolute paths, or non-md if desired).\n\n## Checklist\n- [x] Add path validation in execute_action\n- [x] Decide behavior for invalid paths (task/skip/error)\n- [x] Add tests or minimal validation checks
