# Transaction Number Integration Setup Guide

## What's New

Your accounting system now automatically generates **unique transaction numbers** in the format `DDMMYY-HHMMSS` (e.g., `020825-164630`) and includes a **user-friendly date input** field that displays in **DD/MM/YY format**.

## Updated Data Structure

**New Column Order (with Date):**
1. **A: Transaction Number** - Unique ID (DDMMYY-HHMMSS)
2. **B: Date** - Transaction date in DD/MM/YY format
3. **C: Funds** - Source of funds
4. **D: Cost Center** - Expense category
5. **E: Debit (VND)** - Money going out
6. **F: Credit (VND)** - Money coming in
7. **G: Description** - Transaction details
8. **H: Link Bill** - File attachments

## How to Update Your Google Sheets

### Option 1: Manual Update (Recommended for small sheets)

1. **Insert new column A** at the beginning
2. **Add header** "Transaction Number" in cell A1
3. **Insert new column B** after Transaction Number
4. **Add header** "Date" in cell B1
5. **Shift existing columns** right by two positions
6. **Update your headers** to match the new structure

### Option 2: Use the Update Script

1. **Edit `update_sheet_headers.py`**
2. **Replace** `YOUR_SHEET_ID_HERE` with your actual sheet ID
3. **Replace** `YOUR_WORKSHEET_TITLE` with your worksheet name
4. **Run the script** to automatically update headers

## Example of New Transaction

**Before (old format):**
```
Funds | Cost Center | Debit | Credit | Description | Link
Internal Transfer | Field Operations | 5,000 ₫ | | climbing the mountains | Bill_2025-09-01_12-52-32.png
```

**After (new format with date):**
```
Transaction Number | Date | Funds | Cost Center | Debit | Credit | Description | Link
020825-125339 | 02/08/25 | Internal Transfer | Field Operations | 5,000 ₫ | | climbing the mountains | Bill_2025-09-01_12-52-32.png
```

## Benefits

✅ **Unique identification** - Every transaction has a unique number
✅ **Compact date format** - DD/MM/YY saves space in your ledger
✅ **User-friendly date input** - Easy calendar selection
✅ **Cleaner structure** - Professional accounting layout
✅ **Easy tracking** - Simple to reference specific transactions
✅ **Professional** - Standard accounting practice
✅ **Audit-friendly** - Clear audit trail
✅ **VAS compliant** - Meets Vietnamese accounting standards

## Transaction Number Format

- **DD** = Day (01-31)
- **MM** = Month (01-12)  
- **YY** = Year (25 for 2025)
- **HH** = Hour (00-23)
- **MM** = Minute (00-59)
- **SS** = Second (00-59)

**Example:** `020825-164630` = August 2, 2025 at 16:46:30

**Note:** The transaction number contains the timestamp information, and you now have a separate user-friendly date field.

## Date Input Features

✅ **HTML5 date picker** - Easy calendar selection
✅ **DD/MM/YY format** - Compact, space-saving display
✅ **Required field** - Ensures every transaction has a date
✅ **Validation** - Prevents invalid dates
✅ **Automatic conversion** - Converts from HTML format to DD/MM/YY

## Next Steps

1. **Update your Google Sheets** with the new 8-column structure
2. **Add the Date column** after Transaction Number
3. **Test the system** with a new transaction
4. **Verify** that transaction numbers and dates are being generated
5. **Update any existing reports** that reference column positions

## Support

If you need help updating your sheets or have questions about the new system, refer to your existing Google Sheets setup or contact your development team.
