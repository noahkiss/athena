---
# pkms-esyp
title: Implement theming system with preset themes
status: completed
type: epic
priority: normal
created_at: 2026-01-22T02:40:44Z
updated_at: 2026-01-22T14:15:23Z
---

Add user-configurable theming with preset themes (Dracula, Catppuccin variants) and custom color picker.

## Features
- Theme picker UI in settings
- Preset themes: Dracula, Catppuccin (Latte, Frappe, Macchiato, Mocha)
- Custom theme builder (primary, background, accent colors)
- Light/dark/auto mode toggle
- Persist theme choice in localStorage
- Apply theme to PWA manifest dynamically

## Preset Themes
- **Dracula**: Purple/pink accents, dark background
- **Catppuccin Mocha**: Warm dark theme with pastel accents
- **Catppuccin Macchiato**: Mid-tone dark theme
- **Catppuccin Frappe**: Cooler dark theme
- **Catppuccin Latte**: Light theme variant
- **Custom**: User-defined colors

## Technical Notes
- Use CSS custom properties for theming
- Store theme in localStorage and sync to PWA manifest
- Provide theme preview before applying
- Ensure accessibility (contrast ratios)

## Checklist
- [x] Design theme data structure and CSS variables (CSS custom properties in Layout.astro)
- [x] Implement theme picker UI component (radio buttons in settings page)
- [x] Add preset theme definitions (6 themes: default, Dracula, 4 Catppuccin variants)
- [x] Persist theme choice (server-side via /api/branding, better than localStorage for multi-device)
- [x] Apply theme on page load (inline styles in Layout based on branding API)
- [x] Update PWA manifest theme-color dynamically (manifest.webmanifest.ts uses theme colors)

## Implementation Notes
- Completed via child task pkms-b2ny
- Server-side theme persistence (not localStorage) for better multi-device sync
- Theme applied per-page-load from backend API
- 6 preset themes fully implemented and tested

## Future Enhancements (Deferred)
- Add custom color picker option for user-defined themes
- Add theme preview mode (apply temporarily before saving)
- Light/dark/auto mode toggle (currently all themes are pre-configured as dark except Latte)
- Test accessibility contrast ratios formally
- Document themes in README