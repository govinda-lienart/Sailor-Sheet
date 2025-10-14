/**
 * Global Bridge - Exposes module functions to global scope
 * This file bridges ES6 modules with legacy inline scripts
 */

import { generateTransactionNumber, regenerateTransactionNumberForCountry } from './services/transactionNumberService.js';
import { handleTransactionTypeChange } from './services/transactionDefaultsService.js';
import { loadWorksheets } from './services/worksheetService.js';

// Expose functions to global scope for inline scripts
window.generateTransactionNumber = generateTransactionNumber;
window.regenerateTransactionNumberForCountry = regenerateTransactionNumberForCountry;
window.handleTransactionTypeChange = handleTransactionTypeChange;
window.loadWorksheets = loadWorksheets;

console.log('✅ Global bridge initialized - module functions exposed to window');

