import { test } from '../fixtures/page-manager';
import { IProductInformation } from  '../interfaces/ui/IProductInformation';

test.describe('DemoBlaze Tests - Product List Information tests', () => {
    test('001 - Validate get product list information from first N pages', async ({ headerPage, homePage, assertionsUI }) => {
        const pagesToCollect = 2;
        await test.step('Navigate to homepage', async () => {
            await homePage.navigateToHomePage('/');
            await homePage.waitForElementToBeVisible(headerPage.navbar);
        });

        await test.step('Collect product list from pages and verify non-empty', async () => {
            const allProductsInfo = await homePage.getProductsFromPages(pagesToCollect);

            console.table(allProductsInfo as IProductInformation[]);

            await assertionsUI.isGreaterThan(allProductsInfo.length, 0);
            await assertionsUI.isTruthy(await homePage.writeJSONFile('reports/productsInformation.json', allProductsInfo));
        });
    });
});