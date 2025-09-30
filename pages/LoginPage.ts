import { Locator } from "playwright-core";
import { BasePage } from "./BasePage";

export class LoginPage extends BasePage {
    readonly usernameInput = this.page.getByPlaceholder('Username');
    readonly passwordInput = this.page.getByPlaceholder('Password');
    readonly submitButton = this.page.locator('.orangehrm-login-button');

    readonly errorMessage = this.page.locator('.error-message');
    readonly dashboardHeader = this.page.locator('.orangehrm-dashboard-widget-header111');

    async login(username: string, password: string) {
        await this.fill(this.usernameInput, username);
        await this.fill(this.passwordInput, password);
        await this.click(this.submitButton);
    }
}