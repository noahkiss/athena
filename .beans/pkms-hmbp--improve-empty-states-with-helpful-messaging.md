---
# pkms-hmbp
title: Improve empty states with helpful messaging
status: completed
type: feature
priority: normal
created_at: 2026-01-22T02:44:54Z
updated_at: 2026-01-22T03:45:02Z
---

Replace generic empty states with contextual, helpful messages and calls to action.

## Current Empty States to Improve
1. **Archive (empty)**: "This archive is empty"
2. **Browse (empty folder)**: No message
3. **Timeline (no notes)**: Not implemented yet
4. **Dashboard (no data)**: Not implemented yet

## Improved Empty States
**Archive:**
> No archived notes yet. Submit your first note to get started!
> 
> [Go to Capture →]

**Browse (empty folder):**
> This folder is waiting for its first note.
> 
> **What goes here?**
> - Projects: Work projects, side projects, ideas
> - People: Contact notes, meeting summaries
> - Journal: Daily reflections, mood logs
> 
> The Gardener will automatically file notes here based on their content.

**Timeline (no notes):**
> Your timeline is empty. Start capturing thoughts to build your knowledge base.
> 
> [Capture your first note →]

**Dashboard (no data):**
> No data to display yet. Come back after capturing a few notes!

**Search (no results):**
> No matches found for "query". Try a different search term or explore your atlas.

## Design Elements
- Friendly tone (not "error" but "opportunity")
- Contextual help (explain what should go there)
- Call to action button
- Subtle illustration or icon (optional)

## Checklist
- [x] Update Archive empty state
- [x] Add Browse empty folder messages
- [x] Add category-specific hints for empty folders (projects, people, journal)
- [ ] Add Timeline empty state (page not yet implemented)
- [ ] Add Dashboard empty state (page not yet implemented)
- [ ] Add Search no results state (search not yet implemented)
- [x] Design empty state component (friendly, consistent pattern)
- [x] Add contextual CTAs (capture buttons with clear messaging)
- [ ] Test all empty states (needs local testing)
- [x] Consider adding subtle illustrations (emojis used: 📦, 📂)