import { test, expect } from '@playwright/test';

const DEV_PASSWORD = process.env.VITE_DEV_PASSWORD || 'menaqu';

test.describe('Dev Mode access', () => {
  test('Frontend loads successfully and Dev Mode works', async ({ page }) => {
    // Navigate to the app
    await page.goto('/');

    // Wait for the app to fully load by checking for any visible content
    // This is more robust than looking for specific text that might change
    await page.waitForLoadState('networkidle');
    
    // Check that the page has loaded - look for any heading
    await expect(page.locator('h1').first()).toBeVisible({ timeout: 15000 });

    // Try to find the Dev Mode button
    const devModeButton = page.getByRole('button', { name: /Dev Mode/i });
    await expect(devModeButton).toBeVisible({ timeout: 10000 });

    // Click the Dev Mode button
    await devModeButton.click();

    // Password modal should appear
    const passwordModalHeading = page.getByRole('heading', { name: /Dev Mode Access/i });
    await expect(passwordModalHeading).toBeVisible({ timeout: 5000 });

    // Enter password and unlock
    await page.getByLabel(/Password/i).fill(DEV_PASSWORD);
    await page.getByRole('button', { name: /Unlock/i }).click();

    // Modal should close
    await expect(passwordModalHeading).toBeHidden({ timeout: 5000 });

    // Dev Mode button should now be active (purple background)
    await expect(devModeButton).toHaveClass(/bg-purple-600/, { timeout: 5000 });

    // Check that we're in Dev Mode by looking for dev mode specific content
    // The pipeline panel or assessment selector should be visible
    const devModeContent = page.getByText(/Select Assessment/i).or(
      page.getByText(/Pipeline Steps/i)
    ).or(
      page.getByText(/Step 1/i)
    );
    await expect(devModeContent.first()).toBeVisible({ timeout: 10000 });
  });
});

