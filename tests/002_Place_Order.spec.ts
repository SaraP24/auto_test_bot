import { test } from '../fixtures/page-manager';

    test('002 - Validate user can place an order', async ({ homePage,headerPage, productPage, assertionsUI, cartPage }) => {
         await test.step('Navigate to homepage', async () => {
            await homePage.navigateToHomePage('/');
            await homePage.waitForElementToBeVisible(headerPage.navbar);
        });

        await test.step('Click on the first product and verify product page is opened', async () => {
            await homePage.selectProductByIndex(0);
            await productPage.waitForElementToBeVisible(productPage.productTitle);
        });

        await test.step('Add product to cart', async () => {
            await productPage.clickAddToCart();
        });

        await test.step('Go to Cart page', async () => {
            await cartPage.goToCart();
            await assertionsUI.elementHaveText(cartPage.pageTitle, /products/i);
            await assertionsUI.elementIsVisible(cartPage.cartTable);
        });

        await test.step('Click on Place Order button and verify order modal is opened', async () => {
            await cartPage.clickPlaceOrder();
            await assertionsUI.elementIsVisible(cartPage.placeOrderModal.placeOrderFormIdentifier);
        });

        await test.step('Fill all fields in Place Order form', async () => {
            await cartPage.placeOrderModal.fillAllFields('Test User', 'Test Country', 'Test City', '123456789', '12', '2025');
        });

        await test.step('Click on Purchase button and verify purchase is completed', async () => {
            await assertionsUI.elementIsVisible(cartPage.placeOrderModal.purchaseButton);
            await cartPage.placeOrderModal.clickPurchaseButton();
            await assertionsUI.elementIsVisible(cartPage.purchaseConfirmationModal.confirmationMessage);
        });

        await test.step('Click on OK button and verify modal is closed', async () => {
            await cartPage.purchaseConfirmationModal.clickConfirmationButton();
            await cartPage.purchaseConfirmationModal.waitForElementToBeHidden(cartPage.purchaseConfirmationModal.modalIdentifier)
            await assertionsUI.elementIsHidden(cartPage.purchaseConfirmationModal.modalIdentifier);
        });
    });
