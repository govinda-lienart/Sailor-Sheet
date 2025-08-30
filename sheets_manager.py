# =============================================================================
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

def add_transaction_to_selected_sheet(gc, sheet_id, worksheet_title, name, amount, description, file_link=""):
    """
    Add transaction to a specific selected sheet and worksheet
    Args:
        gc: Google Sheets client
        sheet_id: ID of the specific sheet
        worksheet_title: Title of the specific worksheet
        name: Name from form
        amount: Amount from form
        description: Description from form
        file_link: Optional file link from upload
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
        
        # Prepare data row: [Timestamp, Name, Amount, Description, LINK]
        # This matches your Google Sheet headers exactly
        row = [timestamp, name, numeric_amount, description, file_link]
        
        # Add to next empty row
        worksheet.append_row(row)
        
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



