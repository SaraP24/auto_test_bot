import { test as base } from "@playwright/test";
import { BasePage } from "../pages/BasePage";
import { HeaderPage } from "../pages/HeaderPage";
import { HomePage } from '../pages/HomePage';
import { ProductPage } from '../pages/ProductPage';
import { CartPage } from '../pages/CartPage';
import AssertionsUI from "../utils/AssertionsUI";


type Page_manager = {
  homePage: HomePage;
  headerPage: HeaderPage;
  productPage: ProductPage;
  cartPage: CartPage;
  basePage: BasePage;
  assertionsUI: AssertionsUI;
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
});

export { test };