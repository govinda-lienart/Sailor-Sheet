"""
Google Drive Service
Handles all Google Drive API operations including uploads, downloads, and link processing.
"""

import os
import json
import io
import re
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


class GoogleDriveService:
    """Service for Google Drive operations."""
    
    def __init__(self):
        # Google Drive folder IDs for different file types
        self.folder_ids = {
            'bills': "1UH-mqbvJ6k6Y0wDD4x7DcDRzsEjf0Rz0",           # Bills
            'redBills': "10gGkRi9P9417FjZ9vFeQTnpLA-ExbBVO",        # Red Bills
            'bankStatement': "1QDiSNjqzT2x99AGelRdQceg9l4q9iIrW",   # Bank Statement
            'documentation': "1ylG5_VDP020HaBXxy-o_A4QYuYiK9y8y"    # Documentation
        }
        
        # Default folder ID for backward compatibility
        self.default_folder_id = self.folder_ids['bills']
        
        # Scopes needed for Google Drive
        self.scopes = ["https://www.googleapis.com/auth/drive"]
    
    def get_service_account_credentials(self):
        """Get credentials using same method as main app."""
        # Check if credentials are in environment variable (production)
        google_credentials = os.environ.get('GOOGLE_CREDENTIALS')
        
        if google_credentials:
            # Use credentials from environment variable (production)
            try:
                credentials_dict = json.loads(google_credentials)
                credentials = Credentials.from_service_account_info(
                    credentials_dict,
                    scopes=self.scopes
                )
                return credentials
            except Exception as e:
                raise Exception(f"Error parsing Google credentials from environment: {str(e)}")
        else:
            # Try to use secret file first, then fall back to local file
            try:
                # Try to read from secret file (production)
                credentials = Credentials.from_service_account_file(
                    '/etc/secrets/credentials.json',  # Secret file path
                    scopes=self.scopes
                )
                return credentials
            except FileNotFoundError:
                try:
                    # Fall back to local file (development)
                    credentials = Credentials.from_service_account_file(
                        'credentials.json',  # Local file path
                        scopes=self.scopes
                    )
                    return credentials
                except Exception as e:
                    raise Exception(f"Error loading credentials.json file: {str(e)}")
            except Exception as e:
                raise Exception(f"Error loading secret credentials file: {str(e)}")
    
    def build_drive_service(self, creds):
        """Build Google Drive service."""
        return build("drive", "v3", credentials=creds)
    
    def get_folder_id(self, file_type: str, country_code: str = None) -> str:
        """
        Get the correct folder ID for this file type and country.
        
        Args:
            file_type: Type of file (bills, redBills, bankStatement, documentation)
            country_code: Country code ('BE' or 'VN') for folder selection
            
        Returns:
            str: Folder ID
        """
        if country_code:
            # Load country-specific folder IDs
            try:
                with open('data/countries.json', 'r') as f:
                    countries_data = json.load(f)
                
                country_folders = countries_data['countries'].get(country_code, {}).get('folders', {})
                folder_id = country_folders.get(file_type, self.folder_ids.get(file_type, self.default_folder_id))
                print(f"DEBUG: Using country-specific folder for {country_code}: {folder_id}")
                return folder_id
            except Exception as e:
                print(f"DEBUG: Error loading country folders, using default: {e}")
                return self.folder_ids.get(file_type, self.default_folder_id)
        else:
            # Use default folder IDs
            folder_id = self.folder_ids.get(file_type, self.default_folder_id)
            print(f"DEBUG: No country code provided, using default folder: {folder_id}")
            return folder_id
    
    def upload_file_to_drive(self, file_content, filename: str, folder_id: str, mime_type: str = None) -> dict:
        """
        Upload file content to Google Drive.
        
        Args:
            file_content: File content (BytesIO or bytes)
            filename: Name for the uploaded file
            folder_id: Google Drive folder ID
            mime_type: MIME type of the file
            
        Returns:
            dict: Upload result with success status, file_url, and file_name
        """
        try:
            # Get credentials and build service
            creds = self.get_service_account_credentials()
            drive = self.build_drive_service(creds)
            
            # Check folder access first
            try:
                folder = drive.files().get(
                    fileId=folder_id,
                    supportsAllDrives=True,
                    fields="id,name"
                ).execute()
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Cannot access folder: {str(e)}'
                }
            
            # Determine MIME type if not provided
            if not mime_type:
                import mimetypes
                mime_type, _ = mimetypes.guess_type(filename)
                if not mime_type:
                    mime_type = 'application/octet-stream'
            
            # Upload the file
            media = MediaIoBaseUpload(
                file_content,
                mimetype=mime_type,
                resumable=True
            )
            
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            
            uploaded_file = drive.files().create(
                body=file_metadata,
                media_body=media,
                fields="id,name,webViewLink",
                supportsAllDrives=True
            ).execute()
            
            return {
                'success': True,
                'file_url': uploaded_file['webViewLink'],
                'file_name': uploaded_file['name'],
                'file_id': uploaded_file['id']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Upload failed: {str(e)}'
            }
    
    def download_file_from_drive(self, file_id: str) -> tuple:
        """
        Download file content from Google Drive using the Google Drive API.
        
        Args:
            file_id: Google Drive file ID
            
        Returns:
            tuple: (file_content, file_name) or (None, None) if failed
        """
        try:
            print(f"DEBUG: Downloading file using Google Drive API for file ID: {file_id}")
            
            # Get credentials and build service
            creds = self.get_service_account_credentials()
            drive = self.build_drive_service(creds)
            
            # First, get file metadata to get the filename and MIME type
            print("DEBUG: Getting file metadata...")
            try:
                file_metadata = drive.files().get(
                    fileId=file_id,
                    fields="name,mimeType",
                    supportsAllDrives=True
                ).execute()
            except Exception as metadata_error:
                error_msg = str(metadata_error)
                if '404' in error_msg or 'not found' in error_msg.lower():
                    raise Exception(
                        f"❌ Google Drive file not found!\n\n"
                        f"This could mean:\n"
                        f"1. The file was deleted or moved\n"
                        f"2. The sharing link is incorrect\n"
                        f"3. Your service account doesn't have permission\n\n"
                        f"📋 To fix:\n"
                        f"1. Share the file with: machine@my-project-sailor-sheet-16754.iam.gserviceaccount.com\n"
                        f"   OR\n"
                        f"2. Set sharing to 'Anyone with the link can view'\n\n"
                        f"File ID: {file_id}"
                    )
                else:
                    raise Exception(f"Failed to get file metadata: {error_msg}")
            
            file_name = file_metadata.get('name', 'unknown_file')
            mime_type = file_metadata.get('mimeType', 'unknown')
            
            print(f"DEBUG: File metadata - Name: {file_name}, MIME: {mime_type}")
            
            # Method 1: Try get_media (for regular files)
            try:
                print("DEBUG: Trying get_media method...")
                request = drive.files().get_media(
                    fileId=file_id,
                    supportsAllDrives=True
                )
                file_content = request.execute()
                
                print(f"DEBUG: API download successful! Content length: {len(file_content)} bytes")
                
                # Check if it's binary data or HTML (error page)
                if file_content.startswith(b'<html') or file_content.startswith(b'<!DOCTYPE'):
                    print("DEBUG: WARNING - API returned HTML content, trying export method...")
                    raise Exception("HTML content returned")
                else:
                    print("DEBUG: API returned binary data (good!)")
                    return file_content, file_name
                    
            except Exception as get_media_error:
                print(f"DEBUG: get_media failed: {get_media_error}")
                
                # Method 2: Try export (for Google Docs/Sheets/Slides)
                if 'google-apps' in mime_type:
                    print("DEBUG: Trying export method for Google Workspace file...")
                    try:
                        # Export as PDF for Google Docs/Sheets
                        export_mime = 'application/pdf'
                        request = drive.files().export_media(
                            fileId=file_id,
                            mimeType=export_mime
                        )
                        file_content = request.execute()
                        
                        print(f"DEBUG: Export successful! Content length: {len(file_content)} bytes")
                        
                        # Update filename to have .pdf extension
                        if not file_name.endswith('.pdf'):
                            file_name = f"{file_name}.pdf"
                        
                        print(f"DEBUG: Export filename: {file_name}")
                        return file_content, file_name
                        
                    except Exception as export_error:
                        print(f"DEBUG: Export also failed: {export_error}")
                        return None, None
                else:
                    print(f"DEBUG: Not a Google Workspace file, cannot use export")
                    return None, None
            
        except Exception as e:
            print(f"DEBUG: Error downloading file from Google Drive API: {e}")
            import traceback
            traceback.print_exc()
            return None, None
    
    def extract_file_id_from_url(self, google_drive_url: str) -> str:
        """
        Extract file ID from various Google Drive URL formats.
        
        Args:
            google_drive_url: Google Drive share URL
            
        Returns:
            str: File ID or None if not found
        """
        # Common Google Drive URL patterns
        patterns = [
            r'drive\.google\.com/file/d/([a-zA-Z0-9-_]+)',
            r'drive\.google\.com/open\?id=([a-zA-Z0-9-_]+)',
            r'docs\.google\.com/document/d/([a-zA-Z0-9-_]+)',
            r'docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, google_drive_url)
            if match:
                return match.group(1)
        
        return None

