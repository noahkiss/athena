# THE GARDENER PROTOCOL

**Goal:** Process files in `/inbox` and move them to `/atlas`.

## Classification Rules
Analyze the content and move to the best matching directory:

1. **Projects** (`/atlas/projects`): Business ideas, coding projects, "one-off" builds.
2. **People** (`/atlas/people`): CRM data, gift ideas, relationship notes.
3. **Home** (`/atlas/home`): HVAC, plumbing, cars, woodworking, DIY maintenance.
4. **Wellness** (`/atlas/wellness`): Health logs, workout stats, diet.
5. **Tech** (`/atlas/tech`): Server configs, homelab documentation, reference material.
6. **Journal** (`/atlas/journal`): Life philosophy, parenting, brain dumps.
7. **Reading** (`/atlas/reading`): Book notes, article summaries, media consumption.

> **Note:** This structure is living. If a note clearly belongs to a new category, you may create a new subdirectory and document it here.

## File Format Standard
When moving a file, rewrite it to match this format:

```markdown
---
title: {Suggested Title}
date: {YYYY-MM-DD}
tags: [tag1, tag2]
status: {seed|active|archive}
---

# {Title}

{Summary/Refined Notes}

## Action Items
- [ ] {Task extracted from note}

---
## Raw Source
{Original content verbatim}
```

## Ambiguity Handling
- If you are < 80% sure where a note belongs, do NOT move it.
- Append the content to `/tasks.md` with the header: `## Unsorted Note {Date}` and add a question: "Gardener Query: Where does this go?"
