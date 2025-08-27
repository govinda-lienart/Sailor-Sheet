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
        
        # Automatically format as table to maintain structure
        format_as_table(sheet)
        
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

def format_as_table(sheet):
    """
    Automatically format the data range as a proper table
    This maintains table structure even as new data is added
    """
    try:
        # Get all data to determine the range
        all_values = sheet.get_all_values()
        
        if len(all_values) < 2:  # Need at least header + 1 data row
            return
        
        # Calculate the range (A1:D{last_row})
        last_row = len(all_values)
        range_name = f'A1:D{last_row}'
        
        # Format as table using Google Sheets API
        # This creates a proper table with alternating row colors, borders, etc.
        sheet.format(range_name, {
            'backgroundColor': {
                'red': 0.98,
                'green': 0.98,
                'blue': 0.98
            },
            'horizontalAlignment': 'LEFT',
            'verticalAlignment': 'MIDDLE',
            'textFormat': {
                'bold': False,
                'fontSize': 10
            }
        })
        
        # Format header row (row 1) with bold text and different background
        sheet.format('A1:D1', {
            'backgroundColor': {
                'red': 0.2,
                'green': 0.4,
                'blue': 0.8
            },
            'textFormat': {
                'bold': True,
                'fontSize': 11,
                'foregroundColor': {
                    'red': 1,
                    'green': 1,
                    'blue': 1
                }
            },
            'horizontalAlignment': 'CENTER'
        })
        
        # Add borders to the table
        sheet.format(range_name, {
            'borders': {
                'top': {'style': 'SOLID'},
                'bottom': {'style': 'SOLID'},
                'left': {'style': 'SOLID'},
                'right': {'style': 'SOLID'}
            }
        })
        
        # Auto-resize columns to fit content
        sheet.columns_auto_resize(0, 4)  # Resize columns A through D
        
        print(f"✅ Table formatted successfully for range {range_name}")
        
    except Exception as e:
        print(f"⚠️ Warning: Could not format table: {str(e)}")
        # Don't raise exception - formatting is nice-to-have, not critical
