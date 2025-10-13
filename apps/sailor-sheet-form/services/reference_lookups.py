"""
Reference Lookups Service
Handles lookups for funds, accounts, categories, and sub-categories from JSON files.
"""

import json
import os

class ReferenceLookups:
    """Service for reference data lookups from JSON files."""
    
    def __init__(self, gc):
        """Initialize with Google Sheets client (kept for compatibility)."""
        self.gc = gc
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.current_dir, '..', 'data')
    
    def get_fund_name_by_id(self, fund_id):
        """
        Get fund name by ID for transaction saving
        Args:
            fund_id: ID of the fund to look up
        Returns: Fund name or "Unknown Fund" if not found
        """
        try:
            print(f"DEBUG: get_fund_name_by_id called with fund_id: {fund_id}")
            
            # Load funds from JSON file instead of Google Sheets
            json_file_path = os.path.join(self.data_dir, 'funds.json')
            
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            funds = data.get('funds', [])
            print(f"DEBUG: Retrieved {len(funds)} fund records from JSON")
            
            for i, fund in enumerate(funds):
                print(f"DEBUG: Fund {i}: ID='{fund.get('id')}', Name='{fund.get('name')}'")
                if str(fund.get('id', '')) == str(fund_id):
                    print(f"DEBUG: Found matching fund: {fund.get('name')}")
                    return fund.get('name', '')
            
            print(f"WARNING: Fund ID {fund_id} not found")
            print(f"DEBUG: Available fund IDs: {[str(f.get('id', '')) for f in funds]}")
            return "Unknown Fund"
            
        except Exception as e:
            print(f"ERROR in get_fund_name_by_id: {e}")
            import traceback
            traceback.print_exc()
            return "Unknown Fund"

    def get_account_name_by_code(self, account_code):
        """
        Get account name by code for transaction saving
        Args:
            account_code: Code of the account to look up
        Returns: Account name or "Unknown Account" if not found
        """
        try:
            print(f"DEBUG: get_account_name_by_code called with account_code: {account_code}")
            
            # Try to determine the country from the account code or try multiple files
            # First try Vietnam accounts (VNINDO, ACC03, etc.)
            json_files_to_try = ['accounts_vn.json', 'accounts_be.json', 'accounts.json']
            
            for json_file in json_files_to_try:
                json_file_path = os.path.join(self.data_dir, json_file)
                
                try:
                    with open(json_file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    accounts = data.get('accounts', [])
                    print(f"DEBUG: Checking {json_file} - Retrieved {len(accounts)} account records")
                    
                    for i, acc in enumerate(accounts):
                        print(f"DEBUG: Account {i}: Code='{acc.get('code')}', Name='{acc.get('name')}'")
                        if str(acc.get('code', '')) == str(account_code):
                            print(f"DEBUG: Found matching account in {json_file}: {acc.get('name')}")
                            return acc.get('name', '')
                            
                except FileNotFoundError:
                    print(f"DEBUG: {json_file} not found, trying next file")
                    continue
                except Exception as file_error:
                    print(f"DEBUG: Error reading {json_file}: {file_error}")
                    continue
            
            print(f"WARNING: Account Code {account_code} not found in any account file")
            return "Unknown Account"
            
        except Exception as e:
            print(f"ERROR in get_account_name_by_code: {e}")
            import traceback
            traceback.print_exc()
            return "Unknown Account"

    def get_category_name_by_code(self, category_code):
        """
        Get category name by code for transaction saving
        Args:
            category_code: Code of the category to look up
        Returns: Category name or "Unknown Category" if not found
        """
        try:
            print(f"DEBUG: get_category_name_by_code called with category_code: {category_code}")
            
            # Load categories from JSON file instead of Google Sheets
            json_file_path = os.path.join(self.data_dir, 'categories.json')
            
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            categories = data.get('categories', [])
            print(f"DEBUG: Retrieved {len(categories)} category records from JSON")
            
            for i, cat in enumerate(categories):
                print(f"DEBUG: Category {i}: Code='{cat.get('code')}', Name='{cat.get('name')}'")
                if str(cat.get('code', '')) == str(category_code):
                    print(f"DEBUG: Found matching category: {cat.get('name')}")
                    return cat.get('name', '')
            
            print(f"WARNING: Category Code {category_code} not found")
            print(f"DEBUG: Available category codes: {[str(cat.get('code', '')) for cat in categories]}")
            return "Unknown Category"
            
        except Exception as e:
            print(f"ERROR in get_category_name_by_code: {e}")
            import traceback
            traceback.print_exc()
            return "Unknown Category"

    def get_sub_category_name_by_id(self, sub_category_id):
        """
        Get sub-category name by ID for transaction saving
        Args:
            sub_category_id: ID of the sub-category to look up
        Returns: Sub-category name or empty string if not found or empty
        """
        try:
            print(f"DEBUG: get_sub_category_name_by_id called with sub_category_id: {sub_category_id}")
            
            # If sub_category_id is empty or None, return empty string
            if not sub_category_id or sub_category_id.strip() == "":
                print(f"DEBUG: No sub-category selected, returning empty string")
                return ""
            
            # Load sub-categories from JSON file instead of Google Sheets
            json_file_path = os.path.join(self.data_dir, 'sub-categories.json')
            
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            sub_categories = data.get('sub_categories', [])
            print(f"DEBUG: Loaded {len(sub_categories)} sub-categories from JSON")
            
            # Find the sub-category with matching ID
            for sub_category in sub_categories:
                if str(sub_category.get('id', '')) == str(sub_category_id):
                    name = sub_category.get('name', 'Unknown Sub-Category')
                    print(f"DEBUG: Found sub-category name: {name}")
                    return name
            
            print(f"WARNING: Sub-Category ID {sub_category_id} not found")
            print(f"DEBUG: Available sub-category IDs: {[str(sub.get('id', '')) for sub in sub_categories]}")
            return ""
            
        except Exception as e:
            print(f"ERROR in get_sub_category_name_by_id: {e}")
            import traceback
            traceback.print_exc()
            return ""
