---
# pkms-upxj
title: Improve UI/UX with native iOS/macOS design language
status: in-progress
type: feature
priority: high
created_at: 2026-01-22T17:34:18Z
updated_at: 2026-01-22T17:34:18Z
---

Improve the overall UI/UX to have a premium, native iOS/macOS feel with proper design language.

## Current Issues:
1. **Duplicate navigation on mobile** - Top nav links overflow and duplicate bottom nav bar
2. **Bland appearance** - Interface lacks visual polish and native feel
3. **Poor spacing** - Not following iOS spacing guidelines
4. **Missing design language** - No consistent card-based UI, shadows, or visual hierarchy

## Research:
- Ionic Framework uses adaptive styling and platform-specific visual language
- iOS 26 emphasizes rounded corners (continuous curve/squircle), card-based UI, spacious layouts
- iOS HIG specifies 16px margins on mobile, 24px on iPad
- Minimum touch targets: 44x44pt
- Continuous corner radius (squircle) creates warmer, friendlier feel

## Key Improvements Needed:

### 1. Fix Mobile Navigation (CRITICAL)
- [x] Hide top navigation links on mobile (md:flex hidden by default)
- [x] Keep only page title on mobile
- [x] Bottom nav bar should be the only navigation on mobile
- [x] Ensure no overflow issues

### 2. iOS-Style Card UI
- [ ] Convert panels to card-based design with proper rounded corners
- [ ] Use subtle shadows (elevation) on cards
- [ ] Implement proper spacing between cards (16px on mobile)
- [ ] Use concentric corners where nested (buttons in cards)

### 3. Spacing & Layout
- [ ] Update to iOS spacing: 16px margins on mobile, 24px on tablet
- [ ] Increase whitespace between sections
- [ ] Ensure touch targets are 44x44pt minimum
- [ ] Add proper padding inside cards/panels

### 4. Visual Polish
- [ ] Improve color palette with better contrast
- [ ] Add subtle shadows to create depth
- [ ] Better typography hierarchy (sizes, weights)
- [ ] Smooth transitions and animations
- [ ] iOS-style dividers and separators

### 5. Theme Improvements
- [ ] Review current themes for native feel
- [ ] Ensure themes work in both light and dark mode
- [ ] Better accent colors that feel more premium
- [ ] Proper surface elevation colors

## References:
- Ionic Framework: http://ionicframework.com/docs
- iOS Design Guidelines: https://developer.apple.com/design/human-interface-guidelines
- iOS spacing: https://ivomynttinen.com/blog/ios-design-guidelines/

## Implementation Plan:
1. Start with mobile nav fix (critical UX issue)
2. Update Layout.astro with proper spacing variables
3. Convert panels to card-based components
4. Add shadows and proper rounded corners
5. Test on actual mobile devices
6. Refine themes for premium feel