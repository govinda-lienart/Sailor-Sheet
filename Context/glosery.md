
## HTML Templates

### `templates/index.html`
**Main data entry form with file upload functionality**

**Key Sections:**
- **File Upload (Step 1)**: AJAX-based file upload with progress indicator
  - `<input type="file" id="fileInput">` - File selector with PDF/image/document filters
  - `uploadFile()` JavaScript function - Handles async upload to `/upload_file` route
  - Hidden fields `file_link` and `file_name` - Store upload results for form submission
- **Transaction Form (Step 2)**: Main data entry form
  - **Sheet Selection**: Dropdown populated from `get_available_sheets()` (field name: `sheet_id`)
  - **Worksheet Selection**: Dynamic dropdown using `loadWorksheets()` JavaScript
  - **Fund Selection**: Dropdown with color-coded options from `get_funds_list()`
  - **Standard Fields**: Name, Amount (number), Description (textarea)

### `templates/thank_you.html`
**Simple success confirmation page**

**Purpose**: Clean success page shown after transaction submission
**Features**: 
- Success icon and message
- "Enter New Submission" button linking back to main form
- Consistent styling with main form

## Functions by module

### app.py
- `index()` (route `/`, GET+POST): Renders form (GET), processes submission (POST). Extracts form data, uses worksheet title directly as account name (no lookup needed), calls `add_transaction_to_selected_sheet`, redirects to `thank_you` on success.
- `get_worksheets(sheet_id)` (route `/get_worksheets/<sheet_id>`, GET): Returns JSON list of worksheets for the selected sheet (used by frontend when a sheet is chosen).
- `upload_file()` (route `/upload_file`, POST): AJAX endpoint. Delegates file handling to `file_upload_manager.handle_web_upload()` and returns JSON response.
- `thank_you()` (route `/thank-you`, GET): Renders the success page after a successful transaction.

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
- `add_transaction_to_selected_sheet(gc, sheet_id, worksheet_title, amount, description, fund_id, cost_center_id, transaction_type, date_input, transaction_number, file_link="", account_name="")`: Adds transaction to specified worksheet using worksheet title as account name. Builds row `[Transaction Number, Date, Funds, Cost Center, Account, Debit, Credit, Description, Link]` and appends to worksheet.
- `get_funds_list(gc)`: Reads "Funds Reference" from the master sheet, filters by `Active` status, returns list of `{id, name, color}` for the form dropdown.
- `get_fund_name_by_id(gc, fund_id)`: Looks up the fund name in "Funds Reference" by `Fund_ID`; returns "Unknown Fund" if not found.
- `get_cost_centers_list(gc)`: Reads "Cost Centers" from the master sheet, filters by `Active` status, returns list of `{code, name, category}` for the form dropdown.
- `get_cost_center_name_by_code(gc, cost_center_code)`: Looks up the cost center name by code; returns "Unknown Cost Center" if not found.


