// Country Selection Module - Handles country-specific functionality and UI updates
// Extracted from inline script - Step 9 of incremental refactoring

(function() {
    'use strict';
    
    // Helper function to update dropdown options based on country
    function updateDropdownOptions(dropdown, countryCode, redBillsValue) {
        console.log(`DEBUG: Updating dropdown ${dropdown.id} for country: ${countryCode}`);
        console.log(`DEBUG: Looking for redBillsValue: ${redBillsValue}`);
        
        // Get all options
        const allOptions = dropdown.querySelectorAll('option');
        console.log(`DEBUG: Found ${allOptions.length} options in ${dropdown.id}`);
        
        // Log all options for debugging
        allOptions.forEach((option, index) => {
            console.log(`DEBUG: Option ${index}: value="${option.value}", text="${option.textContent.trim()}"`);
        });
        
        const redBillsOption = Array.from(allOptions).find(option => 
            option.value === redBillsValue || 
            option.textContent.includes('Red Bill') || 
            option.textContent.includes('Red Bill (Special Invoice)')
        );
        
        if (redBillsOption) {
            console.log(`DEBUG: Found Red Bills option: value="${redBillsOption.value}", text="${redBillsOption.textContent.trim()}"`);
            if (countryCode === 'BE') {
                // Belgium doesn't have red bills - hide the option
                redBillsOption.style.display = 'none';
                console.log(`DEBUG: Hidden Red Bills option for Belgium in ${dropdown.id}`);
            } else if (countryCode === 'VN') {
                // Vietnam has red bills - show the option
                redBillsOption.style.display = 'block';
                console.log(`DEBUG: Shown Red Bills option for Vietnam in ${dropdown.id}`);
            }
        } else {
            console.log(`DEBUG: Red Bills option not found in dropdown ${dropdown.id}`);
            console.log(`DEBUG: Searched for value="${redBillsValue}" and text containing "Red Bill"`);
        }
        
        // Update the dropdown to reflect country-specific document types
        console.log(`DEBUG: Dropdown ${dropdown.id} updated for ${countryCode}`);
        console.log(`DEBUG: Available document types for ${countryCode}:`, 
            Array.from(allOptions)
                .filter(option => option.style.display !== 'none' && option.value !== '')
                .map(option => option.textContent.trim())
        );
    }
    
    // Update document type dropdown based on country
    function updateDocumentTypeDropdown(countryCode) {
        console.log(`DEBUG: Updating document type dropdown for country: ${countryCode}`);
        
        // Update both dropdowns: main form and update form
        const documentTypeDropdown = document.getElementById('documentTypeDropdown');
        const documentTypeSelect = document.getElementById('documentTypeSelect');
        
        // Update main form dropdown
        if (documentTypeDropdown) {
            updateDropdownOptions(documentTypeDropdown, countryCode, 'redBills');
        }
        
        // Update update form dropdown
        if (documentTypeSelect) {
            updateDropdownOptions(documentTypeSelect, countryCode, 'redBill');
        }
    }
    
    // Force update of document type dropdowns (can be called manually)
    function forceUpdateDocumentTypeDropdowns() {
        const selectedCountry = sessionStorage.getItem('selectedCountry') || 'BE';
        console.log(`DEBUG: Force updating document type dropdowns for country: ${selectedCountry}`);
        updateDocumentTypeDropdown(selectedCountry);
    }
    
    // Update Quick Access panel visibility based on country
    function updateQuickAccessVisibility(countryCode) {
        console.log(`DEBUG: Updating Quick Access visibility for country: ${countryCode}`);
        
        // Get the Sheet Access elements
        const beMasterLedger = document.querySelector('.access-link-be');
        const vnMasterLedger = document.querySelector('.access-link-vn');
        
        // Get the Files Access elements
        const beFiles = document.querySelectorAll('.access-link-bills-be, .access-link-bank-statement-be, .access-link-documentation-be');
        const vnFiles = document.querySelectorAll('.access-link-bills-vn, .access-link-red-bills-vn, .access-link-bank-statement-vn, .access-link-documentation-vn');
        
        // Get the Update form search sheet dropdown
        const searchSheetDropdown = document.getElementById('searchSheet');
        
        console.log(`DEBUG: Found BE Master Ledger:`, beMasterLedger);
        console.log(`DEBUG: Found VN Master Ledger:`, vnMasterLedger);
        console.log(`DEBUG: Found BE Files:`, beFiles.length);
        console.log(`DEBUG: Found VN Files:`, vnFiles.length);
        console.log(`DEBUG: Found Search Sheet Dropdown:`, searchSheetDropdown);
        
        if (countryCode === 'BE') {
            // Show Belgium elements, hide Vietnam elements
            if (beMasterLedger) beMasterLedger.style.display = 'block';
            if (vnMasterLedger) vnMasterLedger.style.display = 'none';
            
            beFiles.forEach(file => file.style.display = 'block');
            vnFiles.forEach(file => file.style.display = 'none');
            
            // Update the search sheet dropdown to Belgium
            if (searchSheetDropdown) {
                searchSheetDropdown.value = 'be';
                console.log('DEBUG: Updated search sheet dropdown to Belgium');
            }
            
            console.log('DEBUG: Showing Belgium elements, hiding Vietnam elements');
        } else if (countryCode === 'VN') {
            // Show Vietnam elements, hide Belgium elements
            if (beMasterLedger) beMasterLedger.style.display = 'none';
            if (vnMasterLedger) vnMasterLedger.style.display = 'block';
            
            beFiles.forEach(file => file.style.display = 'none');
            vnFiles.forEach(file => file.style.display = 'block');
            
            // Update the search sheet dropdown to Vietnam
            if (searchSheetDropdown) {
                searchSheetDropdown.value = 'vn';
                console.log('DEBUG: Updated search sheet dropdown to Vietnam');
            }
            
            console.log('DEBUG: Showing Vietnam elements, hiding Belgium elements');
        }
    }
    
    // Update all account dropdowns with new account data
    function updateAccountDropdowns(accounts) {
        console.log(`DEBUG: Updating account dropdowns with ${accounts.length} accounts`);
        
        // List of all account dropdown selectors
        const accountSelectors = [
            'select[name="regular_debit_account_id"]',
            'select[name="regular_credit_account_id"]',
            'select[name="master_ledger_a_debit_account_id"]',
            'select[name="master_ledger_a_credit_account_id"]',
            'select[name="master_ledger_b_debit_account_id"]',
            'select[name="master_ledger_b_credit_account_id"]'
        ];
        
        accountSelectors.forEach(selector => {
            const dropdown = document.querySelector(selector);
            if (dropdown) {
                console.log(`DEBUG: Updating dropdown: ${selector}`);
                
                // Clear existing options (except the first placeholder)
                const placeholder = dropdown.querySelector('option[value=""]');
                dropdown.innerHTML = '';
                if (placeholder) {
                    dropdown.appendChild(placeholder);
                }
                
                // Add new account options
                accounts.forEach(account => {
                    if (account.active !== false) { // Only add active accounts
                        const option = document.createElement('option');
                        option.value = account.code;
                        option.textContent = `${account.name} (${account.type})`;
                        dropdown.appendChild(option);
                    }
                });
                
                console.log(`DEBUG: Added ${accounts.length} options to ${selector}`);
            } else {
                console.log(`DEBUG: Dropdown not found: ${selector}`);
            }
        });
    }
    
    // Update accounts data based on country
    function updateAccountsData(accounts) {
        console.log(`DEBUG: Updating accounts data with ${accounts.length} accounts`);
        // Store accounts for later use
        window.currentAccounts = accounts;
        
        // Update all account dropdowns
        updateAccountDropdowns(accounts);
    }
    
    // Update sheet and worksheet selection based on country
    function updateSheetSelection(countryInfo) {
        console.log(`DEBUG: Updating sheet selection for ${countryInfo.name}`);
        console.log(`DEBUG: Looking for sheet: ${countryInfo.sheet_name}`);
        console.log(`DEBUG: Looking for worksheet: ${countryInfo.worksheet_name}`);
        
        const sheetSelect = document.getElementById('sheet_select');
        const worksheetSelect = document.getElementById('worksheet_select');
        
        if (sheetSelect) {
            console.log(`DEBUG: Available sheet options:`);
            for (let option of sheetSelect.options) {
                console.log(`  - ${option.value}: ${option.textContent}`);
            }
            
            // Find and select the country-specific sheet
            let foundSheet = false;
            
            // First try exact match
            for (let option of sheetSelect.options) {
                if (option.textContent.trim() === countryInfo.sheet_name.trim()) {
                    console.log(`DEBUG: Found exact match: ${option.textContent}`);
                    sheetSelect.value = option.value;
                    foundSheet = true;
                    break;
                }
            }
            
            // If no exact match, try partial match
            if (!foundSheet) {
                console.log(`DEBUG: No exact match found, trying partial match`);
                for (let option of sheetSelect.options) {
                    if (option.textContent.includes(countryInfo.sheet_name) || 
                        countryInfo.sheet_name.includes(option.textContent)) {
                        console.log(`DEBUG: Found partial match: ${option.textContent}`);
                        sheetSelect.value = option.value;
                        foundSheet = true;
                        break;
                    }
                }
            }
            
            // If still no match, try case-insensitive match
            if (!foundSheet) {
                console.log(`DEBUG: No partial match found, trying case-insensitive match`);
                const searchName = countryInfo.sheet_name.toLowerCase();
                for (let option of sheetSelect.options) {
                    if (option.textContent.toLowerCase().includes(searchName) || 
                        searchName.includes(option.textContent.toLowerCase())) {
                        console.log(`DEBUG: Found case-insensitive match: ${option.textContent}`);
                        sheetSelect.value = option.value;
                        foundSheet = true;
                        break;
                    }
                }
            }
            
            if (foundSheet) {
                console.log(`DEBUG: Sheet selected: ${sheetSelect.value}`);
                
                // Trigger sheet change to load worksheets
                const event = new Event('change');
                sheetSelect.dispatchEvent(event);
                
                // After worksheets are loaded, select the country-specific worksheet
                setTimeout(() => {
                    console.log(`DEBUG: Looking for worksheet: ${countryInfo.worksheet_name}`);
                    if (worksheetSelect) {
                        console.log(`DEBUG: Available worksheet options:`);
                        for (let option of worksheetSelect.options) {
                            console.log(`  - ${option.value}: ${option.textContent}`);
                        }
                        
                        let foundWorksheet = false;
                        
                        // First try exact match
                        for (let option of worksheetSelect.options) {
                            if (option.textContent.trim() === countryInfo.worksheet_name.trim()) {
                                console.log(`DEBUG: Found exact worksheet match: ${option.textContent}`);
                                worksheetSelect.value = option.value;
                                foundWorksheet = true;
                                break;
                            }
                        }
                        
                        // If no exact match, try partial match
                        if (!foundWorksheet) {
                            console.log(`DEBUG: No exact worksheet match, trying partial match`);
                            for (let option of worksheetSelect.options) {
                                if (option.textContent.includes(countryInfo.worksheet_name) || 
                                    countryInfo.worksheet_name.includes(option.textContent)) {
                                    console.log(`DEBUG: Found partial worksheet match: ${option.textContent}`);
                                    worksheetSelect.value = option.value;
                                    foundWorksheet = true;
                                    break;
                                }
                            }
                        }
                        
                        // If still no match, try case-insensitive match
                        if (!foundWorksheet) {
                            console.log(`DEBUG: No partial worksheet match, trying case-insensitive match`);
                            const searchWorksheet = countryInfo.worksheet_name.toLowerCase();
                            for (let option of worksheetSelect.options) {
                                if (option.textContent.toLowerCase().includes(searchWorksheet) || 
                                    searchWorksheet.includes(option.textContent.toLowerCase())) {
                                    console.log(`DEBUG: Found case-insensitive worksheet match: ${option.textContent}`);
                                    worksheetSelect.value = option.value;
                                    foundWorksheet = true;
                                    break;
                                }
                            }
                        }
                        
                        if (!foundWorksheet) {
                            console.log(`DEBUG: No worksheet match found for: ${countryInfo.worksheet_name}`);
                        }
                    }
                }, 1000); // Increased timeout to ensure worksheets are loaded
            } else {
                console.log(`DEBUG: No sheet match found for: ${countryInfo.sheet_name}`);
            }
        }
    }
    
    // Handle country selection
    function selectCountry(countryCode) {
        console.log(`DEBUG: Selecting country: ${countryCode}`);
        
        // Check if sheet dropdown is populated
        const sheetSelect = document.getElementById('sheet_select');
        if (!sheetSelect || sheetSelect.options.length <= 1) {
            console.log('DEBUG: Sheet dropdown not ready, waiting...');
            setTimeout(() => {
                selectCountry(countryCode);
            }, 1000);
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
                console.log(`DEBUG: Country switched to ${data.country.name}`);
                
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
                console.log(`DEBUG: Stored country ${countryCode} in sessionStorage`);
                
                // Regenerate transaction number with new country prefix
                console.log(`DEBUG: About to regenerate transaction number for country: ${countryCode}`);
                
                // Use setTimeout to ensure sessionStorage is properly set
                setTimeout(() => {
                    if (typeof window.regenerateTransactionNumberForCountry === 'function') {
                        window.regenerateTransactionNumberForCountry();
                        console.log(`DEBUG: Transaction number regeneration called for ${countryCode}`);
                    } else {
                        console.error('DEBUG: regenerateTransactionNumberForCountry function not found');
                        // Fallback: call generateTransactionNumber directly
                        if (typeof window.generateTransactionNumber === 'function') {
                            window.generateTransactionNumber();
                        }
                    }
                }, 100);
                
                // Re-apply transaction defaults for the new country
                setTimeout(() => {
                    const transactionSelect = document.getElementById('transaction_category');
                    if (transactionSelect && transactionSelect.value) {
                        console.log(`🔄 Re-applying transaction defaults for ${countryCode}...`);
                        if (typeof window.applyTransactionDefaults === 'function') {
                            window.applyTransactionDefaults(transactionSelect.value);
                        }
                    }
                }, 500);
                
                console.log('DEBUG: Country selection completed successfully');
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
    
    // Initialize country selection on page load
    function initializeCountrySelection() {
        // Set default country to Belgium
        const countrySelect = document.getElementById('countrySelect');
        if (countrySelect) {
            countrySelect.value = 'BE'; // Default to Belgium
            
            // Wait for sheets to be loaded before selecting country
            setTimeout(() => {
                console.log('DEBUG: Initializing country selection after sheets are loaded');
                selectCountry('BE');
                
                // Also update Quick Access visibility on page load
                updateQuickAccessVisibility('BE');
                
                // Update document type dropdown on page load
                updateDocumentTypeDropdown('BE');
                
                // Apply transaction defaults on page load
                setTimeout(() => {
                    const transactionSelect = document.getElementById('transaction_category');
                    if (transactionSelect && transactionSelect.value) {
                        console.log('🔄 Applying initial transaction defaults for BE...');
                        if (typeof window.applyTransactionDefaults === 'function') {
                            window.applyTransactionDefaults(transactionSelect.value);
                        }
                    }
                }, 1000);
            }, 2000); // Wait 2 seconds for sheets to load
        }
    }
    
    // Set up event listeners when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        // Apply country filtering immediately on page load
        console.log('DEBUG: DOMContentLoaded - applying initial country filtering');
        forceUpdateDocumentTypeDropdowns();
        
        // Country selection functionality
        const countrySelect = document.getElementById('countrySelect');
        if (countrySelect) {
            countrySelect.addEventListener('change', function() {
                const selectedCountry = this.value;
                console.log(`DEBUG: Country changed to: ${selectedCountry}`);
                
                // Immediately update sessionStorage and regenerate transaction number
                sessionStorage.setItem('selectedCountry', selectedCountry);
                console.log(`DEBUG: Immediately regenerating transaction number for ${selectedCountry}`);
                
                // Call the transaction number generation directly
                setTimeout(() => {
                    if (typeof window.generateTransactionNumber === 'function') {
                        window.generateTransactionNumber();
                    }
                }, 50);
                
                // Then call the full country selection process
                selectCountry(selectedCountry);
            });
        }
        
        // Initialize country selection on page load
        initializeCountrySelection();
    });
    
    // Expose functions to global scope for use by other modules
    window.updateDocumentTypeDropdown = updateDocumentTypeDropdown;
    window.forceUpdateDocumentTypeDropdowns = forceUpdateDocumentTypeDropdowns;
    window.selectCountry = selectCountry;
    window.initializeCountrySelection = initializeCountrySelection;
    window.updateQuickAccessVisibility = updateQuickAccessVisibility;
    
    console.log('✅ Country selection module initialized');
    
})();

