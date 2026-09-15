import { CartPage } from '../pages/CartPage';
import AssertionsUI from '../utils/AssertionsUI';
import { CheckoutResult, CustomerDetails } from './domain-models';

export type CheckoutFlowDependencies = {
    cartPage: CartPage;
    assertionsUI: AssertionsUI;
};

export class CheckoutFlow {
    constructor(private readonly deps: CheckoutFlowDependencies) {}

    async purchaseProduct(customer: CustomerDetails): Promise<CheckoutResult> {
        await this.deps.cartPage.goToCart();
        await this.deps.assertionsUI.elementHaveText(this.deps.cartPage.pageTitle, /products/i);
        await this.deps.assertionsUI.elementIsVisible(this.deps.cartPage.cartTable);

        await this.deps.cartPage.clickPlaceOrder();
        await this.deps.assertionsUI.elementIsVisible(this.deps.cartPage.placeOrderModal.placeOrderFormIdentifier);

        await this.deps.cartPage.placeOrderModal.fillAllFields(
            customer.name,
            customer.country,
            customer.city,
            customer.creditCard,
            customer.month,
            customer.year,
        );

        await this.deps.assertionsUI.elementIsVisible(this.deps.cartPage.placeOrderModal.purchaseButton);
        await this.deps.cartPage.placeOrderModal.clickPurchaseButton();
        await this.deps.assertionsUI.elementIsVisible(this.deps.cartPage.purchaseConfirmationModal.confirmationMessage);

        const confirmationMessage = await this.deps.cartPage.purchaseConfirmationModal.confirmationMessage.textContent() ?? 'Purchase completed';

        await this.deps.cartPage.purchaseConfirmationModal.clickConfirmationButton();
        await this.deps.cartPage.purchaseConfirmationModal.waitForElementToBeHidden(this.deps.cartPage.purchaseConfirmationModal.modalIdentifier);
        await this.deps.assertionsUI.elementIsHidden(this.deps.cartPage.purchaseConfirmationModal.modalIdentifier);

        return {
            status: 'completed',
            confirmationMessage,
        };
    }
}
