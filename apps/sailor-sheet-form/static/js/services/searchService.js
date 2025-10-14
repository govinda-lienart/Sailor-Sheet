/**
 * Search Service
 * Handles transaction search and display functionality
 */

/**
 * Search for a transaction
 */
export function searchTransaction() {
    const transactionNumber = document.getElementById('searchTransactionNumber').value.trim();
    const selectedSheet = document.getElementById('searchSheet').value;
    const searchResults = document.getElementById('searchResults');
    
    if (!transactionNumber) {
        alert('Please enter a transaction number to search');
        return;
    }
    
    // Show loading state
    searchResults.style.display = 'block';
    searchResults.innerHTML = `
        <div class="alert alert-info">
            <strong>🔍 Searching for: ${transactionNumber}</strong>
            <p>Searching in ${selectedSheet === 'vn' ? 'Vietnamese' : 'Belgian'} Master Ledger...</p>
            <p><em>Please wait while we retrieve the transaction data...</em></p>
        </div>
    `;
    
    // Call the API
    fetch('/api/search_transaction', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            sheet_type: selectedSheet,
            transaction_number: transactionNumber
        })
    })
    .then(response => {
        console.log('Response status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('API Response received:', data);
        
        if (data && data.success) {
            console.log('Transaction data received:', data.data);
            
            // Store the transaction number for later use in file uploads
            const transactionNumberFromData = data.data['Transaction Number'];
            if (transactionNumberFromData) {
                console.log(`Storing transaction number for uploads: "${transactionNumberFromData}"`);
                if (searchResults) {
                    searchResults.setAttribute('data-transaction-number', transactionNumberFromData);
                }
                sessionStorage.setItem('currentTransactionNumber', transactionNumberFromData);
            }
            
            displayTransactionDetails(data.data);
        } else {
            console.log('Search failed or no data:', data);
            searchResults.innerHTML = `
                <div class="alert alert-danger">
                    <strong>❌ Search Failed</strong>
                    <p>${data ? data.error : 'No response data'}</p>
                </div>
            `;
        }
    })
    .catch(error => {
        console.error('Search error:', error);
        if (searchResults) {
            searchResults.innerHTML = `
                <div class="alert alert-danger">
                    <strong>❌ Error</strong>
                    <p>Search failed: ${error.message}</p>
                    <p>Check console for details.</p>
                </div>
            `;
        }
    });
    
    console.log('🔍 Searching for transaction:', transactionNumber, 'in sheet:', selectedSheet);
}

/**
 * Display transaction details
 */
function displayTransactionDetails(transactionData) {
    console.log('=== DISPLAY TRANSACTION DETAILS ===');
    console.log('Function called with data:', transactionData);
    
    const updateFormContainer = document.getElementById('updateFormContainer');
    const searchResults = document.getElementById('searchResults');
    
    if (!updateFormContainer || !searchResults) {
        console.error('Required elements not found');
        return;
    }
    
    // Make form visible
    updateFormContainer.style.display = 'block';
    
    // Show success message and prepare details container
    searchResults.style.display = 'block';
    searchResults.innerHTML = `
        <div class="alert alert-success">
            <strong>✅ Transaction Found!</strong>
            <p>Transaction details retrieved successfully. Ready for document updates.</p>
        </div>
        
        <div id="transactionDetails" class="transaction-details-table"></div>
    `;
    
    // Wait for DOM update then populate table
    setTimeout(() => {
        const transactionDetails = document.getElementById('transactionDetails');
        if (transactionDetails) {
            displayTransactionTable(transactionData, transactionDetails);
        }
    }, 50);
}

/**
 * Display transaction table
 */
function displayTransactionTable(transactionData, transactionDetails) {
    console.log('Creating transaction table with data:', transactionData);
    
    // Extract account information
    const debitAccount = transactionData['Debit Account'] || 'Not specified';
    const creditAccount = transactionData['Credit Account'] || 'Not specified';
    
    // Create accounts header
    const accountsHeader = `
        <div style="margin-bottom: 15px; padding: 10px; background: #f8f9fa; border-radius: 6px;">
            <h4 style="margin: 0 0 8px 0; color: #495057; font-size: 1.1em;">Accounts Involved in this Transaction:</h4>
            <div style="display: flex; gap: 20px; align-items: center; flex-wrap: wrap;">
                <span><strong style="color: #dc3545;">Debit:</strong> ${debitAccount}</span>
                <span style="color: #6c757d;">↔️</span>
                <span><strong style="color: #28a745;">Credit:</strong> ${creditAccount}</span>
            </div>
        </div>
    `;
    
    // Define column order matching Google Sheets
    const columnOrder = [
        'Transaction Number', 'dd/mm/YY', 'Month', 'Year', 'Funds', 
        'Account', 'Category', 'Debit (VND)', 'Credit (VND)', 
        'Payment Method', 'Description', 'Bank Transaction Number', 
        'Bill', 'Red Bill', 'Documentation'
    ];
    
    // Build table HTML
    let tableHTML = `
        <div class="double-entry-container">
            <h3 style="color: #007bff; margin-bottom: 15px;">📊 Double-Entry Transaction Details</h3>
            ${accountsHeader}
            <table class="transaction-details-styled">
                <thead>
                    <tr>
                        <th style="background: #495057; color: white;">Field</th>
                        <th style="background: #dc3545; color: white;">Debit Details</th>
                        <th style="background: #28a745; color: white;">Credit Details</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    // Add rows for each column
    columnOrder.forEach(field => {
        const debitValue = transactionData[field] || '—';
        const creditValue = transactionData[field] || '—';
        
        tableHTML += `
            <tr>
                <td style="font-weight: 600;">${formatFieldName(field)}</td>
                <td>${formatDocumentField(field, debitValue)}</td>
                <td>${formatDocumentField(field, creditValue)}</td>
            </tr>
        `;
    });
    
    tableHTML += `
                </tbody>
            </table>
        </div>
    `;
    
    transactionDetails.innerHTML = tableHTML;
}

/**
 * Format field name for display
 */
function formatFieldName(fieldName) {
    const nameMap = {
        'dd/mm/YY': 'Date',
        'Debit (VND)': 'Debit Amount',
        'Credit (VND)': 'Credit Amount'
    };
    return nameMap[fieldName] || fieldName;
}

/**
 * Format document field value
 */
function formatDocumentField(field, value) {
    if (!value || value === '—' || value === '') {
        return '—';
    }
    
    // Handle document fields with checkmarks
    if (field === 'Bill' || field === 'Red Bill' || field === 'Documentation') {
        if (value.includes('✔') || value.toLowerCase().includes('available')) {
            return '✔ Available (see sheet)';
        }
    }
    
    return value;
}

/**
 * Initialize search functionality
 */
export function initializeSearch() {
    const searchBtn = document.getElementById('searchTransactionBtn');
    if (searchBtn) {
        searchBtn.addEventListener('click', searchTransaction);
        console.log('✅ Search service initialized');
    }
}

// Expose to global scope for compatibility
window.searchTransaction = searchTransaction;

