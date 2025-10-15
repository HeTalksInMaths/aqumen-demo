import { test, expect } from '@playwright/test';

const DEV_PASSWORD = process.env.VITE_DEV_PASSWORD || 'menaqu';

test.describe('Dev Mode access', () => {
  test('button is interactive and preserves Tailwind styling', async ({ page }) => {
    await page.goto('/');

    const header = page.getByRole('heading', { name: 'AI Code Review Mastery' });
    await expect(header).toBeVisible();

    const devModeButton = page.getByRole('button', { name: /Dev Mode/ });
    await expect(devModeButton).toBeVisible();

    const initialBackground = await devModeButton.evaluate((button) => {
      return window.getComputedStyle(button).backgroundColor;
    });
    expect(initialBackground).toBe('rgb(255, 255, 255)');

    await devModeButton.click();

    const passwordModalHeading = page.getByRole('heading', { name: 'Dev Mode Access' });
    await expect(passwordModalHeading).toBeVisible();

    await page.getByLabel('Password').fill(DEV_PASSWORD);
    await page.getByRole('button', { name: 'Unlock' }).click();

    await expect(passwordModalHeading).toBeHidden();

    await expect(devModeButton).toHaveClass(/bg-purple-600/);

    const activeBackground = await devModeButton.evaluate((button) => {
      return window.getComputedStyle(button).backgroundColor;
    });
    expect(activeBackground).toBe('rgb(147, 51, 234)');

    await expect(page.getByText('Select Assessment:', { exact: false })).toBeVisible();
  });
});
