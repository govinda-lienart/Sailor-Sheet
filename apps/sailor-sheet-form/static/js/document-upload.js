// Document Upload Module - Handles dropdown-based document upload
// Extracted from inline script - Step 4 of incremental refactoring

(function() {
    'use strict';
    
    // Handle document type dropdown change
    function handleDocumentTypeChange() {
        const dropdown = document.getElementById('documentTypeDropdown');
        const uploadModeToggle = document.getElementById('uploadModeToggle');
        const fileUploadSection = document.getElementById('fileUploadSection');
        const googleDriveLinkSection = document.getElementById('googleDriveLinkSection');
        const uploadStatus = document.getElementById('uploadStatus');
        
        if (dropdown.value) {
            uploadModeToggle.style.display = 'block';
            uploadStatus.style.display = 'none';
            
            // Set up event listeners for upload mode radios when they become visible
            const uploadModeRadios = document.querySelectorAll('input[name="updateUploadMode"]');
            uploadModeRadios.forEach((radio) => {
                radio.addEventListener('change', handleUploadModeChange);
            });
            
            // Force show file upload section if "Upload File" is selected
            const uploadFileRadio = document.querySelector('input[name="uploadMode"][value="file"]:checked') || 
                                   document.querySelector('input[name="updateUploadMode"][value="file"]:checked');
            if (uploadFileRadio && fileUploadSection) {
                fileUploadSection.style.display = 'block';
            }
        } else {
            uploadModeToggle.style.display = 'none';
            fileUploadSection.style.display = 'none';
            googleDriveLinkSection.style.display = 'none';
            uploadStatus.style.display = 'none';
        }
    }
    
    // Handle upload mode change (works for both main form and update form)
    function handleUploadModeChange() {
        // Main form elements
        const fileUploadSection = document.getElementById('fileUploadSection');
        const googleDriveLinkSection = document.getElementById('googleDriveLinkSection');
        
        // Update form elements
        const updateFileUploadSection = document.getElementById('updateFileUploadSection');
        const linkInputSection = document.getElementById('linkInputSection');
        
        // Check for both main form (uploadMode) and update form (updateUploadMode) radio buttons
        const mainFormRadio = document.querySelector('input[name="uploadMode"]:checked');
        const updateFormRadio = document.querySelector('input[name="updateUploadMode"]:checked');
        const uploadMode = mainFormRadio ? mainFormRadio.value : (updateFormRadio ? updateFormRadio.value : null);
        
        if (!uploadMode) {
            console.log('ERROR: No upload mode radio button found');
            return;
        }
        
        if (uploadMode === 'file') {
            // Main form
            if (fileUploadSection) fileUploadSection.style.display = 'block';
            if (googleDriveLinkSection) googleDriveLinkSection.style.display = 'none';
            // Update form
            if (updateFileUploadSection) updateFileUploadSection.style.display = 'block';
            if (linkInputSection) linkInputSection.style.display = 'none';
        } else if (uploadMode === 'link') {
            // Main form
            if (fileUploadSection) fileUploadSection.style.display = 'none';
            if (googleDriveLinkSection) googleDriveLinkSection.style.display = 'block';
            // Update form
            if (updateFileUploadSection) updateFileUploadSection.style.display = 'none';
            if (linkInputSection) linkInputSection.style.display = 'block';
        }
    }
    
    // Handle file upload
    function handleFileUpload() {
        const dropdown = document.getElementById('documentTypeDropdown');
        const fileInput = document.getElementById('documentFileInput');
        const uploadBtn = document.getElementById('uploadFileBtn');
        const uploadStatus = document.getElementById('uploadStatus');
        const uploadStatusMessage = document.getElementById('uploadStatusMessage');
        
        const selectedType = dropdown.value;
        const file = fileInput.files[0];
        
        if (!selectedType || !file) {
            alert('Please select a document type and file.');
            return;
        }
        
        // Get transaction number
        const transactionNumber = document.getElementById('transactionNumberInput').value;
        if (!transactionNumber) {
            alert('Please generate a transaction number first.');
            return;
        }
        
        console.log(`DEBUG: Uploading file for ${selectedType}: ${file.name}`);
        console.log(`DEBUG: Transaction number: ${transactionNumber}`);
        
        // Show processing state with progress
        uploadBtn.disabled = true;
        uploadBtn.textContent = '🔄 Uploading...';
        uploadStatus.style.display = 'block';
        uploadStatus.style.background = '#fff3cd';
        uploadStatus.style.borderColor = '#ffc107';
        uploadStatusMessage.style.color = '#856404';
        uploadStatusMessage.innerHTML = '⏳ <strong>Uploading file... 0%</strong>';
        
        // Get current country
        const selectedCountry = sessionStorage.getItem('selectedCountry') || 'BE';
        console.log(`DEBUG: Uploading file for country: ${selectedCountry}`);
        
        // Create form data
        const formData = new FormData();
        formData.append('file', file);
        formData.append('transaction_number', transactionNumber);
        formData.append('country_code', selectedCountry);
        
        // Map document types to file types
        const fileTypeMapping = {
            'bills': 'bills',
            'redBills': 'redBills',
            'bankStatement': 'bankStatement',
            'documentation': 'documentation'
        };
        const fileType = fileTypeMapping[selectedType];
        formData.append('file_type', fileType);
        
        // Simulate progress animation
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) progress = 90;
            uploadStatusMessage.innerHTML = `⏳ <strong>Uploading file... ${Math.round(progress)}%</strong>`;
        }, 200);
        
        // Upload file
        fetch('/api/upload_file', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            clearInterval(progressInterval);
            uploadStatusMessage.innerHTML = '⏳ <strong>Uploading file... 100%</strong>';
            
            if (data.success) {
                // Store processed file data in hidden fields
                // Map dropdown values to correct field IDs
                const fieldMapping = {
                    'bills': 'bills',
                    'redBills': 'redBills', 
                    'documentation': 'documentation'
                };
                
                const fieldPrefix = fieldMapping[selectedType];
                const linkField = document.getElementById(`${fieldPrefix}FileLinkInput`);
                const nameField = document.getElementById(`${fieldPrefix}FileNameInput`);
                
                if (linkField && nameField) {
                    linkField.value = data.file_url;
                    nameField.value = data.file_name;
                }
                
                // Show success
                uploadStatus.style.background = '#d4edda';
                uploadStatus.style.borderColor = '#c3e6cb';
                uploadStatusMessage.style.color = '#155724';
                uploadStatusMessage.innerHTML = `✅ <strong>File uploaded successfully!</strong><br>File: ${data.file_name}`;
                
                // Clear inputs after a delay
                setTimeout(() => {
                    fileInput.value = '';
                    dropdown.value = '';
                    document.getElementById('uploadModeToggle').style.display = 'none';
                    document.getElementById('fileUploadSection').style.display = 'none';
                }, 2000);
                
                console.log('DEBUG: File uploaded successfully');
            } else {
                throw new Error(data.error || 'Upload failed');
            }
        })
        .catch(error => {
            clearInterval(progressInterval);
            console.error('Error uploading file:', error);
            uploadStatus.style.background = '#f8d7da';
            uploadStatus.style.borderColor = '#f5c6cb';
            uploadStatusMessage.style.color = '#721c24';
            uploadStatusMessage.innerHTML = `❌ <strong>Upload failed:</strong> ${error.message}`;
        })
        .finally(() => {
            uploadBtn.disabled = false;
            uploadBtn.textContent = '📤 Upload File';
        });
    }
    
    // Show upload result message
    function showUploadResult(message, type, section = 'main') {
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
    
    // Hide upload result message
    function hideUploadResult(section = 'main') {
        const uploadResult = document.getElementById('uploadResult');
        if (uploadResult) {
            uploadResult.style.display = 'none';
        }
    }
    
    // Set up drag-and-drop functionality
    function setupDragAndDrop() {
        const fileUploadSection = document.getElementById('fileUploadSection');
        const dragDropZone = document.getElementById('dragDropZone');
        const fileInput = document.getElementById('documentFileInput');
        
        if (!fileUploadSection || !fileInput) return;
        
        // Make drag-drop zone clickable to open file browser
        if (dragDropZone) {
            dragDropZone.addEventListener('click', () => {
                fileInput.click();
            });
        }
        
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            fileUploadSection.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });
        
        // Highlight drop area when dragging over it
        ['dragenter', 'dragover'].forEach(eventName => {
            fileUploadSection.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            fileUploadSection.addEventListener(eventName, unhighlight, false);
        });
        
        // Handle dropped files
        fileUploadSection.addEventListener('drop', handleDrop, false);
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        function highlight(e) {
            if (dragDropZone) {
                dragDropZone.style.borderColor = '#0056b3';
                dragDropZone.style.background = '#d4e9ff';
                dragDropZone.style.transform = 'scale(1.02)';
            }
        }
        
        function unhighlight(e) {
            if (dragDropZone) {
                dragDropZone.style.borderColor = '#007bff';
                dragDropZone.style.background = '#f0f8ff';
                dragDropZone.style.transform = 'scale(1)';
            }
        }
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                fileInput.files = files;
                console.log(`✅ File dropped: ${files[0].name}`);
                
                // Show visual feedback
                const uploadStatus = document.getElementById('uploadStatus');
                const uploadStatusMessage = document.getElementById('uploadStatusMessage');
                if (uploadStatus && uploadStatusMessage) {
                    uploadStatus.style.display = 'block';
                    uploadStatus.style.background = '#d1ecf1';
                    uploadStatus.style.borderColor = '#bee5eb';
                    uploadStatusMessage.style.color = '#0c5460';
                    uploadStatusMessage.innerHTML = `📎 <strong>File ready:</strong> ${files[0].name}`;
                }
            }
        }
        
        console.log('✅ Drag-and-drop functionality enabled for file upload');
    }
    
    // Set up event listeners when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        const documentTypeDropdown = document.getElementById('documentTypeDropdown');
        if (documentTypeDropdown) {
            documentTypeDropdown.addEventListener('change', handleDocumentTypeChange);
            console.log('✅ Document type dropdown listener attached');
        }

        const uploadModeRadios = document.querySelectorAll('input[name="uploadMode"]');
        uploadModeRadios.forEach(radio => {
            radio.addEventListener('change', handleUploadModeChange);
        });
        console.log(`✅ Attached listeners to ${uploadModeRadios.length} upload mode radios`);

        const uploadFileBtn = document.getElementById('uploadFileBtn');
        if (uploadFileBtn) {
            uploadFileBtn.addEventListener('click', handleFileUpload);
            console.log('✅ Upload file button listener attached');
        }
        
        // Enable drag-and-drop
        setupDragAndDrop();
    });
    
    // Expose functions to global scope (needed by HTML onclick/onchange handlers)
    window.handleDocumentTypeChange = handleDocumentTypeChange;
    window.handleUploadModeChange = handleUploadModeChange;
    window.handleFileUpload = handleFileUpload;
    window.showUploadResult = showUploadResult;
    window.hideUploadResult = hideUploadResult;
    
    console.log('✅ Document upload module initialized');
})();
