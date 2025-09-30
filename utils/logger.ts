import { BasePage } from "../pages/BasePage";

export class Logger extends BasePage {
    static log(message: string) {
        console.log(`[LOG] ${message}`);
    }
    static error(message: string) {
        console.error(`[ERROR] ${message}`);
    }
    static warn(message: string) {
        console.warn(`[WARN] ${message}`);
    }
}

