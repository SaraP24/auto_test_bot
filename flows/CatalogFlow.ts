import { HomePage } from '../pages/HomePage.ts';
import { ProductPage } from '../pages/ProductPage.ts';
import { CartPage } from '../pages/CartPage.ts';
import AssertionsUI from '../utils/AssertionsUI.ts';
import { ProductSummary } from './domain-models.ts';

export type CatalogFlowDependencies = {
    homePage: HomePage;
    productPage: ProductPage;
    cartPage: CartPage;
    assertionsUI: AssertionsUI;
};

export class CatalogFlow {
    constructor(private readonly deps: CatalogFlowDependencies) {}

    async openHomePage(url: string = '/'): Promise<void> {
        await this.deps.homePage.navigateToHomePage(url);
        await this.deps.homePage.waitForElementToBeVisible(this.deps.homePage.productCard.first());
    }

    async listProducts(pagesToCollect: number = 1): Promise<ProductSummary[]> {
        const products = await this.deps.homePage.getProductsFromPages(pagesToCollect);
        return products.map((product) => ({
            title: product.title,
            price: product.price,
            link: product.link,
        }));
    }

    async openProductByIndex(index: number): Promise<ProductSummary> {
        const products = await this.listProducts(1);
        if (!products[index]) {
            throw new Error(`Product at index ${index} is not available in the catalog.`);
        }

        await this.deps.homePage.selectProductByIndex(index);
        await this.deps.productPage.waitForElementToBeVisible(this.deps.productPage.productTitle);
        return products[index];
    }

    async addProductToCartByIndex(index: number): Promise<ProductSummary> {
        const selectedProduct = await this.openProductByIndex(index);
        await this.deps.productPage.clickAddToCart();
        await this.deps.cartPage.goToCart();
        await this.deps.assertionsUI.elementHaveText(this.deps.cartPage.pageTitle, /products/i);
        await this.deps.assertionsUI.elementIsVisible(this.deps.cartPage.cartTable);
        return selectedProduct;
    }
}
