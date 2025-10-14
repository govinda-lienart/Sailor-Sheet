/**
 * Form State Service
 * Handles saving and restoring form state using session storage
 */

import { applyTransactionDefaults } from './transactionDefaultsService.js';

/**
 * Save form state to session storage
 */
export function saveFormState() {
    try {
        const formState = {
            sheetId: document.getElementById('sheet_select')?.value,
            worksheetId: document.getElementById('worksheet_select')?.value,
            transactionType: document.getElementById('transaction_category')?.value,
            fundId: document.querySelector('select[name="fund_id"]')?.value,
            categoryId: document.querySelector('select[name="category_id"]')?.value,
            subCategoryId: document.querySelector('select[name="sub_category_id"]')?.value,
            debitAccountId: document.querySelector('select[name="regular_debit_account_id"]')?.value,
            creditAccountId: document.querySelector('select[name="regular_credit_account_id"]')?.value,
            paymentMethod: document.getElementById('payment_method')?.value
            // Note: dateInput intentionally excluded - always starts fresh
        };
        
        sessionStorage.setItem('sailorSheetFormState', JSON.stringify(formState));
        console.log('💾 Form state saved to session (excluding date):', formState);
    } catch (e) {
        console.error('❌ Error saving form state:', e);
    }
}

/**
 * Restore form state from session storage
 */
export function restoreFormState() {
    try {
        const savedState = sessionStorage.getItem('sailorSheetFormState');
        if (!savedState) {
            console.log('📂 No saved form state found');
            return;
        }
        
        const formState = JSON.parse(savedState);
        console.log('📂 Restoring form state from session:', formState);
        
        // Restore sheet selection
        if (formState.sheetId) {
            const sheetSelect = document.getElementById('sheet_select');
            if (sheetSelect) sheetSelect.value = formState.sheetId;
        }
        
        // Restore worksheet (will be set after loadWorksheets completes)
        if (formState.worksheetId) {
            const worksheetSelect = document.getElementById('worksheet_select');
            if (worksheetSelect) worksheetSelect.value = formState.worksheetId;
        }
        
        // Restore transaction type
        if (formState.transactionType) {
            const transactionSelect = document.getElementById('transaction_category');
            if (transactionSelect) {
                transactionSelect.value = formState.transactionType;
                applyTransactionDefaults(formState.transactionType);
            }
        }
        
        // Restore fund
        if (formState.fundId) {
            const fundSelect = document.querySelector('select[name="fund_id"]');
            if (fundSelect) fundSelect.value = formState.fundId;
        }
        
        // Restore category
        if (formState.categoryId) {
            const categorySelect = document.querySelector('select[name="category_id"]');
            if (categorySelect) categorySelect.value = formState.categoryId;
        }
        
        // Restore sub-category
        if (formState.subCategoryId) {
            const subCategorySelect = document.querySelector('select[name="sub_category_id"]');
            if (subCategorySelect) subCategorySelect.value = formState.subCategoryId;
        }
        
        // Restore debit account
        if (formState.debitAccountId) {
            const debitSelect = document.querySelector('select[name="regular_debit_account_id"]');
            if (debitSelect) debitSelect.value = formState.debitAccountId;
        }
        
        // Restore credit account
        if (formState.creditAccountId) {
            const creditSelect = document.querySelector('select[name="regular_credit_account_id"]');
            if (creditSelect) creditSelect.value = formState.creditAccountId;
        }
        
        // Restore payment method
        if (formState.paymentMethod) {
            const paymentSelect = document.getElementById('payment_method');
            if (paymentSelect) paymentSelect.value = formState.paymentMethod;
        }
        
        // Note: Date is intentionally NOT restored - always starts fresh
        
        console.log('✅ Form state restored successfully (date field left fresh)');
    } catch (e) {
        console.error('❌ Error restoring form state:', e);
    }
}

