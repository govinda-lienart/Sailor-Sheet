
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

# Google Drive folder IDs for different file types
FOLDER_IDS = {
    'bills': "1UH-mqbvJ6k6Y0wDD4x7DcDRzsEjf0Rz0",           # Bills
    'redBills': "10gGkRi9P9417FjZ9vFeQTnpLA-ExbBVO",        # Red Bills
    'bankStatement': "1QDiSNjqzT2x99AGelRdQceg9l4q9iIrW",   # Bank Statement
    'documentation': "1ylG5_VDP020HaBXxy-o_A4QYuYiK9y8y"    # Documentation
}

# Default folder ID for backward compatibility
FOLDER_ID = FOLDER_IDS['bills']

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
def unique_name(base: str, ext: str, transaction_number: str = None, file_type: str = 'bills') -> str:
    """Generate a unique filename with transaction number and file type"""
    print(f"DEBUG: unique_name called with base={base}, ext={ext}, transaction_number={transaction_number}, file_type={file_type}")
    
    # Map file types to display names
    type_names = {
        'bills': 'bill',
        'redBills': 'red_bill', 
        'bankStatement': 'bank_statement',
        'documentation': 'doc'
    }
    
    type_name = type_names.get(file_type, 'bill')
    
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
def upload_file_to_drive(file, transaction_number=None, file_type='bills'):
    """
    Upload a file to Google Drive shared folder
    Args:
        file: File object to upload
        transaction_number: Optional transaction number to use in filename
        file_type: Type of file (bills, redBills, bankStatement, documentation)
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
        
        # Generate unique name with transaction number and file type
        base = filename.rsplit('.', 1)[0]
        ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = unique_name(base, ext, transaction_number, file_type)
        
        # Get the correct folder ID for this file type
        folder_id = FOLDER_IDS.get(file_type, FOLDER_ID)
        
        print(f"DEBUG: File upload - Original filename: {filename}")
        print(f"DEBUG: File upload - Transaction number: {transaction_number}")
        print(f"DEBUG: File upload - File type: {file_type}")
        print(f"DEBUG: File upload - Folder ID: {folder_id}")
        print(f"DEBUG: File upload - Generated filename: {unique_filename}")
        
        # Get credentials and build service
        creds = get_service_account_credentials()
        drive = build_drive_service(creds)
        
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
        
        # Upload the file
        media = MediaIoBaseUpload(
            io.BytesIO(file.read()),
            mimetype=file.content_type,
            resumable=True
        )
        
        file_metadata = {
            'name': unique_filename,
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

# =============================================================================
# WEB UPLOAD HANDLER
# =============================================================================

# Handle Web Upload Request
# -------------------------
def handle_web_upload(file, transaction_number=None, file_type='bills'):
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
        result = upload_file_to_drive(file, transaction_number, file_type)
        
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


