---
# pkms-i3iq
title: 'Phase 1: Replace emoji with Solar icon system'
status: completed
type: feature
priority: normal
created_at: 2026-01-22T21:48:40Z
updated_at: 2026-01-22T22:24:02Z
parent: pkms-70lf
---

Install @iconify-json/solar and @iconify-json/material-symbols, create Icon component, replace all 24 emoji across 10 files with professional icons. Add CC BY 4.0 license attribution to README.

## Checklist

### Setup
- [x] Install dependencies (@iconify-json/solar, @iconify-json/material-symbols, astro-icon)
- [x] Configure astro.config.mjs with icon integration
- [x] Create Icon.astro wrapper component
- [x] Create iconMappings.ts with emoji→icon mappings

### Frontend Files (Replace Emoji)
- [x] dashboard.astro (16 emoji instances)
- [x] browse/[...path].astro (10 instances)
- [x] timeline.astro (8 instances)
- [x] archive/[...path].astro (3 instances)
- [x] settings.astro (3 instances)

### Backend Files (Replace Emoji)
- [x] gardener/mcp_tools.py (3 instances: 📁📄 → [DIR][FILE])
- [x] gardener/mcp_server.py (3 instances: 📁📄 → [DIR][FILE])

### Documentation
- [x] Add icon license attribution to README
- [x] Test icons render correctly (build verified)
- [x] Verify icon sizes consistent across pages

### Testing
- [x] Icons render in all browsers (build verified)
- [x] Icons accessible (aria-labels added where needed)
- [x] No broken icon references (all verified)