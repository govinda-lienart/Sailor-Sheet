/**
 * Account Default Configurations by Transaction Type and Country
 */

import { COUNTRIES, TRANSACTION_TYPES } from './constants.js';

/**
 * Account name patterns for matching
 */
export const ACCOUNT_PATTERNS = {
    BE: {
        WALLET_GOVINDA: {
            exact: 'BE - Wallet Govinda Lienart (Real Accounts)',
            fallback: ['be', 'wallet', 'govinda']
        },
        REVENUES: {
            exact: 'BE - Revenues (Nominal Accounts)',
            fallback: ['be', 'revenues']
        },
        EXPENSES: {
            exact: 'BE - Expenses (Nominal Accounts)',
            fallback: ['be', 'expenses']
        }
    },
    VN: {
        INDOVINA_BANK: {
            exact: 'VN - Indovina Bank (Real Accounts)',
            fallback: ['vn', 'indovina']
        },
        REVENUES: {
            exact: 'VN - Revenues (Nominal Accounts)',
            fallback: ['vn', 'revenues']
        },
        EXPENSES: {
            exact: 'VN - Expenses (Nominal Accounts)',
            fallback: ['vn', 'expenses']
        }
    },
    COMMON: {
        WALLET: {
            fallback: ['wallet']
        },
        INDOVINA_BANK: {
            fallback: ['indovina bank']
        }
    }
};

/**
 * Transaction default configurations
 * Structure: { transactionType: { country: { debit, credit, category, fund } } }
 */
export const TRANSACTION_DEFAULTS = {
    [TRANSACTION_TYPES.DONATION]: {
        [COUNTRIES.BE]: {
            debit: ACCOUNT_PATTERNS.BE.WALLET_GOVINDA,
            credit: ACCOUNT_PATTERNS.BE.REVENUES,
            category: { pattern: 'donation' },
            fund: { pattern: 'unrestricted' }
        },
        [COUNTRIES.VN]: {
            debit: ACCOUNT_PATTERNS.VN.INDOVINA_BANK,
            credit: ACCOUNT_PATTERNS.VN.REVENUES,
            category: { pattern: 'donation' },
            fund: { pattern: 'unrestricted' }
        }
    },
    [TRANSACTION_TYPES.PAYMENT]: {
        [COUNTRIES.BE]: {
            debit: ACCOUNT_PATTERNS.BE.EXPENSES,
            credit: ACCOUNT_PATTERNS.BE.WALLET_GOVINDA,
            category: { pattern: ['food', 'meals'] },
            fund: null // No default fund for payments
        },
        [COUNTRIES.VN]: {
            debit: ACCOUNT_PATTERNS.VN.EXPENSES,
            credit: ACCOUNT_PATTERNS.VN.INDOVINA_BANK,
            category: { pattern: ['food', 'meals'] },
            fund: null // No default fund for payments
        }
    },
    [TRANSACTION_TYPES.INTERNAL_TRANSFER]: {
        common: { // Same for all countries
            debit: ACCOUNT_PATTERNS.COMMON.WALLET,
            credit: ACCOUNT_PATTERNS.COMMON.INDOVINA_BANK,
            category: { pattern: 'internal bank transfer' },
            fund: { pattern: 'internal transfer' }
        }
    },
    [TRANSACTION_TYPES.GRANT]: {
        [COUNTRIES.BE]: {
            debit: ACCOUNT_PATTERNS.BE.WALLET_GOVINDA,
            credit: ACCOUNT_PATTERNS.BE.REVENUES,
            category: { pattern: 'grant' },
            fund: null // User selects fund for grants
        },
        [COUNTRIES.VN]: {
            debit: ACCOUNT_PATTERNS.VN.INDOVINA_BANK,
            credit: ACCOUNT_PATTERNS.VN.REVENUES,
            category: { pattern: 'grant' },
            fund: null // User selects fund for grants
        }
    }
};

