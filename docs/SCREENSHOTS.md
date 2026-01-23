# Screenshot Standards

This document defines the standard set of screenshots to capture after major UI/UX changes. These screenshots are used in the README and documentation.

## Screenshot Set

### Primary Screenshots (README hero section)

| Filename | Description | Size | Theme |
|----------|-------------|------|-------|
| `screenshot-light.png` | Capture page | 1280x800 | Rose Pine Dawn |
| `screenshot-dark.png` | Capture page | 1280x800 | Catppuccin Mocha |

### Desktop Screenshots (expandable sections)

| Filename | Description | Size | Theme |
|----------|-------------|------|-------|
| `screenshot-dashboard.png` | Dashboard with stats | 1280x900 | Default |
| `screenshot-browse.png` | Browse page with categories | 1280x800 | Default |
| `screenshot-settings-fonts.png` | Settings page (fonts visible) | 1280x900 | Default |
| `screenshot-settings-fonts-scrolled.png` | Settings scrolled to fonts | 1280x900 | Default |
| `screenshot-styleguide.png` | Style guide page | 1280x1200 | Default |
| `screenshot-timeline.png` | Timeline page | 1280x800 | Default |

### Mobile Screenshots (390x844 - iPhone 14 Pro viewport)

| Filename | Description |
|----------|-------------|
| `mobile-capture.png` | Capture page |
| `mobile-dashboard.png` | Dashboard |
| `mobile-browse.png` | Browse page |
| `mobile-timeline.png` | Timeline |
| `mobile-settings.png` | Settings |
| `mobile-archive.png` | Archive |

## Capture Guidelines

1. **Viewport sizes:**
   - Desktop: 1280x800 (or taller as needed)
   - Mobile: 390x844 (iPhone 14 Pro)

2. **Theme settings:**
   - Light screenshots: Rose Pine Dawn
   - Dark screenshots: Catppuccin Mocha (or default dark)

3. **Content:**
   - Use realistic sample data when possible
   - Ensure stats show non-zero values
   - Show category variety in browse screenshots

4. **Timing:**
   - Wait for all animations to complete
   - Ensure skeleton loaders have finished
   - Let hover states settle

## Manual Capture Process

Using Playwright MCP:

```bash
# Desktop - Light mode
1. Navigate to page
2. Set theme to rose-pine-dawn via localStorage
3. Resize to 1280x800
4. Take screenshot

# Desktop - Dark mode
1. Navigate to page
2. Set theme to catppuccin-mocha via localStorage
3. Resize to 1280x800
4. Take screenshot

# Mobile
1. Navigate to page
2. Resize to 390x844
3. Take screenshot
```

## Automation Considerations

A GitHub Actions workflow could:
1. Start the app in Docker
2. Use Playwright to navigate and capture
3. Upload screenshots as artifacts
4. Optionally open a PR with updated screenshots

This would require:
- `playwright` in CI
- A seeded database with sample data
- Theme switching via localStorage injection
