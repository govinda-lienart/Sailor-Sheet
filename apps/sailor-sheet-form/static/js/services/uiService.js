/**
 * UI Service - User Interface Helpers
 * Handles messages, popups, and visual feedback
 */

/**
 * Smooth scroll to a specific section on the page
 */
export function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

/**
 * Show success message popup
 */
export function showSuccessMessage(message) {
    console.log('showSuccessMessage called with:', message);
    
    // Check if there's already a success popup and remove it
    const existingPopup = document.querySelector('.success-popup');
    if (existingPopup) {
        console.log('Removing existing success popup');
        existingPopup.remove();
    }
    
    // Create success popup
    const popup = document.createElement('div');
    popup.className = 'success-popup';
    popup.innerHTML = `
        <div class="success-content">
            <div class="success-icon">✅</div>
            <div class="success-text">${message}</div>
        </div>
    `;
    
    // Add to page
    document.body.appendChild(popup);
    
    // Show popup
    setTimeout(() => popup.classList.add('show'), 100);
    
    // Remove popup after 3 seconds
    setTimeout(() => {
        popup.classList.remove('show');
        setTimeout(() => {
            if (popup.parentNode) {
                document.body.removeChild(popup);
            }
        }, 300);
    }, 3000);
}

/**
 * Show error message popup
 */
export function showErrorMessage(message) {
    // Create error popup
    const popup = document.createElement('div');
    popup.className = 'error-popup';
    popup.innerHTML = `
        <div class="error-content">
            <div class="error-icon">❌</div>
            <div class="error-text">${message}</div>
        </div>
    `;
    
    // Add to page
    document.body.appendChild(popup);
    
    // Show popup
    setTimeout(() => popup.classList.add('show'), 100);
    
    // Remove popup after 5 seconds
    setTimeout(() => {
        popup.classList.remove('show');
        setTimeout(() => document.body.removeChild(popup), 300);
    }, 5000);
}

/**
 * Show temporary message
 */
export function showTemporaryMessage(message, type = 'info') {
    // Create message element
    const messageEl = document.createElement('div');
    messageEl.className = `temp-message temp-message-${type}`;
    messageEl.textContent = message;
    messageEl.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 10px 15px;
        border-radius: 4px;
        color: white;
        font-size: 14px;
        z-index: 10000;
        opacity: 0;
        transition: opacity 0.3s ease;
        ${type === 'success' ? 'background-color: #28a745;' : ''}
        ${type === 'error' ? 'background-color: #dc3545;' : ''}
        ${type === 'info' ? 'background-color: #17a2b8;' : ''}
    `;
    
    document.body.appendChild(messageEl);
    
    // Fade in
    setTimeout(() => messageEl.style.opacity = '1', 10);
    
    // Fade out and remove
    setTimeout(() => {
        messageEl.style.opacity = '0';
        setTimeout(() => document.body.removeChild(messageEl), 300);
    }, 3000);
}

/**
 * Show section validation message
 */
export function showSectionValidationMessage(message) {
    // Remove existing validation message
    const existingMessage = document.querySelector('.section-validation-message');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    // Create new validation message
    const validationMessage = document.createElement('div');
    validationMessage.className = 'section-validation-message';
    validationMessage.style.cssText = `
        background: #f8d7da;
        color: #721c24;
        padding: 12px 16px;
        border: 1px solid #f5c6cb;
        border-radius: 6px;
        margin: 15px 0;
        font-size: 14px;
        animation: slideInFade 0.3s ease-out;
    `;
    validationMessage.textContent = message;
    
    // Insert after current section
    const currentActiveSection = document.querySelector('.form-section.active');
    if (currentActiveSection) {
        currentActiveSection.insertAdjacentElement('afterend', validationMessage);
        
        // Auto-remove after 4 seconds
        setTimeout(() => {
            if (validationMessage.parentNode) {
                validationMessage.remove();
            }
        }, 4000);
    }
}

