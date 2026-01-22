---
# pkms-tp2d
title: Implement timeline/chronological view
status: draft
type: feature
created_at: 2026-01-22T02:41:42Z
updated_at: 2026-01-22T02:41:42Z
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
- [ ] Design timeline layout and note card
- [ ] Add /timeline route to Scribe
- [ ] Implement API endpoint for timeline data
- [ ] Add date grouping logic
- [ ] Build timeline view component
- [ ] Add date range filter
- [ ] Add category filter
- [ ] Implement pagination or infinite scroll
- [ ] Add note preview modal
- [ ] Add to main navigation
- [ ] Make mobile-friendly
- [ ] Test with large note counts