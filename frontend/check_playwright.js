import { chromium } from '@playwright/test';

async function test() {
    console.log('Attempting to launch browser...');
    try {
        const browser = await chromium.launch();
        console.log('Browser launched successfully!');
        const page = await browser.newPage();
        await page.goto('https://www.google.com');
        console.log('Page title:', await page.title());
        await browser.close();
    } catch (error) {
        console.error('Failed to launch browser:', error);
    }
}

test();
