/**
 * Google Drive Service
 * Handles Google Drive link processing and file operations
 */

import { showUploadResult } from './updateFormService.js';

/**
 * Get transaction number from various sources
 */
function getTransactionNumber(context = 'main') {
    let transactionNumber = '';
    
    if (context === 'update') {
        // For update form, try search input first
        const searchInput = document.getElementById('searchTransactionNumber');
        if (searchInput && searchInput.value.trim()) {
            transactionNumber = searchInput.value.trim();
            return transactionNumber;
        }
        
        // Try from search results table
        const searchResults = document.getElementById('searchResults');
        const transactionTable = searchResults ? searchResults.querySelector('table') : null;
        if (transactionTable) {
            const allRows = Array.from(transactionTable.querySelectorAll('tr'));
            const transactionRow = allRows.find(row => 
                row.cells[0] && row.cells[0].textContent.trim().includes('Transaction Number')
            );
            if (transactionRow && transactionRow.cells[1]) {
                const value = transactionRow.cells[1].textContent.trim();
                if (value && value !== '—') {
                    return value;
                }
            }
        }
    }
    
    // Fallback to main form transaction number
    const transactionInput = document.getElementById('transactionNumberInput');
    return transactionInput ? transactionInput.value : '';
}

/**
 * Process Google Drive link (generic function)
 */
async function processGoogleDriveLink(config) {
    const {
        linkInputId,
        buttonId,
        documentType,
        fileLinkInputId,
        fileNameInputId,
        context = 'main',
        section = null
    } = config;
    
    const googleDriveLinkInput = document.getElementById(linkInputId);
    const processBtn = document.getElementById(buttonId);
    
    if (!googleDriveLinkInput || !processBtn) {
        console.error('Required elements not found:', { linkInputId, buttonId });
        return;
    }
    
    const googleDriveLink = googleDriveLinkInput.value.trim();
    
    if (!googleDriveLink) {
        showUploadResult('Please enter a Google Drive URL.', 'error', section);
        return;
    }
    
    if (!googleDriveLink.includes('drive.google.com')) {
        showUploadResult('Please enter a valid Google Drive URL.', 'error', section);
        return;
    }
    
    // Get transaction number
    const transactionNumber = getTransactionNumber(context);
    if (!transactionNumber) {
        const message = context === 'update' 
            ? 'Please search for a transaction first.' 
            : 'Please generate a transaction number first.';
        showUploadResult(message, 'error', section);
        return;
    }
    
    // Get current country
    const selectedCountry = sessionStorage.getItem('selectedCountry') || 'BE';
    
    console.log(`Processing ${documentType} Google Drive link:`, googleDriveLink);
    console.log(`Transaction number:`, transactionNumber);
    console.log(`Country:`, selectedCountry);
    
    // Show processing state
    processBtn.disabled = true;
    const originalText = processBtn.textContent;
    processBtn.textContent = '🔄 Processing...';
    
    try {
        const response = await fetch('/api/process_google_drive_link', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                google_drive_url: googleDriveLink,
                document_type: documentType,
                transaction_number: transactionNumber,
                country_code: selectedCountry
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Store processed file data in hidden fields
            if (fileLinkInputId && fileNameInputId) {
                const fileLinkInput = document.getElementById(fileLinkInputId);
                const fileNameInput = document.getElementById(fileNameInputId);
                if (fileLinkInput) fileLinkInput.value = data.file_url;
                if (fileNameInput) fileNameInput.value = data.file_name;
            }
            
            // Show success message
            const typeLabel = documentType === 'bill' ? 'Bills' : 
                            documentType === 'redBill' ? 'Red Bills' : 
                            documentType === 'bankStatement' ? 'Bank Statement' : 
                            'Documentation';
            showUploadResult(`✅ ${typeLabel} file processed successfully!<br>File: ${data.file_name}`, 'success', section);
            
            // Clear the input
            googleDriveLinkInput.value = '';
            
            console.log(`${documentType} Google Drive link processed successfully`);
            
            // If in update form context, show the update sheets button
            if (context === 'update') {
                const updateSheetsBtn = document.getElementById('updateSheetsBtn');
                if (updateSheetsBtn) {
                    updateSheetsBtn.style.display = 'inline-block';
                }
                
                // Store file data for later update
                window.uploadedFileData = {
                    transactionNumber,
                    documentType,
                    fileUrl: data.file_url
                };
            }
        } else {
            throw new Error(data.error || 'Failed to process Google Drive link');
        }
    } catch (error) {
        console.error(`Error processing ${documentType} Google Drive link:`, error);
        showUploadResult(`❌ Failed to process Google Drive link: ${error.message}`, 'error', section);
    } finally {
        processBtn.disabled = false;
        processBtn.textContent = originalText;
    }
}

/**
 * Process Bills Google Drive link (Main Form)
 */
export function processBillsGoogleDriveLinkMain() {
    processGoogleDriveLink({
        linkInputId: 'billsGoogleDriveLinkMain',
        buttonId: 'billsGoogleDriveBtnMain',
        documentType: 'bill',
        fileLinkInputId: 'billsFileLinkInput',
        fileNameInputId: 'billsFileNameInput',
        context: 'main',
        section: 'bills'
    });
}

/**
 * Process Red Bills Google Drive link (Main Form)
 */
export function processRedBillsGoogleDriveLinkMain() {
    processGoogleDriveLink({
        linkInputId: 'redBillsGoogleDriveLinkMain',
        buttonId: 'redBillsGoogleDriveBtnMain',
        documentType: 'redBill',
        fileLinkInputId: 'redBillsFileLinkInput',
        fileNameInputId: 'redBillsFileNameInput',
        context: 'main',
        section: 'redBills'
    });
}

/**
 * Process Documentation Google Drive link (Main Form)
 */
export function processDocumentationGoogleDriveLinkMain() {
    processGoogleDriveLink({
        linkInputId: 'documentationGoogleDriveLinkMain',
        buttonId: 'documentationGoogleDriveBtnMain',
        documentType: 'documentation',
        fileLinkInputId: 'documentationFileLinkInput',
        fileNameInputId: 'documentationFileNameInput',
        context: 'main',
        section: 'documentation'
    });
}

/**
 * Process Bills Google Drive link (Original/Upload Section)
 */
export function processBillsGoogleDriveLink() {
    processGoogleDriveLink({
        linkInputId: 'billsGoogleDriveLink',
        buttonId: 'billsGoogleDriveBtn',
        documentType: 'bill',
        fileLinkInputId: 'billsFileLinkInput',
        fileNameInputId: 'billsFileNameInput',
        context: 'main',
        section: 'bills'
    });
}

/**
 * Process Red Bills Google Drive link (Original/Upload Section)
 */
export function processRedBillsGoogleDriveLink() {
    processGoogleDriveLink({
        linkInputId: 'redBillsGoogleDriveLink',
        buttonId: 'redBillsGoogleDriveBtn',
        documentType: 'redBill',
        fileLinkInputId: 'redBillsFileLinkInput',
        fileNameInputId: 'redBillsFileNameInput',
        context: 'main',
        section: 'redBills'
    });
}

/**
 * Process Documentation Google Drive link (Original/Upload Section)
 */
export function processDocumentationGoogleDriveLink() {
    processGoogleDriveLink({
        linkInputId: 'documentationGoogleDriveLink',
        buttonId: 'documentationGoogleDriveBtn',
        documentType: 'documentation',
        fileLinkInputId: 'documentationFileLinkInput',
        fileNameInputId: 'documentationFileNameInput',
        context: 'main',
        section: 'documentation'
    });
}

/**
 * Handle Google Drive link (Update Form)
 */
export async function handleGoogleDriveLink() {
    console.log('handleGoogleDriveLink() called for update form');
    
    const documentTypeSelect = document.getElementById('documentTypeSelect');
    const googleDriveLinkInput = document.getElementById('googleDriveLink');
    
    const selectedType = documentTypeSelect ? documentTypeSelect.value : '';
    const googleDriveLink = googleDriveLinkInput ? googleDriveLinkInput.value.trim() : '';
    
    if (!selectedType || !googleDriveLink) {
        showUploadResult('Please select a document type and enter a Google Drive URL.', 'error');
        return;
    }
    
    if (!googleDriveLink.includes('drive.google.com')) {
        showUploadResult('Please enter a valid Google Drive URL.', 'error');
        return;
    }
    
    // Get transaction number
    const transactionNumber = getTransactionNumber('update');
    if (!transactionNumber) {
        showUploadResult('Transaction number not found. Please search for a transaction first.', 'error');
        return;
    }
    
    // Get current country
    const selectedCountry = sessionStorage.getItem('selectedCountry') || 'BE';
    const selectedSheet = document.getElementById('searchSheet')?.value || selectedCountry.toLowerCase();
    
    console.log('Processing Google Drive link for update form:', {
        selectedType,
        transactionNumber,
        selectedCountry,
        selectedSheet,
        googleDriveLink
    });
    
    // Show processing state
    const uploadBtn = document.getElementById('uploadBtn');
    if (uploadBtn) {
        uploadBtn.disabled = true;
        uploadBtn.textContent = '🔄 Processing...';
    }
    
    showUploadResult('Processing Google Drive link...', 'info');
    
    try {
        const response = await fetch('/api/process_google_drive_link', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                google_drive_url: googleDriveLink,
                document_type: selectedType,
                transaction_number: transactionNumber,
                country_code: selectedCountry
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showUploadResult(`✅ File processed successfully!<br>File: ${data.file_name}`, 'success');
            
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
            
            // Clear the input
            if (googleDriveLinkInput) {
                googleDriveLinkInput.value = '';
            }
        } else {
            throw new Error(data.error || 'Failed to process Google Drive link');
        }
    } catch (error) {
        console.error('Error processing Google Drive link:', error);
        showUploadResult(`❌ Failed to process Google Drive link: ${error.message}`, 'error');
    } finally {
        if (uploadBtn) {
            uploadBtn.disabled = false;
            uploadBtn.textContent = '🔗 Process Google Drive Link';
        }
    }
}

/**
 * Initialize Google Drive service
 */
export function initializeGoogleDriveService() {
    console.log('✅ Google Drive service initialized');
}

// Expose to global scope for compatibility
window.processBillsGoogleDriveLink = processBillsGoogleDriveLink;
window.processRedBillsGoogleDriveLink = processRedBillsGoogleDriveLink;
window.processDocumentationGoogleDriveLink = processDocumentationGoogleDriveLink;
window.processBillsGoogleDriveLinkMain = processBillsGoogleDriveLinkMain;
window.processRedBillsGoogleDriveLinkMain = processRedBillsGoogleDriveLinkMain;
window.processDocumentationGoogleDriveLinkMain = processDocumentationGoogleDriveLinkMain;
window.handleGoogleDriveLink = handleGoogleDriveLink;

