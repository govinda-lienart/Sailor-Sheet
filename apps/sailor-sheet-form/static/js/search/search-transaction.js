// Transaction Search Module - Search for and display transaction details
// Extracted from inline script - Step 6 of incremental refactoring

(function() {
    'use strict';
    
    // Helper function to format field names
    function formatFieldName(fieldName) {
        // Convert field names to readable format
        const fieldMap = {
            'Transaction Number': 'Transaction Number',
            'dd/mm/YY': 'Dd/Mm/YY',
            'Date': 'Date',
            'Type': 'Type',
            'Amount': 'Amount',
            'Fund': 'Fund',
            'Funds': 'Funds',
            'Category': 'Category',
            'Debit (VND)': 'Debit (VND)',
            'Credit (VND)': 'Credit (VND)',
            'Debit Account': 'Debit Account',
            'Credit Account': 'Credit Account',
            'Description': 'Description',
            'Payment Method': 'Payment Method',
            'Bank Transaction Number': 'Bank Transaction Number',
            'Bill': 'Bill',
            'Red BIll': 'Red Bill',
            'Red Bills': 'Red Bills',
            'Doc': 'Documentation',
            'Documentation': 'Documentation'
        };
        
        return fieldMap[fieldName] || fieldName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
    
    // Format document fields for display
    function formatDocumentField(field, value) {
        const docFields = new Set(['Bill', 'Red BIll', 'Doc']);
        
        if (docFields.has(field)) {
            if (!value || value.trim() === '') {
                return '—';
            } else if (typeof value === 'string' && (value.startsWith('http') || value.startsWith('https'))) {
                return `<a href="${value}" target="_blank" style="color: #007bff; text-decoration: underline;">📄 View Document</a>`;
            } else if (value === '✔') {
                return '✔ Available (see sheet)';
            } else {
                return `📄 ${value}`;
            }
        }
        
        return value || '—';
    }
    
    // Create three-column layout for double-entry bookkeeping
    function createThreeColumnLayout(transactionData) {
        console.log('Creating three-column layout with data:', transactionData);
        console.log('Available fields:', Object.keys(transactionData));
        console.log('Debit Account:', transactionData['Debit Account']);
        console.log('Credit Account:', transactionData['Credit Account']);
        console.log('Debit (VND):', transactionData['Debit (VND)']);
        console.log('Credit (VND):', transactionData['Credit (VND)']);
        
        // Define the fields to show in order
        const fieldsToShow = [
            'Transaction Number',
            'dd/mm/YY',
            'Month', 
            'Year',
            'Funds',
            'Account',
            'Category',
            'Debit (VND)',
            'Credit (VND)',
            'Payment Method',
            'Description',
            'Bank Transaction Number',
            'Bill',
            'Red BIll',
            'Doc'
        ];
        
        let rows = '';
        
        for (const field of fieldsToShow) {
            const fieldLabel = formatFieldName(field);
            const rawValue = transactionData[field] || '';
            
            // Handle special cases for debit/credit display
            let debitValue = '';
            let creditValue = '';
            
            if (field === 'Account') {
                // Show the specific accounts for debit and credit
                debitValue = transactionData['Debit Account'] || '—';
                creditValue = transactionData['Credit Account'] || '—';
            } else if (field === 'Debit (VND)') {
                // Show debit amount in debit column, empty in credit column
                debitValue = transactionData['Debit (VND)'] || '—';
                creditValue = '—';
            } else if (field === 'Credit (VND)') {
                // Show credit amount in credit column, empty in debit column
                debitValue = '—';
                creditValue = transactionData['Credit (VND)'] || '—';
            } else if (field === 'Bill') {
                // Show separate bill data for debit and credit sides
                debitValue = formatDocumentField(field, transactionData['Debit Bill'] || '');
                creditValue = formatDocumentField(field, transactionData['Credit Bill'] || '');
            } else if (field === 'Red BIll') {
                // Show separate red bill data for debit and credit sides
                debitValue = formatDocumentField(field, transactionData['Debit Red Bill'] || '');
                creditValue = formatDocumentField(field, transactionData['Credit Red Bill'] || '');
            } else if (field === 'Doc') {
                // Show separate doc data for debit and credit sides
                debitValue = formatDocumentField(field, transactionData['Debit Doc'] || '');
                creditValue = formatDocumentField(field, transactionData['Credit Doc'] || '');
            } else {
                // For all other fields, show the same value in both columns
                const displayValue = formatDocumentField(field, rawValue);
                debitValue = displayValue;
                creditValue = displayValue;
            }
            
            rows += `
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 10px; border: 1px solid #ddd; background: #f8f9fa; font-weight: bold;">${fieldLabel}</td>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: center; background: #fff5f5;">${debitValue}</td>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: center; background: #f0fff4;">${creditValue}</td>
                </tr>
            `;
        }
        
        return rows;
    }
    
    // Separate function to display the transaction table
    function displayTransactionTable(transactionData, transactionDetails) {
        console.log('Creating transaction table with data:', transactionData);
        console.log('Available field names:', Object.keys(transactionData));
        
        // Extract debit and credit account information
        console.log('=== EXTRACTING ACCOUNTS ===');
        console.log('Transaction data keys:', Object.keys(transactionData));
        console.log('Full transaction data:', transactionData);
        
        // Use the accounts that were identified by the backend
        const debitAccount = transactionData['Debit Account'] || 'Not specified';
        const creditAccount = transactionData['Credit Account'] || 'Not specified';
        
        console.log('Debit Account from backend:', debitAccount);
        console.log('Credit Account from backend:', creditAccount);
        
        // Create simple accounts header
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
        
        // Create table rows in the exact same order as Google Sheets columns
        const columnOrder = [
            'Transaction Number',    // Column A
            'dd/mm/YY',             // Column B (exact field name from headers)
            'Month',                // Column C
            'Year',                 // Column D
            'Funds',                // Column E
            'Account',              // Column F
            'Category',             // Column G
            'Debit (VND)',          // Column H
            'Credit (VND)',         // Column I
            'Payment Method',        // Column K (Payment)
            'Description',          // Column L
            'Bank Transaction Number', // Column M (Bank Transaction)
            'Bill',                 // Column N (Normal Bill)
            'Red BIll',             // Column O (Red Bill - note the capital I)
            'Doc'                   // Column P (Supporting Documentation)
        ];
        
        let tableRows = '';
        
        // First, add fields in the specified column order
        for (const field of columnOrder) {
            const docFields = new Set(['Bill', 'Red BIll', 'Doc']);
            const rawValue = transactionData[field] ?? '';
            const hasContent = typeof rawValue === 'string' ? rawValue.trim() !== '' : !!rawValue;
            
            // Always show document fields, even if empty
            if (hasContent || docFields.has(field)) {
                let fieldValue = rawValue;

                // Document fields: create clickable links or show placeholders
                if (docFields.has(field)) {
                    if (!fieldValue || fieldValue.trim() === '') {
                        fieldValue = '—';
                    } else if (typeof fieldValue === 'string' && (fieldValue.startsWith('http') || fieldValue.startsWith('https'))) {
                        fieldValue = `<a href="${fieldValue}" target="_blank" style="color: #007bff; text-decoration: underline;">📄 View Document</a>`;
                    } else if (fieldValue === '✔') {
                        fieldValue = '✔ Available (see sheet)';
                    } else {
                        fieldValue = `📄 ${fieldValue}`;
                    }
                }

                tableRows += `
                    <tr>
                        <td class="field-label">${formatFieldName(field)}</td>
                        <td class="field-value">${fieldValue}</td>
                    </tr>
                `;
            }
        }
        
        // Then add any remaining fields not in the column order
        for (const [field, value] of Object.entries(transactionData)) {
            if (value && value.trim() !== '' && 
                field !== 'N' && 
                !columnOrder.includes(field)) {
                tableRows += `
                    <tr>
                        <td class="field-label">${formatFieldName(field)}</td>
                        <td class="field-value">${value}</td>
                    </tr>
                `;
            }
        }
        
        console.log('Generated table rows:', tableRows);
        
        // Create three-column layout for double-entry bookkeeping
        const threeColumnRows = createThreeColumnLayout(transactionData);
        
        transactionDetails.innerHTML = `
            ${accountsHeader}
            <div style="margin: 30px 0; padding: 25px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h4 style="color: #495057; margin-bottom: 20px; font-size: 1.2em;">📊 Double-Entry Transaction Details</h4>
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd; background: white;">
                        <thead>
                            <tr style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                                <th style="padding: 15px; border: 1px solid #ddd; text-align: left; width: 20%; font-weight: 600;">Field</th>
                                <th style="padding: 15px; border: 1px solid #ddd; text-align: center; width: 40%; background: #dc3545; color: white; font-weight: 600;">Debit Details</th>
                                <th style="padding: 15px; border: 1px solid #ddd; text-align: center; width: 40%; background: #28a745; color: white; font-weight: 600;">Credit Details</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${threeColumnRows}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Interactive Document Upload Subform -->
            <div style="margin-top: 30px; padding: 25px; background: #f8f9fa; border-radius: 8px; border: 1px solid #e9ecef;">
                <h4 style="color: #495057; margin-bottom: 20px; font-size: 1.1em;">📎 Update Attached Documents</h4>
                
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #495057;">Select Document Type to Update:</label>
                    <select id="documentTypeSelect" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px;">
                        <option value="">Choose document type...</option>
                        <option value="bill">📄 Bill (Normal Invoice)</option>
                        <option value="redBill">🔴 Red Bill (Special Invoice)</option>
                        <option value="bankStatement">🏦 Bank Statement (Bank transaction records)</option>
                        <option value="documentation">📋 Supporting Documentation</option>
                    </select>
                </div>
                
                <!-- Dynamic Upload Form (initially hidden) -->
                <div id="uploadFormContainer" style="display: none; padding: 20px; background: white; border-radius: 6px; border: 1px solid #dee2e6;">
                    <h5 style="margin: 0 0 15px 0; color: #495057;" id="uploadFormTitle">Upload Document</h5>
                    
                    <form id="documentUploadForm" enctype="multipart/form-data">
                        <!-- Upload Mode Toggle -->
                        <div style="margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-radius: 6px; border: 1px solid #e9ecef;">
                            <label style="display: block; margin-bottom: 10px; font-weight: 600; color: #495057;">📎 Upload Method:</label>
                            <div style="display: flex; gap: 20px; margin-bottom: 10px;">
                                <label style="display: flex; align-items: center; cursor: pointer; padding: 8px 12px; border-radius: 4px; background: #e3f2fd; border: 1px solid #2196f3;">
                                    <input type="radio" name="updateUploadMode" value="file" checked style="margin-right: 8px;">
                                    <span style="font-weight: 500;">📁 Upload New File</span>
                                </label>
                                <label style="display: flex; align-items: center; cursor: pointer; padding: 8px 12px; border-radius: 4px; background: #f3e5f5; border: 1px solid #9c27b0;">
                                    <input type="radio" name="updateUploadMode" value="link" style="margin-right: 8px;">
                                    <span style="font-weight: 500;">🔗 Link Existing File</span>
                                </label>
                            </div>
                            <small style="color: #6c757d; font-size: 12px;">
                                💡 Choose how you want to add the document: upload a new file or link to an existing Google Drive file
                            </small>
                        </div>
                        
                        <!-- File Upload Section -->
                        <div id="updateFileUploadSection" style="margin-bottom: 15px;">
                            <label style="display: block; margin-bottom: 5px; font-weight: 600; color: #495057;">Select File:</label>
                            <input type="file" id="documentFile" name="file" accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.gif,.txt" 
                                   style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
                            <small style="color: #6c757d; font-size: 12px;">Allowed: PDF, DOC, DOCX, XLS, XLSX, JPG, PNG, GIF, TXT</small>
                        </div>
                        
                        <!-- Google Drive Link Section -->
                        <div id="linkInputSection" style="margin-bottom: 15px; display: none;">
                            <label style="display: block; margin-bottom: 5px; font-weight: 600; color: #495057;">Google Drive Link:</label>
                            <input type="url" id="googleDriveLink" placeholder="Paste Google Drive URL here..." 
                                   style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
                            <small style="color: #6c757d; font-size: 12px; margin-top: 5px; display: block;">
                                💡 Tip: Copy the "Share" link from Google Drive (make sure it's set to "Anyone with the link can view")
                            </small>
                        </div>
                        
                        <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                            <button type="submit" id="uploadBtn" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: 600; cursor: pointer;">
                                📤 Upload to Google Drive
                            </button>
                            <button type="button" id="updateSheetsBtn" style="background: linear-gradient(135deg, #007bff 0%, #0056b3 100%); color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: 600; cursor: pointer; display: none;">
                                📊 Update Google Sheets
                            </button>
                            <button type="button" id="cancelUploadBtn" style="background: #6c757d; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: 600; cursor: pointer;">
                                ❌ Cancel
                            </button>
                            <div id="uploadProgress" style="display: none; flex: 1; margin-left: 10px;">
                                <div style="background: #e9ecef; border-radius: 4px; height: 8px; overflow: hidden;">
                                    <div id="progressBar" style="background: linear-gradient(90deg, #28a745, #20c997); height: 100%; width: 0%; transition: width 0.3s ease;"></div>
                                </div>
                                <small id="progressText" style="color: #6c757d; font-size: 12px;">Uploading...</small>
                            </div>
                        </div>
                    </form>
                    
                    <div id="uploadResult" style="margin-top: 15px; display: none;"></div>
                </div>
            </div>
        `;
        
        console.log('Table HTML set successfully');
        
        // Update the alert message
        const searchResults = document.getElementById('searchResults');
        if (searchResults) {
            const alertDiv = searchResults.querySelector('.alert');
            if (alertDiv) {
                alertDiv.className = 'alert alert-success';
                alertDiv.innerHTML = `
                    <strong>✅ Transaction Found!</strong>
                    <p>Transaction details retrieved successfully. Ready for document updates.</p>
                `;
            }
        }
        
        // Initialize document upload functionality (defined in app-inline.js)
        if (typeof window.initializeDocumentUpload === 'function') {
            window.initializeDocumentUpload();
        } else {
            console.warn('initializeDocumentUpload function not found');
        }
    }
    
    // Display Transaction Details Function
    function displayTransactionDetails(transactionData) {
        console.log('=== DEBUGGING DISPLAY TRANSACTION DETAILS ===');
        console.log('1. Function called with data:', transactionData);
        
        // Check if updateFormContainer exists
        const updateFormContainer = document.getElementById('updateFormContainer');
        console.log('2. updateFormContainer found:', !!updateFormContainer);
        
        if (!updateFormContainer) {
            console.error('FATAL: updateFormContainer not found');
            return;
        }
        
        // Make it visible
        updateFormContainer.style.display = 'block';
        console.log('3. Made updateFormContainer visible');
        
        // Check if searchResults exists
        const searchResults = document.getElementById('searchResults');
        console.log('4. searchResults found:', !!searchResults);
        
        if (!searchResults) {
            console.error('FATAL: searchResults not found');
            return;
        }
        
        // Show loading message in searchResults
        searchResults.style.display = 'block';
        searchResults.innerHTML = `
            <div class="alert alert-success">
                <strong>✅ Transaction Found!</strong>
                <p>Transaction details retrieved successfully. Ready for document updates.</p>
            </div>
            
            <!-- Transaction Details Table -->
            <div id="transactionDetails" class="transaction-details-table">
                <!-- Will be populated by JavaScript -->
            </div>
            
            <!-- Transaction details will be populated here -->
        `;
        console.log('5. Set searchResults HTML with new transactionDetails');
        
        // Now find the transactionDetails element
        setTimeout(() => {
            const transactionDetails = document.getElementById('transactionDetails');
            console.log('6. transactionDetails found after creating:', !!transactionDetails);
            
            if (!transactionDetails) {
                console.error('FATAL: Still cannot find transactionDetails after creating it');
                return;
            }
            
            console.log('7. Creating table...');
            displayTransactionTable(transactionData, transactionDetails);
        }, 50);
    }
    
    // Set up search functionality when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        const searchTransactionBtn = document.getElementById('searchTransactionBtn');
        const searchResults = document.getElementById('searchResults');

        if (!searchTransactionBtn) {
            console.error('Search transaction button not found');
            return;
        }

        // Search Transaction Button Click
        searchTransactionBtn.addEventListener('click', function() {
            const transactionNumber = document.getElementById('searchTransactionNumber').value.trim();
            const selectedSheet = document.getElementById('searchSheet').value;
            
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
            
            // Call the real API
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
                console.log('Response headers:', response.headers);
                console.log('Response ok:', response.ok);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('API Response received:', data);
                console.log('Response type:', typeof data);
                console.log('Response keys:', Object.keys(data || {}));
                
                if (data && data.success) {
                    console.log('Transaction data received:', data.data);
                    console.log('Number of fields:', Object.keys(data.data).length);
                    console.log('Field names:', Object.keys(data.data));
                    console.log('Field values:', Object.values(data.data));
                    
                    // Store the transaction number for later use in file uploads
                    const transactionNumberFromData = data.data['Transaction Number'];
                    if (transactionNumberFromData) {
                        console.log(`DEBUG: Storing transaction number for uploads: "${transactionNumberFromData}"`);
                        // Store in a data attribute on the search results container
                        if (searchResults) {
                            searchResults.setAttribute('data-transaction-number', transactionNumberFromData);
                        }
                        // Also store in sessionStorage for backup
                        sessionStorage.setItem('currentTransactionNumber', transactionNumberFromData);
                    }
                    
                    displayTransactionDetails(data.data);
                } else {
                    console.log('Search failed or no data:', data);
                    // Show error message
                    if (searchResults) {
                        searchResults.innerHTML = `
                            <div class="alert alert-danger">
                                <strong>❌ Search Failed</strong>
                                <p>${data ? data.error : 'No response data'}</p>
                            </div>
                        `;
                    }
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
        });
        
        console.log('✅ Transaction search module initialized');
    });
    
    // Expose initializeDocumentUpload check to global scope
    // (The actual function is in app-inline.js and will be called from there)
    
})();

