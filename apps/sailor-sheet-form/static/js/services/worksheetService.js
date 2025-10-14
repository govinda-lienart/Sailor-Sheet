/**
 * Worksheet Service
 * Handles worksheet and sheet API operations
 */

/**
 * Load worksheets for a selected sheet
 */
export function loadWorksheets() {
    console.log('loadWorksheets() called');
    const sheetSelect = document.getElementById('sheet_select');
    const worksheetSelect = document.getElementById('worksheet_select');
    const selectedSheetId = sheetSelect.value;
    console.log('Selected sheet ID:', selectedSheetId);

    worksheetSelect.innerHTML = '<option value="">Loading worksheets...</option>';
    worksheetSelect.disabled = true;

    if (!selectedSheetId) {
        worksheetSelect.innerHTML = '<option value="">First select a sheet...</option>';
        console.log('No sheet selected, returning');
        return;
    }

    console.log('Fetching worksheets for sheet:', selectedSheetId);
    fetch(`/api/get_worksheets/${selectedSheetId}`)
        .then(r => {
            console.log('Response status:', r.status);
            return r.json();
        })
        .then(data => {
            console.log('Worksheets data received:', data);
            worksheetSelect.innerHTML = '<option value="">Choose an account...</option>';
            
            if (data.length > 0) {
                data.forEach(ws => {
                    console.log('Adding worksheet:', ws);
                    const o = document.createElement('option');
                    o.value = ws.title;  // Use worksheet title for backend lookup
                    o.textContent = ws.title;  // Show just the worksheet title
                    worksheetSelect.appendChild(o);
                });
                worksheetSelect.disabled = false;
                console.log('Worksheets loaded successfully');
                
                // Auto-select "Master Ledger" if it exists
                const masterLedgerOption = Array.from(worksheetSelect.options).find(option => 
                    option.textContent.includes('Master Ledger')
                );
                if (masterLedgerOption) {
                    worksheetSelect.value = masterLedgerOption.value;
                    console.log('Auto-selected Master Ledger worksheet');
                }
                
                console.log('Worksheets loaded, transaction defaults will be applied from DOMContentLoaded');
            } else {
                worksheetSelect.innerHTML = '<option value="">No accounts found</option>';
                console.log('No worksheets found');
            }
        })
        .catch(error => {
            console.error('Error loading worksheets:', error);
            worksheetSelect.innerHTML = '<option value="">Error loading worksheets</option>';
        });
}

