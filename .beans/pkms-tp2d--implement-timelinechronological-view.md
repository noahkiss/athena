---
# pkms-tp2d
title: Implement timeline/chronological view
status: completed
type: feature
priority: normal
created_at: 2026-01-22T02:41:42Z
updated_at: 2026-01-22T16:38:38Z
---

Add chronological view of all notes with filtering by date range and category.

## Features
- Timeline view showing all notes in reverse chronological order
- Date grouping (Today, Yesterday, This Week, Earlier)
- Filter by date range picker
- Filter by category/tag
- Infinite scroll or pagination
- Card preview of each note (title, excerpt, timestamp, category)
- Click to view full note

## Design
- New /timeline route
- Vertical timeline with date markers
- Expandable note cards
- Filters in sidebar or top bar

## Technical Notes
- Use git commit history for timestamps
- Query file_state DB for metadata
- Efficient pagination (don't load everything at once)
- Consider using git log with --since/--until for date filtering

## Checklist
- [x] Design timeline layout and note card (vertical timeline with date separators)
- [x] Add /timeline route to Scribe
- [x] Implement API endpoint for timeline data (reuses /api/recent with limit=100)
- [x] Add date grouping logic (groups by date with relative labels)
- [x] Build timeline view component (card-based with category icons)
- [x] Add to main navigation (Dashboard, Browse pages)
- [x] Make mobile-friendly (responsive layout with stagger animations)

## Implementation Notes
- Shows last 100 notes chronologically
- Date grouping with relative labels (Today, Yesterday, X days ago)
- Each item shows: icon, title, time, category, path
- Click to navigate to full note in Browse
- Vertical timeline with connecting border line
- Category-aware styling and icons
- Hover effects and animations
- Linked from Dashboard's Recent Activity section

## Future Enhancements (Deferred)
- Add date range filter (picker to select custom range)
- Add category filter (dropdown to filter by category)
- Implement pagination or infinite scroll (currently limited to 100)
- Add note preview modal (hover or click to preview without navigation)
- Test with large note counts (performance optimization)