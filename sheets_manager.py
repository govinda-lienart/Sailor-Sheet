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
        
        # Format header row (row 1) with professional styling
        sheet.format('A1:D1', {
            'backgroundColor': {
                'red': 0.2,
                'green': 0.6,
                'blue': 0.2
            },
            'textFormat': {
                'bold': True,
                'fontSize': 12,
                'foregroundColor': {
                    'red': 1,
                    'green': 1,
                    'blue': 1
                }
            },
            'horizontalAlignment': 'CENTER',
            'verticalAlignment': 'MIDDLE',
            'borders': {
                'top': {'style': 'SOLID', 'color': {'red': 0.1, 'green': 0.5, 'blue': 0.1}},
                'bottom': {'style': 'SOLID', 'color': {'red': 0.1, 'green': 0.5, 'blue': 0.1}},
                'left': {'style': 'SOLID', 'color': {'red': 0.1, 'green': 0.5, 'blue': 0.1}},
                'right': {'style': 'SOLID', 'color': {'red': 0.1, 'green': 0.5, 'blue': 0.1}}
            }
        })
        
        # Format data rows with alternating colors for better readability
        if last_row > 1:
            data_range = f'A2:D{last_row}'
            
            # Apply alternating row colors
            for row_num in range(2, last_row + 1):
                if row_num % 2 == 0:  # Even rows
                    sheet.format(f'A{row_num}:D{row_num}', {
                        'backgroundColor': {
                            'red': 0.98,
                            'green': 0.98,
                            'blue': 0.98
                        }
                    })
                else:  # Odd rows
                    sheet.format(f'A{row_num}:D{row_num}', {
                        'backgroundColor': {
                            'red': 1,
                            'green': 1,
                            'blue': 1
                        }
                    })
                
                # Add borders to each row
                sheet.format(f'A{row_num}:D{row_num}', {
                    'borders': {
                        'bottom': {'style': 'SOLID', 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}}
                    }
                })
        
        # Add total row if there's data
        if last_row > 1:
            total_row = last_row + 1
            sheet.update(f'A{total_row}', 'TOTAL')
            sheet.update(f'B{total_row}', f'=SUM(B2:B{last_row})')
            sheet.update(f'C{total_row}', f'=COUNT(B2:B{last_row}) & " transactions"')
            
            # Format total row
            sheet.format(f'A{total_row}:D{total_row}', {
                'backgroundColor': {
                    'red': 0.9,
                    'green': 0.9,
                    'blue': 0.9
                },
                'textFormat': {
                    'bold': True,
                    'fontSize': 11
                },
                'borders': {
                    'top': {'style': 'DOUBLE', 'color': {'red': 0.2, 'green': 0.6, 'blue': 0.2}},
                    'bottom': {'style': 'SOLID', 'color': {'red': 0.2, 'green': 0.6, 'blue': 0.2}}
                }
            })
        
        # Auto-resize columns to fit content
        sheet.columns_auto_resize(0, 4)  # Resize columns A through D
        
        # Freeze the header row
        sheet.freeze(rows=1)
        
        print(f"✅ Table formatted successfully for range {range_name}")
        
    except Exception as e:
        print(f"⚠️ Warning: Could not format table: {str(e)}")
        # Don't raise exception - formatting is nice-to-have, not critical
