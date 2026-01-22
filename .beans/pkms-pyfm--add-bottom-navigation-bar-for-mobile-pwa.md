---
# pkms-pyfm
title: Add bottom navigation bar for mobile PWA
status: completed
type: feature
priority: normal
created_at: 2026-01-22T02:43:08Z
updated_at: 2026-01-22T14:13:30Z
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
- [x] Design mobile nav bar layout (4 items: Capture, Browse, Archive, Settings)
- [x] Choose icons (Heroicons SVG inline)
- [x] Implement bottom nav component (in Layout.astro)
- [x] Add active state styling (accent color for active, muted for inactive)
- [x] Add responsive behavior (md:hidden - mobile only)
- [x] Handle iOS safe area insets (env(safe-area-inset-bottom) padding)
- [x] Add smooth transitions (transition-colors on hover/active)

## Implementation Details
- Fixed bottom position with z-40
- 4 main nav items with icons and labels
- Active state detection via currentPath
- Body padding-bottom on mobile to prevent content overlap
- Touchable area optimized (flex-1 h-full)

## Future Enhancements (Deferred)
- Test on iOS Safari and Android Chrome (needs physical devices)
- Add swipe gestures between pages
- Add haptic feedback on tap (iOS PWA feature)
- Consider FAB alternative design for capture