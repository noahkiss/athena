import { test, expect } from '@playwright/test';
import * as path from 'path';

const DOCS_DIR = path.join(__dirname, '../../docs');

interface Screenshot {
  name: string;
  path: string;
  theme: 'catppuccin-mocha' | 'rose-pine-dawn';
  viewport: { width: number; height: number };
  waitFor?: string; // Optional selector to wait for
  scrollTo?: string; // Optional selector to scroll to
}

const DESKTOP_SCREENSHOTS: Screenshot[] = [
  // Primary hero screenshots
  {
    name: 'screenshot-light',
    path: '/',
    theme: 'rose-pine-dawn',
    viewport: { width: 1280, height: 800 },
  },
  {
    name: 'screenshot-dark',
    path: '/',
    theme: 'catppuccin-mocha',
    viewport: { width: 1280, height: 800 },
  },
  // Desktop page screenshots
  {
    name: 'screenshot-dashboard',
    path: '/dashboard',
    theme: 'rose-pine-dawn',
    viewport: { width: 1280, height: 900 },
  },
  {
    name: 'screenshot-browse',
    path: '/browse',
    theme: 'rose-pine-dawn',
    viewport: { width: 1280, height: 800 },
  },
  {
    name: 'screenshot-settings-fonts',
    path: '/settings',
    theme: 'rose-pine-dawn',
    viewport: { width: 1280, height: 900 },
  },
  {
    name: 'screenshot-settings-fonts-scrolled',
    path: '/settings',
    theme: 'rose-pine-dawn',
    viewport: { width: 1280, height: 900 },
    scrollTo: 'text=Header Font',
  },
  {
    name: 'screenshot-styleguide',
    path: '/styleguide',
    theme: 'rose-pine-dawn',
    viewport: { width: 1280, height: 1200 },
  },
  {
    name: 'screenshot-timeline',
    path: '/timeline',
    theme: 'rose-pine-dawn',
    viewport: { width: 1280, height: 800 },
  },
];

const MOBILE_SCREENSHOTS: Screenshot[] = [
  {
    name: 'mobile-capture',
    path: '/',
    theme: 'catppuccin-mocha',
    viewport: { width: 390, height: 844 },
  },
  {
    name: 'mobile-dashboard',
    path: '/dashboard',
    theme: 'catppuccin-mocha',
    viewport: { width: 390, height: 844 },
  },
  {
    name: 'mobile-browse',
    path: '/browse',
    theme: 'catppuccin-mocha',
    viewport: { width: 390, height: 844 },
  },
  {
    name: 'mobile-timeline',
    path: '/timeline',
    theme: 'catppuccin-mocha',
    viewport: { width: 390, height: 844 },
  },
  {
    name: 'mobile-settings',
    path: '/settings',
    theme: 'catppuccin-mocha',
    viewport: { width: 390, height: 844 },
  },
  {
    name: 'mobile-archive',
    path: '/archive',
    theme: 'catppuccin-mocha',
    viewport: { width: 390, height: 844 },
  },
];

const ALL_SCREENSHOTS = [...DESKTOP_SCREENSHOTS, ...MOBILE_SCREENSHOTS];

test.describe('Screenshot Capture', () => {
  for (const shot of ALL_SCREENSHOTS) {
    test(`capture ${shot.name}`, async ({ page }) => {
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
        path: path.join(DOCS_DIR, `${shot.name}.png`),
        type: 'png',
      });
    });
  }
});
