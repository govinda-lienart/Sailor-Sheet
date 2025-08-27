# =============================================================================
# SHEETS MANAGER - Google Sheets Operations
# Purpose: Handle all Google Sheets data operations
# Version: 1.0.0 - Working Version
# Created: 2025-01-27 19:30:00
# Status: ✅ WORKING - Clean operations only
# =============================================================================

from datetime import datetime

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
