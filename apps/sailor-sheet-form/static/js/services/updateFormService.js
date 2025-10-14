/**
 * Update Form Service
 * Handles document upload and Google Sheets update functionality for existing transactions
 */

/**
 * Show upload result message
 */
export function showUploadResult(message, type) {
    const uploadResult = document.getElementById('uploadResult');
    if (!uploadResult) return;
    
    uploadResult.style.display = 'block';
    uploadResult.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'}`;
    uploadResult.innerHTML = `<strong>${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</strong> ${message}`;
    
    // Auto-hide after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            uploadResult.style.display = 'none';
        }, 5000);
    }
}

/**
 * Hide upload result message
 */
export function hideUploadResult() {
    const uploadResult = document.getElementById('uploadResult');
    if (uploadResult) {
        uploadResult.style.display = 'none';
    }
}

/**
 * Get transaction number from various sources
 */
function getTransactionNumber() {
    const searchResults = document.getElementById('searchResults');
    const transactionTable = searchResults ? searchResults.querySelector('table') : null;
    let transactionNumber = '';
    
    // Try to get from displayed table
    if (transactionTable) {
        const allRows = Array.from(transactionTable.querySelectorAll('tr'));
        const transactionRow = allRows.find(row => 
            row.cells[0] && row.cells[0].textContent.trim() === 'Transaction Number'
        );
        if (transactionRow && transactionRow.cells[1]) {
            transactionNumber = transactionRow.cells[1].textContent.trim();
        }
    }
    
    // Fallback to search input
    if (!transactionNumber || transactionNumber === '—') {
        const searchInput = document.getElementById('searchTransactionNumber');
        if (searchInput && searchInput.value.trim()) {
            transactionNumber = searchInput.value.trim();
        }
    }
    
    // Fallback to stored attribute
    if (!transactionNumber || transactionNumber === '—') {
        if (searchResults) {
            const stored = searchResults.getAttribute('data-transaction-number');
            if (stored && stored !== '—') {
                transactionNumber = stored;
            }
        }
    }
    
    // Fallback to sessionStorage
    if (!transactionNumber || transactionNumber === '—') {
        const sessionNum = sessionStorage.getItem('currentTransactionNumber');
        if (sessionNum && sessionNum !== '—') {
            transactionNumber = sessionNum;
        }
    }
    
    console.log('Final transaction number:', transactionNumber);
    return transactionNumber;
}

/**
 * Handle document upload
 */
export async function handleDocumentUpload() {
    const documentTypeSelect = document.getElementById('documentTypeSelect');
    const documentFile = document.getElementById('documentFile');
    const uploadBtn = document.getElementById('uploadBtn');
    
    const selectedType = documentTypeSelect.value;
    const file = documentFile.files[0];
    
    if (!selectedType || !file) {
        showUploadResult('Please select a document type and file.', 'error');
        return;
    }
    
    const transactionNumber = getTransactionNumber();
    
    if (!transactionNumber || transactionNumber === '—') {
        showUploadResult('Could not find transaction number. Please search for a transaction first.', 'error');
        return;
    }
    
    // Show loading state
    uploadBtn.disabled = true;
    uploadBtn.textContent = '⏳ Uploading...';
    showUploadResult('Uploading file to Google Drive...', 'info');
    
    // Create FormData
    const formData = new FormData();
    formData.append('file', file);
    formData.append('transaction_number', transactionNumber);
    formData.append('document_type', selectedType);
    
    try {
        const response = await fetch('/api/upload_document', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showUploadResult(`File uploaded successfully! File URL: ${data.file_url}`, 'success');
            
            // Store file data for Google Sheets update
            window.uploadedFileData = {
                transactionNumber,
                documentType: selectedType,
                fileUrl: data.file_url
            };
            
            // Show "Update Google Sheets" button
            const updateSheetsBtn = document.getElementById('updateSheetsBtn');
            if (updateSheetsBtn) {
                updateSheetsBtn.style.display = 'inline-block';
            }
        } else {
            showUploadResult(`Upload failed: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showUploadResult(`Upload failed: ${error.message}`, 'error');
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = '📤 Upload to Google Drive';
    }
}

/**
 * Handle Google Sheets update
 */
export async function handleGoogleSheetsUpdate() {
    const updateSheetsBtn = document.getElementById('updateSheetsBtn');
    
    if (!window.uploadedFileData) {
        showUploadResult('No file data available. Please upload a file first.', 'error');
        return;
    }
    
    const { transactionNumber, documentType, fileUrl } = window.uploadedFileData;
    
    // Show loading state
    if (updateSheetsBtn) {
        updateSheetsBtn.disabled = true;
        updateSheetsBtn.textContent = '⏳ Updating Sheets...';
    }
    
    showUploadResult('Updating Google Sheets...', 'info');
    
    await updateGoogleSheetsDocument(transactionNumber, documentType, fileUrl);
    
    // Reset button
    if (updateSheetsBtn) {
        updateSheetsBtn.disabled = false;
        updateSheetsBtn.textContent = '📊 Update Google Sheets';
    }
}

/**
 * Update Google Sheets document
 */
export async function updateGoogleSheetsDocument(transactionNumber, documentType, fileUrl) {
    const selectedSheet = document.getElementById('searchSheet')?.value || 'be';
    
    console.log('Updating Google Sheets:', { transactionNumber, documentType, fileUrl, selectedSheet });
    
    try {
        const response = await fetch('/api/update_document', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                sheet_type: selectedSheet,
                transaction_number: transactionNumber,
                document_type: documentType,
                file_url: fileUrl
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showUploadResult('✅ Google Sheets updated successfully!', 'success');
            
            // Clear uploaded file data
            window.uploadedFileData = null;
            
            // Hide update button
            const updateSheetsBtn = document.getElementById('updateSheetsBtn');
            if (updateSheetsBtn) {
                updateSheetsBtn.style.display = 'none';
            }
            
            // Reset form
            const documentUploadForm = document.getElementById('documentUploadForm');
            if (documentUploadForm) {
                documentUploadForm.reset();
            }
        } else {
            showUploadResult(`❌ Update failed: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Update error:', error);
        showUploadResult(`❌ Update failed: ${error.message}`, 'error');
    }
}

/**
 * Initialize update form functionality
 */
export function initializeUpdateForm() {
    const documentTypeSelect = document.getElementById('documentTypeSelect');
    const uploadFormContainer = document.getElementById('uploadFormContainer');
    const uploadFormTitle = document.getElementById('uploadFormTitle');
    const documentUploadForm = document.getElementById('documentUploadForm');
    const cancelUploadBtn = document.getElementById('cancelUploadBtn');
    const updateSheetsBtn = document.getElementById('updateSheetsBtn');
    
    if (!documentTypeSelect || !uploadFormContainer) {
        console.log('Update form elements not found, skipping initialization');
        return;
    }
    
    // Handle upload mode toggle
    const uploadModeRadios = document.querySelectorAll('input[name="updateUploadMode"]');
    const fileUploadSection = document.getElementById('updateFileUploadSection');
    const linkInputSection = document.getElementById('linkInputSection');
    const uploadBtn = document.getElementById('uploadBtn');
    
    uploadModeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'file') {
                fileUploadSection.style.display = 'block';
                linkInputSection.style.display = 'none';
                uploadBtn.textContent = '📤 Upload to Google Drive';
            } else if (this.value === 'link') {
                fileUploadSection.style.display = 'none';
                linkInputSection.style.display = 'block';
                uploadBtn.textContent = '🔗 Process Google Drive Link';
            }
        });
    });
    
    // Show/hide upload form based on document type selection
    documentTypeSelect.addEventListener('change', function() {
        const selectedType = this.value;
        
        if (selectedType) {
            uploadFormContainer.style.display = 'block';
            
            const typeNames = {
                'bill': '📄 Bill (Normal Invoice)',
                'redBill': '🔴 Red Bill (Special Invoice)',
                'bankStatement': '🏦 Bank Statement',
                'documentation': '📋 Supporting Documentation'
            };
            uploadFormTitle.textContent = `Upload ${typeNames[selectedType]}`;
        } else {
            uploadFormContainer.style.display = 'none';
        }
    });
    
    // Cancel upload
    if (cancelUploadBtn) {
        cancelUploadBtn.addEventListener('click', function() {
            uploadFormContainer.style.display = 'none';
            documentTypeSelect.value = '';
            documentUploadForm.reset();
            hideUploadResult();
            
            if (updateSheetsBtn) {
                updateSheetsBtn.style.display = 'none';
            }
            
            window.uploadedFileData = null;
        });
    }
    
    // Handle form submission
    if (documentUploadForm) {
        documentUploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const selectedMode = document.querySelector('input[name="updateUploadMode"]:checked');
            
            if (!selectedMode) {
                showUploadResult('Please select an upload method.', 'error');
                return;
            }
            
            if (selectedMode.value === 'file') {
                handleDocumentUpload();
            } else if (selectedMode.value === 'link') {
                // Google Drive link handling - call from googleDriveService
                if (typeof window.handleGoogleDriveLink === 'function') {
                    window.handleGoogleDriveLink();
                } else {
                    console.error('handleGoogleDriveLink not found');
                }
            }
        });
    }
    
    // Handle Google Sheets update
    if (updateSheetsBtn) {
        updateSheetsBtn.addEventListener('click', handleGoogleSheetsUpdate);
    }
    
    console.log('✅ Update form service initialized');
}

// Expose to global scope for compatibility
window.handleDocumentUpload = handleDocumentUpload;
window.handleGoogleSheetsUpdate = handleGoogleSheetsUpdate;
window.updateGoogleSheetsDocument = updateGoogleSheetsDocument;
window.showUploadResult = showUploadResult;
window.hideUploadResult = hideUploadResult;

