---
# pkms-esyp
title: Implement theming system with preset themes
status: draft
type: epic
created_at: 2026-01-22T02:40:44Z
updated_at: 2026-01-22T02:40:44Z
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
- [ ] Design theme data structure and CSS variables
- [ ] Implement theme picker UI component
- [ ] Add preset theme definitions (Dracula, Catppuccin variants)
- [ ] Add custom color picker option
- [ ] Persist theme choice in localStorage
- [ ] Apply theme on page load
- [ ] Update PWA manifest theme-color dynamically
- [ ] Add theme preview mode
- [ ] Test accessibility (contrast ratios)
- [ ] Document themes in README