/**
 * Transaction Defaults Service
 * Handles auto-selection of accounts, categories, and funds based on transaction type
 */

import { TRANSACTION_TYPES, COUNTRIES } from '../config/constants.js';
import { TRANSACTION_DEFAULTS } from '../config/accountDefaults.js';

/**
 * Find option in select element by pattern
 */
function findOptionByPattern(selectElement, pattern) {
    if (!selectElement) return null;
    
    const options = Array.from(selectElement.options);
    
    // Try exact match first if pattern has exact property
    if (pattern.exact) {
        const exactOption = options.find(option => 
            option.textContent.trim() === pattern.exact
        );
        if (exactOption) return exactOption;
    }
    
    // Try fallback patterns
    if (pattern.fallback) {
        const fallbackPatterns = Array.isArray(pattern.fallback) ? pattern.fallback : [pattern.fallback];
        return options.find(option => {
            const text = option.textContent.toLowerCase();
            return fallbackPatterns.every(p => text.includes(p.toLowerCase()));
        });
    }
    
    return null;
}

/**
 * Find option by text pattern (for categories and funds)
 */
function findOptionByText(selectElement, pattern) {
    if (!selectElement) return null;
    
    const options = Array.from(selectElement.options);
    const patterns = Array.isArray(pattern) ? pattern : [pattern];
    
    return options.find(option => {
        const text = option.textContent.toLowerCase();
        return patterns.some(p => text.includes(p.toLowerCase()));
    });
}

/**
 * Set account selection
 */
function setAccount(selectElement, accountPattern, accountType, country) {
    if (!selectElement) return;
    
    const option = findOptionByPattern(selectElement, accountPattern);
    if (option) {
        selectElement.value = option.value;
        console.log(`✅ Auto-selected ${country} ${accountType}:`, option.textContent);
    } else {
        console.warn(`⚠️ Could not find ${accountType} account for ${country}`);
    }
}

/**
 * Set category selection
 */
function setCategory(selectElement, categoryPattern) {
    if (!selectElement) return;
    
    const option = findOptionByText(selectElement, categoryPattern);
    if (option) {
        selectElement.value = option.value;
        console.log(`✅ Auto-selected category:`, option.textContent);
    }
}

/**
 * Set fund selection
 */
function setFund(selectElement, fundPattern) {
    if (!selectElement) return;
    
    if (fundPattern === null) {
        // Explicitly set to empty for transactions that shouldn't have a default fund
        selectElement.value = '';
        console.log('Fund left on default "Choose a fund..."');
        return;
    }
    
    const option = findOptionByText(selectElement, fundPattern);
    if (option) {
        selectElement.value = option.value;
        console.log(`✅ Auto-selected fund:`, option.textContent);
    }
}

/**
 * Apply transaction defaults based on type and country
 */
export function applyTransactionDefaults(selectedType) {
    console.log(`🎯 Applying defaults for transaction type: ${selectedType}`);
    
    // Get form elements
    const debitAccountSelect = document.querySelector('select[name="regular_debit_account_id"]');
    const creditAccountSelect = document.querySelector('select[name="regular_credit_account_id"]');
    const categorySelect = document.querySelector('select[name="category_id"]');
    const fundSelect = document.querySelector('select[name="fund_id"]');
    
    // Get current country
    const selectedCountry = sessionStorage.getItem('selectedCountry') || COUNTRIES.BE;
    console.log(`🌍 Current country: ${selectedCountry}`);
    
    // Clear previous selections
    if (debitAccountSelect) debitAccountSelect.value = '';
    if (creditAccountSelect) creditAccountSelect.value = '';
    if (categorySelect) categorySelect.value = '';
    if (fundSelect) fundSelect.value = '';
    
    console.log('🧹 Cleared previous selections');
    
    // Get defaults for this transaction type
    const defaults = TRANSACTION_DEFAULTS[selectedType];
    if (!defaults) {
        console.warn(`⚠️ No defaults found for transaction type: ${selectedType}`);
        return;
    }
    
    // Get country-specific or common defaults
    const countryDefaults = defaults[selectedCountry] || defaults.common;
    if (!countryDefaults) {
        console.warn(`⚠️ No defaults found for country: ${selectedCountry}`);
        return;
    }
    
    // Apply defaults
    if (countryDefaults.debit) {
        setAccount(debitAccountSelect, countryDefaults.debit, 'debit account', selectedCountry);
    }
    
    if (countryDefaults.credit) {
        setAccount(creditAccountSelect, countryDefaults.credit, 'credit account', selectedCountry);
    }
    
    if (countryDefaults.category) {
        setCategory(categorySelect, countryDefaults.category.pattern);
    }
    
    if (countryDefaults.fund !== undefined) {
        setFund(fundSelect, countryDefaults.fund?.pattern || null);
    }
}

/**
 * Handle transaction type change
 */
export function handleTransactionTypeChange() {
    const selectedType = document.getElementById('transaction_category')?.value;
    console.log('🚀 Transaction type changed to:', selectedType);
    
    // Get regular account sections
    const regularAccountSections = document.getElementById('regularAccountSections');
    
    // Get all required fields
    const regularDebitField = document.querySelector('select[name="regular_debit_account_id"]');
    const regularCreditField = document.querySelector('select[name="regular_credit_account_id"]');
    const regularPaymentMethodField = document.querySelector('select[name="payment_method"]');
    
    // Get sheet & worksheet elements
    const regularSheetWorksheet = document.getElementById('regular-sheet-worksheet');
    const regularSheetField = document.querySelector('select[name="sheet_id"]');
    const regularWorksheetField = document.querySelector('select[name="worksheet_name"]');
    
    // Show regular sections
    if (regularAccountSections) regularAccountSections.style.display = 'block';
    if (regularSheetWorksheet) regularSheetWorksheet.style.display = 'block';
    
    // Add required attributes
    if (regularDebitField) regularDebitField.setAttribute('required', 'required');
    if (regularCreditField) regularCreditField.setAttribute('required', 'required');
    if (regularPaymentMethodField) regularPaymentMethodField.setAttribute('required', 'required');
    if (regularSheetField) regularSheetField.setAttribute('required', 'required');
    if (regularWorksheetField) regularWorksheetField.setAttribute('required', 'required');
    
    console.log('✅ Required attributes updated for regular transactions');
    
    // Apply transaction-specific defaults
    if (selectedType) {
        applyTransactionDefaults(selectedType);
    }
}

/**
 * Force apply transaction defaults - can be called manually
 */
export function forceApplyTransactionDefaults() {
    const transactionSelect = document.getElementById('transaction_category');
    if (transactionSelect) {
        console.log('🔄 Force applying transaction defaults...');
        applyTransactionDefaults(transactionSelect.value);
    }
}

