# =============================================================================
# LIST FOLDERS - List all accessible folders in Shared Drive
# Purpose: Debug folder access issues
# Version: 1.0.0 - Test Version
# Created: 2025-01-27 19:30:00
# Status: 🔍 DEBUGGING - Folder access
# =============================================================================

import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Scopes needed for Google Drive and Sheets
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def load_credentials():
    """Load credentials using same method as main app"""
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
            print("✅ Credentials loaded from environment variable")
            return credentials
        except Exception as e:
            print(f"❌ ERROR parsing Google credentials from environment: {str(e)}")
            return False
    else:
        # Try to use secret file first, then fall back to local file
        try:
            # Try to read from secret file (production)
            credentials = Credentials.from_service_account_file(
                '/etc/secrets/credentials.json',  # Secret file path
                scopes=SCOPES
            )
            print("✅ Credentials loaded from secret file")
            return credentials
        except FileNotFoundError:
            try:
                # Fall back to local file (development)
                credentials = Credentials.from_service_account_file(
                    'credentials.json',  # Local file path
                    scopes=SCOPES
                )
                print("✅ Credentials loaded from local credentials.json file")
                return credentials
            except Exception as e:
                print(f"❌ ERROR loading credentials.json file: {str(e)}")
                return False
        except Exception as e:
            print(f"❌ ERROR loading secret credentials file: {str(e)}")
            return False

def list_all_folders():
    """List all accessible folders"""
    print("🚀 Listing all accessible folders...")
    print("=" * 50)
    
    # Load credentials
    credentials = load_credentials()
    if not credentials:
        print("❌ Cannot load credentials")
        return
    
    # Build Drive service
    try:
        service = build('drive', 'v3', credentials=credentials)
        print("✅ Successfully connected to Google Drive API")
    except Exception as e:
        print(f"❌ ERROR connecting to Drive API: {e}")
        return
    
    # List all Shared Drives
    print("\n🔍 Listing all accessible Shared Drives...")
    try:
        shared_drives = service.drives().list().execute()
        drives = shared_drives.get('drives', [])
        
        if drives:
            print(f"✅ Found {len(drives)} Shared Drive(s):")
            for drive in drives:
                print(f"   📁 {drive['name']} (ID: {drive['id']})")
                
                # List folders in this Shared Drive
                print(f"      📂 Folders in {drive['name']}:")
                try:
                    results = service.files().list(
                        q=f"'{drive['id']}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false",
                        fields="files(id,name,webViewLink)",
                        supportsAllDrives=True,
                        includeItemsFromAllDrives=True
                    ).execute()
                    
                    folders = results.get('files', [])
                    if folders:
                        for folder in folders:
                            print(f"         - {folder['name']} (ID: {folder['id']})")
                    else:
                        print("         (No folders found)")
                        
                except Exception as e:
                    print(f"         ❌ Error listing folders: {e}")
                print()
        else:
            print("❌ No Shared Drives found!")
    except Exception as e:
        print(f"❌ ERROR listing Shared Drives: {e}")
    
    # Also list folders in My Drive
    print("\n🔍 Listing folders in My Drive...")
    try:
        results = service.files().list(
            q="mimeType='application/vnd.google-apps.folder' and trashed=false",
            fields="files(id,name,webViewLink)"
        ).execute()
        
        folders = results.get('files', [])
        if folders:
            print(f"✅ Found {len(folders)} folder(s) in My Drive:")
            for folder in folders:
                print(f"   📁 {folder['name']} (ID: {folder['id']})")
        else:
            print("❌ No folders found in My Drive")
            
    except Exception as e:
        print(f"❌ ERROR listing My Drive folders: {e}")

if __name__ == "__main__":
    list_all_folders()
