/**
 * File Upload Service
 * Handles file uploads and drag & drop functionality
 */

import { FILE_TYPES } from '../config/constants.js';

/**
 * Prevent default drag and drop behaviors
 */
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

/**
 * Generic upload function for different file types
 */
export function uploadFile(fileType) {
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

/**
 * Specific upload functions for each file type
 */
export function uploadBills() { uploadFile(FILE_TYPES.BILLS); }
export function uploadRedBills() { uploadFile(FILE_TYPES.RED_BILLS); }
export function uploadDocumentation() { uploadFile(FILE_TYPES.DOCUMENTATION); }

/**
 * Setup drag and drop functionality
 */
export function setupDragAndDrop() {
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

/**
 * Reset all upload-related UI state
 */
export function resetUploadState() {
    console.log('🧹 Resetting upload state...');
    
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
    
    // Clear file upload result displays
    const uploadResultElements = [
        'billsUploadResult',
        'redBillsUploadResult', 
        'documentationUploadResult'
    ];
    
    uploadResultElements.forEach(elementId => {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.display = 'none';
            element.innerHTML = '';
        }
    });
    
    // Clear file link displays
    const fileLinkElements = [
        'billsFileLink',
        'redBillsFileLink',
        'documentationFileLink'
    ];
    
    fileLinkElements.forEach(elementId => {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = '';
        }
    });
    
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

