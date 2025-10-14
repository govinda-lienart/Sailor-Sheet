"""
File Naming Service
Handles filename generation and naming conventions for uploaded files.
"""

from datetime import datetime


class FileNamingService:
    """Service for generating unique and consistent filenames."""
    
    def __init__(self):
        # Map file types to display names
        self.type_names = {
            'bills': 'bill',
            'redBills': 'red_bill', 
            'bankStatement': 'bank_statement',
            'documentation': 'doc'
        }
    
    def generate_unique_name(self, base: str, ext: str, transaction_number: str = None, file_type: str = 'bills') -> str:
        """
        Generate a unique filename with transaction number and file type.
        
        Args:
            base: Base filename without extension
            ext: File extension
            transaction_number: Optional transaction number to use in filename
            file_type: Type of file (bills, redBills, bankStatement, documentation)
            
        Returns:
            str: Unique filename
        """
        print(f"DEBUG: unique_name called with base={base}, ext={ext}, transaction_number={transaction_number}, file_type={file_type}")
        
        type_name = self.type_names.get(file_type, 'bill')
        
        if transaction_number and transaction_number.strip():
            # Use transaction number if provided
            result = f"{transaction_number}_{type_name}.{ext}"
            print(f"DEBUG: Using transaction number, result: {result}")
            return result
        else:
            # Fallback to timestamp if no transaction number
            ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            result = f"{ts}_{type_name}.{ext}"
            print(f"DEBUG: No transaction number, using timestamp, result: {result}")
            return result
    
    def get_type_name(self, file_type: str) -> str:
        """
        Get display name for file type.
        
        Args:
            file_type: File type code
            
        Returns:
            str: Display name for file type
        """
        return self.type_names.get(file_type, 'bill')
    
    def extract_base_and_extension(self, filename: str) -> tuple:
        """
        Extract base name and extension from filename.
        
        Args:
            filename: Full filename
            
        Returns:
            tuple: (base_name, extension)
        """
        if '.' in filename:
            base = filename.rsplit('.', 1)[0]
            ext = filename.rsplit('.', 1)[1].lower()
            return base, ext
        else:
            return filename, ''
