import { Page, Locator } from '@playwright/test';
import { BasePage } from '../../pages/BasePage';

export class NewMessageModal extends BasePage {
    readonly contactFormIdentifier: Locator = this.page.locator('#exampleModal .modal-content');
    readonly modalTitle: Locator = this.page.locator('.modal-title#exampleModalLabel');
    readonly emailInput: Locator = this.page.locator('#recipient-email');
    readonly nameInput: Locator = this.page.locator('#recipient-name');
    readonly messageInput: Locator = this.page.locator('textarea#message-text');

    readonly sendMessageButton: Locator = this.page.getByRole('button').getByText('Send message');
    readonly closeButton: Locator = this.page.locator('#exampleModal button.btn-secondary').getByText('Close');

    constructor(page: Page) {
        super(page);
    }

    async getAllModalElements(): Promise<Locator[]> {
        return [
            this.modalTitle,
            this.emailInput,
            this.nameInput,
            this.messageInput,
            this.sendMessageButton,
            this.closeButton
        ];
    }

    private async fillEmail(email: string): Promise<void> {
        await this.fillTextInput(this.emailInput, email);
    }
    private async fillName(name: string): Promise<void> {
        await this.fillTextInput(this.nameInput, name);
    }
    private async fillMessage(message: string): Promise<void> {
        await this.fillTextInput(this.messageInput, message);
    }
    
    async fillAllFields(email: string, name: string, message: string): Promise<void> {
        await this.fillEmail(email);
        await this.fillName(name);
        await this.fillMessage(message);
    }

    async clickSendMessage(): Promise<void> {
        await this.click(this.sendMessageButton);
    }
}