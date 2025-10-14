/**
 * Country Selection Service
 * Handles country switching and related UI updates
 */

import { generateTransactionNumber, regenerateTransactionNumberForCountry } from './transactionNumberService.js';
import { applyTransactionDefaults } from './transactionDefaultsService.js';
import { loadWorksheets } from './worksheetService.js';

/**
 * Update Quick Access panel visibility based on country
 */
function updateQuickAccessVisibility(countryCode) {
    const beElements = document.querySelectorAll('.access-link-be, .access-link-bills-be, .access-link-bank-statement-be, .access-link-documentation-be');
    const vnElements = document.querySelectorAll('.access-link-vn, .access-link-bills-vn, .access-link-red-bills-vn, .access-link-bank-statement-vn, .access-link-documentation-vn');
    
    if (countryCode === 'BE') {
        beElements.forEach(el => el.style.display = 'block');
        vnElements.forEach(el => el.style.display = 'none');
    } else {
        beElements.forEach(el => el.style.display = 'none');
        vnElements.forEach(el => el.style.display = 'block');
    }
}

/**
 * Update document type dropdown for country-specific options
 */
function updateDocumentTypeDropdown(countryCode) {
    const documentTypeDropdown = document.getElementById('documentTypeDropdown');
    const documentTypeSelect = document.getElementById('documentTypeSelect');
    
    if (documentTypeDropdown) {
        updateDropdownOptions(documentTypeDropdown, countryCode, 'redBills');
    }
    
    if (documentTypeSelect) {
        updateDropdownOptions(documentTypeSelect, countryCode, 'redBill');
    }
}

/**
 * Update dropdown options to show/hide Red Bills based on country
 */
function updateDropdownOptions(dropdown, countryCode, redBillsValue) {
    const allOptions = dropdown.querySelectorAll('option');
    
    const redBillsOption = Array.from(allOptions).find(option => 
        option.value === redBillsValue || 
        option.textContent.includes('Red Bill')
    );
    
    if (redBillsOption) {
        if (countryCode === 'BE') {
            // Belgium doesn't have red bills - hide the option
            redBillsOption.style.display = 'none';
        } else if (countryCode === 'VN') {
            // Vietnam has red bills - show the option
            redBillsOption.style.display = 'block';
        }
    }
}

/**
 * Update sheet selection based on country
 */
function updateSheetSelection(countryInfo) {
    console.log(`Updating sheet selection for ${countryInfo.name}`);
    
    const sheetSelect = document.getElementById('sheet_select');
    const worksheetSelect = document.getElementById('worksheet_select');
    
    if (sheetSelect) {
        // Find and select the country-specific sheet
        let foundSheet = false;
        
        // Try exact match first
        for (let option of sheetSelect.options) {
            if (option.textContent.trim() === countryInfo.sheet_name.trim()) {
                sheetSelect.value = option.value;
                foundSheet = true;
                break;
            }
        }
        
        // Try partial match if exact match fails
        if (!foundSheet) {
            for (let option of sheetSelect.options) {
                if (option.textContent.includes(countryInfo.sheet_name) || 
                    countryInfo.sheet_name.includes(option.textContent.trim())) {
                    sheetSelect.value = option.value;
                    foundSheet = true;
                    break;
                }
            }
        }
        
        if (foundSheet) {
            console.log(`✅ Sheet selected: ${sheetSelect.options[sheetSelect.selectedIndex].textContent}`);
            
            // Load worksheets for the selected sheet
            loadWorksheets();
            
            // Wait for worksheets to load then select the default worksheet
            setTimeout(() => {
                if (worksheetSelect) {
                    for (let option of worksheetSelect.options) {
                        if (option.textContent.trim() === countryInfo.worksheet_name.trim() ||
                            option.textContent.includes('Master Ledger')) {
                            worksheetSelect.value = option.value;
                            console.log(`✅ Worksheet selected: ${option.textContent}`);
                            break;
                        }
                    }
                }
            }, 500);
        } else {
            console.warn(`⚠️ Could not find sheet: ${countryInfo.sheet_name}`);
        }
    }
}

/**
 * Update account dropdowns with new accounts data
 */
function updateAccountDropdowns(accounts) {
    const debitSelect = document.querySelector('select[name="regular_debit_account_id"]');
    const creditSelect = document.querySelector('select[name="regular_credit_account_id"]');
    
    if (debitSelect) {
        const currentValue = debitSelect.value;
        debitSelect.innerHTML = '<option value="">Choose an account...</option>';
        
        accounts.forEach(account => {
            const option = document.createElement('option');
            option.value = account.code;
            option.textContent = account.name;
            debitSelect.appendChild(option);
        });
        
        // Try to restore previous selection
        if (currentValue) {
            debitSelect.value = currentValue;
        }
    }
    
    if (creditSelect) {
        const currentValue = creditSelect.value;
        creditSelect.innerHTML = '<option value="">Choose an account...</option>';
        
        accounts.forEach(account => {
            const option = document.createElement('option');
            option.value = account.code;
            option.textContent = account.name;
            creditSelect.appendChild(option);
        });
        
        // Try to restore previous selection
        if (currentValue) {
            creditSelect.value = currentValue;
        }
    }
}

/**
 * Update accounts data
 */
function updateAccountsData(accounts) {
    console.log('Updating accounts data:', accounts);
    updateAccountDropdowns(accounts);
}

/**
 * Select country and update all related UI elements
 */
export function selectCountry(countryCode) {
    console.log(`Selecting country: ${countryCode}`);
    
    // Check if sheet dropdown is populated
    const sheetSelect = document.getElementById('sheet_select');
    if (!sheetSelect || sheetSelect.options.length <= 1) {
        console.log('Sheet dropdown not ready, waiting...');
        setTimeout(() => selectCountry(countryCode), 1000);
        return;
    }
    
    // Show loading state
    const countrySelect = document.getElementById('countrySelect');
    if (countrySelect) {
        countrySelect.disabled = true;
    }
    
    // Call API to select country
    fetch('/api/select_country', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            country_code: countryCode
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log(`Country switched to ${data.country.name}`);
            
            // Update sheet and worksheet dropdowns
            updateSheetSelection(data.country);
            
            // Update accounts data
            updateAccountsData(data.accounts);
            
            // Update Quick Access panel visibility
            updateQuickAccessVisibility(countryCode);
            
            // Update document type dropdown
            updateDocumentTypeDropdown(countryCode);
            
            // Store country in sessionStorage
            sessionStorage.setItem('selectedCountry', countryCode);
            
            // Regenerate transaction number with new country prefix
            setTimeout(() => {
                regenerateTransactionNumberForCountry();
                console.log(`Transaction number regenerated for ${countryCode}`);
            }, 100);
            
            // Re-apply transaction defaults for the new country
            setTimeout(() => {
                const transactionSelect = document.getElementById('transaction_category');
                if (transactionSelect && transactionSelect.value) {
                    console.log(`Re-applying transaction defaults for ${countryCode}...`);
                    applyTransactionDefaults(transactionSelect.value);
                }
            }, 500);
            
            console.log('Country selection completed successfully');
        } else {
            console.error('Error selecting country:', data.error);
            alert(`Error switching country: ${data.error}`);
        }
    })
    .catch(error => {
        console.error('Error selecting country:', error);
        alert(`Error switching country: ${error.message}`);
    })
    .finally(() => {
        // Re-enable country selector
        if (countrySelect) {
            countrySelect.disabled = false;
        }
    });
}

/**
 * Initialize country selection
 */
export function initializeCountrySelection() {
    // Set default country to Belgium
    const countrySelect = document.getElementById('countrySelect');
    if (countrySelect) {
        countrySelect.value = 'BE'; // Default to Belgium
        
        // Add change event listener
        countrySelect.addEventListener('change', function() {
            const selectedCountry = this.value;
            console.log(`Country changed to: ${selectedCountry}`);
            
            // Immediately update sessionStorage and regenerate transaction number
            sessionStorage.setItem('selectedCountry', selectedCountry);
            
            // Call the full country selection process
            selectCountry(selectedCountry);
        });
        
        // Wait for sheets to be loaded before selecting country
        setTimeout(() => {
            console.log('Initializing country selection after sheets are loaded');
            selectCountry('BE');
            
            // Also update Quick Access visibility on page load
            updateQuickAccessVisibility('BE');
            
            // Update document type dropdown on page load
            updateDocumentTypeDropdown('BE');
            
            // Apply transaction defaults on page load
            setTimeout(() => {
                const transactionSelect = document.getElementById('transaction_category');
                if (transactionSelect && transactionSelect.value) {
                    console.log('Applying initial transaction defaults for BE...');
                    applyTransactionDefaults(transactionSelect.value);
                }
            }, 1000);
        }, 2000); // Wait 2 seconds for sheets to load
    }
    
    console.log('✅ Country selection service initialized');
}

// Expose to global scope for compatibility
window.selectCountry = selectCountry;
window.initializeCountrySelection = initializeCountrySelection;

