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
  const rejected = await page.request.post('/api/flags', {
    data: {
      chatId: '33333333-3333-4333-8333-333333333333',
      category: 'safety_review',
      priority: 'high',
      assessmentSource: 'authorized_human_review',
      reviewNote: 'Manual review completed.',
    },
  });
  expect(rejected.status()).toBe(400);
  await expect(rejected.json()).resolves.toMatchObject({ error: 'explicit human confirmation is required' });
  await page.getByRole('textbox', { name: 'Text-free operational note' }).fill('Authorized review requires follow-up.');
  await page.getByRole('checkbox', { name: 'Confirm human assessment' }).check();
  await page.getByRole('button', { name: 'Create flag' }).click();
  await expect(page.getByText(/Flag FLAG-/)).toBeVisible();
});

test('withdraws an open flag through an append-only, confirmed lifecycle decision', async ({ page }) => {
  await page.goto('/');
  await page.locator('.item').first().click();
  await expect(page.getByRole('heading', { name: 'Update flag lifecycle' })).toBeVisible();
  await page.getByRole('textbox', { name: 'Lifecycle operational note' }).fill('Created in error during manual review.');
  await page.getByRole('checkbox', { name: 'Confirm lifecycle decision' }).check();
  await page.getByRole('button', { name: 'Save lifecycle decision' }).click();
  await expect(page.getByText('Status changed to withdrawn.')).toBeVisible();

  await page.reload();
  await page.locator('.item').first().click();
  await expect(page.getByText('This flag is withdrawn.')).toBeVisible();
  const repeated = await page.request.put('/api/flags/33333333-3333-4333-8333-333333333333/status', {
    data: {
      status: 'withdrawn',
      assessmentSource: 'authorized_human_review',
      reviewNote: 'Repeated decision should be rejected.',
      humanConfirmed: true,
    },
  });
  expect(repeated.status()).toBe(400);
  await expect(repeated.json()).resolves.toMatchObject({ error: 'only an open flag can be withdrawn or marked not tracking' });
  await page.getByRole('checkbox', { name: 'Show open flags only' }).check();
  await expect(page.getByText('Showing 0–0 of 0')).toBeVisible();
});

test('marks a separate open flag as not tracking', async ({ page }) => {
  await page.goto('/');
  const unknown = await page.request.put('/api/flags/99999999-9999-4999-8999-999999999999/status', {
    data: {
      status: 'not_tracking',
      assessmentSource: 'authorized_human_review',
      reviewNote: 'Unknown cases cannot receive a lifecycle event.',
      humanConfirmed: true,
    },
  });
  expect(unknown.status()).toBe(400);
  await expect(unknown.json()).resolves.toMatchObject({ error: 'only an open flag can be withdrawn or marked not tracking' });
  await page.locator('.item').nth(1).click();
  await page.getByRole('textbox', { name: 'Text-free operational note' }).fill('Manual decision: exclude from ongoing tracking.');
  await page.getByRole('checkbox', { name: 'Confirm human assessment' }).check();
  await page.getByRole('button', { name: 'Create flag' }).click();
  await expect(page.getByText(/Flag FLAG-/)).toBeVisible();

  await page.reload();
  await page.locator('.item').nth(1).click();
  await page.getByRole('combobox', { name: 'New flag status' }).selectOption('not_tracking');
  await page.getByRole('textbox', { name: 'Lifecycle operational note' }).fill('Authorized decision: no further tracking.');
  await page.getByRole('checkbox', { name: 'Confirm lifecycle decision' }).check();
  await page.getByRole('button', { name: 'Save lifecycle decision' }).click();
  await expect(page.getByText('Status changed to not_tracking.')).toBeVisible();
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
