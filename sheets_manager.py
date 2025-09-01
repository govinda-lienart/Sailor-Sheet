# =============================================================================
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

def add_transaction_to_selected_sheet(gc, sheet_id, worksheet_title, name, amount, description, fund_id, file_link=""):
    """
    Add transaction to a specific selected sheet and worksheet
    Args:
        gc: Google Sheets client
        sheet_id: ID of the specific sheet
        worksheet_title: Title of the specific worksheet
        name: Name from form
        amount: Amount from form
        description: Description from form
        fund_id: ID of the fund from form
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
        
        # Handle file link - create HYPERLINK formula if we have both URL and filename
        if isinstance(file_link, dict) and 'filename' in file_link and 'url' in file_link:
            # Create the HYPERLINK formula as recommended by your colleague
            link_value = f'=HYPERLINK("{file_link["url"]}", "{file_link["filename"]}")'
        else:
            link_value = file_link if file_link else ""
        
        # Prepare data row: [Timestamp, Fund, Name, Amount, Description, LINK]
        # Order matches sheet headers: A=Timestamp, B=Funds, C=Name, D=Amount, E=Description, F=LINK
        row = [timestamp, fund_name, name, numeric_amount, description, link_value]
        
        # Add to next empty row
        worksheet.append_row(row)
        
        # If we added a HYPERLINK formula, we need to format it properly with USER_ENTERED
        if link_value.startswith('=HYPERLINK('):
            # Get the last row number (where we just added data)
            all_values = worksheet.get_all_values()
            last_row = len(all_values)
            
            # Set the formula in the LINK column (column F) with USER_ENTERED
            cell_address = f'F{last_row}'
            worksheet.update(cell_address, link_value, value_input_option='USER_ENTERED')
        
        return True
    except Exception as e:
        print(f"Error adding transaction to selected sheet: {e}")
        return False

# =============================================================================
# GOOGLE DRIVE FILE UPLOAD FUNCTIONS
# =============================================================================

def create_or_get_folder(gc, folder_name_or_id):
    """
    Get a specific folder by ID or name
    Args:
        gc: Google Drive client
        folder_name_or_id: Either folder ID (long string) or folder name
    Returns: Folder info dictionary or None if error
    """
    try:
        # If it looks like a folder ID (long string of letters/numbers)
        if len(folder_name_or_id) > 20 and not folder_name_or_id.startswith(' '):
            # Try to get folder by ID
            folder = gc.get(folder_name_or_id)
            return folder
        else:
            # Try to get folder by name (backward compatibility)
            folders = gc.list(q=f"name='{folder_name_or_id}' and mimeType='application/vnd.google-apps.folder' and trashed=false")
            if folders:
                return folders[0]
            return None
    except Exception as e:
        print(f"Error getting folder: {e}")
        return None

def upload_file_to_drive(gc, file, folder_name="NGO_Documents"):
    """
    Upload a file to Google Drive in a specific folder
    Args:
        gc: Google Drive client
        file: File object from Flask request
        folder_name: Name of the folder to upload to
    Returns: File info dictionary or None if error
    """
    try:
        print(f"DEBUG: Starting file upload to folder: {folder_name}")
        
        # Create or get the folder
        folder = create_or_get_folder(gc, folder_name)
        if folder is None:
            print(f"DEBUG: Failed to get folder: {folder_name}")
            return None
        
        print(f"DEBUG: Got folder: {folder['id']}")
        
        # Prepare file metadata
        file_metadata = {
            'name': file.filename,
            'parents': [folder['id']]
        }
        
        print(f"DEBUG: File metadata prepared: {file_metadata}")
        
        # Upload the file
        uploaded_file = gc.create(file_metadata, file.read())
        
        print(f"DEBUG: File uploaded successfully: {uploaded_file['id']}")
        
        return {
            'id': uploaded_file['id'],
            'name': uploaded_file['name'],
            'url': uploaded_file['webViewLink'],
            'folder': folder_name
        }
        
    except Exception as e:
        print(f"Error uploading file: {e}")
        return None

def get_files_from_folder(gc, folder_name="NGO_Documents"):
    """
    Get list of files from a specific Google Drive folder
    Args:
        gc: Google Drive client
        folder_name: Name of the folder to list files from
    Returns: List of file dictionaries or empty list if error
    """
    try:
        # Get the folder
        folder = create_or_get_folder(gc, folder_name)
        if folder is None:
            return []
        
        # List files in the folder
        files = gc.list(q=f"'{folder['id']}' in parents and trashed=false")
        
        file_list = []
        for file in files:
            file_list.append({
                'id': file['id'],
                'name': file['name'],
                'url': file['webViewLink'],
                'created': file['createdTime']
            })
        
        return file_list
        
    except Exception as e:
        print(f"Error getting files from folder: {e}")
        return []

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



