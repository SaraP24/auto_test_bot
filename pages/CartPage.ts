import { Locator, Page } from "@playwright/test";
import { BasePage } from "./BasePage";
import { PlaceOrderModal } from "./modals/PlaceOrderModal";
import { PurchaseConfirmationModal } from "./modals/PurchaseConfirmationModal"

export class CartPage extends BasePage {
    readonly pageTitle: Locator = this.page.locator('h2').filter({ hasText: 'Products' });
    readonly cartTable: Locator = this.page.locator('#tbodyid')
    readonly placeOrderButton: Locator = this.page.getByRole('button', { name: 'Place Order1' });

    readonly placeOrderModal: PlaceOrderModal;
    readonly purchaseConfirmationModal: PurchaseConfirmationModal;

    constructor(page: Page) {
        super(page);
        this.placeOrderModal = new PlaceOrderModal(page);
        this.purchaseConfirmationModal = new PurchaseConfirmationModal(page);
    }

    async waitForPageLoad(): Promise<void> {
        await this.page.waitForURL('**/cart.html', { waitUntil: 'load' });
    }

    async goToCart(): Promise<void> {
        await this.page.goto('/cart.html');
        await this.waitForPageLoad();
    }

    async clickPlaceOrder(): Promise<void> {
        await this.click(this.placeOrderButton);
        await this.waitForElementToBeVisible(this.placeOrderModal.placeOrderFormIdentifier);
    }
}