"""
File service for handling file upload operations.
"""

import file_upload_manager


class FileService:
    """Service class for file operations."""
    
    def handle_web_upload(self, file, transaction_number, file_type, country_code):
        """Handle web file upload."""
        try:
            return file_upload_manager.handle_web_upload(file, transaction_number, file_type, country_code)
        except Exception as e:
            print(f"ERROR in handle_web_upload: {e}")
            return {'success': False, 'error': str(e)}
    
    def process_google_drive_link(self, google_drive_url, document_type, transaction_number, country_code):
        """Process Google Drive link."""
        try:
            return file_upload_manager.process_google_drive_link(google_drive_url, document_type, transaction_number, country_code)
        except Exception as e:
            print(f"ERROR in process_google_drive_link: {e}")
            return {'success': False, 'error': str(e)}
