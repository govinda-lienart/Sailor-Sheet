// Google Drive Link Processing - Handles Google Drive link processing for different document types
// Extracted from inline script - Step 5 of incremental refactoring

(function() {
    'use strict';
    
    // Utility function to show upload result
    function showUploadResult(message, type, section) {
        console.log(`Upload result (${section}): ${message}`);
        // This function is likely defined elsewhere, so we'll just log for now
        if (typeof window.showUploadResult === 'function') {
            window.showUploadResult(message, type, section);
        }
    }
    
    // Process Google Drive link for Bills
    function processBillsGoogleDriveLink() {
        const googleDriveLink = document.getElementById('billsGoogleDriveLink').value.trim();
        const processBtn = document.getElementById('billsGoogleDriveBtn');
        
        if (!googleDriveLink) {
            alert('Please enter a Google Drive URL.');
            return;
        }
        
        if (!googleDriveLink.includes('drive.google.com')) {
            alert('Please enter a valid Google Drive URL.');
            return;
        }
        
        const transactionNumber = document.getElementById('transactionNumberInput').value;
        if (!transactionNumber) {
            alert('Please generate a transaction number first.');
            return;
        }
        
        const selectedCountry = sessionStorage.getItem('selectedCountry') || 'BE';
        processBtn.disabled = true;
        const originalText = processBtn.textContent;
        
        // Progress animation
        let dots = 0;
        const progressInterval = setInterval(() => {
            dots = (dots + 1) % 4;
            processBtn.textContent = '🔄 Processing' + '.'.repeat(dots);
        }, 300);
        
        fetch('/api/process_google_drive_link', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                google_drive_url: googleDriveLink,
                document_type: 'bill',
                transaction_number: transactionNumber,
                country_code: selectedCountry
            })
        })
        .then(response => response.json())
        .then(data => {
            clearInterval(progressInterval);
            if (data.success) {
                document.getElementById('billsFileLinkInput').value = data.file_url;
                document.getElementById('billsFileNameInput').value = data.file_name;
                processBtn.textContent = '✅ Done!';
                setTimeout(() => {
                    alert(`✅ Bills file processed successfully!\nFile: ${data.file_name}`);
                    document.getElementById('billsGoogleDriveLink').value = '';
                    processBtn.textContent = originalText;
                }, 500);
            } else {
                throw new Error(data.error || 'Failed to process Google Drive link');
            }
        })
        .catch(error => {
            clearInterval(progressInterval);
            console.error('Error processing Bills Google Drive link:', error);
            processBtn.textContent = '❌ Failed';
            alert(`❌ Failed to process Google Drive link: ${error.message}`);
            setTimeout(() => {
                processBtn.textContent = originalText;
            }, 2000);
        })
        .finally(() => {
            processBtn.disabled = false;
        });
    }
    
    // Process Google Drive link for Red Bills (Vietnam only)
    function processRedBillsGoogleDriveLink() {
        const googleDriveLink = document.getElementById('redBillsGoogleDriveLink').value.trim();
        const processBtn = document.getElementById('redBillsGoogleDriveBtn');
        
        if (!googleDriveLink) {
            alert('Please enter a Google Drive URL.');
            return;
        }
        
        if (!googleDriveLink.includes('drive.google.com')) {
            alert('Please enter a valid Google Drive URL.');
            return;
        }
        
        const transactionNumber = document.getElementById('transactionNumberInput').value;
        if (!transactionNumber) {
            alert('Please generate a transaction number first.');
            return;
        }
        
        const selectedCountry = sessionStorage.getItem('selectedCountry') || 'VN';
        processBtn.disabled = true;
        const originalText = processBtn.textContent;
        
        // Progress animation
        let dots = 0;
        const progressInterval = setInterval(() => {
            dots = (dots + 1) % 4;
            processBtn.textContent = '🔄 Processing' + '.'.repeat(dots);
        }, 300);
        
        fetch('/api/process_google_drive_link', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                google_drive_url: googleDriveLink,
                document_type: 'redBill',
                transaction_number: transactionNumber,
                country_code: selectedCountry
            })
        })
        .then(response => response.json())
        .then(data => {
            clearInterval(progressInterval);
            if (data.success) {
                document.getElementById('redBillsFileLinkInput').value = data.file_url;
                document.getElementById('redBillsFileNameInput').value = data.file_name;
                processBtn.textContent = '✅ Done!';
                setTimeout(() => {
                    alert(`✅ Red Bills file processed successfully!\nFile: ${data.file_name}`);
                    document.getElementById('redBillsGoogleDriveLink').value = '';
                    processBtn.textContent = originalText;
                }, 500);
            } else {
                throw new Error(data.error || 'Failed to process Google Drive link');
            }
        })
        .catch(error => {
            clearInterval(progressInterval);
            console.error('Error processing Red Bills Google Drive link:', error);
            processBtn.textContent = '❌ Failed';
            alert(`❌ Failed to process Google Drive link: ${error.message}`);
            setTimeout(() => {
                processBtn.textContent = originalText;
            }, 2000);
        })
        .finally(() => {
            processBtn.disabled = false;
        });
    }
    
    // Process Google Drive link for Documentation
    function processDocumentationGoogleDriveLink() {
        const googleDriveLink = document.getElementById('documentationGoogleDriveLink').value.trim();
        const processBtn = document.getElementById('documentationGoogleDriveBtn');
        
        if (!googleDriveLink) {
            alert('Please enter a Google Drive URL.');
            return;
        }
        
        if (!googleDriveLink.includes('drive.google.com')) {
            alert('Please enter a valid Google Drive URL.');
            return;
        }
        
        const transactionNumber = document.getElementById('transactionNumberInput').value;
        if (!transactionNumber) {
            alert('Please generate a transaction number first.');
            return;
        }
        
        const selectedCountry = sessionStorage.getItem('selectedCountry') || 'BE';
        processBtn.disabled = true;
        const originalText = processBtn.textContent;
        
        // Progress animation
        let dots = 0;
        const progressInterval = setInterval(() => {
            dots = (dots + 1) % 4;
            processBtn.textContent = '🔄 Processing' + '.'.repeat(dots);
        }, 300);
        
        fetch('/api/process_google_drive_link', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                google_drive_url: googleDriveLink,
                document_type: 'documentation',
                transaction_number: transactionNumber,
                country_code: selectedCountry
            })
        })
        .then(response => response.json())
        .then(data => {
            clearInterval(progressInterval);
            if (data.success) {
                document.getElementById('documentationFileLinkInput').value = data.file_url;
                document.getElementById('documentationFileNameInput').value = data.file_name;
                processBtn.textContent = '✅ Done!';
                setTimeout(() => {
                    alert(`✅ Documentation file processed successfully!\nFile: ${data.file_name}`);
                    document.getElementById('documentationGoogleDriveLink').value = '';
                    processBtn.textContent = originalText;
                }, 500);
            } else {
                throw new Error(data.error || 'Failed to process Google Drive link');
            }
        })
        .catch(error => {
            clearInterval(progressInterval);
            console.error('Error processing Documentation Google Drive link:', error);
            processBtn.textContent = '❌ Failed';
            alert(`❌ Failed to process Google Drive link: ${error.message}`);
            setTimeout(() => {
                processBtn.textContent = originalText;
            }, 2000);
        })
        .finally(() => {
            processBtn.disabled = false;
        });
    }
    
    // Handle Google Drive processing for dropdown-based upload
    function handleGoogleDriveProcessing() {
        const dropdown = document.getElementById('documentTypeDropdown');
        const googleDriveLink = document.getElementById('googleDriveLinkInput').value.trim();
        const processBtn = document.getElementById('processGoogleDriveBtn');
        const uploadStatus = document.getElementById('uploadStatus');
        const uploadStatusMessage = document.getElementById('uploadStatusMessage');
        
        const selectedType = dropdown.value;
        
        if (!selectedType || !googleDriveLink) {
            alert('Please select a document type and enter a Google Drive URL.');
            return;
        }
        
        if (!googleDriveLink.includes('drive.google.com')) {
            alert('Please enter a valid Google Drive URL.');
            return;
        }
        
        // Get transaction number
        const transactionNumber = document.getElementById('transactionNumberInput').value;
        if (!transactionNumber) {
            alert('Please generate a transaction number first.');
            return;
        }
        
        // Get current country
        const selectedCountry = sessionStorage.getItem('selectedCountry') || 'BE';
        console.log(`DEBUG: Processing Google Drive link for country: ${selectedCountry}`);
        console.log(`DEBUG: Processing Google Drive link for ${selectedType}: ${googleDriveLink}`);
        console.log(`DEBUG: Transaction number: ${transactionNumber}`);
        
        // Show processing state with progress
        processBtn.disabled = true;
        processBtn.textContent = '🔄 Processing...';
        uploadStatus.style.display = 'block';
        uploadStatus.style.background = '#fff3cd';
        uploadStatus.style.borderColor = '#ffc107';
        uploadStatusMessage.style.color = '#856404';
        uploadStatusMessage.innerHTML = '⏳ <strong>Processing Google Drive link... 0%</strong>';
        
        // Simulate progress animation
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += Math.random() * 12;
            if (progress > 85) progress = 85;
            uploadStatusMessage.innerHTML = `⏳ <strong>Processing Google Drive link... ${Math.round(progress)}%</strong>`;
        }, 250);
        
        // Map document types to API document types
        const documentTypeMapping = {
            'bills': 'bill',
            'redBills': 'redBill',
            'bankStatement': 'bankStatement',
            'documentation': 'documentation'
        };
        const documentType = documentTypeMapping[selectedType];
        
        // Call API to process Google Drive link
        fetch('/api/process_google_drive_link', {
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
        })
        .then(response => response.json())
        .then(data => {
            clearInterval(progressInterval);
            uploadStatusMessage.innerHTML = '⏳ <strong>Processing Google Drive link... 100%</strong>';
            
            if (data.success) {
                // Store processed file data in hidden fields
                // Map dropdown values to correct field IDs
                const fieldMapping = {
                    'bills': 'bills',
                    'redBills': 'redBills', 
                    'bankStatement': 'bankStatement',
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
                uploadStatusMessage.innerHTML = `✅ <strong>Google Drive link processed successfully!</strong><br>File: ${data.file_name}`;
                
                // Clear inputs after a delay
                setTimeout(() => {
                    document.getElementById('googleDriveLinkInput').value = '';
                    dropdown.value = '';
                    document.getElementById('uploadModeToggle').style.display = 'none';
                    document.getElementById('googleDriveLinkSection').style.display = 'none';
                }, 2000);
                
                console.log('DEBUG: Google Drive link processed successfully');
            } else {
                throw new Error(data.error || 'Failed to process Google Drive link');
            }
        })
        .catch(error => {
            clearInterval(progressInterval);
            console.error('Error processing Google Drive link:', error);
            uploadStatus.style.background = '#f8d7da';
            uploadStatus.style.borderColor = '#f5c6cb';
            uploadStatusMessage.style.color = '#721c24';
            uploadStatusMessage.innerHTML = `❌ <strong>Failed to process link:</strong> ${error.message}`;
        })
        .finally(() => {
            processBtn.disabled = false;
            processBtn.textContent = 'Process Google Drive Link';
        });
    }
    
    // Set up event listeners when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        const processGoogleDriveBtn = document.getElementById('processGoogleDriveBtn');
        if (processGoogleDriveBtn) {
            processGoogleDriveBtn.addEventListener('click', handleGoogleDriveProcessing);
            console.log('✅ Process Google Drive Link button listener attached');
        }
    });
    
    // Expose functions to global scope (needed by HTML onclick handlers)
    window.processBillsGoogleDriveLink = processBillsGoogleDriveLink;
    window.processRedBillsGoogleDriveLink = processRedBillsGoogleDriveLink;
    window.processDocumentationGoogleDriveLink = processDocumentationGoogleDriveLink;
    window.handleGoogleDriveProcessing = handleGoogleDriveProcessing;
    
    console.log('✅ Google Drive link processing module initialized');
})();
