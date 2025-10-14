/**
 * NGO Accounting System - Main Application Entry Point
 * Orchestrates all modules and initializes the application
 */

// Import services
import { generateTransactionNumber } from './services/transactionNumberService.js';
import { 
    initializeNavigation, 
    setupFormMonitoring, 
    initializeSectionNavigation 
} from './services/navigationService.js';
import { 
    handleTransactionTypeChange, 
    forceApplyTransactionDefaults 
} from './services/transactionDefaultsService.js';
import { loadWorksheets } from './services/worksheetService.js';
import { 
    setupDragAndDrop, 
    uploadBills, 
    uploadRedBills, 
    uploadDocumentation 
} from './services/fileUploadService.js';
import { setupDateInputHandlers } from './services/dateService.js';
import { showTemporaryMessage } from './services/uiService.js';
import { handleFormSubmit } from './services/formSubmissionService.js';
import { initializeChatbot } from './services/chatbotService.js';
import { initializeSearch } from './services/searchService.js';
import { initializeUpdateForm } from './services/updateFormService.js';
import { initializeCountrySelection } from './services/countrySelectionService.js';
import { initializeGoogleDriveService } from './services/googleDriveService.js';

/**
 * Apply fund colors to option elements
 */
function applyFundColors() {
    const fundSelect = document.querySelector('select[name="fund_id"]');
    if (fundSelect) {
        const options = fundSelect.querySelectorAll('option[data-color]');
        options.forEach(option => {
            const color = option.getAttribute('data-color');
            if (color) {
                option.style.backgroundColor = color;
                option.style.color = 'white';
            }
        });
    }
}

/**
 * Auto-select default fund if none is selected
 */
function autoSelectDefaultFund() {
    const fundSelect = document.querySelector('select[name="fund_id"]');
    if (fundSelect && fundSelect.value === '') {
        // Look for the default fund option (marked as selected in HTML)
        const defaultOption = fundSelect.querySelector('option[selected]');
        if (defaultOption && defaultOption.value !== '') {
            fundSelect.value = defaultOption.value;
            console.log('✅ Auto-selected default fund:', defaultOption.textContent);
        }
    }
}

/**
 * Initialize the application when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing NGO Accounting System...');
    
    // Generate initial transaction number
    generateTransactionNumber();
    
    // Debug: Check if categories are loaded
    const categorySelect = document.getElementById('category_id');
    if (categorySelect) {
        console.log('Category select found, options:', categorySelect.options.length);
    }
    
    // Auto-select default sheet and load its worksheets
    const sheetSelect = document.getElementById('sheet_select');
    const defaultOption = sheetSelect.querySelector('option[selected]');
    if (defaultOption) {
        sheetSelect.value = defaultOption.value;
        loadWorksheets();
    }
    
    // Apply default settings for the pre-selected transaction type
    // Wait for accounts to be loaded before applying defaults
    setTimeout(function() {
        const transactionSelect = document.getElementById('transaction_category');
        const debitAccountSelect = document.querySelector('select[name="regular_debit_account_id"]');
        
        if (transactionSelect && debitAccountSelect && debitAccountSelect.options.length > 1) {
            console.log('✅ Accounts loaded, applying transaction defaults...');
            handleTransactionTypeChange();
        } else {
            console.log('⏳ Accounts not ready yet, retrying in 500ms...');
            // Retry after another 500ms if accounts aren't ready
            setTimeout(function() {
                if (transactionSelect) {
                    console.log('🔄 Retrying to apply transaction defaults...');
                    handleTransactionTypeChange();
                }
            }, 500);
        }
    }, 1000);
    
    // Initialize professional section navigation
    initializeSectionNavigation();
    
    // Initialize navigation panel
    initializeNavigation();
    
    // Initialize drag and drop functionality
    setupDragAndDrop();
    console.log('Drag and drop functionality initialized');
    
    // Initialize form monitoring for navigation progress
    setupFormMonitoring();
    console.log('Form progress monitoring initialized');
    
    // Add form submission event listener
    const mainForm = document.getElementById('mainForm');
    if (mainForm) {
        mainForm.addEventListener('submit', handleFormSubmit);
        console.log('✅ Form submission event listener attached');
    } else {
        console.error('❌ mainForm not found - form submission will not work!');
    }
    
    // Add event listeners for all upload buttons
    const billsUploadBtn = document.getElementById('billsUploadBtn');
    if (billsUploadBtn) {
        billsUploadBtn.addEventListener('click', uploadBills);
    }
    
    const redBillsUploadBtn = document.getElementById('redBillsUploadBtn');
    if (redBillsUploadBtn) {
        redBillsUploadBtn.addEventListener('click', uploadRedBills);
    }
    
    const documentationUploadBtn = document.getElementById('documentationUploadBtn');
    if (documentationUploadBtn) {
        documentationUploadBtn.addEventListener('click', uploadDocumentation);
    }
    
    // Add event listener for submit button in navigation
    const submitNavBtn = document.getElementById('submitNavBtn');
    if (submitNavBtn) {
        submitNavBtn.addEventListener('click', function(e) {
            e.preventDefault();
            // Trigger the form submission using the same handler
            const form = document.getElementById('mainForm');
            if (form) {
                const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
                form.dispatchEvent(submitEvent);
            }
        });
    }
    
    // Apply fund colors
    applyFundColors();
    
    // Auto-select default fund
    autoSelectDefaultFund();
    
    // Re-apply colors when funds are refreshed
    const originalRefreshFormData = window.refreshFormData;
    if (originalRefreshFormData) {
        window.refreshFormData = function() {
            const result = originalRefreshFormData.apply(this, arguments);
            setTimeout(applyFundColors, 100);
            setTimeout(autoSelectDefaultFund, 100);
            return result;
        };
    }

    // Setup date input handlers
    setupDateInputHandlers('date_input', showTemporaryMessage);
    
    // Initialize chatbot
    initializeChatbot();
    
    // Initialize search functionality
    initializeSearch();
    
    // Initialize update form functionality
    initializeUpdateForm();
    
    // Initialize country selection
    initializeCountrySelection();
    
    // Initialize Google Drive service
    initializeGoogleDriveService();
    
    console.log('NGO Accounting System initialized successfully! 🚀');
});

// Export for debugging
window.forceApplyTransactionDefaults = forceApplyTransactionDefaults;

