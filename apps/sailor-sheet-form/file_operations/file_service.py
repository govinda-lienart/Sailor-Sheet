"""
File Service
Main interface for file operations. Coordinates other services to handle file uploads,
Google Drive link processing, and file management.
"""

import io
from werkzeug.utils import secure_filename
from .google_drive_service import GoogleDriveService
from .file_validation_service import FileValidationService
from .file_naming_service import FileNamingService


class FileService:
    """Main service for file operations."""
    
    def __init__(self):
        self.google_drive = GoogleDriveService()
        self.validation = FileValidationService()
        self.naming = FileNamingService()
    
    def upload_file(self, file, transaction_number: str = None, file_type: str = 'bills', country_code: str = None) -> dict:
        """
        Upload a file to Google Drive shared folder.
        
        Args:
            file: File object to upload
            transaction_number: Optional transaction number to use in filename
            file_type: Type of file (bills, redBills, bankStatement, documentation)
            country_code: Country code ('BE' or 'VN') for folder selection
            
        Returns:
            dict: Upload result with success status, file_url, and file_name
        """
        try:
            print(f"DEBUG: File upload - Original filename: {file.filename}")
            print(f"DEBUG: File upload - Transaction number: {transaction_number}")
            print(f"DEBUG: File upload - File type: {file_type}")
            
            # Check if file is allowed
            if not self.validation.is_allowed_file(file.filename):
                return {
                    'success': False,
                    'error': f'File type not allowed. Allowed types: {", ".join(self.validation.allowed_extensions)}'
                }
            
            # Secure the filename
            filename = secure_filename(file.filename)
            
            # Generate unique name with transaction number and file type
            base, ext = self.naming.extract_base_and_extension(filename)
            unique_filename = self.naming.generate_unique_name(base, ext, transaction_number, file_type)
            
            # Get the correct folder ID for this file type and country
            folder_id = self.google_drive.get_folder_id(file_type, country_code)
            print(f"DEBUG: File upload - Folder ID: {folder_id}")
            print(f"DEBUG: File upload - Generated filename: {unique_filename}")
            
            # Upload the file
            result = self.google_drive.upload_file_to_drive(
                io.BytesIO(file.read()),
                unique_filename,
                folder_id,
                file.content_type
            )
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Upload failed: {str(e)}'
            }
    
    def upload_file_content(self, file_content, filename: str, document_type: str, country_code: str = None) -> dict:
        """
        Upload file content (BytesIO) to Google Drive shared folder.
        
        Args:
            file_content: BytesIO object with file content
            filename: Name for the uploaded file
            document_type: Type of document ('bill', 'redBill', 'documentation', 'bankStatement')
            country_code: Country code ('BE' or 'VN') for folder selection
            
        Returns:
            dict: Upload result with success status, file_url, and file_name
        """
        try:
            # Map document_type to file_type for folder selection
            document_type_mapping = {
                'bill': 'bills',
                'redBill': 'redBills',
                'bankStatement': 'bankStatement',
                'documentation': 'documentation'
            }
            file_type = document_type_mapping.get(document_type, 'bills')
            
            # Get the correct folder ID for this file type and country
            folder_id = self.google_drive.get_folder_id(file_type, country_code)
            
            print(f"DEBUG: Content upload - Filename: {filename}")
            print(f"DEBUG: Content upload - Document type: {document_type}")
            print(f"DEBUG: Content upload - File type: {file_type}")
            print(f"DEBUG: Content upload - Folder ID: {folder_id}")
            
            # Upload the file content
            result = self.google_drive.upload_file_to_drive(
                file_content,
                filename,
                folder_id
            )
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Upload failed: {str(e)}'
            }
    
    def process_google_drive_link(self, google_drive_url: str, document_type: str, transaction_number: str = None, country_code: str = None) -> dict:
        """
        Process a Google Drive link by downloading the file and re-uploading it to the correct folder.
        Uses the same naming system as the main form.
        
        Args:
            google_drive_url: The Google Drive share URL
            document_type: The type of document ('bill', 'redBill', 'bankStatement', 'documentation')
            transaction_number: Optional transaction number for naming (from search results)
            country_code: Country code for folder selection (BE or VN)
        
        Returns:
            dict: Processing result with success status, file_url, and file_name
        """
        try:
            print(f"DEBUG: Processing Google Drive link: {google_drive_url}")
            print(f"DEBUG: Document type: {document_type}")
            print(f"DEBUG: Transaction number: {transaction_number}")
            
            # Extract file ID from Google Drive URL
            file_id = self.google_drive.extract_file_id_from_url(google_drive_url)
            if not file_id:
                return {'success': False, 'error': 'Invalid Google Drive URL format'}
            
            print(f"DEBUG: Extracted file ID: {file_id}")
            
            # Download file from Google Drive
            file_content, original_file_name = self.google_drive.download_file_from_drive(file_id)
            if not file_content:
                return {'success': False, 'error': 'Failed to download file from Google Drive'}
            
            print(f"DEBUG: Downloaded file: {original_file_name}")
            print(f"DEBUG: File size: {len(file_content)} bytes")
            
            # Extract file extension from original filename
            if '.' in original_file_name:
                base, ext = self.naming.extract_base_and_extension(original_file_name)
            else:
                # If no extension in original name, try to detect from content
                base = original_file_name
                detected_ext = self.validation.detect_file_type_from_content(file_content)
                if detected_ext and detected_ext in self.validation.allowed_extensions:
                    ext = detected_ext
                    print(f"DEBUG: Detected extension from content: {ext}")
                else:
                    ext = 'bin'  # Will be validated later
            
            # Validate file extension against allowed types
            if ext not in self.validation.allowed_extensions:
                print(f"DEBUG: File extension '{ext}' not in allowed extensions: {self.validation.allowed_extensions}")
                return {
                    'success': False, 
                    'error': f'File type .{ext} not allowed. Allowed types: {", ".join(self.validation.allowed_extensions)}'
                }
            
            # Map document_type to file_type for the unique_name function
            document_type_mapping = {
                'bill': 'bills',
                'redBill': 'redBills',
                'bankStatement': 'bankStatement',
                'documentation': 'documentation'
            }
            file_type = document_type_mapping.get(document_type, 'bills')
            
            # Generate unique filename using the same naming system as main form
            unique_filename = self.naming.generate_unique_name(base, ext, transaction_number, file_type)
            print(f"DEBUG: Generated unique filename: {unique_filename}")
            print(f"DEBUG: Country code for upload: {country_code}")
            
            # Create a file-like object from the downloaded content
            file_obj = io.BytesIO(file_content)
            
            # Upload to the correct folder using the existing upload function with country code
            result = self.upload_file_content(file_obj, unique_filename, document_type, country_code)
            
            if result['success']:
                print(f"DEBUG: File successfully uploaded to {document_type} folder with name: {unique_filename}")
                return {
                    'success': True,
                    'file_url': result['file_url'],
                    'file_name': unique_filename,  # Use the generated unique name
                    'message': f'File downloaded and uploaded to {document_type} folder successfully'
                }
            else:
                return {'success': False, 'error': result['error']}
                
        except Exception as e:
            print(f"DEBUG: Error in process_google_drive_link: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def handle_web_upload(self, file, transaction_number: str = None, file_type: str = 'bills', country_code: str = None) -> dict:
        """
        Handle web upload request from Flask route.
        
        Args:
            file: File object from Flask request
            transaction_number: Optional transaction number from form
            file_type: Type of file (bills, redBills, bankStatement, documentation)
            country_code: Country code ('BE' or 'VN') for folder selection
            
        Returns:
            dict: JSON response for web interface
        """
        try:
            print("DEBUG: handle_web_upload called")
            print(f"DEBUG: File received: {file.filename if file else 'None'}")
            print(f"DEBUG: Transaction number received: '{transaction_number}'")
            
            if not file or not file.filename:
                print("DEBUG: No file in request")
                return {'success': False, 'error': 'No file selected'}
            
            print(f"DEBUG: Uploading file: {file.filename}")
            print(f"DEBUG: Transaction number: {transaction_number}")
            
            # Upload file to Drive
            result = self.upload_file(file, transaction_number, file_type, country_code)
            
            if result['success']:
                print(f"DEBUG: File uploaded successfully: {result}")
                return {
                    'success': True,
                    'file_name': result['file_name'],
                    'file_url': result['file_url'],
                    'file_id': result['file_id']
                }
            else:
                print(f"DEBUG: File upload failed: {result['error']}")
                return {'success': False, 'error': result['error']}
                
        except Exception as e:
            print(f"DEBUG: Error in handle_web_upload: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
