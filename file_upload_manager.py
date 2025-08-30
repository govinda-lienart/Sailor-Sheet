# =============================================================================
# FILE UPLOAD MANAGER - Google Drive File Upload
# Purpose: Handle file uploads to Google Drive shared folder
# Version: 1.0.0 - Working Version
# Created: 2025-01-27 19:30:00
# Status: ✅ WORKING - Integrated from drive_test.py
# =============================================================================

import os
import json
import io
from datetime import datetime
from werkzeug.utils import secure_filename
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaFileUpload

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

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def unique_name(base: str, ext: str) -> str:
    """Generate a unique filename with timestamp"""
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{base}_{ts}.{ext}"

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

def build_drive_service(creds):
    """Build Google Drive service"""
    return build("drive", "v3", credentials=creds)

# =============================================================================
# MAIN UPLOAD FUNCTIONS
# =============================================================================

def upload_file_to_drive(file):
    """
    Upload a file to Google Drive shared folder
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
        
        # Generate unique name
        base = filename.rsplit('.', 1)[0]
        ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = unique_name(base, ext)
        
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

def list_folder_files():
    """List all files in the shared drive folder"""
    try:
        creds = get_service_account_credentials()
        drive = build_drive_service(creds)
        
        res = drive.files().list(
            q=f"'{FOLDER_ID}' in parents and trashed=false",
            fields="files(id,name,webViewLink,createdTime)",
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            corpora="allDrives",
            orderBy="createdTime desc"
        ).execute()
        
        return res.get("files", [])
        
    except Exception as e:
        raise Exception(f"Error listing files: {str(e)}")
