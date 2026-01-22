---
# pkms-hrqw
title: Add color-coded tags for visual diversity
status: draft
type: feature
created_at: 2026-01-22T02:42:47Z
updated_at: 2026-01-22T02:42:47Z
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
- [ ] Design tag color system (hash-based + custom)
- [ ] Implement tag color generation function
- [ ] Add colored tag badges component
- [ ] Apply colors to Browse category folders
- [ ] Apply colors to Timeline note cards
- [ ] Apply colors to Dashboard charts
- [ ] Apply colors to Search results
- [ ] Add tag color customization UI
- [ ] Store custom colors in config
- [ ] Test accessibility (contrast ratios)
- [ ] Add color palette selector (pastel, vibrant, muted)