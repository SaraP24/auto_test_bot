import { test } from "../fixtures/page-manager";
import { Logger } from '../utils/logger';

test.beforeEach(async ({ loginPage }) => {
    await loginPage.navigateToUrl('/');
});

test('dashboard test 1', async ({ loginPage }) => {
    Logger.log('Starting dashboard tests, expecting errors for bot assistance demo');
    
    await loginPage.login('Admin', 'admin123');
    await loginPage.isElementVisible(loginPage.dashboardHeader);

    throw new Error('Test error to check bot assistance');
});

test('dashboard test 2', async ({ page }) => {
    throw new Error('Test error to check bot assistance');
});

test('dasboard test 3', async ({ page }) => {
    throw new Error('Test error to check bot assistance');
});

test('dashboard test 4', async ({ page }) => {
    throw new Error('Test error to check bot assistance');
});

test('dashboard test 5', async ({ page }) => {
    throw new Error('Test error to check bot assistance');
}); 



