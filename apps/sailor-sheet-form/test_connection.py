#!/usr/bin/env python3
"""
Test script to diagnose Google Sheets connection issues
This script will help identify what's preventing the app from loading sheets
"""

import os
import sys
import json
from pathlib import Path

def test_credentials():
    """Test if Google Sheets credentials are available"""
    print("🔍 Testing Google Sheets Credentials...")
    print("=" * 50)
    
    # Load .env file from project root
    env_path = Path(__file__).parent.parent.parent / '.env'
    print(f"🔍 Looking for .env file at: {env_path}")
    
    if env_path.exists():
        print("✅ Found .env file in project root")
        from dotenv import load_dotenv
        load_dotenv(env_path)
        print("✅ Loaded environment variables from .env file")
    else:
        print("❌ .env file not found in project root")
    
    # Check environment variable
    google_creds = os.environ.get('GOOGLE_CREDENTIALS')
    if google_creds:
        print("✅ Found GOOGLE_CREDENTIALS environment variable")
        try:
            json.loads(google_creds)
            print("✅ Environment credentials are valid JSON")
        except:
            print("❌ Environment credentials are invalid JSON")
    else:
        print("❌ GOOGLE_CREDENTIALS environment variable not found")
    
    # Check secret file
    secret_path = Path('/etc/secrets/credentials.json')
    if secret_path.exists():
        print("✅ Found secret credentials file at /etc/secrets/credentials.json")
    else:
        print("❌ Secret credentials file not found at /etc/secrets/credentials.json")
    
    # Check local file
    local_path = Path('./credentials.json')
    if local_path.exists():
        print("✅ Found local credentials file at ./credentials.json")
    else:
        print("❌ Local credentials file not found at ./credentials.json")
    
    print()

def test_imports():
    """Test if required libraries can be imported"""
    print("📦 Testing Required Imports...")
    print("=" * 50)
    
    try:
        import gspread
        print("✅ gspread imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import gspread: {e}")
        return False
    
    try:
        from google.oauth2.service_account import Credentials
        print("✅ google.oauth2.service_account imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import google.oauth2.service_account: {e}")
        return False
    
    try:
        from config import initialize_sheets
        print("✅ config.initialize_sheets imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import config.initialize_sheets: {e}")
        return False
    
    try:
        from sheets_manager import get_available_sheets
        print("✅ sheets_manager.get_available_sheets imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import sheets_manager.get_available_sheets: {e}")
        return False
    
    print()
    return True

def test_sheets_connection():
    """Test actual Google Sheets connection"""
    print("🔗 Testing Google Sheets Connection...")
    print("=" * 50)
    
    try:
        from config import initialize_sheets
        print("🔄 Attempting to initialize Google Sheets connection...")
        gc = initialize_sheets()
        print("✅ Google Sheets client initialized successfully")
        
        print("🔄 Attempting to get available sheets...")
        from sheets_manager import get_available_sheets
        sheets = get_available_sheets(gc)
        
        if sheets:
            print(f"✅ Successfully retrieved {len(sheets)} sheets:")
            for i, sheet in enumerate(sheets[:5]):  # Show first 5 sheets
                print(f"   {i+1}. {sheet['title']} (ID: {sheet['id'][:10]}...)")
            if len(sheets) > 5:
                print(f"   ... and {len(sheets) - 5} more sheets")
        else:
            print("⚠️  No sheets found (empty list returned)")
        
        return sheets
        
    except Exception as e:
        print(f"❌ Failed to connect to Google Sheets: {e}")
        print(f"Error type: {type(e).__name__}")
        return None

def test_json_data():
    """Test if local JSON data files are working"""
    print("📄 Testing Local JSON Data Files...")
    print("=" * 50)
    
    try:
        from app import get_accounts_from_json, get_categories_from_json, get_funds_from_json
        
        accounts = get_accounts_from_json()
        print(f"✅ Accounts JSON: {len(accounts)} accounts loaded")
        
        categories = get_categories_from_json()
        print(f"✅ Categories JSON: {len(categories)} categories loaded")
        
        funds = get_funds_from_json()
        print(f"✅ Funds JSON: {len(funds)} funds loaded")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to load JSON data: {e}")
        return False

def create_mock_credentials():
    """Create a template credentials file"""
    print("🛠️  Creating Mock Credentials Template...")
    print("=" * 50)
    
    mock_creds = {
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "your-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n",
        "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
        "client_id": "your-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
    }
    
    template_path = Path('./credentials_template.json')
    with open(template_path, 'w') as f:
        json.dump(mock_creds, f, indent=2)
    
    print(f"✅ Created credentials template at {template_path}")
    print("📝 You need to replace this with your actual Google Service Account credentials")
    print("📝 Instructions:")
    print("   1. Go to Google Cloud Console")
    print("   2. Create a service account")
    print("   3. Download the JSON key file")
    print("   4. Rename it to 'credentials.json' in this directory")

def run_all_tests():
    """Run all diagnostic tests"""
    print("🧪 NGO Accounting System - Connection Diagnostic Test")
    print("=" * 60)
    print()
    
    # Test 1: Check credentials
    test_credentials()
    
    # Test 2: Check imports
    if not test_imports():
        print("❌ Cannot proceed - missing required libraries")
        return
    
    # Test 3: Test JSON data
    json_ok = test_json_data()
    print()
    
    # Test 4: Test Google Sheets
    sheets = test_sheets_connection()
    print()
    
    # Summary
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    if sheets:
        print(f"✅ Google Sheets: Working ({len(sheets)} sheets found)")
    else:
        print("❌ Google Sheets: Not working (no authentication)")
    
    if json_ok:
        print("✅ Local JSON Data: Working")
    else:
        print("❌ Local JSON Data: Not working")
    
    print()
    print("🔧 RECOMMENDATIONS")
    print("=" * 50)
    
    if not sheets:
        print("1. You need to set up Google Sheets credentials:")
        print("   - Create a Google Service Account")
        print("   - Download the credentials JSON file")
        print("   - Place it as 'credentials.json' in this directory")
        print("   - Or set GOOGLE_CREDENTIALS environment variable")
        print()
        create_mock_credentials()
    
    if not json_ok:
        print("2. Check that data/ directory has the required JSON files:")
        print("   - accounts.json")
        print("   - categories.json") 
        print("   - funds.json")

if __name__ == "__main__":
    run_all_tests()
