#!/usr/bin/env python3
"""
Update Google Sheets Headers Script
This script helps update your Google Sheets to include the new Transaction Number column
"""

from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

def update_sheet_headers(gc, sheet_id, worksheet_title):
    """
    Update worksheet headers to include Transaction Number column (timestamp removed)
    """
    try:
        # Get the specific sheet and worksheet
        sheet = gc.open_by_key(sheet_id)
        worksheet = sheet.worksheet(worksheet_title)
        
        # New headers with Transaction Number column and Date column
        new_headers = [
            "Transaction Number",
            "Date",
            "Funds",
            "Cost Center",
            "Debit (VND)",
            "Credit (VND)",
            "Description",
            "Link Bill"
        ]
        
        # Update the first row (headers)
        worksheet.update('A1:H1', [new_headers])
        
        print(f"✅ Successfully updated headers for worksheet '{worksheet_title}'")
        print(f"   New structure: {new_headers}")
        print(f"   Note: Timestamp column has been removed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating headers: {e}")
        return False

def main():
    """
    Main function to update sheet headers
    """
    print("🔄 Google Sheets Header Update Tool")
    print("=" * 50)
    
    # You'll need to update these values
    SHEET_ID = "YOUR_SHEET_ID_HERE"  # Replace with your actual sheet ID
    WORKSHEET_TITLE = "YOUR_WORKSHEET_TITLE"  # Replace with your worksheet name
    
    print(f"📋 Sheet ID: {SHEET_ID}")
    print(f"📄 Worksheet: {WORKSHEET_TITLE}")
    print()
    
    # Initialize Google Sheets connection
    try:
        # You'll need to set up your credentials
        # This is just a template - you'll need to configure authentication
        print("⚠️  Note: You need to configure Google Sheets authentication first")
        print("   See your existing app.py for authentication setup")
        
        # Example of how to use (uncomment when ready):
        # update_sheet_headers(gc, SHEET_ID, WORKSHEET_TITLE)
        
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        print("   Please check your Google Sheets credentials setup")

if __name__ == "__main__":
    main()
