---
# pkms-azn0
title: Astro frontend with capture UI
status: completed
type: feature
priority: normal
created_at: 2026-01-19T08:01:36Z
updated_at: 2026-01-19T08:25:17Z
parent: pkms-rpqb
---

Initialize Astro project with the capture interface.

## Requirements
- Astro in SSR mode
- TailwindCSS for styling
- HTMX for form submission

## UI Components
- Large, centered textarea (mobile-first)
- Submit button - posts to /api/inbox via HTMX
- Refine button (disabled placeholder for Phase 3)
- Success feedback on submission

## Files to create
- `scribe/package.json`
- `scribe/astro.config.mjs`
- `scribe/src/pages/index.astro`
- `scribe/tailwind.config.js`