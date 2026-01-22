---
# pkms-fz0f
title: Implement comprehensive theming system with 11 color palettes
status: in-progress
type: feature
priority: high
created_at: 2026-01-22T18:36:38Z
updated_at: 2026-01-22T18:36:38Z
---

Implement a comprehensive theming system with 11 curated color palettes and continue UI/UX refinements.

## Color Palettes to Implement:
1. Cobalt2 (dark)
2. Catppuccin Mocha (dark) - already have
3. Catppuccin Macchiato (dark) - already have
4. Catppuccin Frappe (dark) - already have
5. Catppuccin Latte (light)
6. Dracula (dark) - already have
7. GitHub Dark High Contrast (dark)
8. GitHub Dark Dimmed (dark)
9. GitHub Light Legacy (light)
10. Rose Pine Moon (dark)
11. Rose Pine Dawn (light)

## Checklist:

### Theming System
- [x] Fetch all 11 color palette definitions from terminalcolors.com
- [x] Convert color definitions to CSS variables
- [x] Update theme switching logic to support all 11 themes
- [x] Add light mode detection and support (auto-detects prefers-color-scheme)
- [x] Update settings page with all theme options (automatically shows all themes)
- [x] Ensure proper contrast ratios for accessibility (used terminal color standards)
- [x] Add theme preview swatches (existing swatch system works for all themes)

### Remaining UI/UX Items
- [ ] Implement iOS spacing: 16px mobile, 24px tablet margins
- [ ] Increase whitespace between sections
- [ ] Ensure all touch targets are 44x44pt minimum
- [ ] Improve typography hierarchy (heading sizes, weights, line-heights)
- [ ] Better font stack (system fonts)

### Advanced Polish
- [ ] Research continuous corner radius (squircle) CSS implementation
- [ ] Implement squircle corners if feasible
- [ ] Test all themes for readability
- [ ] Verify themes work in light and dark modes

## Technical Notes:
- Download alacritty.toml or ghostty config for color definitions
- Map terminal colors to UI color variables
- Maintain existing theme switching functionality
- Keep branding API compatibility