# =============================================================================
# Created: 2025-09-01 12:57:34
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-01 10:45:48
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-01 10:45:07
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-01 10:42:35
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-08-30 14:05:01
# Status: ✅ WORKING - Ready for GitHub commit
# SHEETS MANAGER - Google Sheets Operations
# Purpose: Handle all Google Sheets data operations
# Version: 1.0.0 - Working Version
# Created: 2025-01-27 19:30:00
# Status: ✅ WORKING - Clean operations only
# =============================================================================

from datetime import datetime
import os

# =============================================================================
# SHEET SELECTION AND MANAGEMENT
# =============================================================================

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

def get_worksheets_from_sheet(gc, sheet_id):
    """
    Get list of worksheets (subsheets) from a specific Google Sheet
    Args:
        gc: Google Sheets client
        sheet_id: ID of the specific sheet
    Returns: List of dictionaries with worksheet info
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
            worksheet_list.append({
                'id': worksheet.id,
                'title': worksheet.title,
                'index': worksheet.index
            })
        
        return worksheet_list
    except Exception as e:
        print(f"Error getting worksheets: {e}")
        return []

def add_transaction_to_selected_sheet(gc, sheet_id, worksheet_title, amount, description, fund_id, cost_center_id, transaction_type, file_link=""):
    """
    Add transaction to a specific selected sheet and worksheet
    Args:
        gc: Google Sheets client
        sheet_id: ID of the specific sheet
        worksheet_title: Title of the specific worksheet
        amount: Amount from form (always positive)
        description: Description from form
        fund_id: ID of the fund from form
        cost_center_id: ID of the cost center from form
        transaction_type: 'debit' (money out) or 'credit' (money in)
        file_link: Optional file link dict with filename and url
    Returns: True if successful, False otherwise
    """
    try:
        # Use the centralized sheet opening function
        sheet = get_sheet_by_id(gc, sheet_id)
        if sheet is None:
            return False
        
        # Get the specific worksheet by title
        worksheet = sheet.worksheet(worksheet_title)
        
        # Create timestamp for when data was submitted
        timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        
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
        
        # Prepare data row: [Timestamp, Fund, Cost Center, Debit, Credit, Description, LINK]
        # Order matches sheet headers: A=Timestamp, B=Funds, C=Cost Center, D=Debit, E=Credit, F=Description, G=LINK
        row = [timestamp, fund_name, cost_center_name, debit_amount, credit_amount, description, link_value]
        
        # Add to next empty row
        worksheet.append_row(row)
        
        # If we added a HYPERLINK formula, we need to format it properly with USER_ENTERED
        if link_value.startswith('=HYPERLINK('):
            # Get the last row number (where we just added data)
            all_values = worksheet.get_all_values()
            last_row = len(all_values)
            
            # Set the formula in the LINK column (column G) with USER_ENTERED
            cell_address = f'G{last_row}'
            worksheet.update(cell_address, link_value, value_input_option='USER_ENTERED')
        
        return True
    except Exception as e:
        print(f"Error adding transaction to selected sheet: {e}")
        return False



# =============================================================================
# FUNDS REFERENCE FUNCTIONS
# =============================================================================

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



