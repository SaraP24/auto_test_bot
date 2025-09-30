import { Locator, Page } from "@playwright/test";
import { DEFAULT_TIMEOUT } from "../utils/timeouts";

export class BasePage {
    protected page: Page;

    constructor(page: Page) {
        this.page = page;
    }

    async navigateToUrl(url: string) {
        await this.page.goto(url);
    }   

    async waitForURL(url: string) {
        await this.page.waitForURL(url, { timeout: DEFAULT_TIMEOUT });
    }

    async getTitle() {
        return this.page.title();
    }

    async navigateToHomePage(url: string) {
        await this.page.goto(url, { waitUntil: 'domcontentloaded', timeout: DEFAULT_TIMEOUT });
    }

    async click(locator: Locator): Promise<void> {
        await locator.click();
    }

    async fill(locator: Locator, text: string): Promise<void> {
        await locator.fill(text);
    }

    async screenshot(options?: { path?: string; fullPage?: boolean }): Promise<Buffer> {
        return this.page.screenshot(options);
    }

    async isElementVisible(locator: Locator): Promise<boolean> {
        try {
            await locator.waitFor({ state: 'visible', timeout: DEFAULT_TIMEOUT });
            return true;
        } catch {
            return false;
        }
    }

}