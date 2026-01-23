---
# pkms-mo2m
title: 'Phase 3: Enhanced empty states and skeleton loaders'
status: completed
type: feature
priority: normal
created_at: 2026-01-22T22:01:31Z
updated_at: 2026-01-23T02:45:52Z
parent: pkms-70lf
---

Create reusable EmptyState and SkeletonLoader components with animations and apply them across the app.

## Checklist

### Components
- [x] Create EmptyState.astro component with icon hover animations
- [x] Add variant prop for default/compact layouts
- [x] Support slot for contextual content
- [x] Create SkeletonLoader.astro with shimmer effects
- [x] Add type presets (card, list, stat, text)
- [x] Respect prefers-reduced-motion

### Page Updates
- [x] Replace browse page empty state with EmptyState component
- [x] Replace timeline page empty state with EmptyState component
- [x] Replace archive page empty state with EmptyState component
- [x] Replace dashboard categories empty state (compact variant)
- [x] Replace dashboard recent activity empty state (compact variant)