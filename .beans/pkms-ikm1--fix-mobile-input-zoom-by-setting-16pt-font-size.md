---
# pkms-ikm1
title: Fix mobile input zoom by setting 16pt font size
status: todo
type: bug
created_at: 2026-01-22T02:45:58Z
updated_at: 2026-01-22T02:45:58Z
---

Prevent iOS Safari from auto-zooming when focusing on input fields by setting font-size to 16pt minimum.

## Problem
On iOS Safari, when a user taps an input field with font-size < 16px, the browser automatically zooms in. This is disruptive UX and makes the interface feel broken.

## Solution
Set all input fields and textareas to font-size: 16px (or 1rem with 16px base) on mobile viewports.

## Files to Update
- Capture textarea (`#note-input`)
- Search input fields
- Any form inputs in settings/modals

## Technical Implementation
```css
/* Mobile inputs should be 16px minimum */
@media (max-width: 768px) {
  input, textarea, select {
    font-size: 16px;
  }
}
```

Or in Tailwind:
```html
<textarea class="text-base md:text-sm" ...>
```

## Additional Considerations
- Ensure desktop can still use smaller fonts (14px is fine on desktop)
- Test on iOS Safari (actual device or simulator)
- May need to adjust line-height and padding to compensate

## Checklist
- [x] Identify all input fields and textareas
- [x] Set font-size: 16px on mobile
- [x] Update capture textarea
- [x] Update search inputs
- [x] Update form inputs in settings
- [x] Test on iOS Safari (iPhone)
- [x] Verify zoom no longer triggers
- [x] Check desktop styling still looks good