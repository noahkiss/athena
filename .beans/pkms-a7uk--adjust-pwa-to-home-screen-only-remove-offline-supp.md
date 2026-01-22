---
# pkms-a7uk
title: Adjust PWA to home-screen only (remove offline support)
status: completed
type: task
priority: normal
created_at: 2026-01-22T05:36:54Z
updated_at: 2026-01-22T05:37:54Z
parent: pkms-kmwc
---

User wants PWA only for iOS home-screen standalone launch; no offline support. Remove service worker caching and related hooks, keep manifest/meta needed for add-to-home.

## Checklist
- [x] Read relevant component AGENTS instructions
- [x] Remove service worker registration and assets
- [x] Keep/update manifest and meta for standalone mode
- [x] Verify build/dev still works
