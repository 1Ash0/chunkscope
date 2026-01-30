import { test, expect } from '@playwright/test';

test.describe('ChunkScope Smoke Test', () => {
    test('should load the landing page', async ({ page }) => {
        await page.goto('/');
        await page.waitForLoadState('networkidle');

        // Check for landing page title or content
        await expect(page).toHaveTitle(/ChunkScope/);
        const heading = page.getByRole('heading', { level: 1 });
        await expect(heading).toBeVisible();
    });

    test('should navigate to visualizer page', async ({ page }) => {
        await page.goto('/visualizer');
        await page.waitForLoadState('networkidle');

        // Check for canvas element presence
        const canvas = page.getByTestId('visualizer-canvas');
        await expect(canvas).toBeVisible();
    });
});
