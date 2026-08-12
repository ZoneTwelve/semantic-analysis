import { defineConfig } from '@playwright/test';

const port = 8766;

export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  retries: 0,
  use: {
    baseURL: `http://127.0.0.1:${port}`,
    browserName: 'chromium',
    headless: true,
  },
  webServer: {
    command: `python3 src/conversation_browser.py --input tests/fixtures/conversations.jsonl --index test-results/conversation-browser.sqlite3 --flag-output-dir test-results/flagged-cases --port ${port}`,
    url: `http://127.0.0.1:${port}/api/conversations?limit=1`,
    reuseExistingServer: false,
    timeout: 30_000,
  },
});
