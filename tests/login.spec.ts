import { test } from "@playwright/test";

test('validate login', async ({ page }) => {
    await page.goto('https://example.com/login');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('https://example.com/dashboard');

    await page.screenshot({ path: 'login-success.png' });

    const welcomeMessage = await page.textContent('.welcome-message');
    test.expect(welcomeMessage).toContain('Welcome, testuser');
})


test('validate login failure', async ({ page }) => {
    await page.goto('https://example.com/login');
    await page.fill('input[name="username"]', 'wronguser');
    await page.fill('input[name="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');
    
    const errorMessage = await page.textContent('.error-message');
    test.expect(errorMessage).toBe('Invalid username or password.');

    await page.screenshot({ path: 'login-failure.png' });
})
