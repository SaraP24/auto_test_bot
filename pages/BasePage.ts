import { Locator, Page } from "@playwright/test";
import { DEFAULT_TIMEOUT } from "../utils/timeouts";

export class BasePage {
    protected page: Page;

    constructor(page: Page) {
        this.page = page;
    }

    async navigate(url: string) {
        await this.page.goto(url);
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

}