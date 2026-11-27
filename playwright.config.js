const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: 'tests/team/e2e',
  timeout: 30000,
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [['list'], ['html', { outputFolder: 'evidence/reports/playwright-report', open: 'never' }]],
  use: {
    baseURL: 'http://127.0.0.1:8000',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
 projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'], channel: process.env.PW_CHANNEL } }],
  // Starts the app from a clean seeded database. Stop any server on port 8000 first.
  webServer: {
    command: 'python scripts/e2e_server.py',
    url: 'http://127.0.0.1:8000/accounts/login/',
    reuseExistingServer: false,
    timeout: 120000,
  },
});