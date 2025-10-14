/**
 * Global Bridge - Exposes module functions to global scope
 * This file bridges ES6 modules with legacy inline scripts
 */

import { generateTransactionNumber, regenerateTransactionNumberForCountry } from './services/transactionNumberService.js';
import { handleTransactionTypeChange } from './services/transactionDefaultsService.js';
import { loadWorksheets } from './services/worksheetService.js';
import { searchTransaction } from './services/searchService.js';
import { 
    handleDocumentUpload, 
    handleGoogleSheetsUpdate, 
    updateGoogleSheetsDocument,
    showUploadResult,
    hideUploadResult
} from './services/updateFormService.js';
import { selectCountry, initializeCountrySelection } from './services/countrySelectionService.js';
import { 
    processBillsGoogleDriveLink,
    processRedBillsGoogleDriveLink,
    processDocumentationGoogleDriveLink,
    processBillsGoogleDriveLinkMain,
    processRedBillsGoogleDriveLinkMain,
    processDocumentationGoogleDriveLinkMain,
    handleGoogleDriveLink
} from './services/googleDriveService.js';

// Expose functions to global scope for inline scripts
window.generateTransactionNumber = generateTransactionNumber;
window.regenerateTransactionNumberForCountry = regenerateTransactionNumberForCountry;
window.handleTransactionTypeChange = handleTransactionTypeChange;
window.loadWorksheets = loadWorksheets;
window.searchTransaction = searchTransaction;
window.handleDocumentUpload = handleDocumentUpload;
window.handleGoogleSheetsUpdate = handleGoogleSheetsUpdate;
window.updateGoogleSheetsDocument = updateGoogleSheetsDocument;
window.showUploadResult = showUploadResult;
window.hideUploadResult = hideUploadResult;
window.selectCountry = selectCountry;
window.initializeCountrySelection = initializeCountrySelection;
window.processBillsGoogleDriveLink = processBillsGoogleDriveLink;
window.processRedBillsGoogleDriveLink = processRedBillsGoogleDriveLink;
window.processDocumentationGoogleDriveLink = processDocumentationGoogleDriveLink;
window.processBillsGoogleDriveLinkMain = processBillsGoogleDriveLinkMain;
window.processRedBillsGoogleDriveLinkMain = processRedBillsGoogleDriveLinkMain;
window.processDocumentationGoogleDriveLinkMain = processDocumentationGoogleDriveLinkMain;
window.handleGoogleDriveLink = handleGoogleDriveLink;

console.log('✅ Global bridge initialized - module functions exposed to window');

