---
# pkms-wvg2
title: Browse page
status: completed
type: feature
priority: normal
created_at: 2026-01-19T08:02:18Z
updated_at: 2026-01-19T08:38:38Z
parent: pkms-38nj
---

Read-only view of organized notes.

## Route
`/browse/[...path]` - Dynamic route for atlas navigation

## Features
- List directories and files in /data/atlas
- Click file to render markdown as HTML
- Breadcrumb navigation
- Simple, clean UI matching capture page style

## Tech
- Astro dynamic routes
- Markdown renderer (marked or similar)
- HTMX for navigation (optional)