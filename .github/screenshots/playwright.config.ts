import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: '.',
  timeout: 120000, // 2 minutes per test
  retries: 1,
  workers: 2, // Run 2 tests in parallel
  use: {
    baseURL: 'http://localhost:3000',
    screenshot: 'off',
    video: 'off',
  },
  projects: [
    {
      name: 'screenshots',
      use: {
        browserName: 'chromium',
      },
    },
  ],
});
