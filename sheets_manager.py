# =============================================================================
# GOOGLE SHEETS MANAGER
# Purpose: Handle all Google Sheets operations
# =============================================================================

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import json

# =============================================================================
# GOOGLE SHEETS SETUP
# =============================================================================

# Define API permissions (scopes) - what our app can do
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',  # Read/write Google Sheets
    'https://www.googleapis.com/auth/drive'          # Access Google Drive
]

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

# =============================================================================
# DATA OPERATIONS
# =============================================================================

def add_transaction(gc, sheet_name, name, amount, description):
    """
    Add a new transaction to Google Sheets
    """
    try:
        # Open the Google Sheet
        sheet = gc.open(sheet_name).sheet1
        
        # Create timestamp for when data was submitted
        timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        
        # Convert amount to number (not string)
        try:
            numeric_amount = float(amount)
        except ValueError:
            raise Exception(f"Invalid amount: {amount}. Please enter a valid number.")
        
        # Prepare data row: [Name, Amount (as number), Description, Timestamp]
        row = [name, numeric_amount, description, timestamp]
        
        # Add the new row to the Google Sheet
        sheet.append_row(row)
        
        # No totals - user will handle manually
        
        return sheet
        
    except Exception as e:
        raise Exception(f"Error adding transaction: {str(e)}")

def get_sheet_data(gc, sheet_name):
    """
    Get all data from Google Sheet
    """
    try:
        sheet = gc.open(sheet_name).sheet1
        return sheet
    except Exception as e:
        raise Exception(f"Error getting sheet data: {str(e)}")

# Total calculator removed - user will handle manually
