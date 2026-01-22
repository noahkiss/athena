---
# pkms-kmwc
title: Implement Progressive Web App (PWA) features
status: completed
type: epic
priority: normal
created_at: 2026-01-22T02:40:24Z
updated_at: 2026-01-22T13:55:56Z
---

Make Scribe installable as a home screen shortcut with standalone mode and custom branding.

## Features
- Home screen install experience (iOS/Android)
- Custom app icon upload (user-configurable)
- Custom app name (user-configurable, sets PWA name)
- Generated icons for iOS, favicons, and PWA manifest
- App manifest with proper metadata
- iOS standalone mode optimizations

## Benefits
- Install on home screen (iOS, Android)
- Native app feel without app store
- User can brand it as their own

## Technical Notes
- Store icon/name in backend config
- Generate manifest and icons dynamically based on user settings

## Checklist
- [x] Add PWA manifest.json with configurable name/icon
- [x] Add settings page for icon upload and app name
- [x] Add install prompt UI or guidance (added collapsible instructions in settings)

## Future Work
- Test on iOS Safari and Android Chrome (requires physical devices)
- Document PWA setup in README (can be added when needed)
