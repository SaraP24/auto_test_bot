import { HeaderPage } from '../pages/HeaderPage';
import AssertionsUI from '../utils/AssertionsUI';
import { LoginCredentials, LoginResult } from './domain-models';

export type LoginFlowDependencies = {
    headerPage: HeaderPage;
    assertionsUI: AssertionsUI;
};

export class LoginFlow {
    constructor(private readonly deps: LoginFlowDependencies) {}

    async openLoginForm(): Promise<void> {
        await this.deps.headerPage.click(this.deps.headerPage.loginLink);
        await this.deps.headerPage.waitForElementToBeVisible(this.deps.headerPage.loginModal.loginModalIdentifier);
    }

    async signUpCustomer(credentials: LoginCredentials): Promise<string> {
        return await this.deps.headerPage.signUp(credentials.username, credentials.password);
    }

    async loginAsCustomer(credentials: LoginCredentials): Promise<LoginResult> {
        const alreadyLoggedIn = await this.isLoggedIn();
        if (alreadyLoggedIn) {
            const username = await this.deps.headerPage.welcomeUserText.textContent();
            return { status: 'logged-in', username: username ?? credentials.username, message: 'Already logged in' };
        }

        const dialogMessagePromise = Promise.race([
            this.deps.headerPage.getDialogMessage(),
            new Promise<string>((resolve) => setTimeout(() => resolve(''), 2500)),
        ]);

        await this.openLoginForm();
        await this.deps.headerPage.loginModal.fillLoginCredentials(credentials.username, credentials.password);
        await this.deps.headerPage.loginModal.clickLoginButton();

        const dialogMessage = await dialogMessagePromise;
        const loggedIn = await this.isLoggedIn();

        if (dialogMessage || !loggedIn) {
            return {
                status: 'invalid-credentials',
                message: dialogMessage || 'Invalid credentials',
            };
        }

        const username = await this.deps.headerPage.welcomeUserText.textContent();
        return {
            status: 'logged-in',
            username: username ?? credentials.username,
            message: 'Login successful',
        };
    }

    async logout(): Promise<void> {
        if (!(await this.isLoggedIn())) {
            return;
        }
        await this.deps.headerPage.click(this.deps.headerPage.logoutLink);
    }

    async isLoggedIn(): Promise<boolean> {
        return await this.deps.headerPage.welcomeUserText.isVisible().catch(() => false);
    }
}
