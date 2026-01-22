---
# pkms-n0mn
title: Add people/contacts feature with standardized contact cards
status: draft
type: feature
created_at: 2026-01-22T02:42:26Z
updated_at: 2026-01-22T02:42:26Z
---

Create structured contact card system for people in the /people atlas category.

## Features
- Standardized contact card template (YAML frontmatter or structured markdown)
- Fields: name, email, phone, company, role, tags, notes, last contact date
- Special UI for viewing contact cards (card layout vs plain markdown)
- Quick actions: email, call (if on mobile), add note
- Birthday reminders (optional)
- Relationship tracking (colleague, friend, family, etc.)
- Contact frequency suggestions ("haven't talked to X in 3 months")

## Template Structure
```markdown
---
name: John Doe
email: john@example.com
phone: +1-555-0100
company: Acme Corp
role: Engineering Manager
tags: [colleague, mentor, tech]
relationship: colleague
last_contact: 2026-01-15
birthday: 1985-06-20
---

# Notes about John

- Met at conference 2024
- Working on Project X
- Interested in AI/ML
```

## UI Enhancements
- Contact card view (vs raw markdown)
- Grid view of all contacts (photo + name)
- Filter by tags, company, relationship
- Sort by last contact date
- "Add Contact" button with template

## Technical Notes
- Use YAML frontmatter parsing (gray-matter library)
- Special rendering for /people category in Browse
- Store photos in athena/people/photos/ (optional)
- Integration with capture: "@mention someone" auto-links to their contact

## Checklist
- [ ] Design contact card template (YAML frontmatter structure)
- [ ] Add contact card parser to gardener
- [ ] Build contact card UI component in Scribe
- [ ] Add grid view for /people category
- [ ] Add "Add Contact" button with template
- [ ] Implement contact card detail view
- [ ] Add quick actions (email, call links)
- [ ] Add filtering and sorting
- [ ] Add last contact date tracking
- [ ] Add relationship tags
- [ ] Add birthday reminders (optional)
- [ ] Add contact frequency suggestions
- [ ] Test @mention auto-linking
- [ ] Document contact template in README