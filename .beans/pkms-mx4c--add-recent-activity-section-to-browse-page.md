---
# pkms-mx4c
title: Add recent activity section to Browse page
status: draft
type: feature
created_at: 2026-01-22T02:43:27Z
updated_at: 2026-01-22T02:43:27Z
---

Show recently added/modified notes on Browse page for quick access.

## Features
- "Recent Activity" section at top of Browse page
- Last 5-10 notes with timestamps
- Show note title, category, relative time ("2 hours ago")
- Click to open note
- Option to expand/collapse section

## Display Format
- Compact list with icons
- Each item: category badge + title + timestamp
- Hover/tap for quick preview
- Responsive on mobile

## Technical Notes
- Query git log for recent commits
- Use file_state DB for metadata
- Cache recent list (refresh on page load)
- Consider adding "View All" link to timeline

## Checklist
- [ ] Design recent activity layout
- [ ] Implement API endpoint for recent notes
- [ ] Build recent activity component
- [ ] Add to Browse page (top section)
- [ ] Add expand/collapse toggle
- [ ] Show category badges
- [ ] Format relative timestamps
- [ ] Add quick preview on hover
- [ ] Link to full notes
- [ ] Test with many recent notes
- [ ] Add "View All" link to timeline