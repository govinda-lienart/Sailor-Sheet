/**
 * NGO Accounting System - Main Application JavaScript
 * This file contains all the JavaScript functionality for the accounting form
 */

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Generate a unique transaction number based on current date/time
 * Format: DDMMYY-HHMMSS
 */
function generateTransactionNumber() {
    const now = new Date();
    const transactionNumber = now.getDate().toString().padStart(2, '0') +
                            (now.getMonth() + 1).toString().padStart(2, '0') +
                            now.getFullYear().toString().slice(-2) + '-' +
                            now.getHours().toString().padStart(2, '0') +
                            now.getMinutes().toString().padStart(2, '0') +
                            now.getSeconds().toString().padStart(2, '0');
    
    document.getElementById('transactionNumberDisplay').value = transactionNumber;
    document.getElementById('transactionNumberInput').value = transactionNumber;
    console.log('Generated transaction number:', transactionNumber);
    return transactionNumber;
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
 * Update navigation panel based on transaction type (regular vs interbanking)
 */
function updateNavigationForInterbanking(isInterbanking) {
    const regularAccountLinks = document.querySelectorAll('.regular-account');
    const interbankingAccountLinks = document.querySelectorAll('.interbanking-account');
    
    if (isInterbanking) {
        // Hide regular account links, show interbanking account links
        regularAccountLinks.forEach(link => link.style.display = 'none');
        interbankingAccountLinks.forEach(link => link.style.display = 'block');
    } else {
        // Show regular account links, hide interbanking account links
        regularAccountLinks.forEach(link => link.style.display = 'block');
        interbankingAccountLinks.forEach(link => link.style.display = 'none');
    }
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
                const interbankingPayment = document.querySelector('select[name="interbanking_payment_method"]');
                if (paymentMethod && paymentMethod.hasAttribute('required')) return paymentMethod.value !== '';
                if (interbankingPayment && interbankingPayment.hasAttribute('required')) return interbankingPayment.value !== '';
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
    
    // Get all account field elements
    const interbankingSections = document.getElementById('interbankingSections');
    const regularAccountSections = document.getElementById('regularAccountSections');
    
    // Get all required fields in both sections
    const regularDebitField = document.querySelector('select[name="regular_debit_account_id"]');
    const regularCreditField = document.querySelector('select[name="regular_credit_account_id"]');
    const regularPaymentMethodField = document.querySelector('select[name="payment_method"]');
    const interbankingPaymentMethodField = document.querySelector('select[name="interbanking_payment_method"]');
    
    // Master Ledger A fields
    const masterLedgerADebitField = document.querySelector('select[name="master_ledger_a_debit_account_id"]');
    const masterLedgerACreditField = document.querySelector('select[name="master_ledger_a_credit_account_id"]');
    const masterLedgerASheetField = document.querySelector('select[name="master_ledger_a_sheet_id"]');
    const masterLedgerAWorksheetField = document.querySelector('select[name="master_ledger_a_worksheet_id"]');
    
    // Master Ledger B fields
    const masterLedgerBDebitField = document.querySelector('select[name="master_ledger_b_debit_account_id"]');
    const masterLedgerBCreditField = document.querySelector('select[name="master_ledger_b_credit_account_id"]');
    const masterLedgerBSheetField = document.querySelector('select[name="master_ledger_b_sheet_id"]');
    const masterLedgerBWorksheetField = document.querySelector('select[name="master_ledger_b_worksheet_id"]');
    
    // Get sheet & worksheet content elements
    const regularSheetWorksheet = document.getElementById('regular-sheet-worksheet');
    const masterLedgerSheetWorksheet = document.getElementById('master-ledger-sheet-worksheet');
    const regularSheetField = document.querySelector('select[name="sheet_id"]');
    const regularWorksheetField = document.querySelector('select[name="worksheet_name"]');
    
    if (selectedType === 'interbanking_transfer') {
        // Show interbanking sections, hide regular sections
        if (interbankingSections) interbankingSections.style.display = 'block';
        if (regularAccountSections) regularAccountSections.style.display = 'none';
        
        // Show Master Ledger sheet/worksheet content, hide regular sheet/worksheet content
        if (regularSheetWorksheet) regularSheetWorksheet.style.display = 'none';
        if (masterLedgerSheetWorksheet) masterLedgerSheetWorksheet.style.display = 'block';
        
        // Remove required from hidden regular fields, add required to visible Master Ledger fields
        if (regularDebitField) regularDebitField.removeAttribute('required');
        if (regularCreditField) regularCreditField.removeAttribute('required');
        if (regularPaymentMethodField) regularPaymentMethodField.removeAttribute('required');
        if (regularSheetField) regularSheetField.removeAttribute('required');
        if (regularWorksheetField) regularWorksheetField.removeAttribute('required');
        
        // Set required for Master Ledger A fields
        if (masterLedgerADebitField) masterLedgerADebitField.setAttribute('required', 'required');
        if (masterLedgerACreditField) masterLedgerACreditField.setAttribute('required', 'required');
        if (masterLedgerASheetField) masterLedgerASheetField.setAttribute('required', 'required');
        if (masterLedgerAWorksheetField) masterLedgerAWorksheetField.setAttribute('required', 'required');
        
        // Set required for Master Ledger B fields
        if (masterLedgerBDebitField) masterLedgerBDebitField.setAttribute('required', 'required');
        if (masterLedgerBCreditField) masterLedgerBCreditField.setAttribute('required', 'required');
        if (masterLedgerBSheetField) masterLedgerBSheetField.setAttribute('required', 'required');
        if (masterLedgerBWorksheetField) masterLedgerBWorksheetField.setAttribute('required', 'required');
        
        // Set required for interbanking payment method
        if (interbankingPaymentMethodField) interbankingPaymentMethodField.setAttribute('required', 'required');
        
        // Update navigation panel for interbanking transfer
        updateNavigationForInterbanking(true);
        
        console.log('✅ Showing interbanking transfer sections (Master Ledger A & B)');
        console.log('✅ Required attributes updated for interbanking transfer');
        
        // Set up sheet selection handlers for Master Ledgers
        setupMasterLedgerSheetHandlers();
        
        // Auto-load worksheets for default selected sheets
        setTimeout(() => {
            const masterLedgerASheetSelect = document.getElementById('masterLedgerASheetSelect');
            const masterLedgerBSheetSelect = document.getElementById('masterLedgerBSheetSelect');
            
            if (masterLedgerASheetSelect && masterLedgerASheetSelect.value) {
                loadWorksheetsForMasterLedger('A', masterLedgerASheetSelect.value);
            }
            
            if (masterLedgerBSheetSelect && masterLedgerBSheetSelect.value) {
                loadWorksheetsForMasterLedger('B', masterLedgerBSheetSelect.value);
            }
        }, 100);
    } else {
        // Show regular sections, hide interbanking sections
        if (interbankingSections) interbankingSections.style.display = 'none';
        if (regularAccountSections) regularAccountSections.style.display = 'block';
        
        // Show regular sheet/worksheet content, hide Master Ledger sheet/worksheet content
        if (regularSheetWorksheet) regularSheetWorksheet.style.display = 'block';
        if (masterLedgerSheetWorksheet) masterLedgerSheetWorksheet.style.display = 'none';
        
        // Add required to visible regular fields, remove required from hidden Master Ledger fields
        if (regularDebitField) regularDebitField.setAttribute('required', 'required');
        if (regularCreditField) regularCreditField.setAttribute('required', 'required');
        if (regularPaymentMethodField) regularPaymentMethodField.setAttribute('required', 'required');
        if (regularSheetField) regularSheetField.setAttribute('required', 'required');
        if (regularWorksheetField) regularWorksheetField.setAttribute('required', 'required');
        
        // Remove required from Master Ledger A fields
        if (masterLedgerADebitField) masterLedgerADebitField.removeAttribute('required');
        if (masterLedgerACreditField) masterLedgerACreditField.removeAttribute('required');
        if (masterLedgerASheetField) masterLedgerASheetField.removeAttribute('required');
        if (masterLedgerAWorksheetField) masterLedgerAWorksheetField.removeAttribute('required');
        
        // Remove required from Master Ledger B fields
        if (masterLedgerBDebitField) masterLedgerBDebitField.removeAttribute('required');
        if (masterLedgerBCreditField) masterLedgerBCreditField.removeAttribute('required');
        if (masterLedgerBSheetField) masterLedgerBSheetField.removeAttribute('required');
        if (masterLedgerBWorksheetField) masterLedgerBWorksheetField.removeAttribute('required');
        
        // Remove required from interbanking payment method
        if (interbankingPaymentMethodField) interbankingPaymentMethodField.removeAttribute('required');
        
        // Update navigation panel for regular transactions
        updateNavigationForInterbanking(false);
        
        console.log('✅ Showing regular account sections');
        console.log('✅ Required attributes updated for regular transactions');
    }
    
    // Apply transaction type specific defaults immediately
    applyTransactionDefaults(selectedType);
}

// ============================================================================
// WORKSHEET AND SHEET MANAGEMENT
// ============================================================================

/**
 * Setup sheet selection handlers for Master Ledger A and B
 */
function setupMasterLedgerSheetHandlers() {
    // Master Ledger A sheet handler
    const masterLedgerASheetSelect = document.getElementById('masterLedgerASheetSelect');
    if (masterLedgerASheetSelect) {
        masterLedgerASheetSelect.addEventListener('change', function() {
            loadWorksheetsForMasterLedger('A', this.value);
        });
    }
    
    // Master Ledger B sheet handler
    const masterLedgerBSheetSelect = document.getElementById('masterLedgerBSheetSelect');
    if (masterLedgerBSheetSelect) {
        masterLedgerBSheetSelect.addEventListener('change', function() {
            loadWorksheetsForMasterLedger('B', this.value);
        });
    }
}

/**
 * Load worksheets for specific Master Ledger (A or B)
 */
function loadWorksheetsForMasterLedger(ledgerType, sheetId) {
    const worksheetSelectId = `masterLedger${ledgerType}WorksheetSelect`;
    const worksheetSelect = document.getElementById(worksheetSelectId);
    
    if (!worksheetSelect || !sheetId) {
        return;
    }
    
    console.log(`Loading worksheets for Master Ledger ${ledgerType}, Sheet ID: ${sheetId}`);
    
    // Clear existing options
    worksheetSelect.innerHTML = '<option value="">Loading worksheets...</option>';
    
    // Fetch worksheets
    fetch(`/get_worksheets/${sheetId}`)
        .then(response => response.json())
        .then(data => {
            console.log(`Worksheets data received for Master Ledger ${ledgerType}:`, data);
            worksheetSelect.innerHTML = '<option value="">Choose worksheet...</option>';
            
            if (data && data.length > 0) {
                data.forEach(worksheet => {
                    const option = document.createElement('option');
                    option.value = worksheet.title;
                    option.textContent = worksheet.title;
                    worksheetSelect.appendChild(option);
                });
                
                // Auto-select default worksheet based on ledger type
                let defaultWorksheet = '';
                if (ledgerType === 'A') {
                    // Master Ledger A default: look for "Expense" or "Belfius" or "Master Ledger"
                    defaultWorksheet = Array.from(worksheetSelect.options).find(option => 
                        option.textContent.toLowerCase().includes('expense') || 
                        option.textContent.toLowerCase().includes('belfius') ||
                        option.textContent.toLowerCase().includes('master ledger')
                    );
                } else if (ledgerType === 'B') {
                    // Master Ledger B default: look for "Revenue" or "Indovina" or "Master Ledger"
                    defaultWorksheet = Array.from(worksheetSelect.options).find(option => 
                        option.textContent.toLowerCase().includes('revenue') || 
                        option.textContent.toLowerCase().includes('indovina') ||
                        option.textContent.toLowerCase().includes('master ledger')
                    );
                }
                
                if (defaultWorksheet) {
                    worksheetSelect.value = defaultWorksheet.value;
                    console.log(`Auto-selected default worksheet for Master Ledger ${ledgerType}: ${defaultWorksheet.textContent}`);
                }
            } else {
                worksheetSelect.innerHTML = '<option value="">No worksheets found</option>';
            }
        })
        .catch(error => {
            console.error(`Error loading worksheets for Master Ledger ${ledgerType}:`, error);
            worksheetSelect.innerHTML = '<option value="">Error loading worksheets</option>';
        });
}

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
    fetch(`/get_worksheets/${selectedSheetId}`)
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
    
    if (selectedType === 'interbanking_transfer') {
        // For interbanking transfers, use the Master Ledger A fields
        debitAccountSelect = document.querySelector('select[name="master_ledger_a_debit_account_id"]');
        creditAccountSelect = document.querySelector('select[name="master_ledger_a_credit_account_id"]');
    } else {
        // For regular transactions, use the regular account fields
        debitAccountSelect = document.querySelector('select[name="regular_debit_account_id"]');
        creditAccountSelect = document.querySelector('select[name="regular_credit_account_id"]');
    }
    
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
        // For donations: Debit Indovina Bank (asset increases), Credit Revenue (income)
        if (debitAccountSelect) {
            const bankOption = Array.from(debitAccountSelect.options).find(option => 
                option.textContent.toLowerCase().includes('indovina bank')
            );
            if (bankOption) {
                debitAccountSelect.value = bankOption.value;
                console.log('Auto-selected Indovina Bank for debit (donation received)');
            }
        }
        
        if (creditAccountSelect) {
            const revenueOption = Array.from(creditAccountSelect.options).find(option => 
                option.textContent.toLowerCase().includes('revenue')
            );
            if (revenueOption) {
                creditAccountSelect.value = revenueOption.value;
                console.log('Auto-selected Revenue account for credit (donation):', revenueOption.textContent);
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
        
        // For payments: Debit VN - Expenses, Credit VN - Indovina Bank
        if (debitAccountSelect) {
            // Try exact match first, then partial matches
            let expenseOption = Array.from(debitAccountSelect.options).find(option => 
                option.textContent.trim() === 'VN - Expenses (Nominal Accounts)'
            );
            
            if (!expenseOption) {
                expenseOption = Array.from(debitAccountSelect.options).find(option => 
                    option.textContent.toLowerCase().includes('expenses (nominal accounts)')
                );
            }
            
            if (expenseOption) {
                debitAccountSelect.value = expenseOption.value;
                console.log('✅ Auto-selected VN - Expenses account for payment debit:', expenseOption.textContent);
            }
        }
        
        if (creditAccountSelect) {
            // Try exact match first, then partial matches
            let bankOption = Array.from(creditAccountSelect.options).find(option => 
                option.textContent.trim() === 'VN - Indovina Bank (Real Accounts)'
            );
            
            if (!bankOption) {
                bankOption = Array.from(creditAccountSelect.options).find(option => 
                    option.textContent.toLowerCase().includes('indovina bank (real accounts)')
                );
            }
            
            if (bankOption) {
                creditAccountSelect.value = bankOption.value;
                console.log('✅ Auto-selected VN - Indovina Bank for payment credit:', bankOption.textContent);
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
    } else if (selectedType === 'interbanking_transfer') {
        console.log('🔄 Applying interbanking transfer defaults for Master Ledger A and B...');
        
        // Set defaults for Master Ledger A (typically Belgium)
        const masterLedgerADebitSelect = document.querySelector('select[name="master_ledger_a_debit_account_id"]');
        const masterLedgerACreditSelect = document.querySelector('select[name="master_ledger_a_credit_account_id"]');
        
        if (masterLedgerADebitSelect) {
            const expensesOption = Array.from(masterLedgerADebitSelect.options).find(option => 
                option.textContent.toLowerCase().includes('be') && 
                option.textContent.toLowerCase().includes('expenses')
            );
            if (expensesOption) {
                masterLedgerADebitSelect.value = expensesOption.value;
                console.log('✅ Auto-selected BE-Expenses for Master Ledger A debit:', expensesOption.textContent);
            }
        }
        
        if (masterLedgerACreditSelect) {
            const belfiusOption = Array.from(masterLedgerACreditSelect.options).find(option => 
                option.textContent.toLowerCase().includes('belfius')
            );
            if (belfiusOption) {
                masterLedgerACreditSelect.value = belfiusOption.value;
                console.log('✅ Auto-selected BE-Belfius for Master Ledger A credit:', belfiusOption.textContent);
            }
        }
        
        // Set defaults for Master Ledger B (typically Vietnam)
        const masterLedgerBDebitSelect = document.querySelector('select[name="master_ledger_b_debit_account_id"]');
        const masterLedgerBCreditSelect = document.querySelector('select[name="master_ledger_b_credit_account_id"]');
        
        if (masterLedgerBDebitSelect) {
            const indovinaOption = Array.from(masterLedgerBDebitSelect.options).find(option => 
                option.textContent.toLowerCase().includes('indovina')
            );
            if (indovinaOption) {
                masterLedgerBDebitSelect.value = indovinaOption.value;
                console.log('✅ Auto-selected VN-Indovina Bank for Master Ledger B debit:', indovinaOption.textContent);
            }
        }
        
        if (masterLedgerBCreditSelect) {
            const revenuesOption = Array.from(masterLedgerBCreditSelect.options).find(option => 
                option.textContent.toLowerCase().includes('vn') && 
                option.textContent.toLowerCase().includes('revenues')
            );
            if (revenuesOption) {
                masterLedgerBCreditSelect.value = revenuesOption.value;
                console.log('✅ Auto-selected VN-Revenues for Master Ledger B credit:', revenuesOption.textContent);
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
        // For grants: Debit Bank account (asset increases), Credit Revenue account
        if (debitAccountSelect) {
            const bankOption = Array.from(debitAccountSelect.options).find(option => 
                option.textContent.toLowerCase().includes('bank')
            );
            if (bankOption) {
                debitAccountSelect.value = bankOption.value;
                console.log('Auto-selected Bank account for grant debit');
            }
        }
        
        if (creditAccountSelect) {
            const revenueOption = Array.from(creditAccountSelect.options).find(option => 
                option.textContent.toLowerCase().includes('revenue')
            );
            if (revenueOption) {
                creditAccountSelect.value = revenueOption.value;
                console.log('Auto-selected Revenue account for grant credit');
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
function uploadRedBills() { uploadFile('redBills'); }
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
    
    // Initialize navigation panel
    initializeNavigation();
    
    // Initialize drag and drop functionality
    setupDragAndDrop();
    console.log('Drag and drop functionality initialized');
    
    // Initialize form monitoring for navigation progress
    setupFormMonitoring();
    console.log('Form progress monitoring initialized');
    
    // Add event listeners for all upload buttons
    document.getElementById('billsUploadBtn').addEventListener('click', uploadBills);
    document.getElementById('redBillsUploadBtn').addEventListener('click', uploadRedBills);
    document.getElementById('documentationUploadBtn').addEventListener('click', uploadDocumentation);
    
    // Add event listener for submit button in navigation
    document.getElementById('submitNavBtn').addEventListener('click', function(e) {
        e.preventDefault();
        // Trigger the form submission using the same handler
        const form = document.getElementById('mainForm');
        if (form) {
            // Create a synthetic submit event
            const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
            form.dispatchEvent(submitEvent);
        }
    });
    
    console.log('NGO Accounting System initialized successfully! 🚀');
});
