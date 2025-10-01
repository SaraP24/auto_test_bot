import { Locator, Page } from "@playwright/test";
import { BasePage } from '../../pages/BasePage';

export class PlaceOrderModal extends BasePage {
    readonly placeOrderFormIdentifier: Locator = this.page.locator('#orderModal .modal-content')
    readonly modalTitle: Locator = this.page.locator('#orderModalLabel').getByRole('heading', { level: 5 });
    readonly nameInput: Locator = this.page.locator('#name');
    readonly countryInput: Locator = this.page.locator('#country')
    readonly cityInput: Locator = this.page.locator('#city');
    readonly creditCardInput: Locator = this.page.locator('#card')
    readonly monthInput: Locator = this.page.locator('#month');
    readonly yearInput: Locator = this.page.locator('#year');
    readonly purchaseButton: Locator = this.page.getByRole('button').getByText('Purchase');
    readonly closeButton: Locator = this.page.locator('#orderModal button.btn-secondary').getByText('Close');

    constructor(page: Page) {
        super(page);
    }

    private async fillName(name: string): Promise<void> {
        await this.fillTextInput(this.nameInput, name);
    }
    private async fillCountry(country: string): Promise<void> {
        await this.fillTextInput(this.countryInput, country);
    }
    private async fillCity(city: string): Promise<void> {
        await this.fillTextInput(this.cityInput, city);
    }
    private async fillCreditCard(creditCard: string): Promise<void> {
        await this.fillTextInput(this.creditCardInput, creditCard);
    }
    private async fillMonth(month: string): Promise<void> {
        await this.fillTextInput(this.monthInput, month);
    }
    private async fillYear(year: string): Promise<void> {
        await this.fillTextInput(this.yearInput, year);
    }

    async fillAllFields(name: string, country: string, city: string, creditCard: string, month: string, year: string): Promise<void> {
        await this.fillName(name);
        await this.fillCountry(country);
        await this.fillCity(city);
        await this.fillCreditCard(creditCard);
        await this.fillMonth(month);
        await this.fillYear(year);
    }

    async clickPurchaseButton(): Promise<void> {
        await this.click(this.purchaseButton);
    }
}