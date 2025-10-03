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

    fetch('/api/upload_file', { method: 'POST', body: formData })
        .then(response => {
            console.log('Upload response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                return response.text().then(text => {
                    console.error('Non-JSON response:', text);
                    throw new Error('Server returned non-JSON response. This usually indicates a server error.');
                });
            }
            
            return response.json();
        })
        .then(data => {
            uploadProgress.style.display = 'none';
            uploadResult.style.display = 'block';

            console.log('Upload response data:', data);

            if (data.success) {
                fileLink.innerHTML = `<a href="${data.file_url}" target="_blank">${data.file_name}</a>`;
                fileLinkInput.value = data.file_url;   // URL for backend
                fileNameInput.value = data.file_name;  // Label for HYPERLINK
                
                console.log(`${fileType} file uploaded successfully with transaction number:`, transactionNumber);
                console.log('File name:', data.file_name);
            } else {
                fileLink.innerHTML = `<div class="alert alert-error">Error: ${data.error || data.message || 'Unknown error'}</div>`;
            }
        })
        .catch(err => {
            console.error('Upload error:', err);
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

// ============================================================================
// REUSABLE UPLOAD FUNCTION - For both main and update forms
// ============================================================================

/**
 * Universal file upload function that works for both main and update forms
 * @param {Object} config - Configuration object with all necessary parameters
 * @param {string} config.fileInputId - ID of the file input element
 * @param {string} config.transactionNumberId - ID of the transaction number input
 * @param {string} config.documentTypeId - ID of the document type select
 * @param {string} config.progressId - ID of the progress container
 * @param {string} config.progressBarId - ID of the progress bar
 * @param {string} config.progressTextId - ID of the progress text
 * @param {string} config.resultUrlId - ID of the hidden field to store file URL
 * @param {Function} config.showResultFunction - Function to show result messages
 * @param {string} config.formType - 'main' or 'update' for different behaviors
 */
async function universalFileUpload(config) {
    console.log('🚀 DEBUG: universalFileUpload called with config:', config);
    
    const {
        fileInputId,
        transactionNumberId,
        documentTypeId,
        progressId,
        progressBarId,
        progressTextId,
        resultUrlId,
        showResultFunction,
        formType = 'main'
    } = config;
    
    console.log('🚀 DEBUG: Form type:', formType);
    console.log('🚀 DEBUG: Transaction number ID:', transactionNumberId);
    
    // Get DOM elements
    const documentFile = document.getElementById(fileInputId);
    const documentTypeSelect = document.getElementById(documentTypeId);
    const uploadProgress = document.getElementById(progressId);
    const progressBar = document.getElementById(progressBarId);
    const progressText = document.getElementById(progressTextId);
    
    const file = documentFile.files[0];
    const selectedType = documentTypeSelect.value;
    
    if (!file) {
        showResultFunction('Please select a file to upload.', 'error');
        return;
    }
    
    // Get transaction number based on form type
    let transactionNumber;
    if (formType === 'main') {
        transactionNumber = document.getElementById(transactionNumberId).value;
        if (!transactionNumber || transactionNumber === 'Generating...') {
            showResultFunction('Transaction number not ready. Please wait.', 'error');
            return;
        }
    } else if (formType === 'update') {
        transactionNumber = document.getElementById(transactionNumberId).value.trim();
        if (!transactionNumber) {
            showResultFunction('Transaction number not found. Please search for a transaction first.', 'error');
            return;
        }
    }
    
    // Show progress
    uploadProgress.style.display = 'flex';
    progressBar.style.width = '25%';
    progressText.textContent = 'Uploading file...';
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('transaction_number', transactionNumber);
    formData.append('file_type', selectedType);
    
    try {
        console.log('🚀 DEBUG: About to make fetch request to /api/upload_file');
        const response = await fetch('/api/upload_file', {
            method: 'POST',
            body: formData
        });
        
        console.log('🚀 DEBUG: Upload response status:', response.status);
        console.log('🚀 DEBUG: Upload response headers:', response.headers);
        console.log('🚀 DEBUG: Response OK:', response.ok);
        
        // Check if response is OK
        if (!response.ok) {
            console.log('🚀 DEBUG: Response not OK, throwing error');
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        console.log('🚀 DEBUG: Content-Type:', contentType);
        
        if (!contentType || !contentType.includes('application/json')) {
            console.log('🚀 DEBUG: Non-JSON response detected, getting text...');
            return response.text().then(text => {
                console.error('🚀 DEBUG: Non-JSON response text:', text);
                throw new Error('Server returned non-JSON response. This usually indicates a server error.');
            });
        }
        
        console.log('🚀 DEBUG: About to parse JSON response...');
        const data = await response.json();
        console.log('🚀 DEBUG: Parsed JSON data:', data);
        
        progressBar.style.width = '100%';
        progressText.textContent = 'Upload complete!';
        
        console.log('Upload response data:', data);
        
        if (data.success) {
            // Store the file URL in the appropriate hidden field
            if (resultUrlId) {
                document.getElementById(resultUrlId).value = data.file_url;
            }
            
            showResultFunction(`
                <div style="color: #28a745; font-weight: 600;">
                    ✅ File uploaded successfully!
                    <br><strong>File:</strong> ${data.file_name}
                    <br><strong>Type:</strong> ${selectedType}
                    <br><a href="${data.file_url}" target="_blank" style="color: #007bff; text-decoration: underline;">📄 View Document</a>
                    <br><br><strong>Note:</strong> File will be attached when you ${formType === 'main' ? 'submit the form' : 'update the transaction'}.
                </div>
            `, 'success');
            
            // Clear file input
            documentFile.value = '';
        } else {
            showResultFunction(data.error || data.message || 'Upload failed', 'error');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showResultFunction(`Upload failed: ${error.message}`, 'error');
    } finally {
        uploadProgress.style.display = 'none';
        progressBar.style.width = '0%';
    }
}

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
            
            // Get transaction number
            const transactionNumber = data.data?.transaction_number || document.getElementById('transactionNumberDisplay').value;
            
            // Check for uploaded files and automatically attach them
            const billUrl = document.getElementById('uploadedBillUrl').value;
            const redBillUrl = document.getElementById('uploadedRedBillUrl').value;
            const docUrl = document.getElementById('uploadedDocUrl').value;
            
            // Attach files automatically if any were uploaded
            if (billUrl || redBillUrl || docUrl) {
                console.log('Automatically attaching uploaded files to transaction:', transactionNumber);
                
                // Attach files in sequence
                const attachPromises = [];
                if (billUrl) {
                    attachPromises.push(attachFileToTransaction(transactionNumber, 'bill', billUrl, 'vn'));
                }
                if (redBillUrl) {
                    attachPromises.push(attachFileToTransaction(transactionNumber, 'redBill', redBillUrl, 'vn'));
                }
                if (docUrl) {
                    attachPromises.push(attachFileToTransaction(transactionNumber, 'documentation', docUrl, 'vn'));
                }
                
                // Wait for all attachments to complete
                Promise.all(attachPromises)
                    .then(results => {
                        const successful = results.filter(r => r).length;
                        console.log(`Attached ${successful} out of ${results.length} files successfully`);
                    })
                    .catch(error => {
                        console.error('Error attaching files:', error);
                    });
            }
            
            // Reset form
            document.getElementById('mainForm').reset();
            // Clear uploaded file URLs
            document.getElementById('uploadedBillUrl').value = '';
            document.getElementById('uploadedRedBillUrl').value = '';
            document.getElementById('uploadedDocUrl').value = '';
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
        } else{
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
    
    // Old upload buttons removed - now using unified upload system
    
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
    
    // Re-apply colors when funds are refreshed
    const originalRefreshFormData = window.refreshFormData;
    if (originalRefreshFormData) {
        window.refreshFormData = function() {
            const result = originalRefreshFormData.apply(this, arguments);
            // Re-apply colors after form data is refreshed
            setTimeout(applyFundColors, 100);
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

// ============================================================================
// POST-SUBMISSION UPLOAD SYSTEM INTEGRATION
// ============================================================================

/**
 * Show the upload section after successful form submission
 */
function showUploadSection(transactionNumber) {
    const uploadSection = document.getElementById('postSubmissionUploadSection');
    if (uploadSection) {
        uploadSection.style.display = 'block';
        uploadSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // Store the transaction number for upload functions
        window.currentTransactionNumber = transactionNumber;
        console.log('Upload section shown for transaction:', transactionNumber);
    }
}

// ============================================================================
// UNIFIED UPLOAD SYSTEM - MAIN FORM
// ============================================================================

/**
 * Initialize main form upload system
 */
function initializeMainFormUploadSystem() {
    // Upload mode toggle
    const mainUploadModeRadios = document.querySelectorAll('input[name="mainUploadMode"]');
    const mainFileUploadSection = document.getElementById('mainFileUploadSection');
    const mainLinkInputSection = document.getElementById('mainLinkInputSection');
    const mainUploadBtn = document.getElementById('mainUploadBtn');
    
    if (mainUploadModeRadios.length > 0) {
        mainUploadModeRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.value === 'file') {
                    mainFileUploadSection.style.display = 'block';
                    mainLinkInputSection.style.display = 'none';
                    mainUploadBtn.textContent = '📤 Upload to Google Drive';
                    mainUploadBtn.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
                } else if (this.value === 'link') {
                    mainFileUploadSection.style.display = 'none';
                    mainLinkInputSection.style.display = 'block';
                    mainUploadBtn.textContent = '🔗 Process Google Drive Link';
                    mainUploadBtn.style.background = 'linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%)';
                }
            });
        });
    }
    
    // Upload button click handler
    if (mainUploadBtn) {
        mainUploadBtn.addEventListener('click', function() {
            const selectedMode = document.querySelector('input[name="mainUploadMode"]:checked').value;
            
            if (selectedMode === 'file') {
                handleMainFormFileUpload();
            } else if (this.value === 'link') {
                handleMainFormLinkUpload();
            }
        });
    }
}

/**
 * Handle file upload for main form - Now uses universal function
 */
async function handleMainFormFileUpload() {
    const selectedType = document.getElementById('mainDocumentTypeSelect').value;
    
    // Determine which hidden field to store the URL based on document type
    let resultUrlId;
    if (selectedType === 'bill') {
        resultUrlId = 'uploadedBillUrl';
    } else if (selectedType === 'redBill') {
        resultUrlId = 'uploadedRedBillUrl';
    } else if (selectedType === 'documentation') {
        resultUrlId = 'uploadedDocUrl';
    }
    
    // Use the universal upload function with main form configuration
    await universalFileUpload({
        fileInputId: 'mainDocumentFile',
        transactionNumberId: 'transactionNumberDisplay',
        documentTypeId: 'mainDocumentTypeSelect',
        progressId: 'mainUploadProgress',
        progressBarId: 'mainProgressBar',
        progressTextId: 'mainProgressText',
        resultUrlId: resultUrlId,
        showResultFunction: showMainUploadResult,
        formType: 'main'
    });
}

/**
 * Handle Google Drive link for main form
 */
async function handleMainFormLinkUpload() {
    const googleDriveLink = document.getElementById('mainGoogleDriveLink').value.trim();
    const documentTypeSelect = document.getElementById('mainDocumentTypeSelect');
    const uploadProgress = document.getElementById('mainUploadProgress');
    const progressBar = document.getElementById('mainProgressBar');
    
    if (!googleDriveLink) {
        showMainUploadResult('Please enter a Google Drive URL.', 'error');
        return;
    }
    
    const transactionNumber = document.getElementById('transactionNumberDisplay').value;
    if (!transactionNumber || transactionNumber === 'Generating...') {
        showMainUploadResult('Transaction number not ready. Please wait.', 'error');
        return;
    }
    
    const selectedType = documentTypeSelect.value;
    
    // Show progress
    uploadProgress.style.display = 'flex';
    progressBar.style.width = '25%';
    
    try {
        const response = await fetch('/api/process_google_drive_link', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                google_drive_url: googleDriveLink,
                document_type: selectedType,
                transaction_number: transactionNumber
            })
        });
        
        const data = await response.json();
        
        progressBar.style.width = '100%';
        
        if (data.success) {
            // Store the file URL in hidden field based on document type
            if (selectedType === 'bill') {
                document.getElementById('uploadedBillUrl').value = data.file_url;
            } else if (selectedType === 'redBill') {
                document.getElementById('uploadedRedBillUrl').value = data.file_url;
            } else if (selectedType === 'documentation') {
                document.getElementById('uploadedDocUrl').value = data.file_url;
            }
            
            showMainUploadResult(`
                <div style="color: #28a745; font-weight: 600;">
                    ✅ Google Drive link processed successfully!
                    <br><strong>File:</strong> ${data.file_name}
                    <br><strong>Type:</strong> ${selectedType}
                    <br><a href="${data.file_url}" target="_blank" style="color: #007bff; text-decoration: underline;">📄 View Document</a>
                    <br><br><strong>Note:</strong> File will be attached when you submit the form.
                </div>
            `, 'success');
            
            // Clear link input
            document.getElementById('mainGoogleDriveLink').value = '';
        } else {
            showMainUploadResult(data.message || 'Failed to process Google Drive link', 'error');
        }
    } catch (error) {
        console.error('Google Drive link processing error:', error);
        showMainUploadResult('Failed to process Google Drive link. Please try again.', 'error');
    } finally {
        uploadProgress.style.display = 'none';
        progressBar.style.width = '0%';
    }
}

/**
 * Show upload result for main form
 */
function showMainUploadResult(message, type) {
    const uploadResult = document.getElementById('mainUploadResult');
    if (uploadResult) {
        uploadResult.innerHTML = `
            <div style="padding: 15px; border-radius: 6px; margin-top: 15px; ${type === 'success' ? 'background: #d4edda; border: 1px solid #c3e6cb; color: #155724;' : 'background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24;'}">
                ${message}
            </div>
        `;
        uploadResult.style.display = 'block';
    }
}

// ============================================================================
// UNIFIED UPLOAD SYSTEM - UPDATE FORM
// ============================================================================

/**
 * Initialize update form upload system
 */
function initializeUpdateFormUploadSystem() {
    // Upload mode toggle
    const updateUploadModeRadios = document.querySelectorAll('input[name="updateUploadMode"]');
    const updateFileUploadSection = document.getElementById('updateFileUploadSection');
    const updateLinkInputSection = document.getElementById('updateLinkInputSection');
    const updateUploadBtn = document.getElementById('updateUploadBtn');
    
    if (updateUploadModeRadios.length > 0) {
        updateUploadModeRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.value === 'file') {
                    updateFileUploadSection.style.display = 'block';
                    updateLinkInputSection.style.display = 'none';
                    updateUploadBtn.textContent = '📤 Upload to Google Drive';
                    updateUploadBtn.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
                } else if (this.value === 'link') {
                    updateFileUploadSection.style.display = 'none';
                    updateLinkInputSection.style.display = 'block';
                    updateUploadBtn.textContent = '🔗 Process Google Drive Link';
                    updateUploadBtn.style.background = 'linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%)';
                }
            });
        });
    }
    
    // Upload button click handler
    if (updateUploadBtn) {
        updateUploadBtn.addEventListener('click', function() {
            const selectedMode = document.querySelector('input[name="updateUploadMode"]:checked')?.value;
            
            if (selectedMode === 'file') {
                handleUpdateFormFileUpload();
            } else if (selectedMode === 'link') {
                handleUpdateFormLinkUpload();
            }
        });
    }
    
    // Update transaction button click handler
    const updateTransactionBtn = document.getElementById('updateTransactionBtn');
    if (updateTransactionBtn) {
        updateTransactionBtn.addEventListener('click', function() {
            handleUpdateFormSubmit();
        });
    }
}

/**
 * Handle file upload for update form - Now uses universal function
 */
async function handleUpdateFormFileUpload() {
    console.log('🚀 DEBUG: handleUpdateFormFileUpload called - using NEW universal function');
    
    const selectedType = document.getElementById('updateDocumentTypeSelect').value;
    console.log('🚀 DEBUG: Selected type:', selectedType);
    
    // Determine which hidden field to store the URL based on document type
    let resultUrlId;
    if (selectedType === 'bill') {
        resultUrlId = 'updateUploadedBillUrl';
    } else if (selectedType === 'redBill') {
        resultUrlId = 'updateUploadedRedBillUrl';
    } else if (selectedType === 'documentation') {
        resultUrlId = 'updateUploadedDocUrl';
    }
    
    console.log('🚀 DEBUG: Result URL ID:', resultUrlId);
    console.log('🚀 DEBUG: About to call universalFileUpload with config...');
    
    // Use the universal upload function with update form configuration
    await universalFileUpload({
        fileInputId: 'updateDocumentFile',
        transactionNumberId: 'searchTransactionNumber',
        documentTypeId: 'updateDocumentTypeSelect',
        progressId: 'updateUploadProgress',
        progressBarId: 'updateProgressBar',
        progressTextId: 'updateProgressText',
        resultUrlId: resultUrlId,
        showResultFunction: showUpdateUploadResult,
        formType: 'update'
    });
    
    console.log('🚀 DEBUG: universalFileUpload completed');
}

/**
 * Handle Google Drive link for update form
 */
async function handleUpdateFormLinkUpload() {
    const googleDriveLink = document.getElementById('updateGoogleDriveLink').value.trim();
    const documentTypeSelect = document.getElementById('updateDocumentTypeSelect');
    const uploadProgress = document.getElementById('updateUploadProgress');
    const progressBar = document.getElementById('updateProgressBar');
    
    if (!googleDriveLink) {
        showUpdateUploadResult('Please enter a Google Drive URL.', 'error');
        return;
    }
    
    // Get transaction number from search
    const transactionNumber = document.getElementById('searchTransactionNumber').value.trim();
    if (!transactionNumber) {
        showUpdateUploadResult('Transaction number not found. Please search for a transaction first.', 'error');
        return;
    }
    
    const selectedType = documentTypeSelect.value;
    
    // Show progress
    uploadProgress.style.display = 'flex';
    progressBar.style.width = '25%';
    
    try {
        const response = await fetch('/api/process_google_drive_link', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                google_drive_url: googleDriveLink,
                document_type: selectedType,
                transaction_number: transactionNumber
            })
        });
        
        const data = await response.json();
        
        progressBar.style.width = '100%';
        
        if (data.success) {
            // Store the file URL in hidden field based on document type
            if (selectedType === 'bill') {
                document.getElementById('updateUploadedBillUrl').value = data.file_url;
            } else if (selectedType === 'redBill') {
                document.getElementById('updateUploadedRedBillUrl').value = data.file_url;
            } else if (selectedType === 'documentation') {
                document.getElementById('updateUploadedDocUrl').value = data.file_url;
            }
            
            showUpdateUploadResult(`
                <div style="color: #28a745; font-weight: 600;">
                    ✅ Google Drive link processed successfully!
                    <br><strong>File:</strong> ${data.file_name}
                    <br><strong>Type:</strong> ${selectedType}
                    <br><a href="${data.file_url}" target="_blank" style="color: #007bff; text-decoration: underline;">📄 View Document</a>
                    <br><br><strong>Note:</strong> File will be attached when you click "Update Transaction".
                </div>
            `, 'success');
            
            // Clear link input
            document.getElementById('updateGoogleDriveLink').value = '';
        } else {
            showUpdateUploadResult(data.message || 'Failed to process Google Drive link', 'error');
        }
    } catch (error) {
        console.error('Google Drive link processing error:', error);
        showUpdateUploadResult('Failed to process Google Drive link. Please try again.', 'error');
    } finally {
        uploadProgress.style.display = 'none';
        progressBar.style.width = '0%';
    }
}

/**
 * Handle update form submission
 */
async function handleUpdateFormSubmit() {
    // Get transaction number from search
    const transactionNumber = document.getElementById('searchTransactionNumber').value.trim();
    const sheetType = document.getElementById('searchSheet').value;
    
    if (!transactionNumber) {
        showUpdateUploadResult('Transaction number not found. Please search for a transaction first.', 'error');
        return;
    }
    
    // Get uploaded file URLs
    const billUrl = document.getElementById('updateUploadedBillUrl').value;
    const redBillUrl = document.getElementById('updateUploadedRedBillUrl').value;
    const docUrl = document.getElementById('updateUploadedDocUrl').value;
    
    if (!billUrl && !redBillUrl && !docUrl) {
        showUpdateUploadResult('No files uploaded. Please upload at least one file.', 'error');
        return;
    }
    
    // Show loading state
    const updateBtn = document.getElementById('updateTransactionBtn');
    const originalText = updateBtn.textContent;
    updateBtn.disabled = true;
    updateBtn.textContent = '🔄 Updating...';
    
    // Attach files in sequence
    const attachPromises = [];
    if (billUrl) {
        attachPromises.push(attachFileToTransaction(transactionNumber, 'bill', billUrl, sheetType));
    }
    if (redBillUrl) {
        attachPromises.push(attachFileToTransaction(transactionNumber, 'redBill', redBillUrl, sheetType));
    }
    if (docUrl) {
        attachPromises.push(attachFileToTransaction(transactionNumber, 'documentation', docUrl, sheetType));
    }
    
    try {
        const results = await Promise.all(attachPromises);
        const successful = results.filter(r => r).length;
        
        if (successful > 0) {
            showUpdateUploadResult(`
                <div style="color: #28a745; font-weight: 600;">
                    ✅ Successfully attached ${successful} out of ${results.length} files to transaction ${transactionNumber}!
                    <br><br>Your transaction has been updated in Google Sheets.
                </div>
            `, 'success');
            
            // Clear uploaded file URLs
            document.getElementById('updateUploadedBillUrl').value = '';
            document.getElementById('updateUploadedRedBillUrl').value = '';
            document.getElementById('updateUploadedDocUrl').value = '';
        } else {
            showUpdateUploadResult('Failed to attach files. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Error attaching files:', error);
        showUpdateUploadResult('Error attaching files. Please try again.', 'error');
    } finally {
        // Reset button state
        updateBtn.disabled = false;
        updateBtn.textContent = originalText;
    }
}

/**
 * Show upload result for update form
 */
function showUpdateUploadResult(message, type) {
    const uploadResult = document.getElementById('updateUploadResult');
    if (uploadResult) {
        uploadResult.innerHTML = `
            <div style="padding: 15px; border-radius: 6px; margin-top: 15px; ${type === 'success' ? 'background: #d4edda; border: 1px solid #c3e6cb; color: #155724;' : 'background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24;'}">
                ${message}
            </div>
        `;
        uploadResult.style.display = 'block';
    }
}

// Removed duplicate handleFormSubmit function - using the original one with upload integration

/**
 * Initialize upload system event listeners
 */
function initializeUploadSystem() {
    // Upload mode toggle
    const uploadModeRadios = document.querySelectorAll('input[name="uploadMode"]');
    const fileUploadSection = document.getElementById('fileUploadSection');
    const linkInputSection = document.getElementById('linkInputSection');
    const uploadBtn = document.getElementById('uploadBtn');
    
    if (uploadModeRadios.length > 0) {
        uploadModeRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.value === 'file') {
                    fileUploadSection.style.display = 'block';
                    linkInputSection.style.display = 'none';
                    uploadBtn.textContent = '📤 Upload to Google Drive';
                    uploadBtn.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
                } else if (this.value === 'link') {
                    fileUploadSection.style.display = 'none';
                    linkInputSection.style.display = 'block';
                    uploadBtn.textContent = '🔗 Process Google Drive Link';
                    uploadBtn.style.background = 'linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%)';
                }
            });
        });
    }
    
    // Upload button click handler
    if (uploadBtn) {
        uploadBtn.addEventListener('click', function() {
            const selectedMode = document.querySelector('input[name="uploadMode"]:checked').value;
            
            if (selectedMode === 'file') {
                handleDocumentUpload();
            } else if (selectedMode === 'link') {
                handleGoogleDriveLink();
            }
        });
    }
    
    // Google Sheets update button
    const updateSheetsBtn = document.getElementById('updateSheetsBtn');
    if (updateSheetsBtn) {
        updateSheetsBtn.addEventListener('click', function() {
            handleGoogleSheetsUpdate();
        });
    }
}

/**
 * Handle document upload (from update form)
 */
function handleDocumentUpload() {
    const documentTypeSelect = document.getElementById('documentTypeSelect');
    const documentFile = document.getElementById('documentFile');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadProgress = document.getElementById('uploadProgress');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    
    const selectedType = documentTypeSelect.value;
    const file = documentFile.files[0];
    
    if (!file) {
        showUploadResult('Please select a file to upload.', 'error');
        return;
    }
    
    if (!window.currentTransactionNumber) {
        showUploadResult('Transaction number not found. Please refresh the page.', 'error');
        return;
    }
    
    // Show progress
    uploadProgress.style.display = 'flex';
    progressBar.style.width = '25%';
    progressText.textContent = 'Uploading file...';
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('transaction_number', window.currentTransactionNumber);
    formData.append('file_type', selectedType);
    
    fetch('/api/upload_file', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        console.log('Upload response status:', response.status);
        console.log('Upload response headers:', response.headers);
        
        // Check if response is ok
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            return response.text().then(text => {
                console.error('Non-JSON response:', text);
                throw new Error('Server returned non-JSON response. This usually indicates a server error.');
            });
        }
        
        return response.json();
    })
    .then(data => {
        progressBar.style.width = '75%';
        progressText.textContent = 'Processing file...';
        
        console.log('Upload response data:', data);
        
        if (data.success) {
            progressBar.style.width = '100%';
            progressText.textContent = 'Upload complete!';
            
            showUploadResult(`
                <div style="color: #28a745; font-weight: 600;">
                    ✅ File uploaded to Google Drive successfully!
                    <br><strong>File:</strong> ${data.file_name}
                    <br><strong>Type:</strong> ${selectedType}
                    <br><a href="${data.file_url}" target="_blank" style="color: #007bff; text-decoration: underline;">📄 View Document</a>
                    <br><br><strong>Next Step:</strong> Click "Update Google Sheets" to add the document link to your transaction.
                </div>
            `, 'success');
            
            // Show the Google Sheets update button
            const updateSheetsBtn = document.getElementById('updateSheetsBtn');
            if (updateSheetsBtn) {
                updateSheetsBtn.style.display = 'inline-block';
            }
            
        } else {
            showUploadResult(data.error || data.message || 'Upload failed', 'error');
        }
    })
    .catch(error => {
        console.error('Upload error:', error);
        showUploadResult(`Upload failed: ${error.message}`, 'error');
    })
    .finally(() => {
        uploadProgress.style.display = 'none';
        progressBar.style.width = '0%';
    });
}

/**
 * Handle Google Drive link processing (from update form)
 */
async function handleGoogleDriveLink() {
    const googleDriveLink = document.getElementById('googleDriveLink').value.trim();
    const documentTypeSelect = document.getElementById('documentTypeSelect');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadProgress = document.getElementById('uploadProgress');
    const progressBar = document.getElementById('progressBar');
    
    if (!googleDriveLink) {
        showUploadResult('Please enter a Google Drive URL.', 'error');
        return;
    }
    
    if (!window.currentTransactionNumber) {
        showUploadResult('Transaction number not found. Please refresh the page.', 'error');
        return;
    }
    
    const selectedType = documentTypeSelect.value;
    
    // Show progress
    uploadProgress.style.display = 'flex';
    progressBar.style.width = '25%';
    
    try {
        // Call backend to process the Google Drive link
        const response = await fetch('/api/process_google_drive_link', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                google_drive_url: googleDriveLink,
                document_type: selectedType,
                transaction_number: window.currentTransactionNumber
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            progressBar.style.width = '100%';
            
            showUploadResult(`
                <div style="color: #28a745; font-weight: 600;">
                    ✅ Google Drive link processed successfully!
                    <br><strong>File:</strong> ${data.file_name}
                    <br><strong>Type:</strong> ${selectedType}
                    <br><a href="${data.file_url}" target="_blank" style="color: #007bff; text-decoration: underline;">📄 View Document</a>
                    <br><br><strong>Next Step:</strong> Click "Update Google Sheets" to add the document link to your transaction.
                </div>
            `, 'success');
            
            // Show the Google Sheets update button
            const updateSheetsBtn = document.getElementById('updateSheetsBtn');
            if (updateSheetsBtn) {
                updateSheetsBtn.style.display = 'inline-block';
            }
            
        } else {
            showUploadResult(data.message || 'Failed to process Google Drive link', 'error');
        }
    } catch (error) {
        console.error('Google Drive link processing error:', error);
        showUploadResult('Failed to process Google Drive link. Please try again.', 'error');
    } finally {
        uploadProgress.style.display = 'none';
        progressBar.style.width = '0%';
    }
}

/**
 * Handle Google Sheets update (from update form)
 */
function handleGoogleSheetsUpdate() {
    const documentTypeSelect = document.getElementById('documentTypeSelect');
    const selectedType = documentTypeSelect.value;
    
    if (!window.currentTransactionNumber) {
        showUploadResult('Transaction number not found. Please refresh the page.', 'error');
        return;
    }
    
    // Get the file URL from the upload result
    const uploadResult = document.getElementById('uploadResult');
    const fileLink = uploadResult.querySelector('a[href]');
    
    if (!fileLink) {
        showUploadResult('No file link found. Please upload a file first.', 'error');
        return;
    }
    
    const fileUrl = fileLink.href;
    
    console.log(`DEBUG: Starting Google Sheets update for transaction: ${window.currentTransactionNumber}`);
    console.log(`DEBUG: Document type: ${selectedType}`);
    console.log(`DEBUG: File URL: ${fileUrl}`);
    
    // Show loading state
    const updateSheetsBtn = document.getElementById('updateSheetsBtn');
    if (updateSheetsBtn) {
        updateSheetsBtn.disabled = true;
        updateSheetsBtn.textContent = '🔄 Updating...';
    }
    
    // Call the Google Sheets update API
    updateGoogleSheetsDocument(window.currentTransactionNumber, selectedType, fileUrl);
}

/**
 * Update Google Sheets with document link (from update form)
 */
function updateGoogleSheetsDocument(transactionNumber, documentType, fileUrl) {
    // Get the current sheet type (default to 'vn' for main form)
    const sheetType = 'vn'; // Main form always uses Vietnamese sheet
    
    console.log(`DEBUG: Updating Google Sheets - Transaction: ${transactionNumber}, Type: ${documentType}, Sheet: ${sheetType}, URL: ${fileUrl}`);
    
    // Call the document update API
    fetch('/api/update_document', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            sheet_type: sheetType,
            transaction_number: transactionNumber,
            document_type: documentType,
            file_url: fileUrl
        })
    })
    .then(response => response.json())
    .then(data => {
        const updateSheetsBtn = document.getElementById('updateSheetsBtn');
        
        if (data.success) {
            showUploadResult(`
                <div style="color: #28a745; font-weight: 600;">
                    ✅ Document link added to Google Sheets successfully!
                    <br><strong>Transaction:</strong> ${transactionNumber}
                    <br><strong>Column:</strong> ${documentType === 'bill' ? 'Bill (O)' : documentType === 'redBill' ? 'Red Bill (P)' : 'Doc (Q)'}
                    <br><br>Your transaction now has the document attached!
                </div>
            `, 'success');
            
            // Hide the update button
            if (updateSheetsBtn) {
                updateSheetsBtn.style.display = 'none';
            }
            
        } else {
            showUploadResult(data.message || 'Failed to update Google Sheets', 'error');
            
            // Reset button
            if (updateSheetsBtn) {
                updateSheetsBtn.disabled = false;
                updateSheetsBtn.textContent = '📊 Update Google Sheets';
            }
        }
    })
    .catch(error => {
        console.error('Google Sheets update error:', error);
        showUploadResult('Failed to update Google Sheets. Please try again.', 'error');
        
        // Reset button
        const updateSheetsBtn = document.getElementById('updateSheetsBtn');
        if (updateSheetsBtn) {
            updateSheetsBtn.disabled = false;
            updateSheetsBtn.textContent = '📊 Update Google Sheets';
        }
    });
}

/**
 * Show upload result message
 */
function showUploadResult(message, type) {
    const uploadResult = document.getElementById('uploadResult');
    if (uploadResult) {
        uploadResult.innerHTML = `
            <div style="padding: 15px; border-radius: 6px; margin-top: 15px; ${type === 'success' ? 'background: #d4edda; border: 1px solid #c3e6cb; color: #155724;' : 'background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24;'}">
                ${message}
            </div>
        `;
        uploadResult.style.display = 'block';
    }
}

/**
 * Attach file to transaction in Google Sheets
 */
async function attachFileToTransaction(transactionNumber, documentType, fileUrl, sheetType = 'vn') {
    try {
        console.log(`Attaching ${documentType} to transaction ${transactionNumber}`);
        
        const response = await fetch('/api/update_document', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                sheet_type: sheetType,
                transaction_number: transactionNumber,
                document_type: documentType,
                file_url: fileUrl
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log(`✅ Successfully attached ${documentType} to transaction ${transactionNumber}`);
            return true;
        } else {
            console.error(`❌ Failed to attach ${documentType}:`, data.message);
            return false;
        }
    } catch (error) {
        console.error(`Error attaching ${documentType}:`, error);
        return false;
    }
}

// Initialize upload system when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize main form upload system
    initializeMainFormUploadSystem();
    
    // Initialize update form upload system (if it exists)
    initializeUpdateFormUploadSystem();
    
    // Initialize original upload system (for backward compatibility)
    initializeUploadSystem();
});
