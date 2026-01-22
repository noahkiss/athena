---
# pkms-hrqw
title: Add color-coded tags for visual diversity
status: completed
type: feature
priority: normal
created_at: 2026-01-22T02:42:47Z
updated_at: 2026-01-22T04:14:44Z
---

Assign colors to tags/categories for visual differentiation and better UI aesthetics.

## Features
- Auto-assign colors to tags/categories (hash-based for consistency)
- User can customize tag colors via settings
- Show colored badges/chips for tags throughout UI
- Color palette options: pastel, vibrant, muted
- Ensure accessibility (sufficient contrast)

## Where to Show Colored Tags
- Capture page: tag suggestions with colors
- Browse: folder icons with category colors
- Timeline: note cards with category badges
- Dashboard: category charts with consistent colors
- Search results: highlight categories with colors

## Technical Approach
- Generate color from tag name hash (consistent across sessions)
- Store custom colors in localStorage or backend config
- Use Tailwind color palette or CSS custom properties
- Ensure WCAG AA contrast compliance

## Tag Color Assignment Logic
```javascript
function hashTagColor(tag) {
  const colors = ['blue', 'green', 'purple', 'pink', 'yellow', 'orange', 'red', 'indigo'];
  const hash = tag.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return colors[hash % colors.length];
}
```

## Checklist
- [x] Design tag color system (hash-based + known categories)
- [x] Implement tag color generation function
- [x] Add colored category badges/cards
- [x] Apply colors to Browse category folders (with borders, backgrounds, icons)
- [x] Apply colors to Browse breadcrumbs
- [ ] Apply colors to Timeline note cards (page not implemented)
- [ ] Apply colors to Dashboard charts (page not implemented)
- [ ] Apply colors to Search results (search not implemented)
- [ ] Add tag color customization UI (future enhancement)
- [ ] Store custom colors in config (future enhancement)
- [x] Test accessibility (dark theme with 40% opacity backgrounds, good contrast)
- [ ] Add color palette selector (future enhancement)