"""
Data loader utility for loading JSON data files.
"""

import os
import json


class DataLoader:
    """Utility class for loading data from JSON files."""
    
    def load_json_data(self, filename):
        """
        Load data from JSON file in the data directory
        """
        try:
            # Get the directory of the current script
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level to reach the main app directory
            app_dir = os.path.dirname(current_dir)
            file_path = os.path.join(app_dir, 'data', filename)
            
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                print(f"DEBUG: Successfully loaded {filename}")
                return data
        except FileNotFoundError:
            print(f"ERROR: JSON file {filename} not found at {file_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in {filename}: {e}")
            return {}
        except Exception as e:
            print(f"ERROR: Unexpected error loading {filename}: {e}")
            return {}
    
    def get_funds(self):
        """
        Get funds list from JSON file instead of Google Sheets
        Returns list of fund dictionaries with id, name, color, active
        """
        try:
            data = self.load_json_data('funds.json')
            funds = data.get('funds', [])
            # Filter only active funds
            active_funds = [fund for fund in funds if fund.get('active', True)]
            print(f"DEBUG: Loaded {len(active_funds)} active funds from JSON")
            return active_funds
        except Exception as e:
            print(f"ERROR: Failed to load funds from JSON: {e}")
            return []
    
    def get_categories(self):
        """
        Get categories list from JSON file instead of Google Sheets
        Returns list of category dictionaries with code, name, category, active
        """
        try:
            data = self.load_json_data('categories.json')
            categories = data.get('categories', [])
            # Filter only active categories
            active_categories = [cat for cat in categories if cat.get('active', True)]
            print(f"DEBUG: Loaded {len(active_categories)} active categories from JSON")
            return active_categories
        except Exception as e:
            print(f"ERROR: Failed to load categories from JSON: {e}")
            return []
    
    def get_accounts(self, country_code='BE'):
        """
        Get accounts list from country-specific JSON file
        Returns list of account dictionaries with code, name, type, active
        """
        try:
            # Use country-specific account file
            account_file = f'accounts_{country_code.lower()}.json'
            data = self.load_json_data(account_file)
            accounts = data.get('accounts', [])
            # Filter only active accounts
            active_accounts = [acc for acc in accounts if acc.get('active', True)]
            print(f"DEBUG: Loaded {len(active_accounts)} active accounts from {account_file}")
            return active_accounts
        except Exception as e:
            print(f"ERROR: Failed to load accounts from {account_file}: {e}")
            # Fallback to Belgium accounts if country-specific file fails
            if country_code != 'BE':
                try:
                    data = self.load_json_data('accounts_be.json')
                    accounts = data.get('accounts', [])
                    active_accounts = [acc for acc in accounts if acc.get('active', True)]
                    print(f"DEBUG: Fallback to Belgium accounts: {len(active_accounts)} accounts")
                    return active_accounts
                except Exception as fallback_e:
                    print(f"ERROR: Fallback also failed: {fallback_e}")
            return []
    
    def get_sub_categories(self):
        """
        Get sub-categories list from JSON file
        Returns list of sub-category dictionaries with id, name, active
        """
        try:
            data = self.load_json_data('sub-categories.json')
            sub_categories = data.get('sub_categories', [])
            # Filter only active sub-categories
            active_sub_categories = [sub for sub in sub_categories if sub.get('active', True)]
            print(f"DEBUG: Loaded {len(active_sub_categories)} active sub-categories from JSON")
            return active_sub_categories
        except Exception as e:
            print(f"ERROR: Failed to load sub-categories from JSON: {e}")
            return []
