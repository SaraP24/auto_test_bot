import { HeaderPage } from '../pages/HeaderPage.ts';
import AssertionsUI from '../utils/AssertionsUI.ts';
import { ContactMessage, ContactResult } from './domain-models.ts';

export type ContactFlowDependencies = {
    headerPage: HeaderPage;
    assertionsUI: AssertionsUI;
};

export class ContactFlow {
    constructor(private readonly deps: ContactFlowDependencies) {}

    async openContactForm(): Promise<void> {
        await this.deps.headerPage.openContactForm();
    }

    async sendMessage(message: ContactMessage): Promise<ContactResult> {
        await this.openContactForm();
        await this.deps.headerPage.newMessageModal.fillAllFields(message.email, message.name, message.message);
        await this.deps.headerPage.newMessageModal.clickSendMessage();
        return {
            status: 'sent',
            message: `Message sent to ${message.email}`,
        };
    }
}
