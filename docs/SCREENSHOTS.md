# Screenshots

Visual overview of Athena's interface. All screenshots use the dark theme (Catppuccin Mocha) and are automatically generated via [GitHub Actions](../.github/workflows/screenshots.yml).

## Table of Contents

- [Capture](#capture) - Quick thought capture
- [Browse](#browse) - Navigate your atlas
- [Timeline](#timeline) - Chronological view
- [Contacts](#contacts) - People management
- [Settings](#settings) - Theme and font customization
- [Archive](#archive) - Archived notes (mobile)
- [Style Guide](#style-guide) - Component documentation

---

## Capture

The main interface for quickly capturing thoughts with AI-powered refinement and exploration.

| Desktop | Mobile |
|---------|--------|
| ![Capture](screenshot-capture.png) | ![Capture Mobile](mobile-capture.png) |

## Browse

Navigate your atlas with category-aware styling, breadcrumb navigation, and recent activity.

| Desktop | Mobile |
|---------|--------|
| ![Browse](screenshot-browse.png) | ![Browse Mobile](mobile-browse.png) |

## Timeline

Chronological view of all your notes, grouped by date.

| Desktop | Mobile |
|---------|--------|
| ![Timeline](screenshot-timeline.png) | ![Timeline Mobile](mobile-timeline.png) |

## Contacts

Structured contact cards with filtering by relationship type.

| Desktop | Mobile |
|---------|--------|
| ![Contacts](screenshot-contacts.png) | ![Contacts Mobile](mobile-contacts.png) |

## Settings

Theme selection and font customization options.

| Desktop | Mobile |
|---------|--------|
| ![Settings](screenshot-settings-fonts.png) | ![Settings Mobile](mobile-settings.png) |

Font customization (scrolled view):

![Settings - Font Options](screenshot-settings-fonts-scrolled.png)

## Archive

View and restore archived notes.

| Mobile |
|--------|
| ![Archive Mobile](mobile-archive.png) |

## Style Guide

Interactive component documentation for developers at `/styleguide`.

![Style Guide](screenshot-styleguide.png)

---

## Updating Screenshots

Screenshots are updated automatically via GitHub Actions:

- **Automatic:** Runs on every push to `main` that changes `scribe/**` or `.github/screenshots/**`
- **Manual:** Go to **Actions** → **Update Screenshots** → **Run workflow**

### Local Capture

```bash
# Start services with sample data
docker compose -f docker-compose.screenshots.yml up -d --build

# Wait for services to be ready
sleep 30

# Run Playwright tests
cd .github/screenshots
npm install
npx playwright install chromium
npx playwright test

# Stop services
docker compose -f docker-compose.screenshots.yml down
```

### Specifications

| Platform | Viewport | Theme |
|----------|----------|-------|
| Desktop | 1280×800-1200 | Catppuccin Mocha |
| Mobile | 390×844 | Catppuccin Mocha |
