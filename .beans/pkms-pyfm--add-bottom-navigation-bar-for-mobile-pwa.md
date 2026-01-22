---
# pkms-pyfm
title: Add bottom navigation bar for mobile PWA
status: draft
type: feature
created_at: 2026-01-22T02:43:08Z
updated_at: 2026-01-22T02:43:08Z
---

Implement mobile-friendly bottom navigation bar for easy thumb-reach navigation.

## Features
- Bottom fixed nav bar (iOS/Android style)
- Icons + labels for: Capture, Browse, Archive, Dashboard (optional)
- Active state indicator
- Swipe gestures between pages (optional)
- Floating action button (FAB) for quick capture (alternative design)

## Navigation Items
1. **Capture** (home icon or plus icon) - Main capture page
2. **Browse** (folder icon) - Atlas navigation
3. **Search** (magnifying glass) - Global search
4. **Dashboard** (chart icon) - Stats and activity
5. **More** (hamburger or ellipsis) - Settings, archive, etc.

## Design Considerations
- Fixed bottom position on mobile only (>= tablet uses top nav)
- Icon size: 24px, touchable area: 48px minimum
- Safe area insets for iOS notch
- Hide on scroll down, show on scroll up (optional)
- Haptic feedback on tap (iOS PWA)

## Alternative: Floating Action Button
- Single FAB for quick capture (always visible)
- Top nav remains for other pages
- FAB position: bottom right corner

## Checklist
- [ ] Design mobile nav bar layout
- [ ] Choose icons (Heroicons, Lucide, or custom)
- [ ] Implement bottom nav component
- [ ] Add active state styling
- [ ] Add responsive behavior (mobile only)
- [ ] Handle iOS safe area insets
- [ ] Add smooth transitions
- [ ] Test on iOS Safari and Android Chrome
- [ ] Add swipe gestures (optional)
- [ ] Add haptic feedback (optional)
- [ ] Consider FAB alternative design