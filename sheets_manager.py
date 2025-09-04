# =============================================================================
# Created: 2025-09-04 14:26:30
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-04 14:23:56
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-04 14:01:24
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-04 04:52:11
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-04 04:50:11
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-04 04:49:54
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-04 04:26:36
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-03 22:51:02
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-03 19:28:04
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-03 19:13:13
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-03 16:09:02
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-03 15:20:50
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-03 11:28:57
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-03 11:27:32
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-02 21:17:10
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-02 12:20:13
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-02 12:18:54
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-02 11:05:49
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-02 10:43:56
# Status: ✅ WORKING - Ready for GitHub commit
# =============================================================================

from datetime import datetime

# =============================================================================
# ACCOUNT REFERENCE MANAGEMENT
# =============================================================================

# Get Account Reference Table
# ---------------------------
def get_account_reference_table(gc, master_sheet_id="1DE3YTidoVIQm4SxFvK2ByRahZ7qR_Kj_LDPTpIv5NQE", worksheet_title="Account - ID Worksheet"):
    """
    Get the account reference table that maps worksheet IDs to account names
    Args:
        gc: Google Sheets client
        master_sheet_id: ID of the master sheet containing the reference table
        worksheet_title: Title of the worksheet containing the reference table
    Returns: Dictionary mapping worksheet IDs to account names
    """
    try:
        print(f"DEBUG: Opening master sheet: {master_sheet_id}")
        print(f"DEBUG: Looking for worksheet: {worksheet_title}")
        
        # Open the master sheet
        master_sheet = gc.open_by_key(master_sheet_id)
        worksheet = master_sheet.worksheet(worksheet_title)
        
        # Get all data from the reference table
        all_data = worksheet.get_all_values()
        print(f"DEBUG: Raw data from reference table: {all_data}")
        
        # Skip header row and build mapping
        account_mapping = {}
        for row in all_data[1:]:  # Skip header row
            if len(row) >= 2 and row[0] and row[1]:  # Check if both columns have data
                account_name = row[0].strip()
                worksheet_id = row[1].strip()
                account_mapping[worksheet_id] = account_name
                print(f"DEBUG: Mapped {worksheet_id} -> {account_name}")
                
                # Also map by worksheet title for easier lookup
                # Extract worksheet title from the URL or use a simpler mapping
                if "1Fvrld1X0OioH7AbKCiSIMNac5U9OvlKJh0OSk02bTTI" in worksheet_id:
                    account_mapping["VN Indovina"] = account_name
                    print(f"DEBUG: Also mapped 'VN Indovina' -> {account_name}")
        
        print(f"DEBUG: Loaded {len(account_mapping)} account mappings")
        print(f"DEBUG: Final mapping: {account_mapping}")
        return account_mapping
        
    except Exception as e:
        print(f"Error getting account reference table: {e}")
        return {}

# Get Account Name From Worksheet ID
# ----------------------------------
def get_account_name_from_worksheet_id(gc, worksheet_id, master_sheet_id="1DE3YTidoVIQm4SxFvK2ByRahZ7qR_Kj_LDPTpIv5NQE"):
    """
    Get the account name for a given worksheet ID from the reference table
    Args:
        gc: Google Sheets client
        worksheet_id: ID of the worksheet to look up (format: sheet_id#gid=N)
        master_sheet_id: ID of the master sheet containing the reference table
    Returns: Account name or None if not found
    """
    try:
        print(f"DEBUG: Looking up worksheet ID: {worksheet_id}")
        print(f"DEBUG: Using master sheet ID: {master_sheet_id}")
        
        # Extract the base sheet ID from the worksheet_id (remove #gid= part)
        if "#gid=" in worksheet_id:
            base_sheet_id = worksheet_id.split("#gid=")[0]
            gid = worksheet_id.split("#gid=")[1]
            print(f"DEBUG: Extracted base sheet ID: {base_sheet_id}")
            print(f"DEBUG: Extracted gid: {gid}")
        else:
            base_sheet_id = worksheet_id
            gid = "0"
            print(f"DEBUG: Using worksheet ID as-is: {base_sheet_id}")
        
        account_mapping = get_account_reference_table(gc, master_sheet_id)
        print(f"DEBUG: Account mapping keys: {list(account_mapping.keys())}")
        
        # Try to find account name using the base sheet ID
        account_name = account_mapping.get(base_sheet_id)
        
        if account_name:
            print(f"DEBUG: Found account name '{account_name}' for base sheet ID '{base_sheet_id}'")
        else:
            print(f"DEBUG: No account name found for base sheet ID '{base_sheet_id}'")
            print(f"DEBUG: Available worksheet IDs: {list(account_mapping.keys())}")
            
        return account_name
        
    except Exception as e:
        print(f"Error getting account name from worksheet ID: {e}")
        return None

# Get Account Name From Worksheet Title
# ------------------------------------
def get_account_name_from_worksheet_title(gc, worksheet_title, master_sheet_id="1DE3YTidoVIQm4SxFvK2ByRahZ7qR_Kj_LDPTpIv5NQE"):
    """
    Get the account name for a given worksheet title from the reference table
    Args:
        gc: Google Sheets client
        worksheet_title: Title of the worksheet to look up
        master_sheet_id: ID of the master sheet containing the reference table
    Returns: Account name or None if not found
    """
    try:
        print(f"DEBUG: Looking up worksheet title: {worksheet_title}")
        print(f"DEBUG: Using master sheet ID: {master_sheet_id}")
        
        # Get the reference table
        master_sheet = gc.open_by_key(master_sheet_id)
        worksheet = master_sheet.worksheet("Account - ID Worksheet")
        
        # Get all data from the reference table
        all_data = worksheet.get_all_values()
        print(f"DEBUG: Master reference table data: {all_data}")
        
        # Skip header row and search for matching worksheet title
        for i, row in enumerate(all_data[1:], start=1):  # Skip header row
            print(f"DEBUG: Row {i}: {row}")
            if len(row) >= 3 and row[0] and row[2]:  # Check if both account name and worksheet title columns have data
                account_name = row[0].strip()
                worksheet_title_in_table = row[2].strip()  # Assuming worksheet title is in column C
                print(f"DEBUG: Comparing '{worksheet_title_in_table}' with '{worksheet_title}'")
                
                if worksheet_title_in_table == worksheet_title:
                    print(f"DEBUG: Found account name '{account_name}' for worksheet title '{worksheet_title}'")
                    return account_name
        
        print(f"DEBUG: No account name found for worksheet title '{worksheet_title}'")
        return None
        
    except Exception as e:
        print(f"Error getting account name from worksheet title: {e}")
        return None

# =============================================================================
# SHEET SELECTION AND MANAGEMENT
# =============================================================================

# Get Available Sheets
# -------------------
def get_available_sheets(gc):
    """
    Get list of available Google Sheets for dropdown selection
    Args:
        gc: Google Sheets client
    Returns: List of dictionaries with sheet info
    """
    try:
        # Get all spreadsheets you have access to
        all_sheets = gc.openall()
        sheet_list = []
        
        for sheet in all_sheets:
            sheet_list.append({
                'id': sheet.id,
                'title': sheet.title
            })
        
        return sheet_list
    except Exception as e:
        print(f"Error getting sheets: {e}")
        return []

# Get Sheet By ID
# ---------------
def get_sheet_by_id(gc, sheet_id):
    """
    Get a specific sheet by its ID
    Args:
        gc: Google Sheets client
        sheet_id: ID of the sheet to retrieve
    Returns: Sheet object or None if not found
    """
    try:
        sheet = gc.open_by_key(sheet_id)
        return sheet
    except Exception as e:
        print(f"Error getting sheet by ID: {e}")
        return None

# Get Worksheets From Sheet
# -------------------------
def get_worksheets_from_sheet(gc, sheet_id):
    """
    Get list of worksheets (subsheets) from a specific Google Sheet
    Args:
        gc: Google Sheets client
        sheet_id: ID of the specific sheet
    Returns: List of dictionaries with worksheet info including account names
    """
    try:
        # Use the centralized sheet opening function
        sheet = get_sheet_by_id(gc, sheet_id)
        if sheet is None:
            return []
        
        # Get all worksheets in this sheet
        worksheets = sheet.worksheets()
        worksheet_list = []
        
        for worksheet in worksheets:
            worksheet_title = worksheet.title
            
            print(f"DEBUG: Processing worksheet: {worksheet_title}")
            
            worksheet_list.append({
                'id': worksheet_title,  # Use worksheet title as ID
                'title': worksheet.title,
                'index': worksheet.index,
                'account_name': worksheet_title  # Use worksheet title as account name
            })
        
        return worksheet_list
    except Exception as e:
        print(f"Error getting worksheets: {e}")
        return []

# =============================================================================
# TRANSACTION MANAGEMENT
# =============================================================================

# Add Transaction To Selected Sheet
# --------------------------------
def add_transaction_to_selected_sheet(gc, sheet_id, worksheet_id, amount, description, fund_id, category_id, debit_account_id, credit_account_id, transaction_type, date_input, transaction_number, file_link="", origin_account="", destination_account="", transfer_type="external"):
    """
    Add double-entry transaction to a specific selected sheet and worksheet
    Creates TWO entries: one debit entry and one credit entry
    Args:
        gc: Google Sheets client
        sheet_id: ID of the specific sheet
        worksheet_id: ID of the specific worksheet (not title)
        amount: Amount from form (always positive)
        description: Description from form
        fund_id: ID of the fund from form
        category_id: ID of the category from form
        debit_account_id: ID of the account to be debited
        credit_account_id: ID of the account to be credited
        transaction_type: Legacy parameter (kept for compatibility)
        date_input: Date from form in DD/MM/YY format
        transaction_number: Pre-generated transaction number from form
        file_link: Optional file link dict with filename and url
        origin_account: Legacy parameter (kept for compatibility)
        destination_account: Legacy parameter (kept for compatibility)
        transfer_type: Legacy parameter (kept for compatibility)
    Returns: True if successful, False otherwise
    """
    try:
        print(f"DEBUG: add_transaction_to_selected_sheet called with:")
        print(f"  - sheet_id: {sheet_id}")
        print(f"  - worksheet_id: {worksheet_id}")
        print(f"  - amount: {amount}")
        print(f"  - transaction_type: {transaction_type}")
        print(f"  - transfer_type: {transfer_type}")
        print(f"  - origin_account: {origin_account}")
        print(f"  - destination_account: {destination_account}")
        print(f"  - fund_id: {fund_id}")
        print(f"  - category_id: {category_id}")
        print(f"  - date_input: {date_input}")
        print(f"  - transaction_number: {transaction_number}")
        print(f"  - file_link: {file_link}")
        print(f"  - description: {description}")
        # Use the centralized sheet opening function
        print(f"DEBUG: Opening sheet with ID: {sheet_id}")
        sheet = get_sheet_by_id(gc, sheet_id)
        if sheet is None:
            print("ERROR: Could not open sheet")
            return False
        print(f"DEBUG: Successfully opened sheet: {sheet.title}")
        
        # Get worksheet by title (since we're now passing worksheet titles)
        print(f"DEBUG: Getting worksheet by title: {worksheet_id}")
        try:
            worksheet = sheet.worksheet(worksheet_id)
            print(f"DEBUG: Found worksheet by title: {worksheet.title}")
        except Exception as e:
            print(f"ERROR: Could not get worksheet by title '{worksheet_id}': {e}")
            worksheets = sheet.worksheets()
            print(f"DEBUG: Available worksheets: {[ws.title for ws in worksheets]}")
            return False
        
        # Use the pre-generated transaction number from the form
        if not transaction_number:
            # Fallback: generate new transaction number if none provided
            now = datetime.now()
            transaction_number = now.strftime('%d%m%y-%H%M%S')
            print(f"Warning: No transaction number provided, generated: {transaction_number}")
        
        # Format the date input to DD/MM/YY format
        try:
            # Parse the date input and convert to DD/MM/YY format
            if date_input:
                # If date_input is in YYYY-MM-DD format (from HTML date picker), convert it
                if '-' in date_input and len(date_input.split('-')[0]) == 4:
                    # Parse YYYY-MM-DD and convert to DD/MM/YY
                    parsed_date = datetime.strptime(date_input, '%Y-%m-%d')
                    formatted_date = parsed_date.strftime('%d/%m/%y')
                else:
                    # If already in DD/MM/YY format, use as is
                    formatted_date = date_input
            else:
                # If no date provided, use today's date in DD/MM/YY format
                formatted_date = now.strftime('%d/%m/%y')
        except Exception as e:
            # Fallback to today's date if parsing fails
            formatted_date = now.strftime('%d/%m/%y')
            print(f"Warning: Could not parse date '{date_input}', using today's date: {formatted_date}")
        
        # Convert amount to number (not string)
        try:
            numeric_amount = float(amount)
        except ValueError:
            raise Exception(f"Invalid amount: {amount}. Please enter a valid number.")
        
        # Get fund name from fund ID (or use directly if it's "Internal Transfer")
        print(f"DEBUG: Looking up fund name for fund_id: {fund_id}")
        if fund_id == "Internal Transfer":
            fund_name = "Internal Transfer"
            print(f"DEBUG: Using hardcoded fund name: {fund_name}")
        else:
            fund_name = get_fund_name_by_id(gc, fund_id)
            print(f"DEBUG: Found fund name: {fund_name}")
        
        # Get category name from category ID (or use directly if it's "Internal Transfer")
        print(f"DEBUG: Looking up category name for category_id: {category_id}")
        if category_id == "Internal Transfer":
            category_name = "Internal Transfer"
            print(f"DEBUG: Using hardcoded category name: {category_name}")
        else:
            category_name = get_category_name_by_code(gc, category_id)
            print(f"DEBUG: Found category name: {category_name}")
        
        # Get account names from account IDs
        print(f"DEBUG: Looking up debit account name for debit_account_id: {debit_account_id}")
        debit_account_name = get_account_name_by_code(gc, debit_account_id)
        print(f"DEBUG: Found debit account name: {debit_account_name}")
        
        print(f"DEBUG: Looking up credit account name for credit_account_id: {credit_account_id}")
        credit_account_name = get_account_name_by_code(gc, credit_account_id)
        print(f"DEBUG: Found credit account name: {credit_account_name}")
        
        # Handle file link - create HYPERLINK formula if we have both URL and filename
        if isinstance(file_link, dict) and 'filename' in file_link and 'url' in file_link:
            # Create the HYPERLINK formula as recommended by your colleague
            link_value = f'=HYPERLINK("{file_link["url"]}", "{file_link["filename"]}")'
        else:
            link_value = file_link if file_link else ""
        
        # Get worksheet title for reference
        worksheet_title = worksheet.title
        print(f"DEBUG: Worksheet title: {worksheet_title}")
        
        # DOUBLE-ENTRY BOOKKEEPING: Create TWO entries
        print(f"DEBUG: Creating double-entry bookkeeping entries")
        
        # Entry 1: DEBIT entry (amount goes in Debit column)
        debit_row = [
            transaction_number,    # A: Transaction Number
            formatted_date,        # B: Date
            fund_name,            # C: Funds
            debit_account_name,   # D: Account (the account being debited)
            category_name,        # E: Category
            numeric_amount,       # F: Debit (VND) - amount goes here
            "",                   # G: Credit (VND) - empty for debit entry
            description,          # H: Description
            link_value            # I: Link Bill
        ]
        
        # Entry 2: CREDIT entry (amount goes in Credit column)
        credit_row = [
            transaction_number,    # A: Transaction Number
            formatted_date,        # B: Date
            fund_name,            # C: Funds
            credit_account_name,  # D: Account (the account being credited)
            category_name,        # E: Category
            "",                   # F: Debit (VND) - empty for credit entry
            numeric_amount,       # G: Credit (VND) - amount goes here
            description,          # H: Description
            link_value            # I: Link Bill
        ]
        
        print(f"DEBUG: Prepared DEBIT entry:")
        for i, cell in enumerate(debit_row):
            column_letter = chr(65 + i)  # A=65, B=66, etc.
            print(f"  - Column {column_letter}: '{cell}' (type: {type(cell)})")
            
        print(f"DEBUG: Prepared CREDIT entry:")
        for i, cell in enumerate(credit_row):
            column_letter = chr(65 + i)  # A=65, B=66, etc.
            print(f"  - Column {column_letter}: '{cell}' (type: {type(cell)})")
        
        # Add both entries to the worksheet
        print(f"DEBUG: Adding DEBIT entry to worksheet: {worksheet.title}")
        worksheet.append_row(debit_row)
        print(f"DEBUG: DEBIT entry successfully added")
        
        print(f"DEBUG: Adding CREDIT entry to worksheet: {worksheet.title}")
        worksheet.append_row(credit_row)
        print(f"DEBUG: CREDIT entry successfully added")
        
        # If we added a HYPERLINK formula, we need to format it properly with USER_ENTERED for both entries
        if link_value.startswith('=HYPERLINK('):
            print(f"DEBUG: Processing HYPERLINK formula: {link_value}")
            # Get the current row count to find the last two rows we just added
            all_values = worksheet.get_all_values()
            last_row = len(all_values)
            
            # Update HYPERLINK for debit entry (second to last row)
            debit_cell_address = f'I{last_row - 1}'
            print(f"DEBUG: Updating debit entry cell {debit_cell_address} with HYPERLINK formula")
            worksheet.update(debit_cell_address, link_value, value_input_option='USER_ENTERED')
            
            # Update HYPERLINK for credit entry (last row)
            credit_cell_address = f'I{last_row}'
            print(f"DEBUG: Updating credit entry cell {credit_cell_address} with HYPERLINK formula")
            worksheet.update(credit_cell_address, link_value, value_input_option='USER_ENTERED')
            
            print(f"DEBUG: HYPERLINK formulas updated successfully for both entries")
        
        print(f"DEBUG: Transaction completed successfully!")
        return True
    except Exception as e:
        print(f"ERROR: Exception occurred in add_transaction_to_selected_sheet:")
        print(f"  - Error message: {e}")
        print(f"  - Error type: {type(e).__name__}")
        import traceback
        print(f"  - Full traceback:")
        traceback.print_exc()
        return False

# =============================================================================
# FUNDS REFERENCE FUNCTIONS
# =============================================================================

# Get Funds List
# --------------
def get_funds_list(gc):
    """
    Get funds from reference sheet for dropdown
    Args:
        gc: Google Sheets client
    Returns: List of fund dictionaries with id, name, and color
    """
    try:
        funds_sheet = gc.open_by_key("1DE3YTidoVIQm4SxFvK2ByRahZ7qR_Kj_LDPTpIv5NQE").worksheet("Funds Reference")
        funds_data = funds_sheet.get_all_records()
        
        # Return only active funds
        active_funds = []
        for fund in funds_data:
            # Check for various possible TRUE values - handle column name with spaces
            active_value = fund.get('Active') or fund.get('Active ')  # Handle both versions
            color_value = fund.get('Fund_Color') or fund.get('Fund_Color ')  # Handle both versions
            
            if active_value == True or active_value == 'TRUE' or active_value == 'true' or str(active_value).upper() == 'TRUE':
                active_funds.append({
                    'id': fund['Fund_ID'],
                    'name': fund['Fund_Name'],
                    'color': color_value
                })
        
        print(f"DEBUG: Found {len(active_funds)} active funds")
        return active_funds
        
    except Exception as e:
        print(f"Error getting funds: {e}")
        return []

# Get Fund Name By ID
# -------------------
def get_fund_name_by_id(gc, fund_id):
    """
    Get fund name by ID for transaction saving
    Args:
        gc: Google Sheets client
        fund_id: ID of the fund to look up
    Returns: Fund name or "Unknown Fund" if not found
    """
    try:
        print(f"DEBUG: get_fund_name_by_id called with fund_id: {fund_id}")
        funds_sheet = gc.open_by_key("1DE3YTidoVIQm4SxFvK2ByRahZ7qR_Kj_LDPTpIv5NQE").worksheet("Funds Reference")
        funds_data = funds_sheet.get_all_records()
        print(f"DEBUG: Retrieved {len(funds_data)} fund records")
        
        for i, fund in enumerate(funds_data):
            print(f"DEBUG: Fund {i}: Fund_ID='{fund.get('Fund_ID')}', Fund_Name='{fund.get('Fund_Name')}'")
            if str(fund['Fund_ID']) == str(fund_id):
                print(f"DEBUG: Found matching fund: {fund['Fund_Name']}")
                return fund['Fund_Name']
        
        print(f"WARNING: Fund ID {fund_id} not found")
        print(f"DEBUG: Available fund IDs: {[str(f.get('Fund_ID')) for f in funds_data]}")
        return "Unknown Fund"
        
    except Exception as e:
        print(f"ERROR in get_fund_name_by_id: {e}")
        import traceback
        traceback.print_exc()
        return "Unknown Fund"


# =============================================================================
# ACCOUNTS REFERENCE FUNCTIONS
# =============================================================================

# Get Accounts List
# -----------------
def get_accounts_list(gc):
    """
    Get accounts from reference sheet for dropdown
    Args:
        gc: Google Sheets client
    Returns: List of account dictionaries with code, name, and type
    """
    try:
        accounts_sheet = gc.open_by_key("1DE3YTidoVIQm4SxFvK2ByRahZ7qR_Kj_LDPTpIv5NQE").worksheet("Accounts")
        accounts_data = accounts_sheet.get_all_records()
        
        # Return all accounts (assuming they're all active)
        accounts_list = []
        for acc in accounts_data:
            accounts_list.append({
                'code': acc.get('Category Code', ''),
                'name': acc.get('Account Name', ''),
                'type': acc.get('Type of Account', '')
            })
        
        print(f"DEBUG: Found {len(accounts_list)} accounts")
        return accounts_list
        
    except Exception as e:
        print(f"Error getting accounts: {e}")
        return []

# Get Account Name By Code
# ------------------------
def get_account_name_by_code(gc, account_code):
    """
    Get account name by code for transaction saving
    Args:
        gc: Google Sheets client
        account_code: Code of the account to look up
    Returns: Account name or "Unknown Account" if not found
    """
    try:
        print(f"DEBUG: get_account_name_by_code called with account_code: {account_code}")
        accounts_sheet = gc.open_by_key("1DE3YTidoVIQm4SxFvK2ByRahZ7qR_Kj_LDPTpIv5NQE").worksheet("Accounts")
        accounts_data = accounts_sheet.get_all_records()
        print(f"DEBUG: Retrieved {len(accounts_data)} account records")
        
        for i, acc in enumerate(accounts_data):
            print(f"DEBUG: Account {i}: Code='{acc.get('Category Code')}', Name='{acc.get('Account Name')}'")
            if str(acc.get('Category Code', '')) == str(account_code):
                print(f"DEBUG: Found matching account: {acc.get('Account Name')}")
                return acc.get('Account Name', '')
        
        print(f"WARNING: Account Code {account_code} not found")
        print(f"DEBUG: Available account codes: {[str(acc.get('Category Code', '')) for acc in accounts_data]}")
        return "Unknown Account"
        
    except Exception as e:
        print(f"ERROR in get_account_name_by_code: {e}")
        import traceback
        traceback.print_exc()
        return "Unknown Account"


# =============================================================================
# CATEGORIES REFERENCE FUNCTIONS
# =============================================================================

# Get Categories List
# ---------------------
def get_categories_list(gc):
    """
    Get categories from reference sheet for dropdown
    Args:
        gc: Google Sheets client
    Returns: List of category dictionaries with code, name, and category
    """
    try:
        categories_sheet = gc.open_by_key("1DE3YTidoVIQm4SxFvK2ByRahZ7qR_Kj_LDPTpIv5NQE").worksheet("Category")
        categories_data = categories_sheet.get_all_records()
        
        # Return only active categories
        active_categories = []
        for cat in categories_data:
            # Check if there's an Active column, default to True if not present
            active_value = cat.get('Active', True)
            if active_value == True or active_value == 'TRUE' or active_value == 'true' or str(active_value).upper() == 'TRUE':
                active_categories.append({
                    'code': cat['Category Code'],
                    'name': cat['Category'],
                    'category': cat['Description']
                })
        
        print(f"DEBUG: Found {len(active_categories)} active categories")
        return active_categories
        
    except Exception as e:
        print(f"Error getting categories: {e}")
        return []

# Get Category Name By Code
# ----------------------------
def get_category_name_by_code(gc, category_code):
    """
    Get category name by code for transaction saving
    Args:
        gc: Google Sheets client
        category_code: Code of the category to look up
    Returns: Category name or "Unknown Category" if not found
    """
    try:
        print(f"DEBUG: get_category_name_by_code called with category_code: {category_code}")
        categories_sheet = gc.open_by_key("1DE3YTidoVIQm4SxFvK2ByRahZ7qR_Kj_LDPTpIv5NQE").worksheet("Category")
        categories_data = categories_sheet.get_all_records()
        print(f"DEBUG: Retrieved {len(categories_data)} category records")
        
        for i, cat in enumerate(categories_data):
            print(f"DEBUG: Category {i}: Code='{cat.get('Category Code')}', Name='{cat.get('Category')}'")
            if str(cat['Category Code']) == str(category_code):
                print(f"DEBUG: Found matching category: {cat['Category']}")
                return cat['Category']
        
        print(f"WARNING: Category Code {category_code} not found")
        print(f"DEBUG: Available category codes: {[str(cat.get('Category Code')) for cat in categories_data]}")
        return "Unknown Category"
        
    except Exception as e:
        print(f"ERROR in get_category_name_by_code: {e}")
        import traceback
        traceback.print_exc()
        return "Unknown Category"



