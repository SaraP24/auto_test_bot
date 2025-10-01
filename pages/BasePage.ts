import { Page, Locator } from '@playwright/test';
import fs from 'fs';
import {DEFAULT_TIMEOUT} from '../utils/Timeouts';

export class BasePage {
    protected page: Page;

    constructor(page: Page) {
        this.page = page;
    }

    async navigateToHomePage(url: string) {
        await this.page.goto(url, { waitUntil: 'domcontentloaded', timeout: DEFAULT_TIMEOUT });
    }

    async click(locator: Locator): Promise<void> {
        await locator.click();
    }

    async getElementCount(locator: Locator): Promise<number> {
        const elements = await locator.count();
        return elements;
    }

    async fillTextInput(locator: Locator, text: string): Promise<void> {
        await locator.fill(text);
    }

    async getTextFromElement(locator: Locator): Promise<string | null> {
        return await locator.textContent();
    }

    async waitForElementToBeVisible(locator: Locator, timeout: number = DEFAULT_TIMEOUT): Promise<void> {
        await locator.waitFor({ state: 'visible', timeout });
    }

    async waitForElementToBeHidden(locator: Locator, timeout: number = DEFAULT_TIMEOUT): Promise<void> {
        await locator.waitFor({ state: 'hidden', timeout });
    }

    async waitForTimeout(timeout: number) {
        await this.page.waitForTimeout(timeout);
    }

    async writeJSONFile(filePath: string, data: object): Promise<boolean> {
        fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8');
        return true;
    }

    async getDialogMessage(): Promise<string> {
        return new Promise<string>((resolve) => {
            this.page.once('dialog', (dialog) => {
                resolve(dialog.message());
            });
        });
    }

    async dismissDialog(): Promise<boolean> {
        let dialogAccepted = false;
        this.page.once('dialog', async dialog => {
            await dialog.accept();
            dialogAccepted = true;
        });
        return dialogAccepted;
    }
}