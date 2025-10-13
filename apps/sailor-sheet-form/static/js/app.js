/**
 * NGO Accounting System - Main Application JavaScript
 * This file contains all the JavaScript functionality for the accounting form
 */

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Generate a unique transaction number based on current date/time and country
 * Format: COUNTRY-DDMMYY-HHMMSS (e.g., BE-081025-165528 or VN-081025-165528)
 */
function generateTransactionNumber() {
    const now = new Date();
    
    // Get current country from sessionStorage, default to BE
    const selectedCountry = sessionStorage.getItem('selectedCountry') || 'BE';
    const countryPrefix = selectedCountry.toUpperCase();
    
    // Generate timestamp part: DDMMYY-HHMMSS
    const timestamp = now.getDate().toString().padStart(2, '0') +
                     (now.getMonth() + 1).toString().padStart(2, '0') +
                     now.getFullYear().toString().slice(-2) + '-' +
                     now.getHours().toString().padStart(2, '0') +
                     now.getMinutes().toString().padStart(2, '0') +
                     now.getSeconds().toString().padStart(2, '0');
    
    // Combine country prefix with timestamp
    const transactionNumber = `${countryPrefix}-${timestamp}`;
    
    document.getElementById('transactionNumberDisplay').value = transactionNumber;
    document.getElementById('transactionNumberInput').value = transactionNumber;
    console.log(`Generated ${countryPrefix} transaction number:`, transactionNumber);
    return transactionNumber;
}

/**
 * Regenerate transaction number when country changes
 */
function regenerateTransactionNumberForCountry() {
    console.log('🔄 Regenerating transaction number for new country...');
    generateTransactionNumber();
}

/**
 * Smooth scroll to a specific section on the page
 */
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

/**
 * Prevent default drag and drop behaviors
 */
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// ============================================================================
// NAVIGATION FUNCTIONS
// ============================================================================

/**
 * Initialize navigation click handlers for smooth scrolling
 */
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            const sectionId = href.substring(1); // Remove the # symbol
            scrollToSection(sectionId);
        });
    });
}


/**
 * Update navigation button visual state based on completion
 */
function updateNavButtonState(navButton, isCompleted) {
    if (isCompleted) {
        // Completed state: Full vibrant blue
        navButton.style.borderLeft = '4px solid #007bff';
        navButton.style.backgroundColor = '#f0f8ff';
        navButton.style.color = '#0056b3';
        navButton.style.fontWeight = '600';
    } else {
        // Incomplete state: Light gray
        navButton.style.borderLeft = '4px solid #e9ecef';
        navButton.style.backgroundColor = '#f8f9fa';
        navButton.style.color = '#6c757d';
        navButton.style.fontWeight = '500';
    }
}

/**
 * Update navigation progress indicators
 */
function updateNavigationProgress() {
    const sections = [
        {
            id: 'transaction-number-section',
            navSelector: 'a[href="#transaction-number-section"]',
            validator: () => document.getElementById('transactionNumberDisplay').value !== 'Generating...' && document.getElementById('transactionNumberDisplay').value.length > 0
        },
        {
            id: 'transaction-type-section', 
            navSelector: 'a[href="#transaction-type-section"]',
            validator: () => document.querySelector('select[name="transaction_category"]').value !== ''
        },
        {
            id: 'sheet-worksheet-section',
            navSelector: 'a[href="#sheet-worksheet-section"]',
            validator: () => {
                const sheetId = document.querySelector('select[name="sheet_id"]')?.value;
                const worksheetName = document.querySelector('select[name="worksheet_name"]')?.value;
                return sheetId && worksheetName;
            }
        },
        {
            id: 'date-section',
            navSelector: 'a[href="#date-section"]', 
            validator: () => document.querySelector('input[name="date_input"]').value !== ''
        },
        {
            id: 'amount-section',
            navSelector: 'a[href="#amount-section"]',
            validator: () => {
                const amount = document.querySelector('input[name="amount"]').value;
                return amount !== '' && parseFloat(amount) > 0;
            }
        },
        {
            id: 'fund-section',
            navSelector: 'a[href="#fund-section"]',
            validator: () => document.querySelector('select[name="fund_id"]').value !== ''
        },
        {
            id: 'category-section',
            navSelector: 'a[href="#category-section"]',
            validator: () => document.querySelector('select[name="category_id"]').value !== ''
        },
        {
            id: 'debit-account-section',
            navSelector: 'a[href="#debit-account-section"]',
            validator: () => {
                const regularDebit = document.querySelector('select[name="regular_debit_account_id"]');
                const masterDebitA = document.querySelector('select[name="master_ledger_a_debit_account_id"]');
                if (regularDebit && regularDebit.hasAttribute('required')) return regularDebit.value !== '';
                if (masterDebitA && masterDebitA.hasAttribute('required')) return masterDebitA.value !== '';
                return true;
            }
        },
        {
            id: 'credit-account-section',
            navSelector: 'a[href="#credit-account-section"]',
            validator: () => {
                const regularCredit = document.querySelector('select[name="regular_credit_account_id"]');
                const masterCreditA = document.querySelector('select[name="master_ledger_a_credit_account_id"]');
                if (regularCredit && regularCredit.hasAttribute('required')) return regularCredit.value !== '';
                if (masterCreditA && masterCreditA.hasAttribute('required')) return masterCreditA.value !== '';
                return true;
            }
        },
        {
            id: 'payment-method-section',
            navSelector: 'a[href="#payment-method-section"]',
            validator: () => {
                const paymentMethod = document.querySelector('select[name="payment_method"]');
                if (paymentMethod && paymentMethod.hasAttribute('required')) return paymentMethod.value !== '';
                return true;
            }
        },
        {
            id: 'description-section',
            navSelector: 'a[href="#description-section"]',
            validator: () => document.querySelector('textarea[name="description"]').value.trim() !== ''
        }
    ];

    sections.forEach(section => {
        const navButton = document.querySelector(section.navSelector);
        if (!navButton) return;

        const isCompleted = section.validator();
        updateNavButtonState(navButton, isCompleted);
    });

    // Update overall progress
    const completedSections = sections.filter(section => section.validator()).length;
    const totalSections = sections.length;
    const progressPercentage = Math.round((completedSections / totalSections) * 100);
    
    console.log(`Form Progress: ${completedSections}/${totalSections} sections completed (${progressPercentage}%)`);
}

/**
 * Setup form monitoring for progress tracking
 */
function setupFormMonitoring() {
    // Monitor all form inputs for changes
    const formInputs = document.querySelectorAll('input, select, textarea');
    formInputs.forEach(input => {
        input.addEventListener('change', updateNavigationProgress);
        input.addEventListener('input', updateNavigationProgress);
    });

    // Initial progress check
    setTimeout(updateNavigationProgress, 1000);
    
    console.log('Form monitoring setup complete - navigation will update as you fill sections');
}

// ============================================================================
// TRANSACTION TYPE HANDLING
// ============================================================================

/**
 * Handle changes to transaction type - shows/hides relevant form sections
 */
function handleTransactionTypeChange() {
    const selectedType = document.getElementById('transaction_category').value;
    console.log('🚀 Transaction type changed to:', selectedType, '(using JSON data - no API calls!)');
    
    // Get regular account sections
    const regularAccountSections = document.getElementById('regularAccountSections');
    
    // Get all required fields for regular transactions
    const regularDebitField = document.querySelector('select[name="regular_debit_account_id"]');
    const regularCreditField = document.querySelector('select[name="regular_credit_account_id"]');
    const regularPaymentMethodField = document.querySelector('select[name="payment_method"]');
    
    // Get sheet & worksheet content elements
    const regularSheetWorksheet = document.getElementById('regular-sheet-worksheet');
    const regularSheetField = document.querySelector('select[name="sheet_id"]');
    const regularWorksheetField = document.querySelector('select[name="worksheet_name"]');
    
    // Show regular sections (always visible now)
    if (regularAccountSections) regularAccountSections.style.display = 'block';
    
    // Show regular sheet/worksheet content
    if (regularSheetWorksheet) regularSheetWorksheet.style.display = 'block';
    
    // Add required to regular fields
    if (regularDebitField) regularDebitField.setAttribute('required', 'required');
    if (regularCreditField) regularCreditField.setAttribute('required', 'required');
    if (regularPaymentMethodField) regularPaymentMethodField.setAttribute('required', 'required');
    if (regularSheetField) regularSheetField.setAttribute('required', 'required');
    if (regularWorksheetField) regularWorksheetField.setAttribute('required', 'required');
    
    console.log('✅ Showing regular account sections');
    console.log('✅ Required attributes updated for regular transactions');
    
    // Apply transaction type specific defaults immediately
    applyTransactionDefaults(selectedType);
}

// ============================================================================
// WORKSHEET AND SHEET MANAGEMENT
// ============================================================================



/**
 * Load worksheets for regular transactions
 */
function loadWorksheets() {
    console.log('loadWorksheets() called');
    const sheetSelect = document.getElementById('sheet_select');
    const worksheetSelect = document.getElementById('worksheet_select');
    const selectedSheetId = sheetSelect.value;
    console.log('Selected sheet ID:', selectedSheetId);

    worksheetSelect.innerHTML = '<option value="">Loading worksheets...</option>';
    worksheetSelect.disabled = true;

    if (!selectedSheetId) {
        worksheetSelect.innerHTML = '<option value="">First select a sheet...</option>';
        console.log('No sheet selected, returning');
        return;
    }

    console.log('Fetching worksheets for sheet:', selectedSheetId);
    fetch(`/api/get_worksheets/${selectedSheetId}`)
        .then(r => {
            console.log('Response status:', r.status);
            return r.json();
        })
        .then(data => {
            console.log('Worksheets data received:', data);
            worksheetSelect.innerHTML = '<option value="">Choose an account...</option>';
            
            if (data.length > 0) {
                data.forEach(ws => {
                    console.log('Adding worksheet:', ws);
                    const o = document.createElement('option');
                    o.value = ws.title;  // Use worksheet title for backend lookup
                    o.textContent = ws.title;  // Show just the worksheet title
                    worksheetSelect.appendChild(o);
                });
                worksheetSelect.disabled = false;
                console.log('Worksheets loaded successfully');
                
                // Auto-select "Master Ledger" if it exists
                const masterLedgerOption = Array.from(worksheetSelect.options).find(option => 
                    option.textContent.includes('Master Ledger')
                );
                if (masterLedgerOption) {
                    worksheetSelect.value = masterLedgerOption.value;
                    console.log('Auto-selected Master Ledger worksheet');
                }
                
                // Don't call handleTransactionTypeChange here - it will be called from DOMContentLoaded
                console.log('Worksheets loaded, transaction defaults will be applied from DOMContentLoaded');
            } else {
                worksheetSelect.innerHTML = '<option value="">No accounts found</option>';
                console.log('No worksheets found');
            }
        })
        .catch(error => {
            console.error('Error loading worksheets:', error);
            worksheetSelect.innerHTML = '<option value="">Error loading worksheets</option>';
        });
}

// ============================================================================
// TRANSACTION DEFAULTS
// ============================================================================

/**
 * Apply default values based on transaction type
 */
function applyTransactionDefaults(selectedType) {
    console.log(`🎯 Applying defaults for transaction type: ${selectedType}`);
    
    // Get the correct selectors based on transaction type
    let debitAccountSelect, creditAccountSelect;
    
    // For regular transactions, use the regular account fields
    debitAccountSelect = document.querySelector('select[name="regular_debit_account_id"]');
    creditAccountSelect = document.querySelector('select[name="regular_credit_account_id"]');
    
    const categorySelect = document.querySelector('select[name="category_id"]');
    const fundSelect = document.querySelector('select[name="fund_id"]');
    
    // Debug: Check if elements are found
    console.log(`🔍 Element availability check:`);
    console.log(`  - Debit Account Select: ${debitAccountSelect ? 'Found' : 'NOT FOUND'}`);
    console.log(`  - Credit Account Select: ${creditAccountSelect ? 'Found' : 'NOT FOUND'}`);
    console.log(`  - Category Select: ${categorySelect ? 'Found' : 'NOT FOUND'}`);
    console.log(`  - Fund Select: ${fundSelect ? 'Found' : 'NOT FOUND'}`);
    
    if (debitAccountSelect) {
        console.log(`  - Debit Account Options: ${debitAccountSelect.options.length}`);
    }
    if (creditAccountSelect) {
        console.log(`  - Credit Account Options: ${creditAccountSelect.options.length}`);
    }
    
    // Clear previous account/category/fund selections first, but preserve worksheet selections
    if (debitAccountSelect) debitAccountSelect.value = '';
    if (creditAccountSelect) creditAccountSelect.value = '';
    if (categorySelect) categorySelect.value = '';
    if (fundSelect) fundSelect.value = '';
    
    console.log('🧹 Cleared previous selections (keeping worksheet selections intact)');
    
    // Set default accounts and category based on transaction type
    if (selectedType === 'donation') {
        console.log('🔄 Applying donation defaults...');
        
        // Get current country from sessionStorage
        const selectedCountry = sessionStorage.getItem('selectedCountry') || 'BE';
        console.log(`🌍 Current country for donation: ${selectedCountry}`);
        
        if (selectedCountry === 'BE') {
            // For Belgium donations: Debit BE - Wallet Govinda Lienart (receiver), Credit BE - Revenues (source)
            if (debitAccountSelect) {
                let walletOption = Array.from(debitAccountSelect.options).find(option => 
                    option.textContent.trim() === 'BE - Wallet Govinda Lienart (Real Accounts)'
                );
                
                if (!walletOption) {
                    walletOption = Array.from(debitAccountSelect.options).find(option => 
                        option.textContent.toLowerCase().includes('be') && 
                        option.textContent.toLowerCase().includes('wallet') &&
                        option.textContent.toLowerCase().includes('govinda')
                    );
                }
                
                if (walletOption) {
                    debitAccountSelect.value = walletOption.value;
                    console.log('✅ Auto-selected BE - Wallet Govinda Lienart for donation debit (receiver):', walletOption.textContent);
                }
            }
            
            if (creditAccountSelect) {
                let revenueOption = Array.from(creditAccountSelect.options).find(option => 
                    option.textContent.trim() === 'BE - Revenues (Nominal Accounts)'
                );
                
                if (!revenueOption) {
                    revenueOption = Array.from(creditAccountSelect.options).find(option => 
                        option.textContent.toLowerCase().includes('be') && 
                        option.textContent.toLowerCase().includes('revenues')
                    );
                }
                
                if (revenueOption) {
                    creditAccountSelect.value = revenueOption.value;
                    console.log('✅ Auto-selected BE - Revenues for donation credit (source):', revenueOption.textContent);
                }
            }
        } else if (selectedCountry === 'VN') {
            // For Vietnam donations: Debit VN - Indovina Bank (receiver), Credit VN - Revenues (source)
            if (debitAccountSelect) {
                let bankOption = Array.from(debitAccountSelect.options).find(option => 
                    option.textContent.trim() === 'VN - Indovina Bank (Real Accounts)'
                );
                
                if (!bankOption) {
                    bankOption = Array.from(debitAccountSelect.options).find(option => 
                        option.textContent.toLowerCase().includes('vn') && 
                        option.textContent.toLowerCase().includes('indovina')
                    );
                }
                
                if (bankOption) {
                    debitAccountSelect.value = bankOption.value;
                    console.log('✅ Auto-selected VN - Indovina Bank for donation debit (receiver):', bankOption.textContent);
                }
            }
            
            if (creditAccountSelect) {
                let revenueOption = Array.from(creditAccountSelect.options).find(option => 
                    option.textContent.trim() === 'VN - Revenues (Nominal Accounts)'
                );
                
                if (!revenueOption) {
                    revenueOption = Array.from(creditAccountSelect.options).find(option => 
                        option.textContent.toLowerCase().includes('vn') && 
                        option.textContent.toLowerCase().includes('revenues')
                    );
                }
                
                if (revenueOption) {
                    creditAccountSelect.value = revenueOption.value;
                    console.log('✅ Auto-selected VN - Revenues for donation credit (source):', revenueOption.textContent);
                }
            }
        }
        
        // Auto-select Donation category for donations
        if (categorySelect) {
            const donationOption = Array.from(categorySelect.options).find(option => 
                option.textContent.toLowerCase().includes('donation')
            );
            if (donationOption) {
                categorySelect.value = donationOption.value;
                console.log('Auto-selected Donation category for donation');
            }
        }
        
        // Auto-select Unrestricted fund for donations
        if (fundSelect) {
            const unrestrictedOption = Array.from(fundSelect.options).find(option => 
                option.textContent.toLowerCase().includes('unrestricted')
            );
            if (unrestrictedOption) {
                fundSelect.value = unrestrictedOption.value;
                console.log('Auto-selected Unrestricted fund for donation');
            }
        }
    } else if (selectedType === 'payment') {
        console.log('🔄 Applying payment defaults...');
        
        // Get current country from sessionStorage
        const selectedCountry = sessionStorage.getItem('selectedCountry') || 'BE';
        console.log(`🌍 Current country: ${selectedCountry}`);
        
        if (selectedCountry === 'BE') {
            // For Belgium payments: Debit BE - Expenses, Credit BE - Wallet Govinda Lienart
            if (debitAccountSelect) {
                let expenseOption = Array.from(debitAccountSelect.options).find(option => 
                    option.textContent.trim() === 'BE - Expenses (Nominal Accounts)'
                );
                
                if (!expenseOption) {
                    expenseOption = Array.from(debitAccountSelect.options).find(option => 
                        option.textContent.toLowerCase().includes('be') && 
                        option.textContent.toLowerCase().includes('expenses')
                    );
                }
                
                if (expenseOption) {
                    debitAccountSelect.value = expenseOption.value;
                    console.log('✅ Auto-selected BE - Expenses account for payment debit:', expenseOption.textContent);
                }
            }
            
            if (creditAccountSelect) {
                let walletOption = Array.from(creditAccountSelect.options).find(option => 
                    option.textContent.trim() === 'BE - Wallet Govinda Lienart (Real Accounts)'
                );
                
                if (!walletOption) {
                    walletOption = Array.from(creditAccountSelect.options).find(option => 
                        option.textContent.toLowerCase().includes('be') && 
                        option.textContent.toLowerCase().includes('wallet') &&
                        option.textContent.toLowerCase().includes('govinda')
                    );
                }
                
                if (walletOption) {
                    creditAccountSelect.value = walletOption.value;
                    console.log('✅ Auto-selected BE - Wallet Govinda Lienart for payment credit:', walletOption.textContent);
                }
            }
        } else if (selectedCountry === 'VN') {
            // For Vietnam payments: Debit VN - Expenses, Credit VN - Indovina Bank
            if (debitAccountSelect) {
                let expenseOption = Array.from(debitAccountSelect.options).find(option => 
                    option.textContent.trim() === 'VN - Expenses (Nominal Accounts)'
                );
                
                if (!expenseOption) {
                    expenseOption = Array.from(debitAccountSelect.options).find(option => 
                        option.textContent.toLowerCase().includes('vn') && 
                        option.textContent.toLowerCase().includes('expenses')
                    );
                }
                
                if (expenseOption) {
                    debitAccountSelect.value = expenseOption.value;
                    console.log('✅ Auto-selected VN - Expenses account for payment debit:', expenseOption.textContent);
                }
            }
            
            if (creditAccountSelect) {
                let bankOption = Array.from(creditAccountSelect.options).find(option => 
                    option.textContent.trim() === 'VN - Indovina Bank (Real Accounts)'
                );
                
                if (!bankOption) {
                    bankOption = Array.from(creditAccountSelect.options).find(option => 
                        option.textContent.toLowerCase().includes('vn') && 
                        option.textContent.toLowerCase().includes('indovina')
                    );
                }
                
                if (bankOption) {
                    creditAccountSelect.value = bankOption.value;
                    console.log('✅ Auto-selected VN - Indovina Bank for payment credit:', bankOption.textContent);
                }
            }
        }
        
        // Auto-select Food & Meals category for payments
        if (categorySelect) {
            const foodOption = Array.from(categorySelect.options).find(option => 
                option.textContent.toLowerCase().includes('food') || 
                option.textContent.toLowerCase().includes('meals')
            );
            if (foodOption) {
                categorySelect.value = foodOption.value;
                console.log('✅ Auto-selected Food & Meals category for payment:', foodOption.textContent);
            }
        }
    } else if (selectedType === 'internal_transfer') {
        console.log('🔄 Applying internal transfer defaults...');
        
        // Auto-set standard internal transfer accounts
        if (debitAccountSelect) {
            const walletOption = Array.from(debitAccountSelect.options).find(option => 
                option.textContent.toLowerCase().includes('wallet')
            );
            if (walletOption) {
                debitAccountSelect.value = walletOption.value;
                console.log('✅ Auto-selected Wallet for internal transfer debit:', walletOption.textContent);
            }
        }
        
        if (creditAccountSelect) {
            const bankOption = Array.from(creditAccountSelect.options).find(option => 
                option.textContent.toLowerCase().includes('indovina bank')
            );
            if (bankOption) {
                creditAccountSelect.value = bankOption.value;
                console.log('✅ Auto-selected Indovina Bank for internal transfer credit:', bankOption.textContent);
            }
        }
        
        // Auto-select Internal Transfer for Fund
        if (fundSelect) {
            const internalTransferFund = Array.from(fundSelect.options).find(option => 
                option.textContent.toLowerCase().includes('internal transfer')
            );
            if (internalTransferFund) {
                fundSelect.value = internalTransferFund.value;
                console.log('✅ Auto-selected Internal Transfer fund:', internalTransferFund.textContent);
            }
        }
        
        // Auto-select Internal Bank Transfer for Category
        if (categorySelect) {
            const internalBankTransferCategory = Array.from(categorySelect.options).find(option => 
                option.textContent.toLowerCase().includes('internal bank transfer')
            );
            if (internalBankTransferCategory) {
                categorySelect.value = internalBankTransferCategory.value;
                console.log('✅ Auto-selected Internal Bank Transfer category:', internalBankTransferCategory.textContent);
            }
        }
    } else if (selectedType === 'grant') {
        console.log('🔄 Applying grant defaults...');
        
        // Get current country from sessionStorage
        const selectedCountry = sessionStorage.getItem('selectedCountry') || 'BE';
        console.log(`🌍 Current country for grant: ${selectedCountry}`);
        
        if (selectedCountry === 'BE') {
            // For Belgium grants: Debit BE - Wallet Govinda Lienart (receiver), Credit BE - Revenues (source)
            if (debitAccountSelect) {
                let walletOption = Array.from(debitAccountSelect.options).find(option => 
                    option.textContent.trim() === 'BE - Wallet Govinda Lienart (Real Accounts)'
                );
                
                if (!walletOption) {
                    walletOption = Array.from(debitAccountSelect.options).find(option => 
                        option.textContent.toLowerCase().includes('be') && 
                        option.textContent.toLowerCase().includes('wallet') &&
                        option.textContent.toLowerCase().includes('govinda')
                    );
                }
                
                if (walletOption) {
                    debitAccountSelect.value = walletOption.value;
                    console.log('✅ Auto-selected BE - Wallet Govinda Lienart for grant debit (receiver):', walletOption.textContent);
                }
            }
            
            if (creditAccountSelect) {
                let revenueOption = Array.from(creditAccountSelect.options).find(option => 
                    option.textContent.trim() === 'BE - Revenues (Nominal Accounts)'
                );
                
                if (!revenueOption) {
                    revenueOption = Array.from(creditAccountSelect.options).find(option => 
                        option.textContent.toLowerCase().includes('be') && 
                        option.textContent.toLowerCase().includes('revenues')
                    );
                }
                
                if (revenueOption) {
                    creditAccountSelect.value = revenueOption.value;
                    console.log('✅ Auto-selected BE - Revenues for grant credit (source):', revenueOption.textContent);
                }
            }
        } else if (selectedCountry === 'VN') {
            // For Vietnam grants: Debit VN - Indovina Bank (receiver), Credit VN - Revenues (source)
            if (debitAccountSelect) {
                let bankOption = Array.from(debitAccountSelect.options).find(option => 
                    option.textContent.trim() === 'VN - Indovina Bank (Real Accounts)'
                );
                
                if (!bankOption) {
                    bankOption = Array.from(debitAccountSelect.options).find(option => 
                        option.textContent.toLowerCase().includes('vn') && 
                        option.textContent.toLowerCase().includes('indovina')
                    );
                }
                
                if (bankOption) {
                    debitAccountSelect.value = bankOption.value;
                    console.log('✅ Auto-selected VN - Indovina Bank for grant debit (receiver):', bankOption.textContent);
                }
            }
            
            if (creditAccountSelect) {
                let revenueOption = Array.from(creditAccountSelect.options).find(option => 
                    option.textContent.trim() === 'VN - Revenues (Nominal Accounts)'
                );
                
                if (!revenueOption) {
                    revenueOption = Array.from(creditAccountSelect.options).find(option => 
                        option.textContent.toLowerCase().includes('vn') && 
                        option.textContent.toLowerCase().includes('revenues')
                    );
                }
                
                if (revenueOption) {
                    creditAccountSelect.value = revenueOption.value;
                    console.log('✅ Auto-selected VN - Revenues for grant credit (source):', revenueOption.textContent);
                }
            }
        }
        
        // Auto-select Grant category for grants
        if (categorySelect) {
            const grantOption = Array.from(categorySelect.options).find(option => 
                option.textContent.toLowerCase().includes('grant')
            );
            if (grantOption) {
                categorySelect.value = grantOption.value;
                console.log('Auto-selected Grant category for grant');
            }
        }
        
        // Keep fund on "Choose a fund..." (no default selection)
        if (fundSelect) {
            fundSelect.value = '';
            console.log('Fund left on default "Choose a fund..." for grant');
        }
    }
}

/**
 * Force apply transaction defaults - can be called manually if needed
 */
function forceApplyTransactionDefaults() {
    const transactionSelect = document.getElementById('transaction_category');
    if (transactionSelect) {
        console.log('🔄 Force applying transaction defaults...');
        applyTransactionDefaults(transactionSelect.value);
    }
}

// Make the function available globally for debugging
window.forceApplyTransactionDefaults = forceApplyTransactionDefaults;

// ============================================================================
// FILE UPLOAD FUNCTIONS
// ============================================================================

/**
 * Generic upload function for different file types
 */
function uploadFile(fileType) {
    const fileInput = document.getElementById(`${fileType}FileInput`);
    const uploadBtn = document.getElementById(`${fileType}UploadBtn`);
    const uploadStatus = document.getElementById(`${fileType}UploadStatus`);
    const uploadProgress = document.getElementById(`${fileType}UploadProgress`);
    const uploadResult = document.getElementById(`${fileType}UploadResult`);
    const fileLink = document.getElementById(`${fileType}FileLink`);
    const fileLinkInput = document.getElementById(`${fileType}FileLinkInput`);
    const fileNameInput = document.getElementById(`${fileType}FileNameInput`);
    const transactionNumberDisplay = document.getElementById('transactionNumberDisplay');

    const file = fileInput.files[0];
    if (!file) {
        alert(`Please select a ${fileType} file first!`);
        return;
    }

    // Use the existing transaction number from the display field
    const transactionNumber = transactionNumberDisplay.value;
    if (!transactionNumber || transactionNumber === 'Generating...') {
        alert('Please wait for transaction number to be generated');
        return;
    }

    console.log(`Using transaction number for ${fileType} file:`, transactionNumber);

    uploadStatus.style.display = 'block';
    uploadProgress.style.display = 'block';
    uploadResult.style.display = 'none';
    uploadBtn.disabled = true;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('transaction_number', transactionNumber);
    formData.append('file_type', fileType);

    fetch('/upload_file', { method: 'POST', body: formData })
        .then(r => r.json())
        .then(data => {
            uploadProgress.style.display = 'none';
            uploadResult.style.display = 'block';

            if (data.success) {
                fileLink.innerHTML = `<a href="${data.file_url}" target="_blank">${data.file_name}</a>`;
                fileLinkInput.value = data.file_url;   // URL for backend
                fileNameInput.value = data.file_name;  // Label for HYPERLINK
                
                console.log(`${fileType} file uploaded successfully with transaction number:`, transactionNumber);
                console.log('File name:', data.file_name);
            } else {
                fileLink.innerHTML = `<div class="alert alert-error">Error: ${data.error}</div>`;
            }
        })
        .catch(err => {
            uploadProgress.style.display = 'none';
            uploadResult.style.display = 'block';
            fileLink.innerHTML = `<div class="alert alert-error">Upload failed: ${err.message}</div>`;
        })
        .finally(() => {
            uploadBtn.disabled = false;
        });
}

// Specific upload functions for each file type
function uploadBills() { uploadFile('bills'); }
function uploadRedBills() { uploadFile('redBills'); }  // This matches FOLDER_IDS['redBills']
function uploadDocumentation() { uploadFile('documentation'); }

/**
 * Enhanced Drag & Drop Functionality
 */
function setupDragAndDrop() {
    const fileInputLabels = document.querySelectorAll('.enhanced-file-input-label');
    
    fileInputLabels.forEach(label => {
        const fileInput = label.parentElement.querySelector('input[type="file"]');
        
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            label.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });
        
        // Highlight drop area when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            label.addEventListener(eventName, () => {
                label.classList.add('drag-over');
            }, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            label.addEventListener(eventName, () => {
                label.classList.remove('drag-over');
            }, false);
        });
        
        // Handle dropped files
        label.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                fileInput.files = files;
                console.log('File dropped:', files[0].name);
                
                // Update label text to show selected file
                const fileName = files[0].name;
                const fileSize = (files[0].size / 1024 / 1024).toFixed(2);
                label.innerHTML = `
                    ✅ ${fileName}
                    <small style="margin-top: 8px; opacity: 0.8;">Size: ${fileSize}MB - Click to change or drop new file</small>
                `;
                
                // Trigger change event for validation or other handlers
                const event = new Event('change', { bubbles: true });
                fileInput.dispatchEvent(event);
            }
        }, false);
        
        // Handle regular file selection (click)
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                const fileName = this.files[0].name;
                const fileSize = (this.files[0].size / 1024 / 1024).toFixed(2);
                label.innerHTML = `
                    ✅ ${fileName}
                    <small style="margin-top: 8px; opacity: 0.8;">Size: ${fileSize}MB - Click to change or drop new file</small>
                `;
                console.log('File selected via click:', fileName);
            } else {
                // Reset to original state
                const originalTexts = {
                    'billsFileInput': '📁 Click to select file or drag & drop<small style="margin-top: 8px; opacity: 0.8;">Receipts, invoices, or supporting documents</small>',
                    'redBillsFileInput': '📁 Click to select file or drag & drop<small style="margin-top: 8px; opacity: 0.8;">Red bills or urgent payment documents</small>',
                    'documentationFileInput': '📁 Click to select file or drag & drop<small style="margin-top: 8px; opacity: 0.8;">Supporting documentation or reference materials</small>'
                };
                label.innerHTML = originalTexts[this.id] || '📁 Click to select file or drag & drop';
            }
        });
    });
}

// ============================================================================
// FORM HANDLING
// ============================================================================

/**
 * Reset all upload-related UI state
 */
function resetUploadState() {
    console.log('🧹 Resetting upload state...');
    
    // ===== MAIN FORM UPLOAD STATE =====
    
    // Reset document type dropdown
    const documentTypeDropdown = document.getElementById('documentTypeDropdown');
    if (documentTypeDropdown) {
        documentTypeDropdown.value = '';
    }
    
    // Clear document file input
    const documentFileInput = document.getElementById('documentFileInput');
    if (documentFileInput) {
        documentFileInput.value = '';
    }
    
    // Clear Google Drive link input
    const googleDriveLinkInput = document.getElementById('googleDriveLinkInput');
    if (googleDriveLinkInput) {
        googleDriveLinkInput.value = '';
    }
    
    // Hide upload mode toggle section
    const uploadModeToggle = document.getElementById('uploadModeToggle');
    if (uploadModeToggle) {
        uploadModeToggle.style.display = 'none';
    }
    
    // Hide file upload section
    const fileUploadSection = document.getElementById('fileUploadSection');
    if (fileUploadSection) {
        fileUploadSection.style.display = 'none';
    }
    
    // Hide Google Drive link section
    const googleDriveLinkSection = document.getElementById('googleDriveLinkSection');
    if (googleDriveLinkSection) {
        googleDriveLinkSection.style.display = 'none';
    }
    
    // Hide and clear upload status
    const uploadStatus = document.getElementById('uploadStatus');
    const uploadStatusMessage = document.getElementById('uploadStatusMessage');
    if (uploadStatus) {
        uploadStatus.style.display = 'none';
    }
    if (uploadStatusMessage) {
        uploadStatusMessage.textContent = '';
    }
    
    // Clear all hidden file link and name inputs
    const hiddenInputs = [
        'billsFileLinkInput', 'billsFileNameInput',
        'redBillsFileLinkInput', 'redBillsFileNameInput',
        'documentationFileLinkInput', 'documentationFileNameInput'
    ];
    
    hiddenInputs.forEach(inputId => {
        const input = document.getElementById(inputId);
        if (input) {
            input.value = '';
        }
    });
    
    // ===== UPDATE FORM UPLOAD STATE =====
    
    // Reset update form file inputs and labels
    const updateFileInputs = [
        { inputId: 'billsFile', icon: '📄', text: 'Choose Bills File' },
        { inputId: 'redBillsFile', icon: '🔴', text: 'Choose Red Bills File' },
        { inputId: 'documentationFile', icon: '📚', text: 'Choose Documentation File' }
    ];
    
    updateFileInputs.forEach(item => {
        const fileInput = document.getElementById(item.inputId);
        if (fileInput) {
            fileInput.value = '';
            
            // Find and reset the corresponding label
            const label = document.querySelector(`label[for="${item.inputId}"]`);
            if (label) {
                label.innerHTML = `
                    <span class="file-icon">${item.icon}</span>
                    <span class="file-text">${item.text}</span>
                    <span class="file-hint">Click to select or drag & drop</span>
                `;
            }
        }
    });
    
    console.log('✅ Upload state reset complete');
}

/**
 * Handle form submission
 */
let isSubmitting = false; // Flag to prevent duplicate submissions

function handleFormSubmit(event) {
    console.log('handleFormSubmit called - Form submission started');
    
    // Prevent default form submission
    event.preventDefault();
    
    // Check if already submitting
    if (isSubmitting) {
        console.log('Already submitting, ignoring duplicate submission');
        return false;
    }
    
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

function submitToGoogleSheets(formData) {
    console.log('submitToGoogleSheets called');
    
    // Convert FormData to JSON
    const jsonData = {};
    for (let [key, value] of formData.entries()) {
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
        if (data.success) {
            showSuccessMessage('Successfully submitted to Google Sheet!');
            // Reset form
            document.getElementById('mainForm').reset();
            // Reset upload state (clear file inputs, labels, and hidden fields)
            resetUploadState();
            // Generate new transaction number
            generateTransactionNumber();
            // Re-apply transaction type defaults after reset
            setTimeout(() => {
                const transactionSelect = document.getElementById('transaction_category');
                if (transactionSelect && transactionSelect.value) {
                    applyTransactionDefaults(transactionSelect.value);
                }
                
                // Reload worksheets for the selected sheet
                const sheetSelect = document.getElementById('sheet_select');
                if (sheetSelect && sheetSelect.value) {
                    loadWorksheets();
                }
                
                // Update navigation progress to clear blue highlighting
                updateNavigationProgress();
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
        isSubmitting = false; // Reset the flag
        console.log('Submission complete, flag reset');
    });
}

function showSuccessMessage(message) {
    console.log('showSuccessMessage called with:', message);
    
    // Check if there's already a success popup and remove it
    const existingPopup = document.querySelector('.success-popup');
    if (existingPopup) {
        console.log('Removing existing success popup');
        existingPopup.remove();
    }
    
    // Create success popup
    const popup = document.createElement('div');
    popup.className = 'success-popup';
    popup.innerHTML = `
        <div class="success-content">
            <div class="success-icon">✅</div>
            <div class="success-text">${message}</div>
        </div>
    `;
    
    // Add to page
    document.body.appendChild(popup);
    
    // Show popup
    setTimeout(() => popup.classList.add('show'), 100);
    
    // Remove popup after 3 seconds
    setTimeout(() => {
        popup.classList.remove('show');
        setTimeout(() => {
            if (popup.parentNode) {
                document.body.removeChild(popup);
            }
        }, 300);
    }, 3000);
}

function showErrorMessage(message) {
    // Create error popup
    const popup = document.createElement('div');
    popup.className = 'error-popup';
    popup.innerHTML = `
        <div class="error-content">
            <div class="error-icon">❌</div>
            <div class="error-text">${message}</div>
        </div>
    `;
    
    // Add to page
    document.body.appendChild(popup);
    
    // Show popup
    setTimeout(() => popup.classList.add('show'), 100);
    
    // Remove popup after 5 seconds
    setTimeout(() => {
        popup.classList.remove('show');
        setTimeout(() => document.body.removeChild(popup), 300);
    }, 5000);
}

// ============================================================================
// INITIALIZATION
// ============================================================================

/**
 * Professional Section Navigation System
 */
let currentSection = 'transaction-number-section';
let completedSections = new Set();

function initializeSectionNavigation() {
    console.log('🎯 Initializing professional section navigation...');
    
    // Define which sections are part of the main navigation flow
    const mainFormSections = [
        'transaction-number-section',
        'transaction-type-section', 
        'sheet-worksheet-section',
        'date-section',
        'amount-section',
        'fund-section',
        'category-section',
        'sub-category-section',
        'debit-account-section',
        'credit-account-section',
        'payment-method-section',
        'description-section',
        'document-upload-section'
    ];
    
    // Hide only the main form sections except the first one
    mainFormSections.forEach(sectionId => {
        const section = document.getElementById(sectionId);
        if (section) {
            section.classList.remove('active');
        }
    });
    
    // Show the first section
    const firstSection = document.getElementById('transaction-number-section');
    if (firstSection) {
        firstSection.classList.add('active');
    }
    
    // Ensure non-main sections (like upload, search) remain visible
    const nonMainSections = document.querySelectorAll('.form-section:not(#transaction-number-section):not(#transaction-type-section):not(#sheet-worksheet-section):not(#date-section):not(#amount-section):not(#fund-section):not(#category-section):not(#sub-category-section):not(#debit-account-section):not(#credit-account-section):not(#payment-method-section):not(#description-section):not(#document-upload-section)');
    nonMainSections.forEach(section => {
        section.style.display = 'block';
        section.style.opacity = '1';
        section.style.transform = 'translateY(0)';
    });
    
    // Set initial navigation state
    updateNavigationState();
    
    // Add click handlers to navigation links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            const sectionId = href.substring(1); // Remove the # symbol
            
            // Check if we can navigate to this section
            if (canNavigateToSection(sectionId)) {
                navigateToSection(sectionId);
            }
        });
    });
    
    console.log('✅ Section navigation initialized');
}

function navigateToSection(sectionId) {
    console.log(`🎯 Navigating to section: ${sectionId}`);
    
    // Auto-validate and mark current section as completed if it has valid data
    if (currentSection && currentSection !== sectionId) {
        checkAndMarkSectionCompleted(currentSection);
    }
    
    // Hide current section
    const currentActiveSection = document.querySelector('.form-section.active');
    if (currentActiveSection) {
        currentActiveSection.classList.remove('active');
    }
    
    // Show target section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
        currentSection = sectionId;
        
        // Scroll to top of form for better UX
        targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    // Update navigation state
    updateNavigationState();
}

function updateNavigationState() {
    // Remove all state classes from navigation
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.classList.remove('current', 'completed');
    });
    
    // Set current section
    const currentNavLink = document.querySelector(`a[href="#${currentSection}"]`);
    if (currentNavLink) {
        currentNavLink.classList.add('current');
    }
    
    // Set completed sections
    completedSections.forEach(sectionId => {
        const completedNavLink = document.querySelector(`a[href="#${sectionId}"]`);
        if (completedNavLink) {
            completedNavLink.classList.add('completed');
        }
    });
}

function markSectionCompleted(sectionId) {
    completedSections.add(sectionId);
    updateNavigationState();
    console.log(`✅ Section completed: ${sectionId}`);
}

function checkAndMarkSectionCompleted(sectionId) {
    const section = document.getElementById(sectionId);
    if (!section) return false;
    
    // Get all required inputs in the section
    const requiredInputs = section.querySelectorAll('input[required], select[required], textarea[required]');
    let allCompleted = true;
    
    requiredInputs.forEach(input => {
        if (!input.value.trim()) {
            allCompleted = false;
        }
    });
    
    // If all required fields are filled, mark as completed
    if (allCompleted && requiredInputs.length > 0) {
        markSectionCompleted(sectionId);
        return true;
    }
    
    return false;
}

function canNavigateToSection(sectionId) {
    // Allow free navigation to any section
    return true;
}

function validateCurrentSection() {
    const section = document.getElementById(currentSection);
    if (!section) return false;
    
    // Get all required inputs in current section
    const requiredInputs = section.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    requiredInputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.style.borderColor = '#dc3545';
        } else {
            input.style.borderColor = '';
        }
    });
    
    if (isValid) {
        markSectionCompleted(currentSection);
        return true;
    } else {
        // Show validation message
        showSectionValidationMessage('Please complete all required fields before proceeding.');
        return false;
    }
}

function showSectionValidationMessage(message) {
    // Remove existing validation message
    const existingMessage = document.querySelector('.section-validation-message');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    // Create new validation message
    const validationMessage = document.createElement('div');
    validationMessage.className = 'section-validation-message';
    validationMessage.style.cssText = `
        background: #f8d7da;
        color: #721c24;
        padding: 12px 16px;
        border: 1px solid #f5c6cb;
        border-radius: 6px;
        margin: 15px 0;
        font-size: 14px;
        animation: slideInFade 0.3s ease-out;
    `;
    validationMessage.textContent = message;
    
    // Insert after current section
    const currentActiveSection = document.querySelector('.form-section.active');
    if (currentActiveSection) {
        currentActiveSection.insertAdjacentElement('afterend', validationMessage);
        
        // Auto-remove after 4 seconds
        setTimeout(() => {
            if (validationMessage.parentNode) {
                validationMessage.remove();
            }
        }, 4000);
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
    
    // Add event listeners for all upload buttons (only if they exist)
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
    
    // Add event listener for submit button in navigation (only if it exists)
    const submitNavBtn = document.getElementById('submitNavBtn');
    if (submitNavBtn) {
        submitNavBtn.addEventListener('click', function(e) {
            e.preventDefault();
            // Trigger the form submission using the same handler
            const form = document.getElementById('mainForm');
            if (form) {
                // Create a synthetic submit event
                const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
                form.dispatchEvent(submitEvent);
            }
        });
    }
    
    // =============================================================================
    // FUND COLOR HANDLING - Apply colors from data attributes
    // =============================================================================
    
    // Apply fund colors to option elements
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
    
    // Apply colors when the page loads
    applyFundColors();
    
    // Auto-select default fund if none is selected
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
    
    // Auto-select default fund when page loads
    autoSelectDefaultFund();
    
    // Re-apply colors when funds are refreshed
    const originalRefreshFormData = window.refreshFormData;
    if (originalRefreshFormData) {
        window.refreshFormData = function() {
            const result = originalRefreshFormData.apply(this, arguments);
            // Re-apply colors after form data is refreshed
            setTimeout(applyFundColors, 100);
            // Re-apply default fund selection
            setTimeout(autoSelectDefaultFund, 100);
            return result;
        };
    }

    // =============================================================================
    // DATE INPUT HANDLING - Smart Date Format Conversion
    // =============================================================================
    
    // Function to convert various date formats to YYYY-MM-DD
    function convertDateFormat(dateString) {
        if (!dateString || dateString.trim() === '') return '';
        
        // Remove any extra spaces
        dateString = dateString.trim();
        
        // Handle different separators and formats
        let parts = [];
        
        // Try different separators
        if (dateString.includes('/')) {
            parts = dateString.split('/');
        } else if (dateString.includes('-')) {
            parts = dateString.split('-');
        } else if (dateString.includes('.')) {
            parts = dateString.split('.');
        } else {
            return dateString; // Return as-is if no recognizable separator
        }
        
        if (parts.length !== 3) return dateString;
        
        let day, month, year;
        
        // Determine format based on part lengths and values
        if (parts[0].length === 4) {
            // YYYY/MM/DD format
            year = parts[0];
            month = parts[1].padStart(2, '0');
            day = parts[2].padStart(2, '0');
        } else if (parts[2].length === 4) {
            // DD/MM/YYYY or MM/DD/YYYY format
            year = parts[2];
            
            // Try to determine if it's DD/MM or MM/DD
            const firstPart = parseInt(parts[0]);
            const secondPart = parseInt(parts[1]);
            
            if (firstPart > 12 && secondPart <= 12) {
                // DD/MM/YYYY (day > 12, month <= 12)
                day = parts[0].padStart(2, '0');
                month = parts[1].padStart(2, '0');
            } else if (secondPart > 12 && firstPart <= 12) {
                // MM/DD/YYYY (month > 12, day <= 12)
                month = parts[0].padStart(2, '0');
                day = parts[1].padStart(2, '0');
            } else {
                // Ambiguous case - assume DD/MM/YYYY (European format)
                day = parts[0].padStart(2, '0');
                month = parts[1].padStart(2, '0');
            }
        } else {
            // Two-digit year - smart century detection
            const currentYear = new Date().getFullYear();
            const currentCentury = Math.floor(currentYear / 100) * 100;
            const twoDigitYear = parseInt(parts[2]);
            
            // Smart year conversion: if 2-digit year is > current year's last 2 digits,
            // assume it's from previous century, otherwise current century
            const currentTwoDigitYear = currentYear % 100;
            if (twoDigitYear > currentTwoDigitYear) {
                year = currentCentury - 100 + twoDigitYear; // Previous century
            } else {
                year = currentCentury + twoDigitYear; // Current century
            }
            
            // For DD/MM/YY format, assume DD/MM (European format)
            day = parts[0].padStart(2, '0');
            month = parts[1].padStart(2, '0');
        }
        
        // Validate the date
        const date = new Date(year, month - 1, day);
        if (date.getFullYear() == year && date.getMonth() == month - 1 && date.getDate() == day) {
            // Return in DD/MM/YY format
            const shortYear = year.toString().slice(-2);
            return `${day}/${month}/${shortYear}`;
        } else {
            return dateString; // Return original if invalid
        }
    }
    
    // Function to validate date format
    function validateDateFormat(dateString) {
        if (!dateString) return false;
        
        // Check if it's already in DD/MM/YY format (our standard format)
        const standardDateRegex = /^\d{2}\/\d{2}\/\d{2}$/;
        if (standardDateRegex.test(dateString)) return true;
        
        // Check if it's in YYYY-MM-DD format
        const isoDateRegex = /^\d{4}-\d{2}-\d{2}$/;
        if (isoDateRegex.test(dateString)) return true;
        
        // Try to convert and validate
        const converted = convertDateFormat(dateString);
        return standardDateRegex.test(converted);
    }
    
    // Add event listeners for date input
    const dateInput = document.getElementById('date_input');
    if (dateInput) {
        // Handle paste events
        dateInput.addEventListener('paste', function(e) {
            setTimeout(() => {
                const value = this.value;
                const converted = convertDateFormat(value);
                if (converted !== value) {
                    this.value = converted;
                    // Show a brief success message
                    showTemporaryMessage('Date format converted successfully!', 'success');
                }
            }, 10); // Small delay to allow paste to complete
        });
        
        // Handle input changes
        dateInput.addEventListener('blur', function() {
            const value = this.value.trim();
            if (value) {
                const converted = convertDateFormat(value);
                if (converted !== value && validateDateFormat(converted)) {
                    this.value = converted;
                    showTemporaryMessage('Date format converted to standard format', 'info');
                } else if (!validateDateFormat(converted)) {
                    showTemporaryMessage('Please enter a valid date format (dd/mm/yyyy or mm/dd/yyyy)', 'error');
                    this.style.borderColor = '#dc3545';
                } else {
                    this.style.borderColor = '';
                }
            }
        });
        
        // Clear error styling on focus
        dateInput.addEventListener('focus', function() {
            this.style.borderColor = '';
        });
    }
    
    // Helper function to show temporary messages
    function showTemporaryMessage(message, type = 'info') {
        // Create message element
        const messageEl = document.createElement('div');
        messageEl.className = `temp-message temp-message-${type}`;
        messageEl.textContent = message;
        messageEl.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 15px;
            border-radius: 4px;
            color: white;
            font-size: 14px;
            z-index: 10000;
            opacity: 0;
            transition: opacity 0.3s ease;
            ${type === 'success' ? 'background-color: #28a745;' : ''}
            ${type === 'error' ? 'background-color: #dc3545;' : ''}
            ${type === 'info' ? 'background-color: #17a2b8;' : ''}
        `;
        
        document.body.appendChild(messageEl);
        
        // Fade in
        setTimeout(() => messageEl.style.opacity = '1', 10);
        
        // Fade out and remove
        setTimeout(() => {
            messageEl.style.opacity = '0';
            setTimeout(() => document.body.removeChild(messageEl), 300);
        }, 3000);
    }

    console.log('NGO Accounting System initialized successfully! 🚀');
});
