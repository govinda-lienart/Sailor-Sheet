#!/usr/bin/env python3
"""
Test script specifically for your Google Sheets credentials
This will help diagnose why you can't access your sheets
"""

import os
import json
from pathlib import Path

def test_your_credentials():
    """Test your specific Google Sheets credentials"""
    print("🔍 Testing Your Google Sheets Credentials...")
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
        print(f"📧 Service Account Email: {creds_dict.get('client_email')}")
        print(f"🏗️  Project ID: {creds_dict.get('project_id')}")
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
        
        # Try to get sheets
        print("\n📊 Attempting to get your sheets...")
        try:
            all_sheets = gc.openall()
            print(f"✅ Successfully retrieved {len(all_sheets)} sheets:")
            
            for i, sheet in enumerate(all_sheets[:10]):  # Show first 10
                print(f"   {i+1}. {sheet.title} (ID: {sheet.id})")
            
            if len(all_sheets) > 10:
                print(f"   ... and {len(all_sheets) - 10} more sheets")
                
            # Check if any sheets are shared with your service account
            print(f"\n🔍 Checking sheet permissions...")
            for sheet in all_sheets[:3]:  # Check first 3 sheets
                try:
                    # Try to access the sheet
                    worksheets = sheet.worksheets()
                    print(f"   ✅ '{sheet.title}': {len(worksheets)} worksheets accessible")
                except Exception as e:
                    print(f"   ❌ '{sheet.title}': Access denied - {e}")
                    
        except Exception as e:
            print(f"❌ Error getting sheets: {e}")
            print(f"Error type: {type(e).__name__}")
            
            # Check if it's a permission issue
            if "invalid_grant" in str(e):
                print("\n🔧 DIAGNOSIS: Invalid JWT Signature")
                print("This usually means:")
                print("1. The service account key is expired or corrupted")
                print("2. The service account was deleted or disabled")
                print("3. The project was deleted or access was revoked")
                print("\n💡 SOLUTION:")
                print("1. Go to Google Cloud Console")
                print("2. Check if your project 'my-project-51387-2022new' still exists")
                print("3. Check if service account 'ngo-accounting-app@my-project-51387-2022new.iam.gserviceaccount.com' still exists")
                print("4. Generate a new key for the service account")
                
            elif "access_denied" in str(e) or "forbidden" in str(e):
                print("\n🔧 DIAGNOSIS: Access Denied")
                print("The service account exists but doesn't have permission to access sheets")
                print("\n💡 SOLUTION:")
                print("1. Share your Google Sheets with the service account email:")
                print(f"   📧 {creds_dict.get('client_email')}")
                print("2. Give it 'Editor' or 'Viewer' permissions")
                
    except ImportError as e:
        print(f"❌ Missing required packages: {e}")
        print("Run: pip install gspread google-auth")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_your_credentials()
