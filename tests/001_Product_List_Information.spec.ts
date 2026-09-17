import { test } from '../fixtures/page-manager.ts';

test.describe('DemoBlaze Tests - Product List Information tests', () => {
    test('001 - Validate get product list information from first N pages', async ({ catalogFlow, assertionsUI }) => {
        const pagesToCollect = 2;

        await test.step('Open the catalog and collect product overview information', async () => {
            await catalogFlow.openHomePage('/');
            const allProductsInfo = await catalogFlow.listProducts(pagesToCollect);

            await assertionsUI.isGreaterThan(allProductsInfo.length, 0);
        });
    });
});