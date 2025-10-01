import { Page, Locator } from '@playwright/test';
import { BasePage } from '../pages/BasePage';
import { IProductInformation } from '../interfaces/ui/IProductInformation';

export class HomePage extends BasePage {
    readonly productCard: Locator = this.page.locator('.card .card-block');
    readonly productTitles: Locator = this.page.locator('h4.card-title');
    readonly productPrice: Locator = this.productCard.getByRole('heading', { level: 5 });
    readonly productLink: Locator = this.productCard.getByRole('link');

    readonly nextPageButton: Locator = this.page.locator('button.page-link').getByText('Next');
    readonly previousPageButton: Locator = this.page.locator('button.page-link').getByText('Previous');

    constructor(page: Page) {
        super(page);
    }

    async navigateToHomePage(url: string): Promise<void> {
        await this.page.goto(url);
    }

    async getProductCount(): Promise<number> {
        await this.waitForElementToBeVisible(this.productCard.first());
        return await this.getElementCount(this.productCard);
    }

    async clickNextPage(): Promise<void> {
        await this.nextPageButton.click();
    }

    private async getProductTitles(): Promise<string[]> {
        return await this.productTitles.allTextContents();
    }

    private async getProductPrices(): Promise<string[]> {
        return await this.productPrice.allInnerTexts();
    }

    private async getProductLinks(): Promise<string[]> {
        const hrefs = await this.productLink.evaluateAll((elements) =>
            elements.map(el => (el).getAttribute('href') || '')
        );
        return hrefs.map(href => `https://www.demoblaze.com/${href}`);
    }

    async selectProductByIndex(index: number): Promise<void> {
        const product = this.productTitles.nth(index);
        return this.click(product);
    }

    async getAllProductsInformation(): Promise<IProductInformation[]> {
        const titles = await this.getProductTitles();
        const prices = await this.getProductPrices();
        const links = await this.getProductLinks();
        const products: IProductInformation[] = titles.map((title, index) => ({
            title,
            price: prices[index],
            link: links[index]
        }));

        return products;
    }

    /**
     * Collect products across N pages (starting from current page).
     * Stops early if the "Next" button is missing or disabled.
     */
    async getProductsFromPages(pages: number): Promise<IProductInformation[]> {
        const allProducts: IProductInformation[] = [];

        const productCount = await this.getProductCount();
        if (productCount === 0) return allProducts;

        let products = await this.getAllProductsInformation();

        for (let i = 0; i < pages; i++) {
            if (i > 0) {
                const canGoNext = await (async () => {
                    try {
                        return await this.nextPageButton.isVisible();
                    } catch {
                        return false;
                    }
                })();

                if (!canGoNext) break;
                const productCount = await this.getProductCount();
                if (productCount === 0) break;
                await this.clickNextPage();
                await this.waitForElementToBeHidden(this.nextPageButton);

            }

            products = await this.getAllProductsInformation();
            allProducts.push(...products);
        }

        return allProducts;
    }
}
