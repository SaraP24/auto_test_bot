import { Locator, Page } from "@playwright/test";
import { BasePage } from '../../pages/BasePage';

export class PurchaseConfirmationModal extends BasePage {
    readonly modalIdentifier: Locator = this.page.locator('.sweet-alert');
    readonly confirmationMessage: Locator = this.page.getByRole('heading', { level: 2 }).first();
    readonly okButton: Locator = this.page.locator('button.confirm');

    constructor(page: Page) {
        super(page);
    }

    async clickConfirmationButton() {
        await this.click(this.okButton);
    }
}