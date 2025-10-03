
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


# Upload File Content To Drive
# ----------------------------
def upload_file_content_to_drive(file_content, filename, document_type):
    """
    Upload file content (BytesIO) to Google Drive shared folder
    Args:
        file_content: BytesIO object with file content
        filename: Name for the uploaded file
        document_type: Type of document ('bill', 'redBill', 'documentation')
    Returns: dict with success status, file_url, and file_name
    """
    try:
        # Map document_type to file_type for folder selection
        document_type_mapping = {
            'bill': 'bills',
            'redBill': 'redBills',
            'documentation': 'documentation'
        }
        file_type = document_type_mapping.get(document_type, 'bills')
        
        # Get the correct folder ID for this file type
        folder_id = FOLDER_IDS.get(file_type, FOLDER_ID)
        
        print(f"DEBUG: Content upload - Filename: {filename}")
        print(f"DEBUG: Content upload - Document type: {document_type}")
        print(f"DEBUG: Content upload - File type: {file_type}")
        print(f"DEBUG: Content upload - Folder ID: {folder_id}")
        
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
        
        # Determine MIME type from filename extension
        import mimetypes
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        # Upload the file content
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


# =============================================================================
# GOOGLE DRIVE LINK PROCESSING
# =============================================================================

def process_google_drive_link(google_drive_url, document_type, transaction_number=None):
    """
    Process a Google Drive link by downloading the file and re-uploading it to the correct folder.
    Uses the same naming system as the main form.
    
    Args:
        google_drive_url: The Google Drive share URL
        document_type: The type of document ('bill', 'redBill', 'documentation')
        transaction_number: Optional transaction number for naming (from search results)
    
    Returns:
        dict: {'success': True/False, 'file_url': str, 'file_name': str, 'error': str}
    """
    try:
        print(f"DEBUG: Processing Google Drive link: {google_drive_url}")
        print(f"DEBUG: Document type: {document_type}")
        print(f"DEBUG: Transaction number: {transaction_number}")
        
        # Extract file ID from Google Drive URL
        file_id = extract_file_id_from_url(google_drive_url)
        if not file_id:
            return {'success': False, 'error': 'Invalid Google Drive URL format'}
        
        print(f"DEBUG: Extracted file ID: {file_id}")
        
        # Download file from Google Drive
        file_content, original_file_name = download_file_from_google_drive(file_id)
        if not file_content:
            return {'success': False, 'error': 'Failed to download file from Google Drive'}
        
        print(f"DEBUG: Downloaded file: {original_file_name}")
        print(f"DEBUG: File size: {len(file_content)} bytes")
        
        # Extract file extension from original filename
        if '.' in original_file_name:
            base = original_file_name.rsplit('.', 1)[0]
            ext = original_file_name.rsplit('.', 1)[1].lower()
        else:
            # If no extension in original name, try to detect from content
            base = original_file_name
            detected_ext = detect_file_type_from_content(file_content)
            if detected_ext and detected_ext in ALLOWED_EXTENSIONS:
                ext = detected_ext
                print(f"DEBUG: Detected extension from content: {ext}")
            else:
                ext = 'bin'  # Will be validated later
        
        # Validate file extension against allowed types
        if ext not in ALLOWED_EXTENSIONS:
            print(f"DEBUG: File extension '{ext}' not in allowed extensions: {ALLOWED_EXTENSIONS}")
            return {
                'success': False, 
                'error': f'File type .{ext} not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }
        
        # Map document_type to file_type for the unique_name function
        document_type_mapping = {
            'bill': 'bills',
            'redBill': 'redBills',
            'documentation': 'documentation'
        }
        file_type = document_type_mapping.get(document_type, 'bills')
        
        # Generate unique filename using the same naming system as main form
        unique_filename = unique_name(base, ext, transaction_number, file_type)
        print(f"DEBUG: Generated unique filename: {unique_filename}")
        
        # Create a file-like object from the downloaded content
        import io
        file_obj = io.BytesIO(file_content)
        
        # Upload to the correct folder using the existing upload function
        result = upload_file_content_to_drive(file_obj, unique_filename, document_type)
        
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


def extract_file_id_from_url(google_drive_url):
    """
    Extract file ID from various Google Drive URL formats.
    
    Args:
        google_drive_url: Google Drive share URL
    
    Returns:
        str: File ID or None if not found
    """
    import re
    
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


def download_file_from_google_drive(file_id):
    """
    Download file content from Google Drive using the file ID.
    
    Args:
        file_id: Google Drive file ID
    
    Returns:
        tuple: (file_content, file_name) or (None, None) if failed
    """
    try:
        import requests
        
        # Google Drive direct download URL
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        print(f"DEBUG: Downloading from URL: {download_url}")
        
        # Make request to download file
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        
        # Get file name from Content-Disposition header
        file_name = None
        if 'Content-Disposition' in response.headers:
            import re
            match = re.search(r'filename="([^"]+)"', response.headers['Content-Disposition'])
            if match:
                file_name = match.group(1)
        
        # If no filename in header, try to get file info from Google Drive API
        if not file_name:
            try:
                # Get credentials and build service to get file metadata
                creds = get_service_account_credentials()
                drive = build_drive_service(creds)
                
                # Get file metadata
                file_metadata = drive.files().get(
                    fileId=file_id,
                    fields="name,mimeType",
                    supportsAllDrives=True
                ).execute()
                
                file_name = file_metadata.get('name', '')
                mime_type = file_metadata.get('mimeType', '')
                
                print(f"DEBUG: Got file metadata - Name: {file_name}, MIME: {mime_type}")
                
                # If we have a name, use it; otherwise generate from MIME type
                if not file_name:
                    extension = get_extension_from_content_type(mime_type)
                    file_name = f"downloaded_file_{file_id[:8]}{extension}"
                elif '.' not in file_name and mime_type:
                    # If filename has no extension but we have MIME type, add it
                    extension = get_extension_from_content_type(mime_type)
                    if extension != '.bin':  # Only add extension if it's not the fallback
                        file_name = f"{file_name}{extension}"
                        
            except Exception as api_error:
                print(f"DEBUG: Could not get file metadata from API: {api_error}")
                # Fallback to content type detection
                content_type = response.headers.get('Content-Type', 'application/octet-stream')
                extension = get_extension_from_content_type(content_type)
                file_name = f"downloaded_file_{file_id[:8]}{extension}"
        
        print(f"DEBUG: Final file name: {file_name}")
        print(f"DEBUG: Content-Type: {response.headers.get('Content-Type')}")
        
        # Read file content
        file_content = response.content
        
        return file_content, file_name
        
    except Exception as e:
        print(f"DEBUG: Error downloading file: {e}")
        return None, None


def get_extension_from_content_type(content_type):
    """
    Get file extension from MIME content type.
    
    Args:
        content_type: MIME content type
    
    Returns:
        str: File extension with dot
    """
    mime_to_extension = {
        'application/pdf': '.pdf',
        'image/jpeg': '.jpg',
        'image/jpg': '.jpg',
        'image/png': '.png',
        'image/gif': '.gif',
        'image/bmp': '.bmp',
        'image/tiff': '.tiff',
        'image/webp': '.webp',
        'application/msword': '.doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        'application/vnd.ms-excel': '.xls',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
        'application/vnd.ms-powerpoint': '.ppt',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
        'text/plain': '.txt',
        'text/csv': '.csv',
        'application/zip': '.zip',
        'application/x-rar-compressed': '.rar',
        'application/x-7z-compressed': '.7z',
        'application/json': '.json',
        'application/xml': '.xml',
        'text/html': '.html',
        'text/css': '.css',
        'application/javascript': '.js',
        'application/octet-stream': '.bin',  # Keep as fallback but try to avoid
    }
    
    return mime_to_extension.get(content_type.lower(), '.bin')


def detect_file_type_from_content(file_content):
    """
    Detect file type from file content using magic bytes.
    
    Args:
        file_content: Bytes content of the file
    
    Returns:
        str: File extension without dot, or None if not detected
    """
    if not file_content:
        return None
    
    # Check magic bytes for common file types
    magic_signatures = {
        b'\x25\x50\x44\x46': 'pdf',  # PDF
        b'\x89\x50\x4E\x47': 'png',  # PNG
        b'\xFF\xD8\xFF': 'jpg',      # JPEG
        b'\x47\x49\x46\x38': 'gif',  # GIF
        b'\x50\x4B\x03\x04': 'docx', # DOCX/XLSX/PPTX (ZIP-based)
        b'\xD0\xCF\x11\xE0': 'doc',  # DOC/XLS/PPT (OLE2)
        b'\x50\x4B\x05\x06': 'zip',  # ZIP
        b'\x52\x61\x72\x21': 'rar',  # RAR
    }
    
    # Check first few bytes
    for signature, ext in magic_signatures.items():
        if file_content.startswith(signature):
            print(f"DEBUG: Detected file type from content: {ext}")
            return ext
    
    # Check for text files
    try:
        # Try to decode as text
        text_content = file_content[:1024].decode('utf-8', errors='ignore')
        if text_content.isprintable():
            print(f"DEBUG: Detected text file")
            return 'txt'
    except:
        pass
    
    print(f"DEBUG: Could not detect file type from content")
    return None


