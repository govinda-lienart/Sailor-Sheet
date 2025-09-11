#!/usr/bin/env python3
"""
Test script to specifically access your TMWC Vietnam Accounting sheet
This will help determine if the issue is with credentials or sheet access
"""

import os
import json
from pathlib import Path

def test_specific_sheet():
    """Test access to your specific Google Sheet"""
    print("🔍 Testing Access to Your Specific Google Sheet...")
    print("=" * 60)
    
    # Load .env file from project root
    env_path = Path(__file__).parent.parent.parent / '.env'
    print(f"📁 Loading .env from: {env_path}")
    
    if env_path.exists():
        from dotenv import load_dotenv
        load_dotenv(env_path)
        print("✅ .env file loaded successfully")
    else:
        print("❌ .env file not found")
        return
    
    # Get your credentials
    google_creds = os.environ.get('GOOGLE_CREDENTIALS')
    if not google_creds:
        print("❌ GOOGLE_CREDENTIALS not found in environment")
        return
    
    try:
        creds_dict = json.loads(google_creds)
        print("✅ Credentials JSON is valid")
        print(f"📧 Service Account: {creds_dict.get('client_email')}")
    except Exception as e:
        print(f"❌ Invalid JSON in credentials: {e}")
        return
    
    # Test Google Sheets connection
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        print("\n🔗 Testing Google Sheets Connection...")
        print("-" * 40)
        
        # Create credentials object
        credentials = Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        # Authorize
        gc = gspread.authorize(credentials)
        print("✅ Successfully authorized with Google Sheets API")
        
        # Test 1: Try to get all sheets (this was failing before)
        print("\n📊 Test 1: Getting all sheets...")
        try:
            all_sheets = gc.openall()
            print(f"✅ Successfully retrieved {len(all_sheets)} sheets")
            
            # Look for your specific sheet
            target_sheet = None
            for sheet in all_sheets:
                if "TMWC" in sheet.title or "Vietnam" in sheet.title or "Accounting" in sheet.title:
                    target_sheet = sheet
                    print(f"🎯 Found target sheet: '{sheet.title}' (ID: {sheet.id})")
                    break
            
            if not target_sheet:
                print("⚠️  Target sheet not found in openall() results")
                print("Available sheets:")
                for i, sheet in enumerate(all_sheets[:5]):
                    print(f"   {i+1}. {sheet.title}")
                    
        except Exception as e:
            print(f"❌ Error getting all sheets: {e}")
            print("This confirms the JWT signature issue")
        
        # Test 2: Try to access your specific sheet directly by ID
        print("\n📊 Test 2: Accessing sheet directly by ID...")
        sheet_id = "1Fvrld1X0OioH7AbKCiSIMNac5U9OvlKJh0OSk02bTTI"
        
        try:
            # Try to open the sheet directly
            sheet = gc.open_by_key(sheet_id)
            print(f"✅ Successfully opened sheet: '{sheet.title}'")
            
            # Get worksheets
            worksheets = sheet.worksheets()
            print(f"✅ Found {len(worksheets)} worksheets:")
            
            for i, ws in enumerate(worksheets):
                print(f"   {i+1}. '{ws.title}' (ID: {ws.id})")
                
            # Try to read some data from the first worksheet
            if worksheets:
                first_ws = worksheets[0]
                print(f"\n📖 Test 3: Reading data from '{first_ws.title}'...")
                
                try:
                    # Get first few rows
                    data = first_ws.get_all_values()
                    print(f"✅ Successfully read {len(data)} rows")
                    
                    if data:
                        print("📋 First few rows:")
                        for i, row in enumerate(data[:3]):  # Show first 3 rows
                            print(f"   Row {i+1}: {row[:5]}...")  # Show first 5 columns
                            
                        # Check if this looks like your accounting data
                        if len(data) > 1:
                            headers = data[0]
                            print(f"\n📊 Headers found: {headers[:5]}...")
                            
                            if any("Transaction" in str(h) for h in headers):
                                print("✅ This looks like your accounting data!")
                            else:
                                print("⚠️  Headers don't match expected accounting format")
                    
                except Exception as e:
                    print(f"❌ Error reading worksheet data: {e}")
                    
        except Exception as e:
            print(f"❌ Error accessing sheet by ID: {e}")
            print(f"Error type: {type(e).__name__}")
            
            if "invalid_grant" in str(e):
                print("\n🔧 CONFIRMED: Invalid JWT Signature")
                print("The service account credentials are definitely corrupted/expired")
            elif "not found" in str(e) or "404" in str(e):
                print("\n🔧 CONFIRMED: Sheet not found or no access")
                print("The service account doesn't have access to this sheet")
            elif "forbidden" in str(e) or "403" in str(e):
                print("\n🔧 CONFIRMED: Access denied")
                print("The service account doesn't have permission to access this sheet")
                
    except ImportError as e:
        print(f"❌ Missing required packages: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_specific_sheet()
