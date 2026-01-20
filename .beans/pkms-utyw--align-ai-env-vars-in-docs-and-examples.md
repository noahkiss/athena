---
# pkms-utyw
title: Align AI env vars in docs and examples
status: completed
type: task
priority: normal
created_at: 2026-01-20T00:31:50Z
updated_at: 2026-01-20T03:42:14Z
---

.env.example documents AI_MODEL_FAST/AI_MODEL_THINKING but runtime uses AI_MODEL. Decide on single-model or dual-model config, update docs/README/.env.example accordingly, and add any missing vars (GARDENER_BACKEND, AI_TIMEOUT).\n\n## Checklist\n- [x] Decide on model config approach\n- [x] Update .env.example\n- [x] Update README/AGENTS if needed\n- [x] Verify config code matches docs
