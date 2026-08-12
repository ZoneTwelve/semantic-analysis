import { expect, test } from '@playwright/test';

test('browses newest conversations and opens the selected turn', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByText('Showing 1–3 of 3')).toBeVisible();
  await expect(page.locator('.item').first()).toContainText('Please summarize the planning notes.');
  await page.locator('.item').first().click();

  await expect(page.getByRole('heading', { name: '33333333-3333-4333-8333-333333333333' })).toBeVisible();
  await expect(page.locator('.message').filter({ hasText: 'Please summarize the planning notes.' })).toBeVisible();
  await expect(page.locator('.message.assistant').filter({ hasText: 'Here is a summary.' })).toBeVisible();
});

test('creates a flag only after explicit human confirmation', async ({ page }) => {
  await page.goto('/');
  await page.locator('.item').first().click();
  await expect(page.getByRole('heading', { name: 'Create human review flag' })).toBeVisible();
  await page.getByRole('textbox', { name: 'Text-free operational note' }).fill('Authorized review requires follow-up.');
  await page.getByRole('checkbox', { name: 'Confirm human assessment' }).check();
  await page.getByRole('button', { name: 'Create flag' }).click();
  await expect(page.getByText(/Flag FLAG-/)).toBeVisible();
});

test('searches the latest user-message preview without knowing a chat ID', async ({ page }) => {
  await page.goto('/');

  await page.getByRole('textbox', { name: 'Search conversations' }).fill('report');
  await page.getByRole('button', { name: 'Search' }).click();

  await expect(page.getByText('Showing 1–1 of 1')).toBeVisible();
  await expect(page.locator('.item')).toHaveCount(1);
  await expect(page.locator('.item')).toContainText('Can you help me find the report?');
});

test('shows a clear browser-side error when the API is unavailable', async ({ page }) => {
  await page.route('**/api/conversations?**', route => route.abort());
  await page.goto('/');

  await expect(page.getByText(/Unable to load conversations/)).toBeVisible();
});
