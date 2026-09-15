import { test } from '../fixtures/page-manager';

test('004 - Verify to send a message from Contact form modal', async ({ homePage, contactFlow, assertionsUI }) => {
    await test.step('Navigate to homepage and send a contact message', async () => {
        await homePage.navigateToHomePage('/');
        const result = await contactFlow.sendMessage({
            email: 'userTestAccount@gmail.com',
            name: 'Test User',
            message: 'This is a test message',
        });

        await assertionsUI.isTruthy(result.status === 'sent');
        await assertionsUI.isTruthy(Boolean(result.message));
    });
});