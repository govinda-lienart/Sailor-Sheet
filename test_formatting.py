#!/usr/bin/env python3
"""
Test script to manually apply formatting to Google Sheets
Run this to fix lost formatting
"""

from sheets_manager import initialize_sheets, format_as_table
import os

def main():
    print("🔧 Fixing Google Sheets formatting...")
    
    try:
        # Initialize Google Sheets connection
        gc = initialize_sheets()
        
        # Get your sheet name from environment or use default
        sheet_name = os.environ.get('SHEET_NAME', 'Test_Sheet')
        
        # Open the sheet
        sheet = gc.open(sheet_name).sheet1
        
        print(f"📊 Working on sheet: {sheet_name}")
        
        # Apply formatting
        format_as_table(sheet)
        
        print("✅ Formatting applied successfully!")
        print("🔄 Please refresh your Google Sheets page to see the changes.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
