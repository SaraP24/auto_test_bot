import { test as base } from "@playwright/test";
import { LoginPage } from "../pages/LoginPage";
import { TodoPage } from "../pages/TodoPage";
import { BasePage } from "../pages/BasePage";

type Page_manager = {
  basePage: BasePage;
  loginPage: LoginPage;
  todoPage: TodoPage;

}

const test = base.extend<Page_manager>({
  basePage: async ({ page }, use) => {
    await use(new BasePage(page));
  },
  
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },

  todoPage: async ({ page }, use) => {
    await use(new TodoPage(page));
  },
});

export { test };