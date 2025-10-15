// Update Transaction Button Module - Handles the update transaction button functionality
// Extracted from inline script - Step 10 (Final module) of incremental refactoring

(function() {
    'use strict';
    
    // Set up event listeners when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        
        // Update Transaction Button Click
        const updateTransactionBtn = document.getElementById('updateTransactionBtn');
        if (updateTransactionBtn) {
            updateTransactionBtn.addEventListener('click', function() {
                const billsFile = document.getElementById('billsFile').files[0];
                const redBillsFile = document.getElementById('redBillsFile').files[0];
                const documentationFile = document.getElementById('documentationFile').files[0];
                
                if (!billsFile && !redBillsFile && !documentationFile) {
                    alert('Please select at least one file to upload');
                    return;
                }
                
                // Show processing message and progress bar
                const updateBtn = this;
                const originalText = updateBtn.innerHTML;
                updateBtn.innerHTML = '🔄 Uploading...';
                updateBtn.disabled = true;
                
                // Show progress bar
                const uploadProgress = document.getElementById('uploadProgress');
                const progressBar = document.getElementById('progressBar');
                const progressText = document.getElementById('progressText');
                
                if (uploadProgress && progressBar && progressText) {
                    uploadProgress.style.display = 'block';
                    progressBar.style.width = '0%';
                    progressText.textContent = 'Preparing upload...';
                    
                    // Simulate progress
                    let progress = 0;
                    const progressInterval = setInterval(() => {
                        progress += Math.random() * 15;
                        if (progress > 90) progress = 90;
                        progressBar.style.width = progress + '%';
                        progressText.textContent = `Uploading... ${Math.round(progress)}%`;
                    }, 200);
                    
                    // Complete upload after 2 seconds
                    setTimeout(() => {
                        clearInterval(progressInterval);
                        progressBar.style.width = '100%';
                        progressText.textContent = 'Complete!';
                        
                        // Show success message
                        setTimeout(() => {
                            alert('✅ Transaction documents updated successfully!\n\nNew files will replace existing ones in Google Sheets.');
                            updateBtn.innerHTML = originalText;
                            updateBtn.disabled = false;
                            
                            // Hide progress bar
                            uploadProgress.style.display = 'none';
                            
                            // Reset file inputs
                            document.getElementById('billsFile').value = '';
                            document.getElementById('redBillsFile').value = '';
                            document.getElementById('documentationFile').value = '';
                        }, 500);
                    }, 2000);
                } else {
                    // Fallback if progress elements not found
                    setTimeout(() => {
                        alert('✅ Transaction documents updated successfully!\n\nNew files will replace existing ones in Google Sheets.');
                        updateBtn.innerHTML = originalText;
                        updateBtn.disabled = false;
                        
                        // Reset file inputs
                        document.getElementById('billsFile').value = '';
                        document.getElementById('redBillsFile').value = '';
                        document.getElementById('documentationFile').value = '';
                    }, 2000);
                }
                
                console.log('🔄 Updating transaction documents...');
            });
            
            console.log('✅ Update transaction button listener attached');
        }
    });
    
    console.log('✅ Update transaction button module initialized');
    
})();

