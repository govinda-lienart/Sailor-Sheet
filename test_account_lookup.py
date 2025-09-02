#!/usr/bin/env python3
"""
Test script for the account lookup system
Tests the new account reference table functionality
"""

from config import initialize_sheets
from sheets_manager import get_account_reference_table, get_account_name_from_worksheet_id

def test_account_lookup():
    """Test the account lookup functionality"""
    print("Testing Account Lookup System...")
    print("=" * 50)
    
    try:
        # Initialize Google Sheets connection
        gc = initialize_sheets()
        print("✅ Google Sheets connection established")
        
        # Test 1: Get account reference table
        print("\n1. Testing account reference table retrieval...")
        account_mapping = get_account_reference_table(gc)
        
        if account_mapping:
            print(f"✅ Successfully loaded {len(account_mapping)} account mappings")
            print("Account mappings:")
            for worksheet_id, account_name in account_mapping.items():
                print(f"   {worksheet_id[:20]}... -> {account_name}")
        else:
            print("❌ Failed to load account reference table")
            return
        
        # Test 2: Test specific account lookup
        print("\n2. Testing specific account lookup...")
        if account_mapping:
            # Test with the first worksheet ID from the mapping
            test_worksheet_id = list(account_mapping.keys())[0]
            account_name = get_account_name_from_worksheet_id(gc, test_worksheet_id)
            
            if account_name:
                print(f"✅ Found account '{account_name}' for worksheet ID '{test_worksheet_id[:20]}...'")
            else:
                print(f"❌ No account found for worksheet ID '{test_worksheet_id[:20]}...'")
        
        # Test 3: Test with non-existent worksheet ID
        print("\n3. Testing with non-existent worksheet ID...")
        fake_id = "fake_worksheet_id_123"
        account_name = get_account_name_from_worksheet_id(gc, fake_id)
        
        if account_name is None:
            print("✅ Correctly returned None for non-existent worksheet ID")
        else:
            print(f"❌ Unexpectedly found account '{account_name}' for fake ID")
        
        print("\n" + "=" * 50)
        print("✅ Account lookup system test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_account_lookup()
