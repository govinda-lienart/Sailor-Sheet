# =============================================================================
# Created: 2025-09-04 14:23:56
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-04 14:01:24
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-04 04:52:11
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-04 04:50:11
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-04 04:49:54
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-04 04:26:36
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-03 22:51:02
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-03 19:28:04
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-03 19:13:13
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-03 16:09:02
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-03 15:20:50
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-03 11:28:57
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-03 11:27:32
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
# CONFIG.PY - Google Sheets Configuration
# Purpose: Handle all authentication and configuration
# Version: 1.0.0 - Working Version
# Created: 2025-01-27 19:30:00
# Status: ✅ WORKING - Clean configuration management
# =============================================================================

import gspread
from google.oauth2.service_account import Credentials
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# GOOGLE SHEETS SETUP
# =============================================================================

# Define API permissions (scopes) - what our app can do
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',  # Read/write Google Sheets
    'https://www.googleapis.com/auth/drive'          # Access Google Drive
]

# Initialize Sheets Connection
# ---------------------------
def initialize_sheets():
    """
    Initialize Google Sheets connection
    Returns: gspread client
    """
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
        except FileNotFoundError:
            try:
                # Fall back to local file (development)
                credentials = Credentials.from_service_account_file(
                    'credentials.json',  # Local file path
                    scopes=SCOPES
                )
            except Exception as e:
                raise Exception(f"Error loading credentials.json file: {str(e)}")
        except Exception as e:
            raise Exception(f"Error loading secret credentials file: {str(e)}")
    
    # Authorize our app to use Google Sheets
    return gspread.authorize(credentials)
