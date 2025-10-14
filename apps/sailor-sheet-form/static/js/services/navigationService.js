/**
 * Navigation Service
 * Handles all navigation and section tracking logic
 */

import { scrollToSection, showSectionValidationMessage } from './uiService.js';
import { MAIN_FORM_SECTIONS } from '../config/constants.js';

// State management
let manuallyCheckedSections = new Set();
let currentSection = 'transaction-number-section';
let completedSections = new Set();

/**
 * Initialize navigation click handlers for smooth scrolling
 */
export function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            const sectionId = href.substring(1); // Remove the # symbol
            scrollToSection(sectionId);
        });
    });
}

/**
 * Toggle section manual check state
 */
export function toggleSectionCheck(navButton) {
    const sectionId = navButton.getAttribute('href').substring(1); // Remove #
    
    if (manuallyCheckedSections.has(sectionId)) {
        // Uncheck - remove green checkmark, but keep blue if has data
        manuallyCheckedSections.delete(sectionId);
        const hasData = checkSectionHasData(sectionId);
        updateNavButtonState(navButton, false, hasData);
        console.log(`❌ Unchecked section: ${sectionId}`);
    } else {
        // Check - add green checkmark, but keep blue if has data
        manuallyCheckedSections.add(sectionId);
        const hasData = checkSectionHasData(sectionId);
        updateNavButtonState(navButton, true, hasData);
        console.log(`✅ Checked section: ${sectionId}`);
    }
}

/**
 * Update navigation button visual state
 */
export function updateNavButtonState(navButton, isManuallyChecked, hasData = false) {
    // Remove any existing checkmark first
    const existingCheckmark = navButton.querySelector('.manual-checkmark');
    if (existingCheckmark) {
        existingCheckmark.remove();
    }
    
    // Apply base styling (blue if has data, gray if not)
    if (hasData) {
        // Has data state: Blue highlighting
        navButton.style.borderLeft = '4px solid #007bff';
        navButton.style.backgroundColor = '#f0f8ff';
        navButton.style.color = '#0056b3';
        navButton.style.fontWeight = '600';
    } else {
        // Empty state: Light gray
        navButton.style.borderLeft = '4px solid #e9ecef';
        navButton.style.backgroundColor = '#f8f9fa';
        navButton.style.color = '#6c757d';
        navButton.style.fontWeight = '500';
    }
    
    // Add green checkmark if manually checked (without changing base styling)
    if (isManuallyChecked) {
        const checkmark = document.createElement('span');
        checkmark.className = 'manual-checkmark';
        checkmark.innerHTML = ' ✅';
        checkmark.style.float = 'right';
        navButton.appendChild(checkmark);
    }
}

/**
 * Check if a section has data filled in
 */
export function checkSectionHasData(sectionId) {
    switch (sectionId) {
        case 'transaction-number-section':
            return document.getElementById('transactionNumberDisplay')?.value !== 'Generating...' && document.getElementById('transactionNumberDisplay')?.value.length > 0;
        case 'transaction-type-section':
            return document.getElementById('transaction_category')?.value !== '';
        case 'sheet-worksheet-section':
            const sheetId = document.getElementById('sheet_select')?.value;
            const worksheetName = document.getElementById('worksheet_select')?.value;
            return sheetId && worksheetName;
        case 'date-section':
            return document.getElementById('date_input')?.value !== '';
        case 'amount-section':
            const amount = document.querySelector('input[name="amount"]')?.value;
            return amount !== '' && parseFloat(amount) > 0;
        case 'fund-section':
            return document.querySelector('select[name="fund_id"]')?.value !== '';
        case 'category-section':
            return document.querySelector('select[name="category_id"]')?.value !== '';
        case 'debit-account-section':
            const regularDebit = document.querySelector('select[name="regular_debit_account_id"]');
            const masterDebitA = document.querySelector('select[name="master_ledger_a_debit_account_id"]');
            if (regularDebit && regularDebit.hasAttribute('required')) return regularDebit.value !== '';
            if (masterDebitA && masterDebitA.hasAttribute('required')) return masterDebitA.value !== '';
            return true;
        case 'credit-account-section':
            const regularCredit = document.querySelector('select[name="regular_credit_account_id"]');
            const masterCreditA = document.querySelector('select[name="master_ledger_a_credit_account_id"]');
            if (regularCredit && regularCredit.hasAttribute('required')) return regularCredit.value !== '';
            if (masterCreditA && masterCreditA.hasAttribute('required')) return masterCreditA.value !== '';
            return true;
        case 'payment-method-section':
            const paymentMethod = document.getElementById('payment_method');
            if (paymentMethod && paymentMethod.hasAttribute('required')) return paymentMethod.value !== '';
            return true;
        case 'description-section':
            return document.querySelector('textarea[name="description"]')?.value.trim() !== '';
        default:
            return false;
    }
}

/**
 * Update all navigation states based on current form data
 */
export function updateAllNavigationStates() {
    const sectionIds = [
        'transaction-number-section',
        'transaction-type-section', 
        'sheet-worksheet-section',
        'date-section',
        'amount-section',
        'fund-section',
        'category-section',
        'debit-account-section',
        'credit-account-section',
        'payment-method-section',
        'description-section'
    ];

    sectionIds.forEach(sectionId => {
        const navButton = document.querySelector(`a[href="#${sectionId}"]`);
        if (navButton) {
            const isManuallyChecked = manuallyCheckedSections.has(sectionId);
            const hasData = checkSectionHasData(sectionId);
            updateNavButtonState(navButton, isManuallyChecked, hasData);
        }
    });
}

/**
 * Setup manual navigation tracking
 */
export function setupManualNavigationTracking() {
    const sectionIds = [
        'transaction-number-section',
        'transaction-type-section', 
        'sheet-worksheet-section',
        'date-section',
        'amount-section',
        'fund-section',
        'category-section',
        'debit-account-section',
        'credit-account-section',
        'payment-method-section',
        'description-section'
    ];

    sectionIds.forEach(sectionId => {
        const navButton = document.querySelector(`a[href="#${sectionId}"]`);
        if (navButton) {
            // Remove any existing click listeners
            navButton.removeEventListener('click', handleNavClick);
            // Add manual check toggle
            navButton.addEventListener('click', handleNavClick);
        }
    });
    
    // Monitor form changes to update blue highlighting
    const formInputs = document.querySelectorAll('input, select, textarea');
    formInputs.forEach(input => {
        input.addEventListener('change', updateAllNavigationStates);
        input.addEventListener('input', updateAllNavigationStates);
    });
    
    // Initial state update
    updateAllNavigationStates();
    
    console.log('✅ Manual navigation tracking setup complete - blue for data, green for manual check');
}

/**
 * Handle navigation link clicks
 */
function handleNavClick(event) {
    // Prevent default scroll behavior temporarily
    event.preventDefault();
    
    const navButton = event.currentTarget;
    const sectionId = navButton.getAttribute('href').substring(1);
    
    // Toggle manual check
    toggleSectionCheck(navButton);
    
    // Then scroll to section after a brief delay
    setTimeout(() => {
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.scrollIntoView({ behavior: 'smooth' });
        }
    }, 100);
}

/**
 * Setup form monitoring
 */
export function setupFormMonitoring() {
    // Setup manual navigation tracking instead of automatic
    setupManualNavigationTracking();
    
    console.log('✅ Manual form tracking setup complete - click section links to mark as checked');
}

/**
 * Clear manual check marks (used on form reset)
 */
export function clearManualCheckmarks() {
    manuallyCheckedSections.clear();
}

// ==============================================================================
// PROFESSIONAL SECTION NAVIGATION SYSTEM
// ==============================================================================

/**
 * Initialize professional section navigation
 */
export function initializeSectionNavigation() {
    console.log('🎯 Initializing professional section navigation...');
    
    // Hide only the main form sections except the first one
    MAIN_FORM_SECTIONS.forEach(sectionId => {
        const section = document.getElementById(sectionId);
        if (section) {
            section.classList.remove('active');
        }
    });
    
    // Show the first section
    const firstSection = document.getElementById('transaction-number-section');
    if (firstSection) {
        firstSection.classList.add('active');
    }
    
    // Ensure non-main sections (like upload, search) remain visible
    const nonMainSections = document.querySelectorAll('.form-section:not(#transaction-number-section):not(#transaction-type-section):not(#sheet-worksheet-section):not(#date-section):not(#amount-section):not(#fund-section):not(#category-section):not(#sub-category-section):not(#debit-account-section):not(#credit-account-section):not(#payment-method-section):not(#description-section):not(#document-upload-section)');
    nonMainSections.forEach(section => {
        section.style.display = 'block';
        section.style.opacity = '1';
        section.style.transform = 'translateY(0)';
    });
    
    // Set initial navigation state
    updateNavigationState();
    
    // Add click handlers to navigation links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            const sectionId = href.substring(1);
            
            // Check if we can navigate to this section
            if (canNavigateToSection(sectionId)) {
                navigateToSection(sectionId);
            }
        });
    });
    
    console.log('✅ Section navigation initialized');
}

/**
 * Navigate to a specific section
 */
export function navigateToSection(sectionId) {
    console.log(`🎯 Navigating to section: ${sectionId}`);
    
    // Auto-validate and mark current section as completed if it has valid data
    if (currentSection && currentSection !== sectionId) {
        checkAndMarkSectionCompleted(currentSection);
    }
    
    // Hide current section
    const currentActiveSection = document.querySelector('.form-section.active');
    if (currentActiveSection) {
        currentActiveSection.classList.remove('active');
    }
    
    // Show target section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
        currentSection = sectionId;
        
        // Scroll to top of form for better UX
        targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    // Update navigation state
    updateNavigationState();
}

/**
 * Update navigation state classes
 */
function updateNavigationState() {
    // Remove all state classes from navigation
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.classList.remove('current', 'completed');
    });
    
    // Set current section
    const currentNavLink = document.querySelector(`a[href="#${currentSection}"]`);
    if (currentNavLink) {
        currentNavLink.classList.add('current');
    }
    
    // Set completed sections
    completedSections.forEach(sectionId => {
        const completedNavLink = document.querySelector(`a[href="#${sectionId}"]`);
        if (completedNavLink) {
            completedNavLink.classList.add('completed');
        }
    });
}

/**
 * Mark section as completed
 */
export function markSectionCompleted(sectionId) {
    completedSections.add(sectionId);
    updateNavigationState();
    console.log(`✅ Section completed: ${sectionId}`);
}

/**
 * Check and mark section completed if valid
 */
function checkAndMarkSectionCompleted(sectionId) {
    const section = document.getElementById(sectionId);
    if (!section) return false;
    
    // Get all required inputs in the section
    const requiredInputs = section.querySelectorAll('input[required], select[required], textarea[required]');
    let allCompleted = true;
    
    requiredInputs.forEach(input => {
        if (!input.value.trim()) {
            allCompleted = false;
        }
    });
    
    // If all required fields are filled, mark as completed
    if (allCompleted && requiredInputs.length > 0) {
        markSectionCompleted(sectionId);
        return true;
    }
    
    return false;
}

/**
 * Check if can navigate to section
 */
function canNavigateToSection(sectionId) {
    // Allow free navigation to any section
    return true;
}

/**
 * Validate current section
 */
export function validateCurrentSection() {
    const section = document.getElementById(currentSection);
    if (!section) return false;
    
    // Get all required inputs in current section
    const requiredInputs = section.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    requiredInputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.style.borderColor = '#dc3545';
        } else {
            input.style.borderColor = '';
        }
    });
    
    if (isValid) {
        markSectionCompleted(currentSection);
        return true;
    } else {
        // Show validation message
        showSectionValidationMessage('Please complete all required fields before proceeding.');
        return false;
    }
}

