
# NGO Accounting System - Glossary for Beginners

## What is this system?
This is a web-based accounting system designed for NGOs (Non-Governmental Organizations) that operate in multiple countries (Vietnam and Belgium). It helps record financial transactions and automatically creates proper accounting entries.

## Key Concepts for Beginners

### What is Accounting?
Accounting is the process of recording, organizing, and tracking money coming in and going out of an organization. Every transaction must be recorded in at least two places to keep the books balanced.

### What is Dual-Entry Accounting?
Dual-entry accounting means every transaction affects two accounts:
- **Debit**: Money going out of an account (like spending from a bank account)
- **Credit**: Money coming into an account (like receiving income)

### Transaction Types in this System:
1. **Payment**: Spending money (e.g., buying office supplies)
2. **Donation**: Receiving money from donors
3. **Grant**: Receiving money from funding organizations
4. **Internal Transfer**: Moving money between accounts within the same organization
5. **Interbanking Transfer**: Moving money between different countries (Vietnam ↔ Belgium)

### How the System Works:
1. **User fills out a form** with transaction details
2. **System automatically selects** appropriate accounts based on transaction type
3. **System creates entries** in Google Sheets (like Excel spreadsheets)
4. **For interbanking transfers**, system creates entries in both Vietnam and Belgium accounting systems

### Data Storage:
- **JSON Files**: Fast, local storage for account names, fund names, and categories
- **Google Sheets**: Where the actual accounting records are stored
- **Google Drive**: Where uploaded receipts and documents are stored

## HTML Templates

### `templates/index.html`
**Main data entry form with file upload and dual-entry accounting functionality**

**Key Sections:**
- **File Upload (Step 1)**: AJAX-based file upload with progress indicator
  - `<input type="file" id="fileInput">` - File selector with PDF/image/document filters
  - `uploadFile()` JavaScript function - Handles async upload to `/upload_file` route
  - Hidden fields `file_link` and `file_name` - Store upload results for form submission
- **Transaction Form (Step 2)**: Main data entry form
  - **Transaction Type**: Dropdown with options (Payment, Internal Transfer, Interbanking Transfer, Donation, Grant)
  - **Sheet Selection**: Dropdown populated from `get_available_sheets()` (field name: `sheet_id`)
  - **Worksheet Selection**: Dynamic dropdown using `loadWorksheets()` JavaScript
  - **Fund Selection**: Dropdown with color-coded options from JSON data
  - **Category Selection**: Dropdown with transaction categories from JSON data
  - **Standard Fields**: Amount (number), Description (textarea)
  - **Account Selection**: Debit and Credit dropdowns for single-entry transactions
  - **Dual Account Sections**: Special sections for Interbanking Transfers with Origin (Vietnam) and Destination (Belgium) accounts

### `templates/thank_you.html`
**Simple success confirmation page**

**Purpose**: Clean success page shown after transaction submission
**Features**: 
- Success icon and message
- "Enter New Submission" button linking back to main form
- Consistent styling with main form

## CSS Styling

### Transfer Fields Styling
- **`#transferFields`**: Light gray background with border for internal transfer section
- **`#internalTransferCheck`**: Custom checkbox styling with proper spacing
- **Form Group Spacing**: Optimized margins for transfer-specific fields
- **Visual Hierarchy**: Clear separation between transfer and standard transaction fields

## JavaScript Functions

### Core Form Management
- `generateTransactionNumber()`: Creates timestamped transaction numbers in format `DDMMYY-HHMMSS`
- `loadWorksheets()`: AJAX call to populate worksheet dropdown when sheet is selected
- `handleTransactionTypeChange()`: Main function that handles transaction type selection and shows/hides appropriate form sections
- `applyTransactionDefaults()`: Sets default values for accounts and categories based on selected transaction type

### Dual-Entry Accounting System
- `testDualSections()`: Debug function to manually show dual account sections for testing
- **Show/Hide Logic**: Automatically displays dual account sections only for "Interbanking Transfer" transactions
- **Default Value Setting**: Pre-fills Origin (Vietnam) and Destination (Belgium) account dropdowns with appropriate defaults

### Form Validation
- **Transaction Type Validation**: Ensures appropriate form sections are shown based on transaction type
- **Dual Account Validation**: For interbanking transfers, ensures all 4 account fields (origin debit/credit, destination debit/credit) are filled
- **Required Field Management**: Dynamically manages required attributes based on transaction type
- **Transaction Number Generation**: Automatic generation and validation

## New Features & System Architecture

### Dual-Entry Accounting System
**Professional accounting system for NGO with separate Vietnam and Belgium accounting**

**What is Dual-Entry Accounting?**
Dual-entry accounting means every transaction affects two accounts - one is debited (money goes out) and one is credited (money comes in). This ensures the books always balance.

**Key Components:**
- **Transaction Type Selection**: Choose from Payment, Internal Transfer, Interbanking Transfer, Donation, or Grant
- **Automatic Defaults**: System pre-fills appropriate accounts based on transaction type
- **Dual Account Sections**: Special form sections for Interbanking Transfers with separate Origin (Vietnam) and Destination (Belgium) account controls
- **JSON Data Storage**: Account, fund, and category data stored in local JSON files for fast access (no Google Sheets API calls)

**Interbanking Transfer System:**
- **Origin Account (Vietnam)**: 
  - Debit: VN - Indovina Bank (money leaving Vietnam bank)
  - Credit: VN - Revenues (income recorded in Vietnam)
- **Destination Account (Belgium)**:
  - Debit: BE - Expenses (expense recorded in Belgium)
  - Credit: BE - Belfius (money arriving in Belgium bank)
- **Automatic Dual Entries**: Creates matching entries in both Vietnam and Belgium accounting systems

**Data Storage Structure:**
- **`data/accounts.json`**: Contains all account information (VN-Indovina Bank, BE-Belfius, etc.)
- **`data/funds.json`**: Contains fund information (Internal Transfer, MBZ Funds, etc.)
- **`data/categories.json`**: Contains transaction categories (Donation, Food & Meals, etc.)

**Spreadsheet Structure:**
- **Column A**: Transaction Number
- **Column B**: Date  
- **Column C**: Funds
- **Column D**: Account
- **Column E**: Category
- **Column F**: Debit (VND)
- **Column G**: Credit (VND)
- **Column H**: Description
- **Column I**: Link Bill

### Enhanced Debug Logging
**Comprehensive error tracking and debugging throughout the system**

**Debug Features:**
- **Function Entry Logging**: All parameters logged at function start
- **Step-by-Step Tracking**: Each major operation logged with results
- **Error Context**: Full exception details with stack traces
- **Data Validation Logging**: Fund/cost center lookup results
- **Transaction Flow Tracking**: Complete audit trail of data processing

## Functions by module

### app.py
- `index()` (route `/`, GET+POST): Main form handler. Renders form (GET), processes submission (POST). Handles dual-entry accounting for interbanking transfers, creates entries in both Vietnam and Belgium systems, redirects to success page.
- `get_worksheets(sheet_id)` (route `/get_worksheets/<sheet_id>`, GET): Returns JSON list of worksheets for the selected sheet (used by frontend when a sheet is chosen).
- `upload_file()` (route `/upload_file`, POST): AJAX endpoint. Delegates file handling to `file_upload_manager.handle_web_upload()` and returns JSON response.
- `refresh_form_data()` (route `/refresh_form_data`, POST): AJAX endpoint. Returns fresh account, category, and fund data from JSON files.
- `thank_you()` (route `/thank-you`, GET): Renders the success page after a successful transaction.

**JSON Data Functions:**
- `get_funds_from_json()`: Loads fund data from `data/funds.json` instead of Google Sheets
- `get_categories_from_json()`: Loads category data from `data/categories.json` instead of Google Sheets  
- `get_accounts_from_json()`: Loads account data from `data/accounts.json` instead of Google Sheets

### config.py
- `initialize_sheets()`: Loads service‑account credentials from `GOOGLE_CREDENTIALS`, secret file, or local `credentials.json`; authorizes gspread and returns a Sheets client. Scopes include Sheets and Drive.

### file_upload_manager.py
- `allowed_file(filename)`: Returns True if extension is in `ALLOWED_EXTENSIONS`.
- `unique_name(base, ext)`: Returns a unique, timestamped filename like `Bill_YYYY-MM-DD_HH-MM-SS.ext`.
- `get_service_account_credentials()`: Builds Google credentials from env/secret/local file using Drive scope.
- `build_drive_service(creds)`: Returns a Drive v3 service client.
- `upload_file_to_drive(file)`: Validates extension, secures filename, generates unique name, builds `MediaIoBaseUpload`, uploads to shared folder `FOLDER_ID`, returns `{success, file_url, file_name, file_id}` or error.
- `handle_web_upload(file, transaction_number)`: Web interface handler that processes upload requests from Flask routes, calls `upload_file_to_drive()`, and returns formatted JSON responses.

### sheets_manager.py
- `get_available_sheets(gc)`: Lists spreadsheets accessible by the service account (id, title) for the sheet dropdown.
- `get_sheet_by_id(gc, sheet_id)`: Opens a spreadsheet by key and returns the handle (gspread Spreadsheet object for that sheet so you can call methods on it).
- `get_worksheets_from_sheet(gc, sheet_id)`: Lists worksheets (title, index) for a selected spreadsheet. Returns worksheet titles directly for dropdown selection.
- `add_transaction_to_selected_sheet(gc, sheet_id, worksheet_title, amount, description, fund_id, category_id, debit_account_id, credit_account_id, transaction_type, date_input, transaction_number, file_link="", origin_account="", destination_account="", transfer_type="external")`: Main transaction function that adds entries to Google Sheets. Handles both single-entry and dual-entry transactions.
- `get_account_name_by_code(gc, account_code)`: **UPDATED** - Now uses JSON data instead of Google Sheets to look up account names. Returns account name or "Unknown Account" if not found.

**Legacy Functions (Still Available):**
- `get_funds_list(gc)`: Reads "Funds Reference" from the master sheet (legacy - now uses JSON)
- `get_categories_list(gc)`: Reads categories from the master sheet (legacy - now uses JSON)  
- `get_accounts_list(gc)`: Reads accounts from the master sheet (legacy - now uses JSON)


