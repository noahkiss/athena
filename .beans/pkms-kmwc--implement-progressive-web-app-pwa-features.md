---
# pkms-kmwc
title: Implement Progressive Web App (PWA) features
status: draft
type: epic
created_at: 2026-01-22T02:40:24Z
updated_at: 2026-01-22T02:40:24Z
---

Make Scribe installable as a PWA with offline support, custom branding, and native app experience.

## Features
- Install prompt on mobile/desktop
- Offline capture with sync queue
- Custom app icon upload (user-configurable)
- Custom app name (user-configurable, sets PWA name)
- Service worker for caching and offline support
- App manifest with proper metadata
- iOS standalone mode optimizations

## Benefits
- Install on home screen (iOS, Android)
- Native app feel without app store
- Works offline (queue notes for sync)
- User can brand it as their own

## Technical Notes
- Use Astro service worker integration or Workbox
- Store icon/name in localStorage or backend config
- Generate manifest.json dynamically based on user settings
- Handle offline queue with IndexedDB

## Checklist
- [ ] Add PWA manifest.json with configurable name/icon
- [ ] Implement service worker for offline caching
- [ ] Add settings page for icon upload and app name
- [ ] Add offline detection and sync queue
- [ ] Add install prompt UI
- [ ] Test on iOS Safari and Android Chrome
- [ ] Add push notifications for processing complete (optional)
- [ ] Document PWA setup in README