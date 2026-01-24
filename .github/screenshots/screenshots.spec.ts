import { test, expect } from '@playwright/test';
import * as path from 'path';

const DOCS_DIR = path.join(__dirname, '../../docs');

type Theme = 'catppuccin-mocha' | 'rose-pine-dawn';

interface ScreenshotConfig {
  name: string;
  path: string;
  viewport: { width: number; height: number };
  scrollTo?: string;
}

interface Screenshot extends ScreenshotConfig {
  theme: Theme;
  outputName: string;
}

// Base configs for desktop screenshots (will be captured in both themes)
const DESKTOP_CONFIGS: ScreenshotConfig[] = [
  {
    name: 'capture',
    path: '/',
    viewport: { width: 1280, height: 800 },
  },
  {
    name: 'dashboard',
    path: '/dashboard',
    viewport: { width: 1280, height: 900 },
  },
  {
    name: 'browse',
    path: '/browse',
    viewport: { width: 1280, height: 800 },
  },
  {
    name: 'settings-fonts',
    path: '/settings',
    viewport: { width: 1280, height: 900 },
  },
  {
    name: 'settings-fonts-scrolled',
    path: '/settings',
    viewport: { width: 1280, height: 900 },
    scrollTo: 'text=Header Font',
  },
  {
    name: 'styleguide',
    path: '/styleguide',
    viewport: { width: 1280, height: 1200 },
  },
  {
    name: 'timeline',
    path: '/timeline',
    viewport: { width: 1280, height: 800 },
  },
  {
    name: 'contacts',
    path: '/browse/people',
    viewport: { width: 1280, height: 900 },
  },
  {
    name: 'contact-detail',
    path: '/browse/people/sarah-chen.md',
    viewport: { width: 1280, height: 900 },
  },
];

// Base configs for mobile screenshots (will be captured in both themes)
const MOBILE_CONFIGS: ScreenshotConfig[] = [
  {
    name: 'capture',
    path: '/',
    viewport: { width: 390, height: 844 },
  },
  {
    name: 'dashboard',
    path: '/dashboard',
    viewport: { width: 390, height: 844 },
  },
  {
    name: 'browse',
    path: '/browse',
    viewport: { width: 390, height: 844 },
  },
  {
    name: 'timeline',
    path: '/timeline',
    viewport: { width: 390, height: 844 },
  },
  {
    name: 'settings',
    path: '/settings',
    viewport: { width: 390, height: 844 },
  },
  {
    name: 'archive',
    path: '/archive',
    viewport: { width: 390, height: 844 },
  },
  {
    name: 'contacts',
    path: '/browse/people',
    viewport: { width: 390, height: 844 },
  },
];

// Generate theme variants for each config
// Set SCREENSHOT_THEMES=both to generate both light and dark
function generateScreenshots(
  configs: ScreenshotConfig[],
  prefix: string
): Screenshot[] {
  const screenshots: Screenshot[] = [];
  const includeBothThemes = process.env.SCREENSHOT_THEMES === 'both';

  for (const config of configs) {
    // Dark theme (default) - no suffix
    screenshots.push({
      ...config,
      theme: 'catppuccin-mocha',
      outputName: `${prefix}${config.name}`,
    });

    // Light theme - with -light suffix (only if enabled)
    if (includeBothThemes) {
      screenshots.push({
        ...config,
        theme: 'rose-pine-dawn',
        outputName: `${prefix}${config.name}-light`,
      });
    }
  }

  return screenshots;
}

const DESKTOP_SCREENSHOTS = generateScreenshots(DESKTOP_CONFIGS, 'screenshot-');
const MOBILE_SCREENSHOTS = generateScreenshots(MOBILE_CONFIGS, 'mobile-');
const ALL_SCREENSHOTS = [...DESKTOP_SCREENSHOTS, ...MOBILE_SCREENSHOTS];

test.describe('Screenshot Capture', () => {
  for (const shot of ALL_SCREENSHOTS) {
    test(`capture ${shot.outputName}`, async ({ page }) => {
      // Set viewport
      await page.setViewportSize(shot.viewport);

      // Set theme in localStorage before navigation
      await page.addInitScript((theme) => {
        localStorage.setItem('athena-theme', theme);
      }, shot.theme);

      // Navigate to page
      await page.goto(shot.path);

      // Wait for page to be fully loaded
      await page.waitForLoadState('networkidle');

      // Additional wait for any animations to settle
      await page.waitForTimeout(500);

      // Scroll if needed
      if (shot.scrollTo) {
        const element = page.locator(shot.scrollTo).first();
        await element.scrollIntoViewIfNeeded();
        await page.waitForTimeout(300);
      }

      // Take screenshot
      await page.screenshot({
        path: path.join(DOCS_DIR, `${shot.outputName}.png`),
        type: 'png',
      });
    });
  }
});
