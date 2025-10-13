"""
Account Management Service
Handles account reference table operations and worksheet ID lookups.
"""

class AccountManagement:
    """Service for account reference management and lookups."""
    
    def __init__(self, gc):
        """Initialize with Google Sheets client."""
        self.gc = gc
    
    def get_account_reference_table(self, master_sheet_id="1DE3YTidoVIQm4SxFvK2ByRahZ7qR_Kj_LDPTpIv5NQE", worksheet_title="Account - ID Worksheet"):
        """
        Get the account reference table that maps worksheet IDs to account names
        Args:
            master_sheet_id: ID of the master sheet containing the reference table
            worksheet_title: Title of the worksheet containing the reference table
        Returns: Dictionary mapping worksheet IDs to account names
        """
        try:
            print(f"DEBUG: Opening master sheet: {master_sheet_id}")
            print(f"DEBUG: Looking for worksheet: {worksheet_title}")
            
            # Open the master sheet
            master_sheet = self.gc.open_by_key(master_sheet_id)
            worksheet = master_sheet.worksheet(worksheet_title)
            
            # Get all data from the reference table
            all_data = worksheet.get_all_values()
            print(f"DEBUG: Raw data from reference table: {all_data}")
            
            # Skip header row and build mapping
            account_mapping = {}
            for row in all_data[1:]:  # Skip header row
                if len(row) >= 2 and row[0] and row[1]:  # Check if both columns have data
                    account_name = row[0].strip()
                    worksheet_id = row[1].strip()
                    account_mapping[worksheet_id] = account_name
                    print(f"DEBUG: Mapped {worksheet_id} -> {account_name}")
                    
                    # Also map by worksheet title for easier lookup
                    # Extract worksheet title from the URL or use a simpler mapping
                    if "1Fvrld1X0OioH7AbKCiSIMNac5U9OvlKJh0OSk02bTTI" in worksheet_id:
                        account_mapping["VN Indovina"] = account_name
                        print(f"DEBUG: Also mapped 'VN Indovina' -> {account_name}")
            
            print(f"DEBUG: Loaded {len(account_mapping)} account mappings")
            print(f"DEBUG: Final mapping: {account_mapping}")
            return account_mapping
            
        except Exception as e:
            print(f"Error getting account reference table: {e}")
            return {}

    def get_account_name_from_worksheet_id(self, worksheet_id, master_sheet_id="1DE3YTidoVIQm4SxFvK2ByRahZ7qR_Kj_LDPTpIv5NQE"):
        """
        Get the account name for a given worksheet ID from the reference table
        Args:
            worksheet_id: ID of the worksheet to look up (format: sheet_id#gid=N)
            master_sheet_id: ID of the master sheet containing the reference table
        Returns: Account name or None if not found
        """
        try:
            print(f"DEBUG: Looking up worksheet ID: {worksheet_id}")
            print(f"DEBUG: Using master sheet ID: {master_sheet_id}")
            
            # Extract the base sheet ID from the worksheet_id (remove #gid= part)
            if "#gid=" in worksheet_id:
                base_sheet_id = worksheet_id.split("#gid=")[0]
                gid = worksheet_id.split("#gid=")[1]
                print(f"DEBUG: Extracted base sheet ID: {base_sheet_id}")
                print(f"DEBUG: Extracted gid: {gid}")
            else:
                base_sheet_id = worksheet_id
                gid = "0"
                print(f"DEBUG: Using worksheet ID as-is: {base_sheet_id}")
            
            account_mapping = self.get_account_reference_table(master_sheet_id)
            print(f"DEBUG: Account mapping keys: {list(account_mapping.keys())}")
            
            # Try to find account name using the base sheet ID
            account_name = account_mapping.get(base_sheet_id)
            
            if account_name:
                print(f"DEBUG: Found account name '{account_name}' for base sheet ID '{base_sheet_id}'")
            else:
                print(f"DEBUG: No account name found for base sheet ID '{base_sheet_id}'")
                print(f"DEBUG: Available worksheet IDs: {list(account_mapping.keys())}")
                
            return account_name
            
        except Exception as e:
            print(f"Error getting account name from worksheet ID: {e}")
            return None

    def get_account_name_from_worksheet_title(self, worksheet_title, master_sheet_id="1DE3YTidoVIQm4SxFvK2ByRahZ7qR_Kj_LDPTpIv5NQE"):
        """
        Get the account name for a given worksheet title from the reference table
        Args:
            worksheet_title: Title of the worksheet to look up
            master_sheet_id: ID of the master sheet containing the reference table
        Returns: Account name or None if not found
        """
        try:
            print(f"DEBUG: Looking up worksheet title: {worksheet_title}")
            print(f"DEBUG: Using master sheet ID: {master_sheet_id}")
            
            # Get the reference table
            master_sheet = self.gc.open_by_key(master_sheet_id)
            worksheet = master_sheet.worksheet("Account - ID Worksheet")
            
            # Get all data from the reference table
            all_data = worksheet.get_all_values()
            print(f"DEBUG: Master reference table data: {all_data}")
            
            # Skip header row and search for matching worksheet title
            for i, row in enumerate(all_data[1:], start=1):  # Skip header row
                print(f"DEBUG: Row {i}: {row}")
                if len(row) >= 3 and row[0] and row[2]:  # Check if both account name and worksheet title columns have data
                    account_name = row[0].strip()
                    worksheet_title_in_table = row[2].strip()  # Assuming worksheet title is in column C
                    print(f"DEBUG: Comparing '{worksheet_title_in_table}' with '{worksheet_title}'")
                    
                    if worksheet_title_in_table == worksheet_title:
                        print(f"DEBUG: Found account name '{account_name}' for worksheet title '{worksheet_title}'")
                        return account_name
            
            print(f"DEBUG: No account name found for worksheet title '{worksheet_title}'")
            return None
            
        except Exception as e:
            print(f"Error getting account name from worksheet title: {e}")
            return None
