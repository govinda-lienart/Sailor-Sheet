# Account Lookup System Implementation

## Overview
This system implements a robust account lookup mechanism that maps worksheet IDs to official account names, ensuring consistency even when worksheet names change.

## How It Works

### 1. Master Reference Table
- **Location**: Google Sheet ID: `1DE3YTidoVIQm4SxFvK2ByRahZ7qR_Kj_LDPTpIv5NQE`
- **Worksheet**: "Account - ID Worksheet"
- **Structure**:
  ```
  Account            | ID Worksheet
  VN Indovina Bank  | 1Fvrld1X0OioH7AbKCISIMNac5U9OvIKJh0OSk02bTTI
  Staff Wallets     | [worksheet ID]
  General Revenue   | [worksheet ID]
  General Expenses  | [worksheet ID]
  ```

### 2. Form Display
- **Worksheet dropdown** now shows: `Account Name (Worksheet Name)`
- **Example**: `VN Indovina Bank (Bank_Sheet)`
- **Users see** the official account name first, worksheet name second

### 3. Transaction Recording
- **Stores**: Official account name (not worksheet name)
- **New column structure**: 
  ```
  [Transaction Number, Date, Account, Fund, Cost Center, Debit, Credit, Description, Link Bill]
  ```
- **Account column**: Contains the official account name from reference table

## Benefits

### ✅ **Robust Against Changes**
- Worksheet names can be renamed without breaking transactions
- Account names remain consistent and professional
- No more confusion about which account is which

### ✅ **Audit-Friendly**
- Clear account categorization
- Professional appearance
- Standard accounting practices

### ✅ **User Experience**
- Users see meaningful account names
- Easy to understand which account they're working with
- Fallback to worksheet name if no mapping exists

## Technical Implementation

### New Functions Added
1. **`get_account_reference_table()`** - Loads the master reference table
2. **`get_account_name_from_worksheet_id()`** - Looks up account name for a worksheet ID

### Modified Functions
1. **`get_worksheets_from_sheet()`** - Now includes account names in dropdown data
2. **`add_transaction_to_selected_sheet()`** - Records transactions with account names

### Data Flow
1. User selects a worksheet from dropdown
2. System looks up worksheet ID in reference table
3. Finds matching account name
4. Records transaction with official account name
5. If worksheet gets renamed, system still works

## Testing

Run the test script to verify the system works:
```bash
python test_account_lookup.py
```

## Usage

### For Users
1. Select a sheet from the dropdown
2. Choose an account from the "Select Account" dropdown
3. The dropdown shows: `Account Name (Worksheet Name)`
4. Fill in transaction details and submit

### For Administrators
1. Update the "Account - ID Worksheet" reference table
2. Add new accounts by mapping worksheet IDs to account names
3. Rename worksheets without affecting existing transactions

## Future Enhancements

- **Account codes**: Add numeric account codes (1000, 2000, etc.)
- **Account types**: Categorize accounts (Asset, Liability, Equity, Revenue, Expense)
- **Validation**: Ensure all worksheets have account mappings
- **Bulk import**: Import account mappings from CSV/Excel

## Troubleshooting

### Common Issues
1. **"No account name found" warning**: Worksheet ID not in reference table
2. **Empty account column**: Check reference table mapping
3. **Dropdown shows worksheet names only**: Verify reference table is accessible

### Debug Information
- Check console logs for account mapping details
- Verify Google Sheets API permissions
- Ensure reference table worksheet name is exactly "Account - ID Worksheet"
