# =============================================================================
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
def add_transaction_to_selected_sheet(gc, sheet_id, worksheet_id, amount, description, fund_id, cost_center_id, transaction_type, date_input, transaction_number, file_link="", account_name=""):
    """
    Add transaction to a specific selected sheet and worksheet
    Args:
        gc: Google Sheets client
        sheet_id: ID of the specific sheet
        worksheet_id: ID of the specific worksheet (not title)
        amount: Amount from form (always positive)
        description: Description from form
        fund_id: ID of the fund from form
        cost_center_id: ID of the cost center from form
        transaction_type: 'debit' (money out) or 'credit' (money in)
        date_input: Date from form in DD/MM/YY format
        transaction_number: Pre-generated transaction number from form
        file_link: Optional file link dict with filename and url
        account_name: Account name to use (passed from frontend lookup)
    Returns: True if successful, False otherwise
    """
    try:
        print(f"DEBUG: add_transaction_to_selected_sheet called with:")
        print(f"  - sheet_id: {sheet_id}")
        print(f"  - worksheet_id: {worksheet_id}")
        print(f"  - account_name: {account_name}")
        print(f"  - amount: {amount}")
        print(f"  - transaction_type: {transaction_type}")
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
        
        # Get fund name from fund ID
        fund_name = get_fund_name_by_id(gc, fund_id)
        
        # Get cost center name from cost center ID
        cost_center_name = get_cost_center_name_by_code(gc, cost_center_id)
        
        # Handle file link - create HYPERLINK formula if we have both URL and filename
        if isinstance(file_link, dict) and 'filename' in file_link and 'url' in file_link:
            # Create the HYPERLINK formula as recommended by your colleague
            link_value = f'=HYPERLINK("{file_link["url"]}", "{file_link["filename"]}")'
        else:
            link_value = file_link if file_link else ""
        
        # Determine Debit/Credit values based on transaction type
        if transaction_type == 'debit':
            debit_amount = numeric_amount
            credit_amount = ""  # Empty for debit transactions
        elif transaction_type == 'credit':
            debit_amount = ""   # Empty for credit transactions
            credit_amount = numeric_amount
        else:
            raise Exception(f"Invalid transaction type: {transaction_type}. Must be 'debit' or 'credit'.")
        
        # Use the account name passed from the frontend (already looked up from master reference table)
        worksheet_title = worksheet.title
        print(f"DEBUG: Using account name from frontend: {account_name}")
        print(f"DEBUG: Worksheet title: {worksheet_title}")
        
        # If no account name was passed, fall back to looking it up
        if not account_name:
            print(f"DEBUG: No account name passed, looking up from worksheet ID: {worksheet_id}")
            account_name = get_account_name_from_worksheet_id(gc, worksheet_id)
            print(f"DEBUG: Retrieved account name: {account_name}")
            
            # If still no account name found, use worksheet title as fallback
            if not account_name:
                account_name = worksheet_title
                print(f"WARNING: No account name found for worksheet ID {worksheet_id}, using worksheet title: {worksheet_title}")
        
        print(f"DEBUG: Final account name to be stored: {account_name}")
        
        # Prepare data row to match EXACT Google Sheet column order
        # A=Transaction Number, B=Date, C=Funds, D=Cost Center, E=Account, F=Debit(VND), G=Credit(VND), H=Description, I=Link Bill
        row = [
            transaction_number,    # A: Transaction Number
            formatted_date,        # B: Date
            fund_name,            # C: Funds
            cost_center_name,     # D: Cost Center
            account_name,         # E: Account
            debit_amount,         # F: Debit (VND)
            credit_amount,        # G: Credit (VND)
            description,          # H: Description
            link_value            # I: Link Bill
        ]
        
        # Add to next empty row
        worksheet.append_row(row)
        
        # If we added a HYPERLINK formula, we need to format it properly with USER_ENTERED
        if link_value.startswith('=HYPERLINK('):
            # Get the last row number (where we just added data)
            all_values = worksheet.get_all_values()
            last_row = len(all_values)
            
            # Set the formula in the LINK column (column I) with USER_ENTERED
            cell_address = f'I{last_row}'
            worksheet.update(cell_address, link_value, value_input_option='USER_ENTERED')
        
        return True
    except Exception as e:
        print(f"Error adding transaction to selected sheet: {e}")
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
        
        print(f"DEBUG: Raw funds data from sheet: {funds_data}")
        
        # Return only active funds
        active_funds = []
        for fund in funds_data:
            print(f"DEBUG: Processing fund: {fund}")
            print(f"DEBUG: Active value: '{fund.get('Active')}' (type: {type(fund.get('Active'))})")
            
            # Check for various possible TRUE values - handle column name with spaces
            active_value = fund.get('Active') or fund.get('Active ')  # Handle both versions
            color_value = fund.get('Fund_Color') or fund.get('Fund_Color ')  # Handle both versions
            
            if active_value == True or active_value == 'TRUE' or active_value == 'true' or str(active_value).upper() == 'TRUE':
                active_funds.append({
                    'id': fund['Fund_ID'],
                    'name': fund['Fund_Name'],
                    'color': color_value
                })
                print(f"DEBUG: Added fund: {fund['Fund_Name']}")
        
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
        funds_sheet = gc.open_by_key("1DE3YTidoVIQm4SxFvK2ByRahZ7qR_Kj_LDPTpIv5NQE").worksheet("Funds Reference")
        funds_data = funds_sheet.get_all_records()
        
        for fund in funds_data:
            if str(fund['Fund_ID']) == str(fund_id):
                return fund['Fund_Name']
        
        print(f"WARNING: Fund ID {fund_id} not found")
        return "Unknown Fund"
        
    except Exception as e:
        print(f"Error getting fund name: {e}")
        return "Unknown Fund"


# =============================================================================
# COST CENTERS REFERENCE FUNCTIONS
# =============================================================================

# Get Cost Centers List
# ---------------------
def get_cost_centers_list(gc):
    """
    Get cost centers from reference sheet for dropdown
    Args:
        gc: Google Sheets client
    Returns: List of cost center dictionaries with code, name, and category
    """
    try:
        cost_centers_sheet = gc.open_by_key("1DE3YTidoVIQm4SxFvK2ByRahZ7qR_Kj_LDPTpIv5NQE").worksheet("Cost Centers")
        cost_centers_data = cost_centers_sheet.get_all_records()
        
        print(f"DEBUG: Raw cost centers data from sheet: {cost_centers_data}")
        
        # Return only active cost centers
        active_cost_centers = []
        for cc in cost_centers_data:
            # Check if there's an Active column, default to True if not present
            active_value = cc.get('Active', True)
            if active_value == True or active_value == 'TRUE' or active_value == 'true' or str(active_value).upper() == 'TRUE':
                active_cost_centers.append({
                    'code': cc['Cost Center Code'],
                    'name': cc['Cost Center Name'],
                    'category': cc['Category']
                })
                print(f"DEBUG: Added cost center: {cc['Cost Center Name']}")
        
        print(f"DEBUG: Found {len(active_cost_centers)} active cost centers")
        return active_cost_centers
        
    except Exception as e:
        print(f"Error getting cost centers: {e}")
        return []

# Get Cost Center Name By Code
# ----------------------------
def get_cost_center_name_by_code(gc, cost_center_code):
    """
    Get cost center name by code for transaction saving
    Args:
        gc: Google Sheets client
        cost_center_code: Code of the cost center to look up
    Returns: Cost center name or "Unknown Cost Center" if not found
    """
    try:
        cost_centers_sheet = gc.open_by_key("1DE3YTidoVIQm4SxFvK2ByRahZ7qR_Kj_LDPTpIv5NQE").worksheet("Cost Centers")
        cost_centers_data = cost_centers_sheet.get_all_records()
        
        for cc in cost_centers_data:
            if str(cc['Cost Center Code']) == str(cost_center_code):
                return cc['Cost Center Name']
        
        print(f"WARNING: Cost Center Code {cost_center_code} not found")
        return "Unknown Cost Center"
        
    except Exception as e:
        print(f"Error getting cost center name: {e}")
        return "Unknown Cost Center"



