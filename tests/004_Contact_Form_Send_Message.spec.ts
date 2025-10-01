import { test } from '../fixtures/page-manager';

test('004 - Verify to send a message from Contact form modal', async ({ homePage, headerPage, assertionsUI }) => {
    await test.step('Navigate to homepage', async () => {
        await homePage.navigateToHomePage('/');
        await homePage.waitForElementToBeVisible(headerPage.navbar);
    });

    await test.step('Verify Contact form is visible', async () => {
        await headerPage.openContactForm();
    });

    await test.step('Verify all elements are present', async () => {
        const modalElements = await headerPage.newMessageModal.getAllModalElements();
        for (const element of modalElements) {
            await assertionsUI.elementIsVisible(element);
        }
    });

    await test.step('Fill all fields in Contact form', async () => {
        await headerPage.newMessageModal.fillAllFields('userTestAccount@gmail.com', 'Test User', 'This is a test message');
    });

    await test.step('Click on Send message button', async () => {
        await assertionsUI.elementIsVisible(headerPage.newMessageModal.sendMessageButton);
        await headerPage.newMessageModal.clickSendMessage();
    });

    await test.step('Verify modal is closed', async () => {
        await assertionsUI.elementIsHidden(headerPage.newMessageModal.contactFormIdentifier);
    });
});