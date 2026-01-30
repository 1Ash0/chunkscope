import { test, expect } from '@playwright/test';

test.describe('ChunkScope Smoke Test', () => {
    test('should load the landing page', async ({ page }) => {
        await page.goto('/');

        // Check for landing page title or content
        // Based on previous work, it should have "Visual RAG Pipeline Builder" or similar
        await expect(page).toHaveTitle(/ChunkScope/);
        const heading = page.getByRole('heading', { level: 1 });
        await expect(heading).toBeVisible();

        // Visual Regression baseline
        await expect(page).toHaveScreenshot('landing-page.png');
    });

    test('should navigate to visualizer page', async ({ page }) => {
        await page.goto('/visualizer');

        // Check for canvas element presence (data-testid that I added earlier)
        const canvas = page.getByTestId('visualizer-canvas');
        await expect(canvas).toBeVisible();

        // Visual Regression baseline
        await expect(page).toHaveScreenshot('visualizer-page.png');
    });
});
