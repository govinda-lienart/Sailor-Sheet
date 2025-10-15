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
                
                // Show processing message
                const updateBtn = this;
                const originalText = updateBtn.innerHTML;
                updateBtn.innerHTML = '⏳ Processing...';
                updateBtn.disabled = true;
                
                // Simulate file upload processing
                setTimeout(() => {
                    alert('✅ Transaction documents updated successfully!\n\nNew files will replace existing ones in Google Sheets.');
                    updateBtn.innerHTML = originalText;
                    updateBtn.disabled = false;
                    
                    // Reset file inputs
                    document.getElementById('billsFile').value = '';
                    document.getElementById('redBillsFile').value = '';
                    document.getElementById('documentationFile').value = '';
                }, 2000);
                
                console.log('🔄 Updating transaction documents...');
            });
            
            console.log('✅ Update transaction button listener attached');
        }
    });
    
    console.log('✅ Update transaction button module initialized');
    
})();

