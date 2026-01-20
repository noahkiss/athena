---
# pkms-3o7c
title: Ensure Scribe uses runtime GARDNER_URL
status: completed
type: bug
priority: normal
created_at: 2026-01-20T00:31:55Z
updated_at: 2026-01-20T03:42:00Z
---

Scribe server routes use import.meta.env.GARDNER_URL which may be build-time only. In Docker, runtime env could be ignored and default to localhost. Switch to process.env (server-only) or configure Astro env properly.\n\n## Checklist\n- [x] Confirm Astro env resolution at runtime\n- [x] Update server routes/pages to use runtime env\n- [x] Verify docker-compose GARDNER_URL works
