import { test } from '../fixtures/page-manager';
import loginTestData from '../test_data/loginTestData';

test.describe('DemoBlaze Tests - Login tests', () => {
    test.beforeEach(async ({ homePage, headerPage }) => {
        await homePage.navigateToHomePage('/');
        await homePage.waitForElementToBeVisible(headerPage.navbar);

        await headerPage.click(headerPage.loginLink);
        await headerPage.waitForElementToBeVisible(headerPage.loginModal.loginModalIdentifier);
    });

    test('003.1 - Validate valid login', async ({ headerPage, assertionsUI }) => {
        await test.step('Fill required credentials', async () => {
            await headerPage.loginModal.fillLoginCredentials(loginTestData.valid[0].username, loginTestData.valid[0].password);
            await headerPage.loginModal.clickLoginButton();
        });

        await test.step('Verify successful login', async () => {
            await headerPage.waitForElementToBeHidden(headerPage.loginModal.loginModalIdentifier);
            await assertionsUI.elementHaveText(headerPage.welcomeUserText, /welcome/i);
        });
    });

    test('003.2 - Validate invalid login', async ({ headerPage, assertionsUI }) => {
        await test.step('Verify using invalid credentials for login', async () => {
            await headerPage.loginModal.fillLoginCredentials(loginTestData.invalid[0].username, loginTestData.invalid[0].password);
            await headerPage.loginModal.clickLoginButton();
        });

        await test.step('Verify login error', async () => {
            const dialogMessage = await headerPage.loginModal.getDialogMessage();
            await assertionsUI.isTruthy(dialogMessage.includes('Please fill out Username and Password.'));
        });
    });
});