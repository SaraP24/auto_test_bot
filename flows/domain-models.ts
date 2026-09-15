export type ProductSummary = {
    title: string;
    price: string;
    link: string;
};

export type CustomerDetails = {
    name: string;
    country: string;
    city: string;
    creditCard: string;
    month: string;
    year: string;
};

export type LoginCredentials = {
    username: string;
    password: string;
};

export type LoginResult = {
    status: 'logged-in' | 'invalid-credentials';
    username?: string;
    message?: string;
};

export type ContactMessage = {
    email: string;
    name: string;
    message: string;
};

export type ContactResult = {
    status: 'sent';
    message: string;
};

export type CheckoutResult = {
    status: 'completed';
    confirmationMessage: string;
};
