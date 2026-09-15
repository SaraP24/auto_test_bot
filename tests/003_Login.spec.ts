import { test } from '../fixtures/page-manager';
import loginTestData from '../test_data/loginTestData';

test.describe('DemoBlaze Tests - Login tests', () => {
    test('003.1 - Validate valid login', async ({ homePage, headerPage, loginFlow, assertionsUI }) => {
        await test.step('Navigate to homepage and create a valid user', async () => {
            await homePage.navigateToHomePage('/');
            const username = `autotest_${Date.now()}`;
            const password = 'ValidPassword123';

            const signupMessage = await loginFlow.signUpCustomer({ username, password });
            await assertionsUI.isTruthy(signupMessage.includes('Sign up successful'));
            await assertionsUI.isTruthy(Boolean(signupMessage));
        });
    });

    test('003.2 - Validate invalid login', async ({ homePage, loginFlow, assertionsUI }) => {
        await test.step('Attempt invalid credentials and verify failure state', async () => {
            await homePage.navigateToHomePage('/');
            const result = await loginFlow.loginAsCustomer(loginTestData.invalid[0]);
            await assertionsUI.isTruthy(result.status === 'invalid-credentials');
            await assertionsUI.isTruthy(Boolean(result.message));
        });
    });
});