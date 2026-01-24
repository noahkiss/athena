# Screenshots

Visual overview of Athena's interface. These screenshots are automatically generated using the [screenshot workflow](../.github/workflows/screenshots.yml).

All screenshots are captured in both dark mode (Catppuccin Mocha) and light mode (Rosé Pine Dawn). Dark mode is shown by default.

## Capture Page

The main interface for quickly capturing thoughts.

![Capture](screenshot-capture.png)

<details>
<summary>View in light mode</summary>

![Capture (Light)](screenshot-capture-light.png)

</details>

## Desktop Views

### Dashboard
Clean stats overview with category breakdown and recent activity.

![Dashboard](screenshot-dashboard.png)

<details>
<summary>View in light mode</summary>

![Dashboard (Light)](screenshot-dashboard-light.png)

</details>

### Browse
Navigate your atlas with category-aware styling and breadcrumb navigation.

![Browse](screenshot-browse.png)

<details>
<summary>View in light mode</summary>

![Browse (Light)](screenshot-browse-light.png)

</details>

### Timeline
Chronological view of all your notes, grouped by date.

![Timeline](screenshot-timeline.png)

<details>
<summary>View in light mode</summary>

![Timeline (Light)](screenshot-timeline-light.png)

</details>

### Contacts
Structured contact cards with grid view, filtering, and detail pages.

![Contacts](screenshot-contacts.png)

<details>
<summary>View in light mode</summary>

![Contacts (Light)](screenshot-contacts-light.png)

</details>

![Contact Detail](screenshot-contact-detail.png)

<details>
<summary>View in light mode</summary>

![Contact Detail (Light)](screenshot-contact-detail-light.png)

</details>

### Settings
Theme selection and font customization.

![Settings](screenshot-settings-fonts.png)

<details>
<summary>View in light mode</summary>

![Settings (Light)](screenshot-settings-fonts-light.png)

</details>

![Settings (Scrolled)](screenshot-settings-fonts-scrolled.png)

<details>
<summary>View in light mode</summary>

![Settings Scrolled (Light)](screenshot-settings-fonts-scrolled-light.png)

</details>

### Style Guide
Interactive component documentation at `/styleguide`.

![Style Guide](screenshot-styleguide.png)

<details>
<summary>View in light mode</summary>

![Style Guide (Light)](screenshot-styleguide-light.png)

</details>

## Mobile Views (390×844)

Optimized for touch with iOS-style bottom navigation.

### Capture
![Mobile Capture](mobile-capture.png)

<details>
<summary>View in light mode</summary>

![Mobile Capture (Light)](mobile-capture-light.png)

</details>

### Dashboard
![Mobile Dashboard](mobile-dashboard.png)

<details>
<summary>View in light mode</summary>

![Mobile Dashboard (Light)](mobile-dashboard-light.png)

</details>

### Browse
![Mobile Browse](mobile-browse.png)

<details>
<summary>View in light mode</summary>

![Mobile Browse (Light)](mobile-browse-light.png)

</details>

### Timeline
![Mobile Timeline](mobile-timeline.png)

<details>
<summary>View in light mode</summary>

![Mobile Timeline (Light)](mobile-timeline-light.png)

</details>

### Settings
![Mobile Settings](mobile-settings.png)

<details>
<summary>View in light mode</summary>

![Mobile Settings (Light)](mobile-settings-light.png)

</details>

### Archive
![Mobile Archive](mobile-archive.png)

<details>
<summary>View in light mode</summary>

![Mobile Archive (Light)](mobile-archive-light.png)

</details>

### Contacts
![Mobile Contacts](mobile-contacts.png)

<details>
<summary>View in light mode</summary>

![Mobile Contacts (Light)](mobile-contacts-light.png)

</details>

---

## Updating Screenshots

Screenshots are updated automatically via GitHub Actions:

**Automatic:** Runs on every push to `main` that changes `scribe/**` or `.github/screenshots/**`

**Manual:** Go to **Actions** → **Update Screenshots** → **Run workflow**

Screenshots are committed directly to `main`. The workflow uses sample data from `.screenshot-data/athena/` to ensure consistent, realistic screenshots.

### Manual Update

To capture screenshots locally:

```bash
# Start services with sample data
docker compose -f docker-compose.screenshots.yml up -d --build

# Wait for services
sleep 30

# Run Playwright tests
cd .github/screenshots
npm install
npx playwright install chromium
npx playwright test

# Stop services
docker compose -f docker-compose.screenshots.yml down
```

### Screenshot Specifications

| Category | Viewport | Themes |
|----------|----------|--------|
| Desktop | 1280×800-1200 | Catppuccin Mocha (default), Rosé Pine Dawn |
| Mobile | 390×844 | Catppuccin Mocha (default), Rosé Pine Dawn |
