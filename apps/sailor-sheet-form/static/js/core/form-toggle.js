// Form Toggle - Switch between New Entry and Update Entry modes
// Extracted from inline script - Step 3 of incremental refactoring

(function() {
    'use strict';
    
    document.addEventListener('DOMContentLoaded', function() {
        const newEntryBtn = document.getElementById('newEntryBtn');
        const updateEntryBtn = document.getElementById('updateEntryBtn');
        const mainFormContainer = document.querySelector('.form-container:not(.update-form-container)');
        const updateFormContainer = document.getElementById('updateFormContainer');

        if (!newEntryBtn || !updateEntryBtn || !mainFormContainer || !updateFormContainer) {
            console.warn('Form toggle: Required elements not found');
            return;
        }

        // New Entry Button Click
        newEntryBtn.addEventListener('click', function() {
            // Update active states
            newEntryBtn.classList.add('active');
            updateEntryBtn.classList.remove('active');
            
            // Show/hide forms
            mainFormContainer.style.display = 'block';
            updateFormContainer.style.display = 'none';
            
            console.log('✏️ Switched to New Entry mode');
        });

        // Update Entry Button Click
        updateEntryBtn.addEventListener('click', function() {
            // Update active states
            updateEntryBtn.classList.add('active');
            newEntryBtn.classList.remove('active');
            
            // Show/hide forms
            mainFormContainer.style.display = 'none';
            updateFormContainer.style.display = 'block';
            
            console.log('🔄 Switched to Update Entry mode');
        });

        console.log('✅ Form toggle initialized');
    });
})();

