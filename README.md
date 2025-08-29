# NGO Accounting App - Complete Function Flow

## **Detailed Function Flow with All Functions Involved:**

### **1. User visits your website**
→ `app.py` runs the `index()` function (GET request)

### **2. app.py calls config.py**
→ `config.py` runs `initialize_sheets()` function
→ Sets up Google Sheets connection and returns `gc` (Google Sheets client)

### **3. app.py calls sheets_manager.py**
→ `sheets_manager.py` runs `get_available_sheets(gc)` function
→ Gets list of available Google Sheets with IDs and titles

### **4. app.py sends data to templates/index.html**
→ `app.py` calls `render_template('index.html', sheets=available_sheets)`
→ Jinja2 processes template and displays form with sheet dropdown

### **5. User selects a Google Sheet**
→ JavaScript in HTML runs `loadWorksheets()` function
→ Gets selected sheet ID from dropdown

### **6. JavaScript makes AJAX request to app.py**
→ Calls `fetch('/get_worksheets/${selectedSheetId}')`
→ `app.py` runs `get_worksheets(sheet_id)` function

### **7. app.py calls sheets_manager.py**
→ `sheets_manager.py` runs `get_worksheets_from_sheet(gc, sheet_id)` function
→ This function calls `get_sheet_by_id(gc, sheet_id)` internally
→ Gets list of worksheets for the selected sheet

### **8. JavaScript receives response and updates HTML**
→ JavaScript processes the JSON response
→ Creates new `<option>` elements for each worksheet
→ Enables the worksheet dropdown

### **9. User fills form and submits**
→ `app.py` runs `index()` function (POST request)
→ Extracts form data: `selected_sheet_id`, `selected_worksheet`, `name`, `amount`, `description`

### **10. app.py validates form data**
→ Checks if `selected_sheet_id` is not empty
→ Checks if `selected_worksheet` is not empty
→ If validation fails, calls `flash()` function with error message

### **11. app.py calls sheets_manager.py**
→ `sheets_manager.py` runs `add_transaction_to_selected_sheet(gc, sheet_id, worksheet_title, name, amount, description)` function
→ This function calls `get_sheet_by_id(gc, sheet_id)` internally
→ Gets the specific worksheet using `sheet.worksheet(worksheet_title)`
→ Creates timestamp using `datetime.now().strftime('%d-%m-%Y %H:%M:%S')`
→ Converts amount to float and validates it
→ Prepares row data: `[name, numeric_amount, description, timestamp]`
→ Calls `worksheet.append_row(row)` to save to Google Sheets

### **12. app.py shows success/error message**
→ If successful: calls `flash('Transaction added successfully!', 'success')`
→ If failed: calls `flash('Error adding transaction!', 'error')`
→ Redirects to `thank_you()` function or re-renders form with error

### **13. Jinja2 displays flash messages**
→ `templates/index.html` processes `{% with messages = get_flashed_messages(with_categories=true) %}`
→ Loops through messages with `{% for category, message in messages %}`
→ Displays success messages in green, error messages in red

## **Function Summary by File:**

### **app.py Functions:**
- `index()` - Main route handler (GET/POST)
- `get_worksheets(sheet_id)` - AJAX route for worksheets
- `thank_you()` - Thank you page route

### **sheets_manager.py Functions:**
- `get_available_sheets(gc)` - Gets list of all Google Sheets
- `get_sheet_by_id(gc, sheet_id)` - Safely opens a specific sheet
- `get_worksheets_from_sheet(gc, sheet_id)` - Gets worksheets from a sheet
- `add_transaction_to_selected_sheet(gc, sheet_id, worksheet_title, name, amount, description)` - Saves transaction data

### **config.py Functions:**
- `initialize_sheets()` - Sets up Google Sheets connection

### **templates/index.html Functions:**
- `loadWorksheets()` - JavaScript function for dynamic worksheet loading
- Jinja2 template functions: `get_flashed_messages()`, `url_for()`

## **Data Flow Between Functions:**

```
User Input → app.py (index) → sheets_manager.py → Google Sheets API
                ↓
            templates/index.html (Jinja2 + JavaScript)
                ↓
            User sees result
```