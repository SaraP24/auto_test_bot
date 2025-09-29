import { test as base } from "@playwright/test";
import { LoginPage } from "../../pages/LoginPage";
import { TodoPage } from "../../pages/TodoPage";

type CustomFixtures = {
  loginPage: LoginPage;
  todoPage: TodoPage;

}

const test = base.extend<CustomFixtures>({
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },

  todoPage: async ({ page }, use) => {
    await use(new TodoPage(page));
  },
});

export { test };