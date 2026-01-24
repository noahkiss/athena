---
# pkms-k280
title: Fix navigation inconsistencies
status: todo
type: feature
created_at: 2026-01-24T16:32:14Z
updated_at: 2026-01-24T16:32:14Z
---

## Overview

Redesign navigation architecture to be consistent across all pages, following iOS-native patterns and good thumb ergonomics.

## Current Problems

### Inconsistent Header Nav Per Page
| Page | Navigation Links |
|------|-----------------|
| Capture | Browse →, Archive → |
| Dashboard | Capture, Browse, Timeline, Settings |
| Browse | ← Capture, Dashboard, Timeline, 🎲 Random, Archive, Settings |
| Settings | Capture, Browse, Archive |
| Timeline | Capture, Dashboard, Browse, Settings |
| Archive | ← Capture, Browse |

### Dashboard Link Broken
- Clicking Dashboard from capture page shows "address could not be found"

## New Navigation Architecture

### Mobile Bottom Bar (4 tabs, left to right)
1. **Capture** - main entry point (left position for branding)
2. **Dashboard** - overview/stats
3. **Contacts** - people (promoted to main nav)
4. **Browse** - view content (far right for thumb ergonomics)

### Browse Sub-Navigation (Segmented Control)
Within Browse, show iOS-style segmented control at top:
```
┌─────────┬──────────┬─────────┐
│  Atlas  │ Timeline │ Archive │
└─────────┴──────────┴─────────┘
```
- **Atlas** - default browse view (folders/categories)
- **Timeline** - chronological view (integrated into Browse, not separate page)
- **Archive** - archived items (integrated into Browse, not separate page)

**Decision:** Timeline and Archive will be fully integrated into the Browse page with client-side segment switching, not separate pages. Old routes will redirect for backwards compatibility.

### Settings Access
- App icon displayed in header on every page
- Tapping icon opens Settings (or menu with Settings option)
- Frees up bottom bar slot for Contacts

### Random Feature
- Move from nav to a button/action within Browse
- Could be floating action button or toolbar button with 🎲

### Desktop Adaptation
- Same 4 main sections
- Header shows: [App Icon] + page title + segmented control (for Browse)
- No bottom bar - nav in header or sidebar
- Can show more context inline

## Code Audit Findings

### Current Structure
- **Layout.astro** (lines 1401-1445): Mobile bottom bar with Capture, Browse, Dashboard, Settings
- **Per-page headers**: Each page defines its own `<nav class="page-nav">` with different links
- **No shared header component** - each page duplicates the header structure
- **No contacts page** - contacts shown at `/browse/people` within Browse

### Files to Modify
1. `scribe/src/layouts/Layout.astro` - Mobile bottom bar, add app icon header
2. `scribe/src/pages/index.astro` - Remove per-page nav
3. `scribe/src/pages/dashboard.astro` - Remove per-page nav
4. `scribe/src/pages/browse/[...path].astro` - Add segmented control, remove per-page nav
5. `scribe/src/pages/timeline.astro` - Convert to Browse sub-view or integrate
6. `scribe/src/pages/archive/[...path].astro` - Convert to Browse sub-view or keep separate
7. `scribe/src/pages/settings.astro` - Remove per-page nav

### New Components Needed
1. `PageHeader.astro` - Shared header with app icon → Settings link
2. `SegmentedControl.astro` - iOS-style tabs for Browse sub-navigation
3. `contacts.astro` - New dedicated contacts page (or promote from /browse/people)

## Checklist

### Phase 1: Shared Header Component
- [ ] Create `PageHeader.astro` component with app icon linking to Settings
- [ ] Add app icon display (fetch from branding API, same as Layout.astro)
- [ ] Replace per-page headers in all pages with shared component

### Phase 2: Mobile Bottom Bar
- [ ] Update Layout.astro bottom bar: Capture → Dashboard → Contacts → Browse
- [ ] Create `/contacts` page (can initially redirect to or mirror `/browse/people`)
- [ ] Add contacts icon to bottom bar

### Phase 3: Browse Sub-Navigation
- [ ] Create `SegmentedControl.astro` component
- [ ] Add segmented control to Browse page header (Atlas | Timeline | Archive)
- [ ] Wire up segment switching (could be URL params or client-side state)
- [ ] Move Random button to toolbar/FAB within Browse

### Phase 4: Integrate Timeline/Archive into Browse
- [ ] Move Timeline view logic into Browse page (fetch timeline data based on segment)
- [ ] Move Archive view logic into Browse page (fetch archive data based on segment)
- [ ] Add URL param support (e.g., `/browse?view=timeline`, `/browse?view=archive`)
- [ ] Keep `/timeline` and `/archive` routes as redirects to Browse with params (backwards compat)
- [ ] Remove standalone timeline.astro and archive/[...path].astro pages (or convert to redirects)

### Phase 5: Desktop Header
- [ ] Decide if desktop needs nav links or just app icon + page title
- [ ] Update page-nav styles for consistent desktop experience
- [ ] Consider sidebar nav for desktop as alternative

### Phase 6: Testing
- [ ] Test mobile navigation flow on all pages
- [ ] Test desktop navigation
- [ ] Verify /dashboard route works (was broken)
- [ ] Test keyboard shortcuts still work (g+c, g+b, etc.)