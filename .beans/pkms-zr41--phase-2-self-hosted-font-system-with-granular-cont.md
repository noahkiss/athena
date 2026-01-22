---
# pkms-zr41
title: 'Phase 2: Self-hosted font system with granular control'
status: completed
type: feature
priority: normal
created_at: 2026-01-22T22:00:54Z
updated_at: 2026-01-22T23:35:31Z
parent: pkms-70lf
---

Download and subset 20 fonts (6 header, 6 body, 8 mono). Create fonts.css with @font-face declarations. Update Layout.astro for 3-category font loading. Modify Settings page for header/body/mono selection. Update branding.py to store 3 font choices.

## Checklist

### Font Acquisition & Setup
- [ ] Create /scribe/public/fonts/{headers,body,mono}/ directory structure
- [ ] Download & subset header fonts (6): Atkinson Hyperlegible, Roboto Flex, Rubik, Inter, EB Garamond, Fraunces
- [ ] Download & subset body fonts (6): Inter, Atkinson Hyperlegible, Source Sans 3, Noto Sans, Literata, IBM Plex Sans
- [ ] Download & subset mono fonts (8): Iosevka, Fira Code, JetBrains Mono, Hack, DejaVu Sans Mono, Meslo, Source Code Pro, Cascadia Code
- [ ] Create /scribe/src/styles/fonts.css with all @font-face declarations

### Frontend Updates
- [ ] Replace /scribe/src/lib/fonts.ts with 3-category system
- [ ] Update Layout.astro blocking script for 3 font categories
- [ ] Update Layout.astro to import fonts.css
- [ ] Update settings.astro with 3-section font selector (header/body/mono)
- [ ] Add live preview of font combinations

### Backend Updates
- [ ] Update gardener/branding.py BrandingSettings for font_header, font_body, font_mono
- [ ] Update branding API endpoints to handle 3 font choices

### CSS Integration
- [ ] Define CSS variables: --font-family-header, --font-family-body, --font-family-mono
- [ ] Apply header font to h1-h6
- [ ] Apply body font to p, span, body
- [ ] Apply mono font to code, pre, .editor

### Testing
- [ ] Verify all fonts load correctly
- [ ] Test font persistence via localStorage
- [ ] Verify FOUT minimized with font-display: swap
- [ ] Test font combinations visually