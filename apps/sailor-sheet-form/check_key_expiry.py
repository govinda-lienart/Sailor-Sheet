#!/usr/bin/env python3
"""
Script to check if your service account key is expired or corrupted
This will examine the key details and try to determine the exact issue
"""

import os
import json
import base64
from pathlib import Path
from datetime import datetime
import hashlib

def check_key_expiry_and_corruption():
    """Check if the service account key is expired or corrupted"""
    print("🔍 Checking Service Account Key Status...")
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
    
    # Extract and analyze the private key
    print("\n🔑 Analyzing Private Key...")
    print("-" * 40)
    
    private_key = creds_dict.get('private_key', '')
    private_key_id = creds_dict.get('private_key_id', '')
    
    if private_key:
        print(f"🔑 Private Key ID: {private_key_id}")
        print(f"📏 Private Key Length: {len(private_key)} characters")
        
        # Check private key format
        if private_key.startswith('-----BEGIN PRIVATE KEY-----'):
            print("✅ Private key has correct BEGIN header")
        else:
            print("❌ Private key missing correct BEGIN header")
            
        if private_key.endswith('-----END PRIVATE KEY-----\n'):
            print("✅ Private key has correct END footer")
        else:
            print("❌ Private key missing correct END footer")
        
        # Check for common corruption issues
        if '\\n' in private_key:
            print("❌ Private key contains escaped newlines (\\n) - this is likely the problem!")
            print("   The key should have actual newlines, not \\n characters")
            print("   This is a common issue when copying from JSON files")
        else:
            print("✅ Private key newlines look correct")
        
        # Count newlines
        newline_count = private_key.count('\n')
        print(f"📊 Newline count: {newline_count}")
        
        # Check if it looks like a valid RSA key
        if 'MII' in private_key:
            print("✅ Private key contains MII header (typical for RSA keys)")
        else:
            print("❌ Private key missing MII header (might be corrupted)")
        
        # Try to decode the key to check for corruption
        try:
            # Extract the base64 part between headers
            key_content = private_key.replace('-----BEGIN PRIVATE KEY-----\n', '').replace('\n-----END PRIVATE KEY-----\n', '')
            key_content = key_content.replace('\n', '')
            
            # Try to decode base64
            decoded_key = base64.b64decode(key_content)
            print(f"✅ Private key base64 decoding successful ({len(decoded_key)} bytes)")
            
            # Check if it looks like a valid ASN.1 structure
            if decoded_key.startswith(b'\x30'):
                print("✅ Private key has valid ASN.1 structure")
            else:
                print("❌ Private key ASN.1 structure looks invalid")
                
        except Exception as e:
            print(f"❌ Private key base64 decoding failed: {e}")
            print("   This indicates the key is corrupted")
    
    # Check other credential fields
    print("\n📋 Checking Other Credential Fields...")
    print("-" * 40)
    
    client_email = creds_dict.get('client_email', '')
    project_id = creds_dict.get('project_id', '')
    
    print(f"📧 Client Email: {client_email}")
    print(f"🏗️  Project ID: {project_id}")
    
    # Validate email format
    if '@' in client_email and '.iam.gserviceaccount.com' in client_email:
        print("✅ Service account email format looks correct")
    else:
        print("❌ Service account email format looks incorrect")
    
    # Check if project ID matches email
    if project_id in client_email:
        print("✅ Project ID matches service account email")
    else:
        print("❌ Project ID doesn't match service account email")
    
    # Test with Google Auth library
    print("\n🔗 Testing with Google Auth Library...")
    print("-" * 40)
    
    try:
        from google.oauth2.service_account import Credentials
        from google.auth.transport.requests import Request
        import google.auth.exceptions
        
        # Create credentials object
        print("🔄 Creating credentials object...")
        credentials = Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        print("✅ Credentials object created successfully")
        
        # Try to get token info
        print("🔄 Attempting to get token info...")
        try:
            # This will try to refresh the token
            credentials.refresh(Request())
            print("✅ Token refresh successful")
            
            if credentials.expiry:
                print(f"📅 Token expires at: {credentials.expiry}")
                now = datetime.now(credentials.expiry.tzinfo)
                if credentials.expiry > now:
                    print("✅ Token is still valid")
                else:
                    print("❌ Token has expired")
            
        except Exception as e:
            print(f"❌ Token refresh failed: {e}")
            
            # Analyze the specific error
            error_str = str(e)
            if "invalid_grant" in error_str:
                print("\n🔧 ERROR ANALYSIS: Invalid Grant")
                if "Invalid JWT Signature" in error_str:
                    print("   → The private key signature is invalid")
                    print("   → This usually means the key is corrupted or expired")
                elif "Token has been expired" in error_str:
                    print("   → The token has expired")
                elif "Invalid key" in error_str:
                    print("   → The private key is malformed")
                else:
                    print(f"   → Unknown invalid_grant error: {error_str}")
            elif "unauthorized_client" in error_str:
                print("\n🔧 ERROR ANALYSIS: Unauthorized Client")
                print("   → The service account is not authorized for this API")
            elif "invalid_scope" in error_str:
                print("\n🔧 ERROR ANALYSIS: Invalid Scope")
                print("   → The requested scopes are not valid")
            else:
                print(f"\n🔧 ERROR ANALYSIS: {error_str}")
    
    except ImportError as e:
        print(f"❌ Missing required packages: {e}")
        print("Run: pip install google-auth")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    # Summary and recommendations
    print("\n📊 DIAGNOSIS SUMMARY")
    print("=" * 60)
    
    if '\\n' in private_key:
        print("🔧 PRIMARY ISSUE: Escaped newlines in private key")
        print("   → The private key contains \\n instead of actual newlines")
        print("   → This is a common formatting issue")
        print("\n💡 SOLUTION:")
        print("   1. Copy the private key from your original JSON file")
        print("   2. Make sure it has actual newlines, not \\n characters")
        print("   3. Or generate a new service account key")
    else:
        print("🔧 PRIMARY ISSUE: Invalid JWT Signature")
        print("   → The private key signature is invalid")
        print("   → This usually means the key is expired or corrupted")
        print("\n💡 SOLUTION:")
        print("   1. Generate a new service account key")
        print("   2. Replace the GOOGLE_CREDENTIALS in your .env file")
        print("   3. Make sure to copy the key exactly as provided")

if __name__ == "__main__":
    check_key_expiry_and_corruption()
