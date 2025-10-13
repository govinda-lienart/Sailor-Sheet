"""
Sheets service for Google Sheets operations.
Handles all Google Sheets related business logic.
"""

from .sheets_operations import SheetsOperations
from .transaction_operations import TransactionOperations
from config import initialize_sheets


class SheetsService:
    """Service class for Google Sheets operations."""
    
    def __init__(self):
        """Initialize the sheets service with Google Sheets connection."""
        self.gc = initialize_sheets()
        self.sheets_ops = SheetsOperations(self.gc)
        self.transaction_ops = TransactionOperations(self.gc)
    
    def get_available_sheets(self):
        """Get list of available Google Sheets."""
        try:
            return self.sheets_ops.get_available_sheets()
        except Exception as e:
            print(f"ERROR in get_available_sheets: {e}")
            return []
    
    def get_worksheets_from_sheet(self, sheet_id):
        """Get worksheets from a specific sheet."""
        try:
            return self.sheets_ops.get_worksheets_from_sheet(sheet_id)
        except Exception as e:
            print(f"ERROR in get_worksheets_from_sheet: {e}")
            return []
    
    def add_transaction(self, transaction_data):
        """Add a transaction to the selected sheet."""
        try:
            return self.transaction_ops.add_transaction_to_selected_sheet(
                transaction_data['sheet_id'],
                transaction_data['worksheet_name'],
                transaction_data['amount'],
                transaction_data['description'],
                transaction_data['fund_id'],
                transaction_data['category_id'],
                transaction_data['debit_account_id'],
                transaction_data['credit_account_id'],
                transaction_data.get('transaction_type', 'external'),
                transaction_data.get('date_input', ''),
                transaction_data.get('transaction_number', ''),
                transaction_data.get('file_links', {}),
                transaction_data.get('origin_account', ''),
                transaction_data.get('destination_account', ''),
                transaction_data.get('transfer_type', 'external'),
                transaction_data.get('payment_method', 'bank'),
                transaction_data.get('reference_number', ''),
                transaction_data.get('sub_category_id', '')
            )
        except Exception as e:
            print(f"ERROR in add_transaction: {e}")
            return False
    
    def search_transaction(self, sheet_type, transaction_number):
        """Search for a transaction in Google Sheets."""
        try:
            return self.sheets_ops.search_transaction_tool(sheet_type, transaction_number)
        except Exception as e:
            print(f"ERROR in search_transaction: {e}")
            return None
    
    def update_document_link(self, sheet_type, transaction_number, document_type, file_url):
        """Update document link in Google Sheets."""
        try:
            return self.sheets_ops.update_document_link(sheet_type, transaction_number, document_type, file_url)
        except Exception as e:
            print(f"ERROR in update_document_link: {e}")
            return False
