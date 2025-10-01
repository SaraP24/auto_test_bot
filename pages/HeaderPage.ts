import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';
import { NewMessageModal } from './modals/NewMessageModal';
import { LoginModal } from './modals/LoginModal';


export class HeaderPage extends BasePage {
    readonly navbar: Locator = this.page.locator('#narvbarx');
    readonly homeLink: Locator = this.page.getByRole('link', { name: 'Home' });
    readonly contactLink: Locator = this.page.getByRole('link', { name: 'Contact' });
    readonly aboutUsLink: Locator = this.page.getByRole('link', { name: 'About us' });
    readonly cartLink: Locator = this.page.getByRole('link', { name: 'Cart' });
    readonly loginLink: Locator = this.page.getByRole('link', { name: 'Log in' });
    readonly signUpLink: Locator = this.page.getByRole('link', { name: 'Sign up' });
    readonly welcomeUserText: Locator =  this.page.locator('a#nameofuser');

    readonly newMessageModal: NewMessageModal;
    readonly loginModal: LoginModal;

    constructor(page: Page) {
        super(page);
        this.newMessageModal = new NewMessageModal(page);
        this.loginModal =  new LoginModal(page);
    }

    async openContactForm(): Promise<void> {
        await this.click(this.contactLink);
        await this.waitForElementToBeVisible(this.newMessageModal.contactFormIdentifier);
    }
}
