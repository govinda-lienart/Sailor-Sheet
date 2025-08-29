# =============================================================================
# SHEETS MANAGER - Google Sheets Operations
# Purpose: Handle all Google Sheets data operations
# Version: 1.0.0 - Working Version
# Created: 2025-01-27 19:30:00
# Status: ✅ WORKING - Clean operations only
# =============================================================================

from datetime import datetime

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

def add_transaction_to_selected_sheet(gc, sheet_id, worksheet_title, name, amount, description):
    """
    Add transaction to a specific selected sheet and worksheet
    Args:
        gc: Google Sheets client
        sheet_id: ID of the specific sheet
        worksheet_title: Title of the specific worksheet
        name: Name from form
        amount: Amount from form
        description: Description from form
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
        
        # Prepare data row: [Name, Amount (as number), Description, Timestamp]
        row = [name, numeric_amount, description, timestamp]
        
        # Add to next empty row
        worksheet.append_row(row)
        
        return True
    except Exception as e:
        print(f"Error adding transaction to selected sheet: {e}")
        return False



