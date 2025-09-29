import { BasePage } from "./BasePage";

export class LoginPage extends BasePage {
    readonly usernameInput = 'input[name="username"]';
    readonly passwordInput = 'input[name="password"]';
    readonly submitButton = 'button[type="submit"]';
    readonly welcomeMessage = '.welcome-message';
    readonly errorMessage = '.error-message';     
 
    
    async navigate() {
        await this.page.goto('https://example.com/login');
    }

    async login(username: string, password: string) {
        await this.page.fill(this.usernameInput, username);
        await this.page.fill(this.passwordInput, password);
        await this.page.click(this.submitButton);
    }   

    async getWelcomeMessage() {
        return this.page.textContent(this.welcomeMessage);
    }

    async getErrorMessage() {
        return this.page.textContent(this.errorMessage);
    }   
}