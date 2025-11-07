/**
 * Form Submission Service
 * Handles form submission and API communication
 */

import { showSuccessMessage, showErrorMessage } from './uiService.js';
import { saveFormState, restoreFormState } from './formStateService.js';
import { resetUploadState } from './fileUploadService.js';
import { generateTransactionNumber } from './transactionNumberService.js';
import { handleTransactionTypeChange } from './transactionDefaultsService.js';
import { loadWorksheets } from './worksheetService.js';
import { clearManualCheckmarks, setupManualNavigationTracking } from './navigationService.js';

let isSubmitting = false; // Flag to prevent duplicate submissions

/**
 * Handle form submission
 */
export function handleFormSubmit(event) {
    console.log('✅ handleFormSubmit called - Form submission started');
    
    // Prevent default form submission
    event.preventDefault();
    
    // Check if already submitting
    if (isSubmitting) {
        console.log('⚠️ Already submitting, ignoring duplicate submission');
        return false;
    }
    
    console.log('🔓 Setting isSubmitting = true');
    isSubmitting = true;
    
    // Get form data
    const formData = new FormData(document.getElementById('mainForm'));
    
    console.log('Form data:');
    for (let [key, value] of formData.entries()) {
        console.log(`  ${key}: "${value}"`);
    }
    
    // Check if transaction number is generated
    const transactionNumber = document.getElementById('transactionNumberInput').value;
    console.log('Transaction number:', transactionNumber);
    
    if (!transactionNumber) {
        console.log('No transaction number found, generating one...');
        generateTransactionNumber();
    }
    
    // Disable submit button and show loading
    const submitBtn = document.querySelector('.enhanced-submit-btn');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '⏳ Submitting to Google Sheets...';
    
    // Submit via AJAX
    submitToGoogleSheets(formData);
    
    return false; // Prevent default form submission
}

/**
 * Submit form data to Google Sheets
 */
function submitToGoogleSheets(formData) {
    console.log('submitToGoogleSheets called');
    
    // Convert FormData to JSON
    const jsonData = {};
    for (let [key, value] of formData.entries()) {
        // Strip leading apostrophes from date_input (Excel uses ' to force text)
        if (key === 'date_input' && value) {
            value = value.trim().replace(/^'+/g, '');
        }
        jsonData[key] = value;
    }
    
    // Handle bank fee checkbox
    const bankFeeCheckbox = document.getElementById('include_bank_fees');
    jsonData['include_bank_fees'] = bankFeeCheckbox ? bankFeeCheckbox.checked : false;
    
    // Submit to Flask API
    fetch('/api/submit_transaction', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(jsonData)
    })
    .then(response => response.json())
    .then(data => {
        console.log('📨 Server response:', data);
        if (data.success) {
            showSuccessMessage('Successfully submitted to Google Sheet!');
            
            // Save form state before reset
            saveFormState();
            
            // Get current sheet and transaction type before reset
            const currentSheetId = document.getElementById('sheet_select')?.value;
            const currentTransactionType = document.getElementById('transaction_category')?.value;
            
            // Reset form
            const mainForm = document.getElementById('mainForm');
            mainForm.reset();
            
            // Re-attach form submission handler after reset
            mainForm.removeEventListener('submit', handleFormSubmit);
            mainForm.addEventListener('submit', handleFormSubmit);
            console.log('🔄 Form submission handler re-attached after reset');
            
            // Reset upload state
            resetUploadState();
            
            // Generate new transaction number
            generateTransactionNumber();
            
            // Re-apply transaction type defaults and restore saved state
            setTimeout(() => {
                const transactionSelect = document.getElementById('transaction_category');
                if (transactionSelect && currentTransactionType) {
                    transactionSelect.value = currentTransactionType;
                    handleTransactionTypeChange();
                }
                
                // Reload worksheets for the selected sheet
                const sheetSelect = document.getElementById('sheet_select');
                if (sheetSelect && currentSheetId) {
                    sheetSelect.value = currentSheetId;
                    loadWorksheets();
                }
                
                // Restore form state after reset
                setTimeout(() => {
                    restoreFormState();
                    // Clear manual checkmarks after form reset
                    clearManualCheckmarks();
                    setupManualNavigationTracking();
                }, 200); // Wait for worksheets to load
            }, 100);
        } else {
            showErrorMessage('❌ Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorMessage('❌ Network error: ' + error.message);
    })
    .finally(() => {
        // Re-enable submit button and reset submission flag
        const submitBtn = document.querySelector('.enhanced-submit-btn');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '🚀 Submit to Google Sheets';
        isSubmitting = false;
        console.log('🔓 Submission complete, isSubmitting = false');
    });
}

