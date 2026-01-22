---
# pkms-kmwc
title: Implement Progressive Web App (PWA) features
status: in-progress
type: epic
priority: normal
created_at: 2026-01-22T02:40:24Z
updated_at: 2026-01-22T05:53:34Z
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
- [ ] Add install prompt UI or guidance
- [ ] Test on iOS Safari and Android Chrome
- [ ] Document PWA setup in README
