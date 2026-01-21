---
# pkms-7c1o
title: Create synthetic data generator
status: completed
type: task
created_at: 2026-01-21T07:30:57Z
updated_at: 2026-01-21T14:21:05Z
parent: pkms-9qpq
---

Implement a realistic test data generator for stress testing.

## Requirements

- Generate 1,000-10,000 markdown notes with varying characteristics
- Support different lengths (1KB - 100KB)
- Cover various content types (projects, journal entries, tasks, reading notes, people notes)
- Use templates based on the 7 atlas categories
- Include realistic patterns (timestamps, links, tags, code blocks)
- Include edge cases (unicode, special chars, very long lines)
- Generate both easily classifiable and ambiguous cases

## Deliverables

- `gardener/tests/fixtures/generate_notes.py` - Note generator script
- `gardener/tests/fixtures/templates/` - Note templates directory
- Template files for each atlas category
- CLI interface for generating custom note sets
