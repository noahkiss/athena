# Athena Scribe Design System

A comprehensive guide to the visual language and component patterns used in Athena Scribe.

## Table of Contents

1. [Color System](#color-system)
2. [Typography](#typography)
3. [Spacing](#spacing)
4. [Components](#components)
5. [Animations](#animations)
6. [Icons](#icons)

---

## Color System

### CSS Variables

All colors are defined as CSS variables in the `:root` scope and can be overridden by themes.

#### Base Colors

| Variable | Default | Description |
|----------|---------|-------------|
| `--color-bg` | `#0b1120` | Page background |
| `--color-surface` | `#111827` | Card/panel background |
| `--color-surface-alt` | `#1f2937` | Elevated surface |
| `--color-surface-muted` | `#0f172a` | Subtle backgrounds |
| `--color-border` | `#1f2937` | Border color |
| `--color-text` | `#f3f4f6` | Primary text |
| `--color-text-muted` | `#9ca3af` | Secondary text |
| `--color-text-subtle` | `#6b7280` | Tertiary text |

#### Semantic Colors

| Variable | RGB Variable | Description |
|----------|-------------|-------------|
| `--accent` | `--accent-rgb: 59 130 246` | Primary accent (blue) |
| `--focus` | `--focus-rgb: 56 189 248` | Focus state (cyan) |
| `--danger` | `--danger-rgb: 248 113 113` | Error/danger (red) |
| `--warning` | `--warning-rgb: 251 191 36` | Warning (amber) |
| `--success` | `--success-rgb: 52 211 153` | Success (green) |

#### Category Colors

Used for content categorization with 8 distinct colors:

| Class | RGB Variable | Color |
|-------|-------------|-------|
| `.category-1` | `--category-1-rgb: 96 165 250` | Blue |
| `.category-2` | `--category-2-rgb: 167 139 250` | Purple |
| `.category-3` | `--category-3-rgb: 74 222 128` | Green |
| `.category-4` | `--category-4-rgb: 34 211 238` | Cyan |
| `.category-5` | `--category-5-rgb: 251 191 36` | Amber |
| `.category-6` | `--category-6-rgb: 244 114 182` | Pink |
| `.category-7` | `--category-7-rgb: 251 146 60` | Orange |
| `.category-8` | `--category-8-rgb: 94 234 212` | Teal |

### Utility Classes

```css
.bg-app          /* Page background */
.bg-surface      /* Panel background */
.bg-surface-alt  /* Elevated background */
.bg-surface-muted /* Subtle background */
.text-primary    /* Primary text color */
.text-muted      /* Secondary text */
.text-subtle     /* Tertiary text */
.text-success    /* Success messages */
.text-warning    /* Warning messages */
.text-danger     /* Error messages */
```

---

## Typography

### Font Categories

The system supports 3 font categories, each independently configurable:

1. **Header fonts** (`--font-family-header`): Used for h1-h6 and `.page-title`
2. **Body fonts** (`--font-family-body`): Used for all body text
3. **Mono fonts** (`--font-family-mono`): Used for code, textareas

### Type Scale

| Variable | Size | Line Height | Usage |
|----------|------|-------------|-------|
| `--font-size-xs` | 0.75rem (12px) | normal | Captions |
| `--font-size-sm` | 0.875rem (14px) | normal | Small body |
| `--font-size-base` | 1rem (16px) | relaxed | Body text |
| `--font-size-lg` | 1.125rem (18px) | normal | Subheadings |
| `--font-size-xl` | 1.25rem (20px) | normal | Headings |
| `--font-size-2xl` | 1.5rem (24px) | tight | Large headings |
| `--font-size-3xl` | 1.875rem (30px) | tight | Hero/page titles |

### Font Weights

| Variable | Value | Usage |
|----------|-------|-------|
| `--font-weight-normal` | 400 | Body text |
| `--font-weight-medium` | 500 | Subheadings, buttons |
| `--font-weight-semibold` | 600 | Headings |
| `--font-weight-bold` | 700 | Emphasis |
| `--font-weight-light` | 300 | Page titles |

---

## Spacing

### iOS-Inspired Spacing Scale

| Variable | Mobile | Tablet+ | Usage |
|----------|--------|---------|-------|
| `--spacing-page` | 16px | 24px | Page margins |
| `--spacing-section` | 24px | 32px | Between sections |
| `--spacing-card` | 16px | 24px | Card internal padding |
| `--spacing-element` | 12px | 12px | Between elements |

### Touch Targets

```css
--touch-target-min: 44px; /* iOS minimum touch target */
```

All interactive elements should have a minimum size of 44×44px.

---

## Components

### Buttons

#### Primary Button

```html
<button class="btn-primary btn-ripple focus-ring">
  Button Text
</button>
```

Features:
- Accent background color
- Rounded corners (0.875rem)
- Minimum 44px height (touch target)
- Hover: lift + shadow
- Active: scale down to 0.98
- Ripple effect on click

#### Secondary Button

```html
<button class="btn-secondary btn-ripple focus-ring">
  Button Text
</button>
```

Features:
- Surface alt background with border
- Same dimensions as primary
- Hover: background change + lift

### Panels

```html
<div class="panel">
  Panel content
</div>
```

Features:
- Surface background
- 1px border
- 1rem border radius
- Subtle gradient overlay for depth
- Hover: lift with enhanced shadow

### Input Fields

```html
<input class="input-field focus-ring" />
<textarea class="input-field textarea-autogrow focus-ring"></textarea>
```

Features:
- Surface muted background
- Focus: cyan glow + background change
- Auto-grow textarea option
- Placeholder transition on focus

### Category Chips

```html
<span class="category-chip category-1">
  Category Name
</span>
```

Features:
- Semi-transparent background
- Matching border color
- Text in category color

### Empty States

```astro
<EmptyState
  icon="folder-open"
  title="No items yet"
  description="Description text here"
  actionText="Call to Action"
  actionHref="/path"
  actionIcon="icon-name"
  variant="default|compact"
>
  <!-- Optional slot for contextual content -->
</EmptyState>
```

### Skeleton Loaders

```astro
<SkeletonLoader type="card|list|stat|text" count={3} />
```

---

## Animations

### Timing Variables

```css
--transition-fast: 150ms;
--transition-base: 200ms;
--transition-slow: 300ms;
```

### Easing Functions

```css
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in: cubic-bezier(0.4, 0, 1, 1);
```

### Animation Classes

| Class | Effect | Duration |
|-------|--------|----------|
| `.animate-fadeIn` | Fade in | base |
| `.animate-slideUp` | Slide up + fade | slow |
| `.stagger-item` | Staggered fade in | base + delay |

### Stagger Animation

Items with `.stagger-item` class animate with incremental delays:

```css
.stagger-item:nth-child(1) { animation-delay: 0ms; }
.stagger-item:nth-child(2) { animation-delay: 50ms; }
/* ... up to 10 items */
```

### Micro-interactions

| Element | Effect |
|---------|--------|
| Buttons | `translateY(-1px)` on hover, `scale(0.98)` on active |
| Panels | Lift + enhanced shadow on hover |
| Links | Animated underline (`.link-animated`) |
| Cards | Lift effect (`.card-interactive`) |
| Icons | Scale + rotate on hover |

### Reduced Motion

All animations respect `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Icons

### Icon System

Athena uses **Solar Icons** as the primary icon set, accessed via the `<Icon>` component:

```astro
<Icon name="folder" size={24} class="text-primary" aria-label="Folder" />
```

### Icon Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `name` | string | required | Solar icon name |
| `size` | number/string | 24 | Width and height in px |
| `class` | string | - | Additional CSS classes |
| `aria-label` | string | - | Accessibility label |

### Category Icons

| Category | Icon Name |
|----------|-----------|
| Projects | `case-linear` |
| People | `users-group-rounded-linear` |
| Journal | `notebook-linear` |
| Tech | `settings-linear` |
| Reading | `book-2-linear` |
| Wellness | `health-linear` |
| Home | `home-2-linear` |

### Common Icons

| Purpose | Icon Name |
|---------|-----------|
| Document | `document-linear` |
| Folder | `folder-linear` |
| Folder Open | `folder-open-linear` |
| Add | `document-add-linear` |
| Calendar | `calendar-linear` |
| Archive | `archive-down-minimlistic-linear` |
| Settings | `settings-linear` |
| Search | `magnifer-linear` |
| Edit | `pen-new-square-linear` |
| Random | `shuffle-linear` |
| Arrow Right | `alt-arrow-right-linear` |

> **Note:** Solar icons require the full name with style suffix. Use `-linear` for most icons to maintain visual consistency.

---

## Themes

Athena supports 13 color themes:

### Dark Themes
- Default (Midnight)
- Cobalt2
- Dracula
- Catppuccin Mocha/Macchiato/Frappe
- GitHub Dark High Contrast/Dimmed
- Rose Pine Moon

### Light Themes
- Catppuccin Latte
- GitHub Light
- Rose Pine Dawn

Themes are applied via the `data-theme` attribute on `<html>` and override CSS variables accordingly.

---

## Best Practices

1. **Always use CSS variables** for colors, spacing, and typography
2. **Use semantic classes** (`.text-primary`, `.bg-surface`) instead of raw values
3. **Apply focus rings** to all interactive elements for accessibility
4. **Respect touch targets** - minimum 44×44px for interactive elements
5. **Use stagger animations** for lists to create visual rhythm
6. **Support reduced motion** - animations should be optional
7. **Test in both light and dark themes** before shipping

---

## File Structure

```
scribe/src/
├── components/
│   ├── Icon.astro          # Icon wrapper component
│   ├── EmptyState.astro    # Empty state component
│   └── SkeletonLoader.astro # Loading skeleton component
├── layouts/
│   └── Layout.astro        # Global styles and layout
├── lib/
│   ├── fonts.ts            # Font definitions
│   ├── themes.ts           # Theme definitions
│   └── iconMappings.ts     # Icon name mappings
└── styles/
    └── fonts.css           # Font imports
```
