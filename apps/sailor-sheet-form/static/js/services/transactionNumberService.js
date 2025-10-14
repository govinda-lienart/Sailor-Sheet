/**
 * Transaction Number Service
 * Handles generation of unique transaction numbers
 */

/**
 * Generate a unique transaction number based on current date/time and country
 * Format: COUNTRY-DDMMYY-HHMMSS (e.g., BE-081025-165528 or VN-081025-165528)
 */
export function generateTransactionNumber() {
    const now = new Date();
    
    // Get current country from sessionStorage, default to BE
    const selectedCountry = sessionStorage.getItem('selectedCountry') || 'BE';
    const countryPrefix = selectedCountry.toUpperCase();
    
    // Generate timestamp part: DDMMYY-HHMMSS
    const timestamp = now.getDate().toString().padStart(2, '0') +
                     (now.getMonth() + 1).toString().padStart(2, '0') +
                     now.getFullYear().toString().slice(-2) + '-' +
                     now.getHours().toString().padStart(2, '0') +
                     now.getMinutes().toString().padStart(2, '0') +
                     now.getSeconds().toString().padStart(2, '0');
    
    // Combine country prefix with timestamp
    const transactionNumber = `${countryPrefix}-${timestamp}`;
    
    document.getElementById('transactionNumberDisplay').value = transactionNumber;
    document.getElementById('transactionNumberInput').value = transactionNumber;
    console.log(`Generated ${countryPrefix} transaction number:`, transactionNumber);
    return transactionNumber;
}

/**
 * Regenerate transaction number when country changes
 */
export function regenerateTransactionNumberForCountry() {
    console.log('🔄 Regenerating transaction number for new country...');
    generateTransactionNumber();
}

