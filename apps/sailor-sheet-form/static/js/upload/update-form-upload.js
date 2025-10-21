// Update Form Document Upload - Handles document upload/link processing for update form
// Extracted from inline script - Step 7 of incremental refactoring

(function() {
    'use strict';
    
    // Show upload result
    function showUploadResult(message, type) {
        const uploadResult = document.getElementById('uploadResult');
        if (!uploadResult) return;
        
        uploadResult.style.display = 'block';
        uploadResult.innerHTML = message;
        uploadResult.style.padding = '10px';
        uploadResult.style.borderRadius = '4px';
        uploadResult.style.marginTop = '15px';
        
        if (type === 'success') {
            uploadResult.style.backgroundColor = '#d4edda';
            uploadResult.style.border = '1px solid #c3e6cb';
            uploadResult.style.color = '#155724';
        } else {
            uploadResult.style.backgroundColor = '#f8d7da';
            uploadResult.style.border = '1px solid #f5c6cb';
            uploadResult.style.color = '#721c24';
        }
    }
    
    // Hide upload result
    function hideUploadResult() {
        const uploadResult = document.getElementById('uploadResult');
        if (uploadResult) {
            uploadResult.style.display = 'none';
        }
    }
    
    // Update Google Sheets with document link
    function updateGoogleSheetsDocument(transactionNumber, documentType, fileUrl) {
        // Get the current sheet type from the search form
        const sheetTypeSelect = document.getElementById('searchSheet');
        const sheetType = sheetTypeSelect ? sheetTypeSelect.value : 'vn';
        
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
        .then(response => {
            console.log('DEBUG: API response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('DEBUG: API response data:', data);
            if (data.success) {
                console.log('✅ Google Sheets updated successfully:', data.message);
                
                // Reset button state
                const updateSheetsBtn = document.getElementById('updateSheetsBtn');
                if (updateSheetsBtn) {
                    updateSheetsBtn.disabled = false;
                    updateSheetsBtn.textContent = '✅ Updated Successfully!';
                    updateSheetsBtn.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
                }
                
                // Show success message to user
                showUploadResult(`
                    <div style="color: #28a745; font-weight: 600;">
                        ✅ Google Sheets updated successfully!
                        <br><strong>Transaction:</strong> ${transactionNumber}
                        <br><strong>Document Type:</strong> ${documentType}
                        <br><strong>Status:</strong> Both debit and credit rows updated with document link
                        <br><a href="${fileUrl}" target="_blank" style="color: #007bff; text-decoration: underline;">📄 View Document</a>
                    </div>
                `, 'success');
                
                // Clear the uploaded file data
                window.uploadedFileData = null;
                
            } else {
                console.error('❌ Google Sheets update failed:', data.error);
                
                // Reset button state
                const updateSheetsBtn = document.getElementById('updateSheetsBtn');
                if (updateSheetsBtn) {
                    updateSheetsBtn.disabled = false;
                    updateSheetsBtn.textContent = '📊 Update Google Sheets';
                }
                
                showUploadResult(`❌ Google Sheets update failed: ${data.error}`, 'error');
            }
        })
        .catch(error => {
            console.error('❌ Error updating Google Sheets:', error);
            showUploadResult(`❌ Error updating Google Sheets: ${error.message}`, 'error');
        });
    }
    
    // Handle Google Sheets update (Step 2)
    function handleGoogleSheetsUpdate() {
        if (!window.uploadedFileData) {
            showUploadResult('❌ No uploaded file data found. Please upload a file first.', 'error');
            return;
        }
        
        let { transactionNumber, documentType, fileUrl, fileName } = window.uploadedFileData;
        
        // Double-check the transaction number from the displayed search results
        const searchResults = document.getElementById('searchResults');
        const transactionTable = searchResults ? searchResults.querySelector('table') : null;
        
        console.log('DEBUG: handleGoogleSheetsUpdate - searchResults:', searchResults);
        console.log('DEBUG: handleGoogleSheetsUpdate - transactionTable:', transactionTable);
        console.log('DEBUG: handleGoogleSheetsUpdate - initial transactionNumber:', transactionNumber);
        
        // First, try to get transaction number from the search input field (most reliable)
        const searchInput = document.getElementById('searchTransactionNumber');
        if (searchInput && searchInput.value.trim()) {
            const searchInputTransactionNumber = searchInput.value.trim();
            console.log('DEBUG: handleGoogleSheetsUpdate - Transaction number from search input:', searchInputTransactionNumber);
            // Only use search input if current transaction number is empty or is the em dash
            if (!transactionNumber || transactionNumber === '—') {
                transactionNumber = searchInputTransactionNumber;
                console.log('DEBUG: handleGoogleSheetsUpdate - Using transaction number from search input:', transactionNumber);
            }
        }
        
        if (transactionTable) {
            const allRows = Array.from(transactionTable.querySelectorAll('tr'));
            console.log('DEBUG: handleGoogleSheetsUpdate - Found', allRows.length, 'table rows');
            
            allRows.forEach((row, index) => {
                if (row.cells && row.cells[0]) {
                    console.log(`DEBUG: handleGoogleSheetsUpdate - Row ${index}: "${row.cells[0].textContent.trim()}"`);
                    if (row.cells[1]) {
                        console.log(`DEBUG: handleGoogleSheetsUpdate - Row ${index} value: "${row.cells[1].textContent.trim()}"`);
                    }
                }
            });
            
            const transactionRow = allRows.find(row => {
                if (!row.cells[0]) return false;
                const headerText = row.cells[0].textContent.trim();
                return headerText === 'Transaction Number' || 
                       headerText === 'BE-Transaction Number' || 
                       headerText === 'VN-Transaction Number';
            });
            
            console.log('DEBUG: handleGoogleSheetsUpdate - transactionRow found:', transactionRow);
            
            if (transactionRow && transactionRow.cells[1]) {
                const tableTransactionNumber = transactionRow.cells[1].textContent.trim();
                console.log(`DEBUG: Transaction number from uploaded data: "${transactionNumber}"`);
                console.log(`DEBUG: Transaction number from search results table: "${tableTransactionNumber}"`);
                
                // Use the transaction number from the search results table (most reliable)
                // Only use table value if it's not the em dash placeholder
                if (tableTransactionNumber && tableTransactionNumber !== '—') {
                    transactionNumber = tableTransactionNumber;
                    console.log(`DEBUG: Using transaction number from search results: "${transactionNumber}"`);
                } else {
                    console.log('DEBUG: handleGoogleSheetsUpdate - Table has em dash placeholder, keeping current value');
                }
            }
        }
        
        console.log(`DEBUG: Starting Google Sheets update for transaction: ${transactionNumber}`);
        console.log(`DEBUG: Document type: ${documentType}`);
        console.log(`DEBUG: File URL: ${fileUrl}`);
        
        // Show loading state
        const updateSheetsBtn = document.getElementById('updateSheetsBtn');
        if (updateSheetsBtn) {
            updateSheetsBtn.disabled = true;
            updateSheetsBtn.textContent = '🔄 Updating...';
        }
        
        // Call the Google Sheets update API
        updateGoogleSheetsDocument(transactionNumber, documentType, fileUrl);
    }
    
    // Handle document upload
    function handleDocumentUpload() {
        const documentTypeSelect = document.getElementById('documentTypeSelect');
        const documentFile = document.getElementById('documentFile');
        const fileDescription = document.getElementById('fileDescription');
        const uploadBtn = document.getElementById('uploadBtn');
        const uploadProgress = document.getElementById('uploadProgress');
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        const selectedType = documentTypeSelect.value;
        const file = documentFile.files[0];
        
        if (!selectedType || !file) {
            showUploadResult('Please select a document type and file.', 'error');
            return;
        }
        
        // Get current transaction number from the search results instead of input field
        const searchResults = document.getElementById('searchResults');
        const transactionTable = searchResults ? searchResults.querySelector('table') : null;
        let transactionNumber = '';
        
        // Try to get transaction number from the displayed table
        if (transactionTable) {
            console.log('DEBUG: Looking for Transaction Number row in table...');
            const allRows = Array.from(transactionTable.querySelectorAll('tr'));
            console.log(`DEBUG: Found ${allRows.length} rows in table`);
            
            allRows.forEach((row, index) => {
                if (row.cells && row.cells.length >= 2) {
                    const firstCell = row.cells[0].textContent.trim();
                    const secondCell = row.cells[1].textContent.trim();
                    console.log(`DEBUG: Row ${index}: "${firstCell}" -> "${secondCell}"`);
                }
            });
            
            const transactionRow = allRows.find(row => 
                row.cells[0] && row.cells[0].textContent.trim() === 'Transaction Number'
            );
            if (transactionRow && transactionRow.cells[1]) {
                transactionNumber = transactionRow.cells[1].textContent.trim();
                console.log(`DEBUG: Found transaction number in table: "${transactionNumber}"`);
            } else {
                console.log('DEBUG: No Transaction Number row found in table');
            }
        } else {
            console.log('DEBUG: No transaction table found');
        }
        
        // Fallback to search input field if table method fails or returns em dash
        if (!transactionNumber || transactionNumber === '—' || transactionNumber === '-') {
            const searchInput = document.getElementById('searchTransactionNumber');
            if (searchInput && searchInput.value.trim()) {
                transactionNumber = searchInput.value.trim();
                console.log(`DEBUG: Using transaction number from search input: "${transactionNumber}"`);
            }
        }
        
        // Fallback to stored transaction number from search results
        if (!transactionNumber || transactionNumber === '—' || transactionNumber === '-') {
            if (searchResults) {
                const storedTransactionNumber = searchResults.getAttribute('data-transaction-number');
                if (storedTransactionNumber && storedTransactionNumber !== '—' && storedTransactionNumber !== '-') {
                    transactionNumber = storedTransactionNumber;
                    console.log(`DEBUG: Using stored transaction number from search results: "${transactionNumber}"`);
                }
            }
        }
        
        // Fallback to sessionStorage
        if (!transactionNumber || transactionNumber === '—' || transactionNumber === '-') {
            const sessionTransactionNumber = sessionStorage.getItem('currentTransactionNumber');
            if (sessionTransactionNumber && sessionTransactionNumber !== '—' && sessionTransactionNumber !== '-') {
                transactionNumber = sessionTransactionNumber;
                console.log(`DEBUG: Using transaction number from sessionStorage: "${transactionNumber}"`);
            }
        }
        
        // Final fallback to hidden input field
        if (!transactionNumber || transactionNumber === '—' || transactionNumber === '-') {
            const hiddenInput = document.getElementById('transactionNumberInput');
            if (hiddenInput && hiddenInput.value.trim()) {
                transactionNumber = hiddenInput.value.trim();
                console.log(`DEBUG: Using transaction number from hidden input: "${transactionNumber}"`);
            }
        }
        
        console.log(`DEBUG: Final transaction number to be used: "${transactionNumber}"`);
        console.log(`DEBUG: Transaction number from input field: "${document.getElementById('transactionNumberInput').value}"`);
        
        // Debug: Check all possible sources
        console.log('DEBUG: === TRANSACTION NUMBER DEBUG ===');
        console.log('1. Search input field:', document.getElementById('searchTransactionNumber')?.value);
        console.log('2. Hidden input field:', document.getElementById('transactionNumberInput')?.value);
        console.log('3. Search results data attribute:', searchResults?.getAttribute('data-transaction-number'));
        console.log('4. SessionStorage:', sessionStorage.getItem('currentTransactionNumber'));
        console.log('5. Final transaction number:', transactionNumber);
        console.log('=== END DEBUG ===');
        
        if (!transactionNumber || transactionNumber === '—' || transactionNumber === '-') {
            showUploadResult('Transaction number not found. Please search for a transaction first.', 'error');
            return;
        }
        
        // Show progress
        uploadBtn.disabled = true;
        uploadBtn.textContent = '🔄 Uploading...';
        uploadProgress.style.display = 'flex';
        progressBar.style.width = '0%';
        progressText.textContent = 'Preparing upload...';
        
        // Get current country
        const selectedCountry = sessionStorage.getItem('selectedCountry') || 'BE';
        console.log(`DEBUG: Uploading file for country: ${selectedCountry}`);
        
        // Create form data
        console.log(`DEBUG: Creating FormData with transaction_number: "${transactionNumber}"`);
        const formData = new FormData();
        formData.append('file', file);
        formData.append('transaction_number', transactionNumber);
        formData.append('country_code', selectedCountry);
        console.log(`DEBUG: FormData created, transaction_number set to: "${transactionNumber}"`);
        
        // Map document types to file types that match Python FOLDER_IDS keys
        const fileTypeMapping = {
            'bill': 'bills',
            'redBill': 'redBills',  // Add 's' to match FOLDER_IDS['redBills']
            'documentation': 'documentation'
        };
        const fileType = fileTypeMapping[selectedType] || selectedType;
        formData.append('file_type', fileType);
        
        // Simulate progress
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) progress = 90;
            progressBar.style.width = progress + '%';
            progressText.textContent = `Uploading... ${Math.round(progress)}%`;
        }, 200);
        
        // Upload file
        fetch('/api/upload_file', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            clearInterval(progressInterval);
            progressBar.style.width = '100%';
            progressText.textContent = 'Complete!';
            
            if (data.success) {
                // Store the upload data for Google Sheets update
                window.uploadedFileData = {
                    transactionNumber: transactionNumber,
                    documentType: selectedType,
                    fileUrl: data.file_url,
                    fileName: data.file_name
                };
                
                // Show success message and enable Google Sheets update button
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
                showUploadResult(`❌ Upload failed: ${data.error}`, 'error');
            }
        })
        .catch(error => {
            clearInterval(progressInterval);
            showUploadResult(`❌ Upload failed: ${error.message}`, 'error');
        })
        .finally(() => {
            uploadBtn.disabled = false;
            uploadBtn.textContent = '📤 Upload to Google Drive';
            setTimeout(() => {
                uploadProgress.style.display = 'none';
            }, 1000);
        });
    }
    
    // Handle Google Drive link processing for update form
    async function handleGoogleDriveLink() {
        console.log('DEBUG: handleGoogleDriveLink() called');
        
        const documentTypeSelect = document.getElementById('documentTypeSelect');
        const googleDriveLinkInput = document.getElementById('googleDriveLink');
        const uploadBtn = document.getElementById('uploadBtn');
        const uploadProgress = document.getElementById('uploadProgress');
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        const selectedType = documentTypeSelect ? documentTypeSelect.value : '';
        const googleDriveLink = googleDriveLinkInput ? googleDriveLinkInput.value.trim() : '';
        
        console.log('DEBUG: Selected type:', selectedType);
        console.log('DEBUG: Google Drive link:', googleDriveLink);
        
        if (!selectedType || !googleDriveLink) {
            console.error('DEBUG: Validation failed - selectedType:', selectedType, 'googleDriveLink:', googleDriveLink);
            showUploadResult('Please select a document type and enter a Google Drive URL.', 'error');
            return;
        }
        
        if (!googleDriveLink.includes('drive.google.com')) {
            showUploadResult('Please enter a valid Google Drive URL.', 'error');
            return;
        }
        
        // Get current transaction number from the search results
        const searchResults = document.getElementById('searchResults');
        const transactionTable = searchResults ? searchResults.querySelector('table') : null;
        let transactionNumber = '';
        
        console.log('DEBUG: searchResults element:', searchResults);
        console.log('DEBUG: transactionTable element:', transactionTable);
        
        // First, try to get transaction number from the search input field (most reliable)
        const searchInput = document.getElementById('searchTransactionNumber');
        console.log('DEBUG: searchInput element:', searchInput);
        console.log('DEBUG: searchInput value:', searchInput ? searchInput.value : 'NOT FOUND');
        
        if (searchInput && searchInput.value.trim()) {
            transactionNumber = searchInput.value.trim();
            console.log('DEBUG: Transaction number from search input:', transactionNumber);
        } else {
            console.log('DEBUG: Search input is empty or not found');
        }
        
        // If not found in search input, try to get from the table
        if (!transactionNumber && transactionTable) {
            const allRows = Array.from(transactionTable.querySelectorAll('tr'));
            console.log('DEBUG: Found', allRows.length, 'table rows');
            
            allRows.forEach((row, index) => {
                if (row.cells && row.cells[0]) {
                    const headerText = row.cells[0].textContent.trim();
                    console.log(`DEBUG: Row ${index}: "${headerText}"`);
                    if (row.cells[1]) {
                        console.log(`DEBUG: Row ${index} value: "${row.cells[1].textContent.trim()}"`);
                    }
                    
                    // Check if this looks like a transaction number header
                    if (headerText.includes('Transaction Number')) {
                        console.log(`DEBUG: FOUND TRANSACTION NUMBER HEADER: "${headerText}"`);
                    }
                }
            });
            
            const transactionRow = allRows.find(row => {
                if (!row.cells[0]) return false;
                const headerText = row.cells[0].textContent.trim();
                return headerText === 'Transaction Number' || 
                       headerText === 'BE-Transaction Number' || 
                       headerText === 'VN-Transaction Number';
            });
            
            console.log('DEBUG: transactionRow found:', transactionRow);
            
            if (transactionRow && transactionRow.cells[1]) {
                const tableTransactionNumber = transactionRow.cells[1].textContent.trim();
                // Only use table value if it's not the em dash placeholder
                if (tableTransactionNumber && tableTransactionNumber !== '—') {
                    transactionNumber = tableTransactionNumber;
                    console.log('DEBUG: Transaction number from table:', transactionNumber);
                } else {
                    console.log('DEBUG: Table has em dash placeholder, ignoring');
                }
            }
        }
        
        // Final fallback
        if (!transactionNumber) {
            const fallbackInput = document.getElementById('transactionNumberInput');
            transactionNumber = fallbackInput ? fallbackInput.value : '';
            console.log('DEBUG: Fallback transaction number from input:', transactionNumber);
        }
        
        console.log('DEBUG: Final transaction number:', transactionNumber);
        
        if (!transactionNumber) {
            showUploadResult('Transaction number not found. Please search for a transaction first.', 'error');
            return;
        }
        
        // Get current country
        const selectedCountry = sessionStorage.getItem('selectedCountry') || 'BE';
        console.log('DEBUG: Selected country from sessionStorage:', selectedCountry);
        
        // Show progress
        uploadBtn.disabled = true;
        uploadProgress.style.display = 'flex';
        progressBar.style.width = '0%';
        progressText.textContent = 'Processing Google Drive link...';
        
        try {
            // Simulate progress
            progressBar.style.width = '30%';
            progressText.textContent = 'Downloading file...';
            
            // Call API to process Google Drive link
            const requestData = {
                google_drive_url: googleDriveLink,
                document_type: selectedType,
                transaction_number: transactionNumber,
                country_code: selectedCountry
            };
            console.log('DEBUG: Sending API request with data:', requestData);
            
            const response = await fetch('/api/process_google_drive_link', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });
            
            progressBar.style.width = '70%';
            progressText.textContent = 'Uploading to correct folder...';
            
            const data = await response.json();
            
            if (data.success) {
                // Store the uploaded file data for later use
                window.uploadedFileData = {
                    transactionNumber: transactionNumber,
                    documentType: selectedType,
                    fileUrl: data.file_url,
                    fileName: data.file_name
                };
                
                progressBar.style.width = '100%';
                progressText.textContent = 'Complete!';
                
                // Update button states
                setTimeout(() => {
                    uploadBtn.disabled = true;
                    uploadBtn.textContent = '✅ Link Processed Successfully!';
                    uploadBtn.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
                    
                    // Show Google Sheets update button
                    const updateSheetsBtn = document.getElementById('updateSheetsBtn');
                    if (updateSheetsBtn) {
                        updateSheetsBtn.style.display = 'inline-block';
                    }
                    
                    showUploadResult(`✅ Google Drive link processed successfully!<br>File: ${data.file_name}<br>Ready to update Google Sheets.`, 'success');
                }, 500);
                
            } else {
                throw new Error(data.error || 'Failed to process Google Drive link');
            }
            
        } catch (error) {
            console.error('Error processing Google Drive link:', error);
            uploadProgress.style.display = 'none';
            uploadBtn.disabled = false;
            uploadBtn.textContent = '🔗 Process Google Drive Link';
            uploadBtn.style.background = 'linear-gradient(135deg, #9c27b0 0%, #673ab7 100%)';
            
            showUploadResult(`❌ Failed to process Google Drive link: ${error.message}`, 'error');
        }
    }
    
    // Initialize document upload functionality
    function initializeDocumentUpload() {
        const documentTypeSelect = document.getElementById('documentTypeSelect');
        const uploadFormContainer = document.getElementById('uploadFormContainer');
        const uploadFormTitle = document.getElementById('uploadFormTitle');
        const documentUploadForm = document.getElementById('documentUploadForm');
        const cancelUploadBtn = document.getElementById('cancelUploadBtn');
        
        // Set up drag-and-drop for update form (now that it's visible)
        setupDragAndDropForUpdateForm();
        
        // Apply country filtering to update form dropdown when it becomes visible
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                    const target = mutation.target;
                    if (target.id === 'updateOptions' && target.style.display !== 'none') {
                        console.log('DEBUG: Update form became visible, applying country filtering');
                        const selectedCountry = sessionStorage.getItem('selectedCountry') || 'BE';
                        // Call the global function if available
                        if (typeof window.updateDocumentTypeDropdown === 'function') {
                            window.updateDocumentTypeDropdown(selectedCountry);
                        }
                    }
                }
            });
        });
        
        // Observe the update form container for visibility changes
        const updateOptions = document.getElementById('updateOptions');
        if (updateOptions) {
            observer.observe(updateOptions, { attributes: true, attributeFilter: ['style'] });
        }
        
        // Upload mode toggle elements (for update form)
        const uploadModeRadios = document.querySelectorAll('input[name="updateUploadMode"]');
        const fileUploadSection = document.getElementById('updateFileUploadSection');
        const linkInputSection = document.getElementById('linkInputSection');
        const uploadBtn = document.getElementById('uploadBtn');
        
        if (!documentTypeSelect || !uploadFormContainer) return;
        
        // Handle upload mode toggle
        uploadModeRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.value === 'file') {
                    // Show file upload, hide link input
                    fileUploadSection.style.display = 'block';
                    linkInputSection.style.display = 'none';
                    uploadBtn.textContent = '📤 Upload to Google Drive';
                    uploadBtn.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
                    
                    // Clear link input
                    document.getElementById('googleDriveLink').value = '';
                } else if (this.value === 'link') {
                    // Show link input, hide file upload
                    fileUploadSection.style.display = 'none';
                    linkInputSection.style.display = 'block';
                    uploadBtn.textContent = '🔗 Process Google Drive Link';
                    uploadBtn.style.background = 'linear-gradient(135deg, #9c27b0 0%, #673ab7 100%)';
                    
                    // Clear file input
                    document.getElementById('documentFile').value = '';
                }
            });
        });
        
        // Show/hide upload form based on document type selection
        documentTypeSelect.addEventListener('change', function() {
            const selectedType = this.value;
            
            if (selectedType) {
                // Show upload form
                uploadFormContainer.style.display = 'block';
                
                // Update form title based on selection
                const typeNames = {
                    'bill': '📄 Bill (Normal Invoice)',
                    'redBill': '🔴 Red Bill (Special Invoice)',
                    'bankStatement': '🏦 Bank Statement (Bank transaction records)',
                    'documentation': '📋 Supporting Documentation'
                };
                uploadFormTitle.textContent = `Upload ${typeNames[selectedType]}`;
            } else {
                // Hide upload form
                uploadFormContainer.style.display = 'none';
            }
        });
        
        // Apply country filtering when dropdown is clicked/focused
        documentTypeSelect.addEventListener('focus', function() {
            console.log('DEBUG: Update form dropdown focused, applying country filtering');
            if (typeof window.forceUpdateDocumentTypeDropdowns === 'function') {
                window.forceUpdateDocumentTypeDropdowns();
            }
        });
        
        documentTypeSelect.addEventListener('click', function() {
            console.log('DEBUG: Update form dropdown clicked, applying country filtering');
            if (typeof window.forceUpdateDocumentTypeDropdowns === 'function') {
                window.forceUpdateDocumentTypeDropdowns();
            }
        });
        
        // Cancel upload
        if (cancelUploadBtn) {
            cancelUploadBtn.addEventListener('click', function() {
                uploadFormContainer.style.display = 'none';
                documentTypeSelect.value = '';
                documentUploadForm.reset();
                hideUploadResult();
                
                // Hide the Google Sheets update button
                const updateSheetsBtn = document.getElementById('updateSheetsBtn');
                if (updateSheetsBtn) {
                    updateSheetsBtn.style.display = 'none';
                    updateSheetsBtn.disabled = false;
                    updateSheetsBtn.textContent = '📊 Update Google Sheets';
                    updateSheetsBtn.style.background = 'linear-gradient(135deg, #007bff 0%, #0056b3 100%)';
                }
                
                // Clear uploaded file data
                window.uploadedFileData = null;
            });
        }
        
        // Handle form submission (Step 1: Upload to Google Drive or Process Link)
        if (documentUploadForm) {
            documentUploadForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                // Check which mode is selected (for update form)
                const allUploadModeElements = document.querySelectorAll('input[name="updateUploadMode"]');
                console.log('DEBUG: All update upload mode elements found:', allUploadModeElements.length);
                allUploadModeElements.forEach((el, index) => {
                    console.log(`DEBUG: Update upload mode ${index}:`, el.value, 'checked:', el.checked);
                });
                
                const selectedModeElement = document.querySelector('input[name="updateUploadMode"]:checked');
                console.log('DEBUG: Selected update mode element:', selectedModeElement);
                
                if (!selectedModeElement) {
                    console.error('ERROR: No upload mode selected');
                    showUploadResult('Please select an upload method.', 'error');
                    return;
                }
                
                const selectedMode = selectedModeElement.value;
                console.log('DEBUG: Selected mode value:', selectedMode);
                
                if (selectedMode === 'file') {
                    console.log('DEBUG: Calling handleDocumentUpload()');
                    handleDocumentUpload();
                } else if (selectedMode === 'link') {
                    console.log('DEBUG: Calling handleGoogleDriveLink()');
                    handleGoogleDriveLink();
                } else {
                    console.error('ERROR: Unknown upload mode:', selectedMode);
                    showUploadResult('Unknown upload method selected.', 'error');
                }
            });
        }
        
        // Handle Google Sheets update (Step 2: Update Google Sheets)
        const updateSheetsBtn = document.getElementById('updateSheetsBtn');
        if (updateSheetsBtn) {
            updateSheetsBtn.addEventListener('click', function() {
                handleGoogleSheetsUpdate();
            });
        }
    }
    
    // Set up drag-and-drop functionality for update form
    // Flag to track if drag-and-drop has been initialized
    let dragDropInitialized = false;
    
    function setupDragAndDropForUpdateForm() {
        // Prevent double initialization
        if (dragDropInitialized) {
            console.log('⏭️ Drag-and-drop already initialized for update form');
            return;
        }
        
        const updateFileUploadSection = document.getElementById('updateFileUploadSection');
        const fileInput = document.getElementById('documentFile');
        
        if (!updateFileUploadSection || !fileInput) {
            console.log('⚠️ Update form drag-and-drop elements not found yet');
            return;
        }
        
        // Create and insert drag-and-drop zone before the file input
        const dragDropZone = document.createElement('div');
        dragDropZone.id = 'updateDragDropZone';
        dragDropZone.style.cssText = `
            border: 3px dashed #007bff;
            background: #f0f8ff;
            padding: 30px 20px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
        `;
        dragDropZone.innerHTML = `
            <div style="font-size: 40px; margin-bottom: 8px;">📎</div>
            <div style="font-size: 16px; font-weight: 600; color: #007bff; margin-bottom: 6px;">
                Drag & Drop your file here
            </div>
            <div style="font-size: 13px; color: #6c757d; margin-bottom: 10px;">
                or click to browse
            </div>
            <div style="color: #6c757d; font-size: 11px;">
                <strong>Allowed:</strong> PDF, DOC, DOCX, XLS, XLSX, JPG, PNG, GIF, TXT<br>
                <strong>Max size:</strong> 16MB
            </div>
        `;
        
        // Insert before the file input
        updateFileUploadSection.insertBefore(dragDropZone, updateFileUploadSection.firstChild);
        
        // Make drag-drop zone clickable
        dragDropZone.addEventListener('click', () => {
            fileInput.click();
        });
        
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            updateFileUploadSection.addEventListener(eventName, preventDefaults, false);
        });
        
        // Highlight drop area when dragging over it
        ['dragenter', 'dragover'].forEach(eventName => {
            updateFileUploadSection.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            updateFileUploadSection.addEventListener(eventName, unhighlight, false);
        });
        
        // Handle dropped files
        updateFileUploadSection.addEventListener('drop', handleDrop, false);
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        function highlight(e) {
            const zone = document.getElementById('updateDragDropZone');
            if (zone) {
                zone.style.borderColor = '#0056b3';
                zone.style.background = '#d4e9ff';
                zone.style.transform = 'scale(1.02)';
            }
        }
        
        function unhighlight(e) {
            const zone = document.getElementById('updateDragDropZone');
            if (zone) {
                zone.style.borderColor = '#007bff';
                zone.style.background = '#f0f8ff';
                zone.style.transform = 'scale(1)';
            }
        }
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                fileInput.files = files;
                console.log(`✅ File dropped in update form: ${files[0].name}`);
                
                // Show visual feedback
                const uploadResult = document.getElementById('uploadResult');
                if (uploadResult) {
                    uploadResult.style.display = 'block';
                    uploadResult.innerHTML = `📎 <strong>File ready:</strong> ${files[0].name}`;
                    uploadResult.style.padding = '10px';
                    uploadResult.style.borderRadius = '4px';
                    uploadResult.style.marginTop = '15px';
                    uploadResult.style.backgroundColor = '#d1ecf1';
                    uploadResult.style.border = '1px solid #bee5eb';
                    uploadResult.style.color = '#0c5460';
                }
            }
        }
        
        dragDropInitialized = true;
        console.log('✅ Drag-and-drop functionality enabled for update form');
    }
    
    // Expose functions to global scope
    window.initializeDocumentUpload = initializeDocumentUpload;
    window.showUploadResult = showUploadResult;
    window.hideUploadResult = hideUploadResult;
    
    console.log('✅ Update form document upload module initialized');
    
})();

