---
# pkms-i3iq
title: 'Phase 1: Replace emoji with Solar icon system'
status: in-progress
type: feature
priority: normal
created_at: 2026-01-22T21:48:40Z
updated_at: 2026-01-22T22:00:23Z
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
- [ ] archive/[...path].astro (4 instances)
- [ ] settings.astro (3 instances)

### Backend Files (Replace Emoji)
- [ ] gardener/mcp_tools.py (2 instances: 📁📄)
- [ ] gardener/mcp_server.py (2 instances: 📁📄)

### Documentation
- [ ] Add icon license attribution to README
- [ ] Test icons render correctly
- [ ] Verify icon sizes consistent across pages

### Testing
- [ ] Icons render in all browsers
- [ ] Icons accessible (aria-labels where needed)
- [ ] No broken icon references