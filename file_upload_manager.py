# =============================================================================
# Created: 2025-09-03 16:09:02
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-03 15:20:50
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-02 21:17:10
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-02 12:20:13
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-02 12:18:54
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-02 11:05:49
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-02 10:43:56
# Status: ✅ WORKING - Ready for GitHub commit
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
# FILE UPLOAD MANAGER - Google Drive File Upload
# Purpose: Handle file uploads to Google Drive shared folder
# Version: 1.0.0 - Working Version
# Created: 2025-01-27 19:30:00
# Status: ✅ WORKING - Integrated from drive_test.py
# =============================================================================

# =============================================================================
# IMPORTS - Each library serves a specific purpose for file uploads
# =============================================================================

import os                                                 # Operating system functions (file paths, environment variables)
import json                                               # JSON data handling (for Google API credentials)
import io                                                 # Input/Output operations (for handling file data in memory)
from datetime import datetime                             # Date and time functions (for creating timestamped filenames)
from werkzeug.utils import secure_filename                # Flask utility to make filenames safe (prevents security issues)
from google.oauth2.service_account import Credentials     # Google authentication (for accessing Drive API)
from googleapiclient.discovery import build               # Google API client builder (creates Drive service)
from googleapiclient.http import MediaIoBaseUpload        # Google API file upload handler (uploads files to Drive)

# =============================================================================
# CONFIGURATION
# =============================================================================

# Shared Drive folder ID (Bills WebApp) - from your working test
FOLDER_ID = "1UH-mqbvJ6k6Y0wDD4x7DcDRzsEjf0Rz0"

# Scopes needed for Google Drive
SCOPES = ["https://www.googleapis.com/auth/drive"]

# Allowed file extensions for security
ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 
    'jpg', 'jpeg', 'png', 'gif', 'txt'
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

# Check Allowed File
# ------------------
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Generate Unique Name
# --------------------
def unique_name(base: str, ext: str, transaction_number: str = None) -> str:
    """Generate a unique filename with transaction number (like 'Bill_transactionnumber')"""
    print(f"DEBUG: unique_name called with base={base}, ext={ext}, transaction_number={transaction_number}")
    
    if transaction_number and transaction_number.strip():
        # Use transaction number if provided
        result = f"Bill_{transaction_number}.{ext}"
        print(f"DEBUG: Using transaction number, result: {result}")
        return result
    else:
        # Fallback to timestamp if no transaction number
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        result = f"Bill_{ts}.{ext}"
        print(f"DEBUG: No transaction number, using timestamp, result: {result}")
        return result

# Get Service Account Credentials
# -------------------------------
def get_service_account_credentials():
    """Get credentials using same method as main app"""
    # Check if credentials are in environment variable (production)
    google_credentials = os.environ.get('GOOGLE_CREDENTIALS')
    
    if google_credentials:
        # Use credentials from environment variable (production)
        try:
            credentials_dict = json.loads(google_credentials)
            credentials = Credentials.from_service_account_info(
                credentials_dict,
                scopes=SCOPES
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
                scopes=SCOPES
            )
            return credentials
        except FileNotFoundError:
            try:
                # Fall back to local file (development)
                credentials = Credentials.from_service_account_file(
                    'credentials.json',  # Local file path
                    scopes=SCOPES
                )
                return credentials
            except Exception as e:
                raise Exception(f"Error loading credentials.json file: {str(e)}")
        except Exception as e:
            raise Exception(f"Error loading secret credentials file: {str(e)}")

# Build Drive Service
# -------------------
def build_drive_service(creds):
    """Build Google Drive service"""
    return build("drive", "v3", credentials=creds)

# =============================================================================
# MAIN UPLOAD FUNCTIONS
# =============================================================================

# Upload File To Drive
# ---------------------
def upload_file_to_drive(file, transaction_number=None):
    """
    Upload a file to Google Drive shared folder
    Args:
        file: File object to upload
        transaction_number: Optional transaction number to use in filename
    Returns: dict with success status, file_url, and file_name
    """
    try:
        # Check if file is allowed
        if not allowed_file(file.filename):
            return {
                'success': False,
                'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }
        
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Generate unique name with transaction number
        base = filename.rsplit('.', 1)[0]
        ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = unique_name(base, ext, transaction_number)
        
        print(f"DEBUG: File upload - Original filename: {filename}")
        print(f"DEBUG: File upload - Transaction number: {transaction_number}")
        print(f"DEBUG: File upload - Generated filename: {unique_filename}")
        
        # Get credentials and build service
        creds = get_service_account_credentials()
        drive = build_drive_service(creds)
        
        # Check folder access first
        try:
            folder = drive.files().get(
                fileId=FOLDER_ID,
                supportsAllDrives=True,
                fields="id,name"
            ).execute()
        except Exception as e:
            return {
                'success': False,
                'error': f'Cannot access folder: {str(e)}'
            }
        
        # Upload the file
        media = MediaIoBaseUpload(
            io.BytesIO(file.read()),
            mimetype=file.content_type,
            resumable=True
        )
        
        file_metadata = {
            'name': unique_filename,
            'parents': [FOLDER_ID]
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

# =============================================================================
# WEB UPLOAD HANDLER
# =============================================================================

# Handle Web Upload Request
# -------------------------
def handle_web_upload(file, transaction_number=None):
    """
    Handle web upload request from Flask route
    Args:
        file: File object from Flask request
        transaction_number: Optional transaction number from form
    Returns: JSON response for web interface
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
        result = upload_file_to_drive(file, transaction_number)
        
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


