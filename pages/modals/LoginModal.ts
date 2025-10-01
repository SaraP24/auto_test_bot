import { Page, Locator } from '@playwright/test';
import { BasePage } from '../../pages/BasePage';

export class LoginModal extends BasePage {
    readonly loginModalIdentifier: Locator = this.page.locator('#logInModal .modal-content');
    readonly usernameField: Locator = this.page.locator('#loginusername');
    readonly passwordField: Locator = this.page.locator('#loginpassword');
    readonly loginButton: Locator = this.page.getByRole('button', { name: 'Log in' });

    constructor(page: Page) {
        super(page);
    }

    async fillLoginCredentials(username: string, password: string): Promise<void> {
        await this.fillTextInput(this.usernameField, username);
        await this.fillTextInput(this.passwordField, password);
    }

    async clickLoginButton(): Promise<void> {
        await this.click(this.loginButton);
    }
}