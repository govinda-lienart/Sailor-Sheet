/**
 * Date Service
 * Handles date formatting and conversion
 */

/**
 * Convert various date formats to DD/MM/YY
 */
export function convertDateFormat(dateString) {
    if (!dateString || dateString.trim() === '') return '';
    
    // Remove any extra spaces and leading apostrophes (Excel uses ' to force text)
    dateString = dateString.trim().replace(/^'+/g, ''); // Strip leading apostrophes
    
    // Handle different separators and formats
    let parts = [];
    
    // Try different separators
    if (dateString.includes('/')) {
        parts = dateString.split('/');
    } else if (dateString.includes('-')) {
        parts = dateString.split('-');
    } else if (dateString.includes('.')) {
        parts = dateString.split('.');
    } else {
        return dateString; // Return as-is if no recognizable separator
    }
    
    if (parts.length !== 3) return dateString;
    
    let day, month, year;
    
    // Determine format based on part lengths and values
    if (parts[0].length === 4) {
        // YYYY/MM/DD format
        year = parts[0];
        month = parts[1].padStart(2, '0');
        day = parts[2].padStart(2, '0');
    } else if (parts[2].length === 4) {
        // DD/MM/YYYY or MM/DD/YYYY format
        year = parts[2];
        
        // Try to determine if it's DD/MM or MM/DD
        const firstPart = parseInt(parts[0]);
        const secondPart = parseInt(parts[1]);
        
        if (firstPart > 12 && secondPart <= 12) {
            // DD/MM/YYYY (day > 12, month <= 12)
            day = parts[0].padStart(2, '0');
            month = parts[1].padStart(2, '0');
        } else if (secondPart > 12 && firstPart <= 12) {
            // MM/DD/YYYY (month > 12, day <= 12)
            month = parts[0].padStart(2, '0');
            day = parts[1].padStart(2, '0');
        } else {
            // Ambiguous case - assume DD/MM/YYYY (European format)
            day = parts[0].padStart(2, '0');
            month = parts[1].padStart(2, '0');
        }
    } else {
        // Two-digit year - smart century detection
        const currentYear = new Date().getFullYear();
        const currentCentury = Math.floor(currentYear / 100) * 100;
        const twoDigitYear = parseInt(parts[2]);
        
        // Smart year conversion: if 2-digit year is > current year's last 2 digits,
        // assume it's from previous century, otherwise current century
        const currentTwoDigitYear = currentYear % 100;
        if (twoDigitYear > currentTwoDigitYear) {
            year = currentCentury - 100 + twoDigitYear; // Previous century
        } else {
            year = currentCentury + twoDigitYear; // Current century
        }
        
        // For DD/MM/YY format, assume DD/MM (European format)
        day = parts[0].padStart(2, '0');
        month = parts[1].padStart(2, '0');
    }
    
    // Validate the date
    const date = new Date(year, month - 1, day);
    if (date.getFullYear() == year && date.getMonth() == month - 1 && date.getDate() == day) {
        // Return in DD/MM/YY format
        const shortYear = year.toString().slice(-2);
        return `${day}/${month}/${shortYear}`;
    } else {
        return dateString; // Return original if invalid
    }
}

/**
 * Validate date format
 */
export function validateDateFormat(dateString) {
    if (!dateString) return false;
    
    // Check if it's already in DD/MM/YY format (our standard format)
    const standardDateRegex = /^\d{2}\/\d{2}\/\d{2}$/;
    if (standardDateRegex.test(dateString)) return true;
    
    // Check if it's in YYYY-MM-DD format
    const isoDateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (isoDateRegex.test(dateString)) return true;
    
    // Try to convert and validate
    const converted = convertDateFormat(dateString);
    return standardDateRegex.test(converted);
}

/**
 * Setup date input handlers
 */
export function setupDateInputHandlers(dateInputId, showMessageCallback) {
    const dateInput = document.getElementById(dateInputId);
    if (!dateInput) return;

    // Handle paste events
    dateInput.addEventListener('paste', function(e) {
        setTimeout(() => {
            let value = this.value.trim();
            // Strip leading apostrophes immediately
            value = value.replace(/^'+/g, '');
            const converted = convertDateFormat(value);
            // Ensure converted value also has no apostrophes
            const finalValue = converted.replace(/^'+/g, '');
            if (finalValue !== this.value) {
                this.value = finalValue;
                showMessageCallback('Date format converted successfully!', 'success');
            }
        }, 10); // Small delay to allow paste to complete
    });
    
    // Handle input changes
    dateInput.addEventListener('blur', function() {
        let value = this.value.trim();
        // Strip leading apostrophes immediately
        value = value.replace(/^'+/g, '');
        
        if (value) {
            const converted = convertDateFormat(value);
            if (converted !== value && validateDateFormat(converted)) {
                this.value = converted;
                showMessageCallback('Date format converted to standard format', 'info');
            } else if (!validateDateFormat(converted)) {
                showMessageCallback('Please enter a valid date format (dd/mm/yyyy or mm/dd/yyyy)', 'error');
                this.style.borderColor = '#dc3545';
            } else {
                // Ensure no apostrophe in final value
                this.value = converted.replace(/^'+/g, '');
                this.style.borderColor = '';
            }
        }
    });
    
    // Also strip apostrophes on input (real-time)
    dateInput.addEventListener('input', function() {
        if (this.value.startsWith("'")) {
            this.value = this.value.replace(/^'+/g, '');
        }
    });
    
    // Clear error styling on focus
    dateInput.addEventListener('focus', function() {
        this.style.borderColor = '';
    });
}

