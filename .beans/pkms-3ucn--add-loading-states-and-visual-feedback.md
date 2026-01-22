---
# pkms-3ucn
title: Add loading states and visual feedback
status: in-progress
type: feature
priority: normal
created_at: 2026-01-22T02:44:11Z
updated_at: 2026-01-22T03:32:51Z
---

Improve perceived responsiveness with loading indicators and success feedback.

## Features to Add
- **Button loading states**: Show spinner when Refine/Explore/Submit are processing
- **Success animations**: Brief checkmark or slide-out when note submitted
- **Error states**: Inline validation messages with retry buttons
- **Progress indicators**: Show processing status for long operations
- **Optimistic updates**: Immediate UI feedback before server response

## Specific Improvements
1. **Capture form**
   - Submit button shows spinner while processing
   - Success checkmark animation on complete
   - Error message with retry button if failed
   - Disable form while submitting

2. **Refine/Explore buttons**
   - Loading spinner in button
   - Animated skeleton loader for results
   - Error handling with retry

3. **Browse/Archive**
   - Loading skeleton while fetching directory listing
   - Smooth transitions when navigating

## Design System
- Use consistent loading states (spinner icon, disabled state)
- Success: green checkmark + brief animation
- Error: red x + error message + retry button
- Loading: blue spinner + "Processing..." text

## Checklist
- [x] Add loading spinner component
- [x] Add submit button loading state
- [x] Add success animation (pulse effect on feedback)
- [ ] Add error state with retry button (API already handles errors, retry needs UX)
- [x] Add loading state to Refine/Explore
- [x] Add smooth fade-in animations for results
- [ ] Add loading state to Browse navigation (SSR, browser handles)
- [ ] Test all loading states (needs local testing)
- [ ] Test error recovery (needs local testing)
- [ ] Add haptic feedback on mobile (optional, future enhancement)