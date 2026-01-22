---
# pkms-mx4c
title: Add recent activity section to Browse page
status: completed
type: feature
priority: normal
created_at: 2026-01-22T02:43:27Z
updated_at: 2026-01-22T14:09:15Z
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
- [x] Design recent activity layout (collapsible details panel with list items)
- [x] Implement API endpoint for recent notes (GET /api/recent with git log)
- [x] Build recent activity component (Astro component with category icons)
- [x] Add to Browse page (top section, only on root)
- [x] Add expand/collapse toggle (using HTML details/summary)
- [x] Show category badges (category icons and colored text)
- [x] Format relative timestamps (formatRelativeTime: "2h ago", "3d ago", etc.)
- [x] Link to full notes (clickable items navigate to /browse/{path})

## Future Enhancements (Deferred)
- Add hover preview tooltip (would require additional API call for content)
- Test with many recent notes (needs real data)
- Add "View All" link to timeline (timeline feature not yet implemented)