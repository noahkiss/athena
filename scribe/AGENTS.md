# SCRIBE DEVELOPMENT CONTEXT (Live Document)

**Role:** You are a Senior Frontend Architect.
**Project:** "Scribe" - The UI for Project Athena.

**Tech Stack:**
- **Framework:** Astro 5 (SSR Mode with Node adapter)
- **Interactivity:** HTMX 2 (for form submissions and partial replacements)
- **Styling:** TailwindCSS with Typography plugin
- **Markdown:** marked (for rendering in browse view)

## Project Structure

```
scribe/
├── src/
│   ├── layouts/
│   │   └── Layout.astro       # Base HTML layout with HTMX
│   └── pages/
│       ├── index.astro        # Capture page (main UI)
│       ├── browse/
│       │   └── [...path].astro  # Dynamic browse route
│       └── api/
│           ├── inbox.ts       # Proxy to Gardener /api/inbox
│           ├── refine.ts      # Proxy to Gardener /api/refine
│           └── browse/[...path].ts  # Proxy to Gardener /api/browse
├── package.json
├── astro.config.mjs
├── tailwind.config.js
└── Dockerfile
```

## Pages

| Route | Description |
|-------|-------------|
| `/` | Capture page - textarea with Submit/Refine buttons |
| `/api/ask` | Proxy to Gardener /api/ask (Explore/Ask) |
| `/browse` | Atlas root directory listing |
| `/browse/{path}` | Directory listing or markdown file view |

## Design Philosophy
- **Mobile First:** The primary use case is "Walking and talking" or "Quick text dump."
- **Grug Brain:** The interface should be stupid simple. A text box and a button.
- **Latency:** Capture must be instant. "Refining" is optional.

## Environment Variables
- `GARDENER_URL` - Backend API URL (default: `http://localhost:8000`)

**Constraints:**
- No complex state management libraries (Redux, etc.). Use HTML attributes and HTMX.
- All API calls proxy through Astro endpoints to Gardener backend.
