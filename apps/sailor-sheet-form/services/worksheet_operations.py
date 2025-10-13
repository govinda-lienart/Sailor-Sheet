"""
Worksheet Operations Service
Handles worksheet-related operations and sheet management.
"""

class WorksheetOperations:
    """Service for worksheet operations and sheet management."""
    
    def __init__(self, gc):
        """Initialize with Google Sheets client."""
        self.gc = gc
    
    def get_worksheets_from_sheet(self, sheet_id):
        """
        Get list of worksheets (subsheets) from a specific Google Sheet
        Args:
            sheet_id: ID of the specific sheet
        Returns: List of dictionaries with worksheet info including account names
        """
        try:
            # Use the centralized sheet opening function
            sheet = self.get_sheet_by_id(sheet_id)
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

    def get_sheet_by_id(self, sheet_id):
        """
        Get a specific sheet by its ID
        Args:
            sheet_id: ID of the sheet to retrieve
        Returns: Sheet object or None if not found
        """
        try:
            sheet = self.gc.open_by_key(sheet_id)
            return sheet
        except Exception as e:
            print(f"Error getting sheet by ID: {e}")
            return None
