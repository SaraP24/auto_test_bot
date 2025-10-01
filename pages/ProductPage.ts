import { Page, Locator } from '@playwright/test';
import { SHORT_TIMEOUT } from '../utils/Timeouts';
import { BasePage } from '../pages/BasePage';

export class ProductPage extends BasePage {
    readonly pageIdentifier: Locator = this.page.locator('.product-content.product-deatil');
    readonly productTitle: Locator = this.page.getByRole('heading', { level: 2 });
    readonly productPrice: Locator = this.page.locator('h3.price-container');
    readonly addToCartButton: Locator = this.page.locator('a.btn-success').getByText('Add to cart');

    constructor(page: Page) {
        super(page);
    }

    async clickAddToCart(): Promise<void> {
        await this.click(this.addToCartButton);
        await this.waitForTimeout(SHORT_TIMEOUT);
    }
}
