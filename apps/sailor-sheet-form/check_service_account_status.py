#!/usr/bin/env python3
"""
Script to check the status of your Google Service Account credentials
This will help determine if the account is active, expired, or has other issues
"""

import os
import json
from pathlib import Path
from datetime import datetime

def check_service_account_status():
    """Check the status and validity of your service account credentials"""
    print("🔍 Checking Service Account Status...")
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
    except Exception as e:
        print(f"❌ Invalid JSON in credentials: {e}")
        return
    
    # Extract credential information
    print("\n📋 Service Account Information:")
    print("-" * 40)
    print(f"📧 Email: {creds_dict.get('client_email')}")
    print(f"🏗️  Project ID: {creds_dict.get('project_id')}")
    print(f"🔑 Private Key ID: {creds_dict.get('private_key_id')}")
    print(f"🆔 Client ID: {creds_dict.get('client_id')}")
    
    # Check private key format
    private_key = creds_dict.get('private_key', '')
    if private_key:
        if private_key.startswith('-----BEGIN PRIVATE KEY-----'):
            print("✅ Private key format looks correct")
        else:
            print("❌ Private key format is incorrect")
        
        # Check if private key is properly formatted
        if '\\n' in private_key:
            print("⚠️  Private key contains escaped newlines (\\n) - this might be the issue!")
            print("   The key should have actual newlines, not \\n characters")
        else:
            print("✅ Private key newlines look correct")
    
    # Test different authentication methods
    print("\n🔗 Testing Authentication Methods...")
    print("-" * 40)
    
    try:
        from google.oauth2.service_account import Credentials
        from google.auth.transport.requests import Request
        import google.auth.exceptions
        
        # Method 1: Create credentials object
        print("🔄 Method 1: Creating credentials object...")
        try:
            credentials = Credentials.from_service_account_info(
                creds_dict,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            print("✅ Credentials object created successfully")
        except Exception as e:
            print(f"❌ Failed to create credentials object: {e}")
            return
        
        # Method 2: Test token refresh
        print("🔄 Method 2: Testing token refresh...")
        try:
            # Force a token refresh
            credentials.refresh(Request())
            print("✅ Token refresh successful")
            print(f"📅 Token expires at: {credentials.expiry}")
            
            if credentials.expiry:
                now = datetime.now(credentials.expiry.tzinfo)
                if credentials.expiry > now:
                    print("✅ Token is still valid")
                else:
                    print("❌ Token has expired")
                    
        except Exception as e:
            print(f"❌ Token refresh failed: {e}")
            print(f"Error type: {type(e).__name__}")
            
            # Analyze the specific error
            if "invalid_grant" in str(e):
                print("\n🔧 DIAGNOSIS: Invalid Grant Error")
                print("This typically means:")
                print("1. The private key is corrupted or malformed")
                print("2. The service account was deleted or disabled")
                print("3. The key was revoked or expired")
                print("4. The project was deleted or access was revoked")
                
            elif "invalid_scope" in str(e):
                print("\n🔧 DIAGNOSIS: Invalid Scope Error")
                print("The requested scopes are not valid for this service account")
                
            elif "unauthorized_client" in str(e):
                print("\n🔧 DIAGNOSIS: Unauthorized Client Error")
                print("The service account is not authorized to use this API")
        
        # Method 3: Test with gspread
        print("\n🔄 Method 3: Testing with gspread...")
        try:
            import gspread
            gc = gspread.authorize(credentials)
            print("✅ gspread authorization successful")
            
            # Try a simple operation
            print("🔄 Testing simple operation...")
            try:
                # This should work even if we can't access specific sheets
                all_sheets = gc.openall()
                print(f"✅ Successfully retrieved {len(all_sheets)} sheets")
            except Exception as e:
                print(f"❌ Failed to retrieve sheets: {e}")
                
        except Exception as e:
            print(f"❌ gspread authorization failed: {e}")
    
    except ImportError as e:
        print(f"❌ Missing required packages: {e}")
        print("Run: pip install google-auth google-auth-oauthlib gspread")
    
    # Additional checks
    print("\n🔍 Additional Credential Checks...")
    print("-" * 40)
    
    # Check if all required fields are present
    required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 
                      'client_email', 'client_id', 'auth_uri', 'token_uri']
    
    missing_fields = []
    for field in required_fields:
        if field not in creds_dict:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"❌ Missing required fields: {missing_fields}")
    else:
        print("✅ All required fields are present")
    
    # Check credential type
    if creds_dict.get('type') == 'service_account':
        print("✅ Credential type is correct (service_account)")
    else:
        print(f"❌ Wrong credential type: {creds_dict.get('type')}")
    
    # Summary and recommendations
    print("\n📊 SUMMARY & RECOMMENDATIONS")
    print("=" * 60)
    print("Based on the tests above:")
    print("1. If token refresh failed with 'invalid_grant' → Generate new service account key")
    print("2. If all tests passed → The issue might be with sheet permissions")
    print("3. If private key has \\n characters → Fix the formatting in your .env file")
    print("\n💡 Next steps:")
    print("- Go to Google Cloud Console")
    print("- Navigate to IAM & Admin → Service Accounts")
    print("- Find your service account and generate a new key")
    print("- Replace the GOOGLE_CREDENTIALS in your .env file")

if __name__ == "__main__":
    check_service_account_status()
