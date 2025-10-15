import { test, expect } from '@playwright/test';

const gradientSelector = '[class*="bg-gradient-to-br"]';
const pipelineGradientSelector = '[class*="bg-gradient-to-r"]';

test.describe('landing gradients', () => {
  test('page shell shows Vite gradient background', async ({ page }) => {
    await page.goto('/');
    const shell = page.locator(`${gradientSelector}:visible`).first();
    await expect(shell).toBeVisible();

    const backgroundImage = await shell.evaluate((element) =>
      window.getComputedStyle(element).backgroundImage,
    );

    expect(backgroundImage).toContain('gradient');
  });

  test('pipeline mode panel keeps gradient accent', async ({ page }) => {
    await page.goto('/');
    const pipelineCard = page.locator(`${pipelineGradientSelector}:visible`).first();
    await expect(pipelineCard).toBeVisible();

    const backgroundImage = await pipelineCard.evaluate((element) =>
      window.getComputedStyle(element).backgroundImage,
    );

    expect(backgroundImage).toContain('gradient');
  });
});
