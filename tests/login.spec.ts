import { test } from "../fixtures/page-manager";

test.beforeEach(async ({ loginPage }) => {
    await loginPage.navigateToUrl('/');
});

test.describe('Login tests', () => {
    test('validate login', async ({ loginPage }) => {
        await loginPage.login('Admin', 'admin123'); //replace with storage state
        await loginPage.isElementVisible(loginPage.dashboardHeader);
        await loginPage.screenshot({ path: 'login-success.png' });

    });

    test('validate login failure', async ({ loginPage }) => {
        await loginPage.login('Admin11', '123456');

        await loginPage.isElementVisible(loginPage.errorMessage);
        await loginPage.screenshot({ path: 'login-failure.png' });
    });
});