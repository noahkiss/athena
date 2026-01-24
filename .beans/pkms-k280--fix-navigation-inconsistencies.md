---
# pkms-k280
title: Fix navigation inconsistencies
status: todo
type: bug
created_at: 2026-01-24T16:32:14Z
updated_at: 2026-01-24T16:32:14Z
---

## Issues Found During Demo Testing

Two navigation-related issues discovered while testing the demo:

### 1. Dashboard Link Broken
- Clicking the Dashboard link from the capture page (/) shows "address could not be found"
- Need to verify the dashboard route is working and the link is correct

### 2. Header Navigation Links Change Per Page
- The header navigation links appear to change depending on which page you're on
- This is unexpected - navigation should be consistent across all pages
- Need to audit the Layout.astro header to ensure consistent nav items

## Checklist

- [ ] Verify /dashboard route exists and works
- [ ] Check dashboard link href in navigation
- [ ] Audit header nav items in Layout.astro
- [ ] Ensure nav is consistent across all pages
- [ ] Test navigation from multiple pages