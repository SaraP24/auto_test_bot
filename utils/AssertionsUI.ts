import { Page, expect, Locator } from '@playwright/test';
import { IAssertionOptions } from '../interfaces/IAssertionOptions';
import { SHORT_TIMEOUT } from '../utils/Timeouts';

export default class AssertionsUI {
    constructor(protected page: Page) { }

    async elementIsVisible(element: Locator, options?: IAssertionOptions): Promise<void> {
        await expect(element, options?.message || 'Element is HIDDEN instead of VISIBLE').toBeVisible({ timeout: options?.timeout || SHORT_TIMEOUT });
    }
    async elementIsHidden(element: Locator, options?: IAssertionOptions): Promise<void> {
        await expect(element, options?.message || 'Element is VISIBLE instead of HIDDEN').toBeHidden({ timeout: options?.timeout || SHORT_TIMEOUT });
    }
    
    async isTruthy(value: boolean, options?: IAssertionOptions): Promise<void> {
        expect(value, options?.message || 'Value is FALSE instead of TRUE').toBeTruthy();
    }

    async isFalsy(value: boolean, options?: IAssertionOptions): Promise<void> {
        expect(value, options?.message || 'Value is TRUE instead of FALSE').toBeFalsy();
    }

    async isGreaterThan(value: number, compareToValue: number, options?: IAssertionOptions): Promise<void> {
        expect(value, options?.message || `Value ${value} is NOT greater than ${compareToValue}`).toBeGreaterThan(compareToValue);
    }

    async elementHaveText(element: Locator, text: string | RegExp, options?: IAssertionOptions): Promise<void> {
        await expect(element, options?.message || `Element does NOT contain text: ${text}`).toHaveText(text, { timeout: options?.timeout || SHORT_TIMEOUT });
    }
}