import { test } from '../fixtures/page-manager';

    test('002 - Validate user can place an order', async ({ catalogFlow, checkoutFlow }) => {
        await test.step('Open the catalog and buy the first product', async () => {
            await catalogFlow.openHomePage('/');
            await catalogFlow.addProductToCartByIndex(0);
        });

        await test.step('Complete checkout for the selected customer', async () => {
            const result = await checkoutFlow.purchaseProduct({
                name: 'Test User',
                country: 'Test Country',
                city: 'Test City',
                creditCard: '123456789',
                month: '12',
                year: '2025',
            });

            await test.expect(result.status).toBe('completed');
        });
    });
