import { test as base } from "@playwright/test";
import { BasePage } from "../pages/BasePage.ts";
import { HeaderPage } from "../pages/HeaderPage.ts";
import { HomePage } from '../pages/HomePage.ts';
import { ProductPage } from '../pages/ProductPage.ts';
import { CartPage } from '../pages/CartPage.ts';
import AssertionsUI from "../utils/AssertionsUI.ts";
import { CatalogFlow } from '../flows/CatalogFlow.ts';
import { CheckoutFlow } from '../flows/CheckoutFlow.ts';
import { LoginFlow } from '../flows/LoginFlow.ts';
import { ContactFlow } from '../flows/ContactFlow.ts';


type Page_manager = {
  homePage: HomePage;
  headerPage: HeaderPage;
  productPage: ProductPage;
  cartPage: CartPage;
  basePage: BasePage;
  assertionsUI: AssertionsUI;
  catalogFlow: CatalogFlow;
  checkoutFlow: CheckoutFlow;
  loginFlow: LoginFlow;
  contactFlow: ContactFlow;
}

const test = base.extend<Page_manager>({
  basePage: async ({ page }, use) => {
    await use(new BasePage(page));
  },
  headerPage: async ({ page }, use) => {
    await use(new HeaderPage(page));
  },
  homePage: async ({ page }, use) => {
    await use(new HomePage(page));
  },
   productPage: async ({ page }, use) => {
    await use(new ProductPage(page));
  },

  cartPage: async ({ page }, use) => {
    await use(new CartPage(page));
  },
  assertionsUI: async ({ page }, use) => {
    await use(new AssertionsUI(page));
  },
  catalogFlow: async ({ homePage, productPage, cartPage, assertionsUI }, use) => {
    await use(new CatalogFlow({ homePage, productPage, cartPage, assertionsUI }));
  },
  checkoutFlow: async ({ cartPage, assertionsUI }, use) => {
    await use(new CheckoutFlow({ cartPage, assertionsUI }));
  },
  loginFlow: async ({ headerPage, assertionsUI }, use) => {
    await use(new LoginFlow({ headerPage, assertionsUI }));
  },
  contactFlow: async ({ headerPage, assertionsUI }, use) => {
    await use(new ContactFlow({ headerPage, assertionsUI }));
  },
});

export { test };