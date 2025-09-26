
# =============================================================================

from datetime import datetime

# =============================================================================
# EFFICIENT TRANSACTION SEARCH TOOL
# =============================================================================

def search_transaction_tool(gc, sheet_type, transaction_number):
    """
    Efficiently search for a transaction by number without downloading all data.
    
    Method 1: Get only transaction number column first, then fetch specific row.
    This avoids downloading all rows and columns.
    
    Args:
        gc: Google Sheets client
        sheet_type: 'vn' for Vietnamese or 'be' for Belgian
        transaction_number: Transaction number to search for
    
    Returns:
        dict: Transaction data if found, None if not found
    """
    try:
        print(f"DEBUG: Searching for transaction: {transaction_number}")
        print(f"DEBUG: In sheet type: {sheet_type}")
        
        # Define sheet IDs
        sheet_ids = {
            'vn': '1Fvrld1X0OioH7AbKCiSIMNac5U9OvlKJh0OSk02bTTI',  # Vietnamese Master Ledger
            'be': '1o5RnuAmm00YAqZzLkyrhZx7CocEETBhi-snPGUzbqSk'   # Belgian Master Ledger
        }
        
        if sheet_type not in sheet_ids:
            print(f"ERROR: Invalid sheet type: {sheet_type}")
            return None
        
        sheet_id = sheet_ids[sheet_type]
        print(f"DEBUG: Using sheet ID: {sheet_id}")
        print(f"DEBUG: This should be the SAME sheet as the search function")
        
        # Open the sheet
        sheet = gc.open_by_key(sheet_id)
        worksheet = sheet.sheet1  # Assuming we're searching the first worksheet
        
        print(f"DEBUG: Opened sheet: {sheet.title}")
        print(f"DEBUG: Using worksheet: {worksheet.title}")
        print(f"DEBUG: Worksheet ID: {worksheet.id}")
        
        # Step 1: Get only the transaction number column (Column A)
        # This is much faster than getting all data
        print("DEBUG: Getting transaction number column...")
        transaction_column = worksheet.col_values(1)  # Column A only
        
        # Step 2: Check if transaction number exists
        if transaction_number not in transaction_column:
            print(f"DEBUG: Transaction {transaction_number} not found in column")
            return None
        
        # Step 3: Find ALL rows with this transaction number (debit and credit entries)
        row_indices = []
        for i, cell_value in enumerate(transaction_column):
            if cell_value == transaction_number:
                row_indices.append(i + 1)  # Convert to 1-based indexing
        
        print(f"DEBUG: Found transaction at rows: {row_indices}")
        
        # Step 4: Get all rows for this transaction
        print("DEBUG: Getting all rows data...")
        all_rows_data = []
        for row_index in row_indices:
            row_data = worksheet.row_values(row_index)
            all_rows_data.append(row_data)
            print(f"DEBUG: Row {row_index} data: {row_data}")
        
        # Step 5: Get column headers to map data properly
        headers = worksheet.row_values(1)  # First row contains headers
        
        # Step 6: Create combined transaction data from all rows
        transaction_data = {}
        
        # Initialize with common fields from first row
        for i, header in enumerate(headers):
            if i < len(all_rows_data[0]):
                transaction_data[header] = all_rows_data[0][i]
            else:
                transaction_data[header] = ""
        
        # Identify debit and credit rows and extract their specific data
        debit_row_data = None
        credit_row_data = None
        debit_account = None
        credit_account = None
        debit_amount = None
        credit_amount = None
        
        print(f"DEBUG: Headers: {headers}")
        
        for row_idx, row_data in enumerate(all_rows_data):
            print(f"DEBUG: Processing row {row_idx + 1}: {row_data}")
            if len(row_data) > 0:  # Make sure row has data
                # Find column indices
                account_col = None
                debit_amount_col = None
                credit_amount_col = None
                
                for i, header in enumerate(headers):
                    if 'Account' in header:
                        account_col = i
                    elif 'Debit' in header and 'VND' in header:
                        debit_amount_col = i
                    elif 'Credit' in header and 'VND' in header:
                        credit_amount_col = i
                
                print(f"DEBUG: Account col: {account_col}, Debit col: {debit_amount_col}, Credit col: {credit_amount_col}")
                
                # Get account name from Account column
                if account_col is not None and account_col < len(row_data):
                    account_name = row_data[account_col]
                    print(f"DEBUG: Account name: {account_name}")
                    
                    # Check if this row has debit amount
                    has_debit = (debit_amount_col is not None and 
                               debit_amount_col < len(row_data) and 
                               row_data[debit_amount_col] and 
                               row_data[debit_amount_col].strip())
                    
                    # Check if this row has credit amount  
                    has_credit = (credit_amount_col is not None and 
                                credit_amount_col < len(row_data) and 
                                row_data[credit_amount_col] and 
                                row_data[credit_amount_col].strip())
                    
                    print(f"DEBUG: Has debit: {row_data[debit_amount_col] if debit_amount_col is not None and debit_amount_col < len(row_data) else 'N/A'}, Has credit: {row_data[credit_amount_col] if credit_amount_col is not None and credit_amount_col < len(row_data) else 'N/A'}")
                    
                    # Store the complete row data for debit or credit
                    if has_debit and not debit_row_data:
                        debit_row_data = row_data
                        debit_account = account_name
                        debit_amount = row_data[debit_amount_col] if debit_amount_col is not None and debit_amount_col < len(row_data) else ""
                        print(f"DEBUG: Set debit row data: {debit_row_data}")
                        print(f"DEBUG: Set debit account: {debit_account}, amount: {debit_amount}")
                    elif has_credit and not credit_row_data:
                        credit_row_data = row_data
                        credit_account = account_name
                        credit_amount = row_data[credit_amount_col] if credit_amount_col is not None and credit_amount_col < len(row_data) else ""
                        print(f"DEBUG: Set credit row data: {credit_row_data}")
                        print(f"DEBUG: Set credit account: {credit_account}, amount: {credit_amount}")
        
        # Add the identified accounts and amounts to the transaction data
        if debit_account:
            transaction_data['Debit Account'] = debit_account
        if credit_account:
            transaction_data['Credit Account'] = credit_account
        if debit_amount:
            transaction_data['Debit (VND)'] = debit_amount
        if credit_amount:
            transaction_data['Credit (VND)'] = credit_amount
            
        # Add document fields from both rows (Bill, Red Bill, Doc)
        if debit_row_data:
            # Find document column indices
            bill_col = None
            red_bill_col = None
            doc_col = None
            
            for i, header in enumerate(headers):
                if header == 'Bill':
                    bill_col = i
                elif header == 'Red BIll':  # Note the capital I
                    red_bill_col = i
                elif header == 'Doc':
                    doc_col = i
            
            print(f"DEBUG: Document columns - Bill: {bill_col}, Red Bill: {red_bill_col}, Doc: {doc_col}")
            
            # Add debit side document data
            if bill_col is not None and bill_col < len(debit_row_data):
                transaction_data['Debit Bill'] = debit_row_data[bill_col] if debit_row_data[bill_col] else ""
                print(f"DEBUG: Debit Bill: {transaction_data['Debit Bill']}")
            if red_bill_col is not None and red_bill_col < len(debit_row_data):
                transaction_data['Debit Red Bill'] = debit_row_data[red_bill_col] if debit_row_data[red_bill_col] else ""
                print(f"DEBUG: Debit Red Bill: {transaction_data['Debit Red Bill']}")
            if doc_col is not None and doc_col < len(debit_row_data):
                transaction_data['Debit Doc'] = debit_row_data[doc_col] if debit_row_data[doc_col] else ""
                print(f"DEBUG: Debit Doc: {transaction_data['Debit Doc']}")
        
        if credit_row_data:
            # Find document column indices
            bill_col = None
            red_bill_col = None
            doc_col = None
            
            for i, header in enumerate(headers):
                if header == 'Bill':
                    bill_col = i
                elif header == 'Red BIll':  # Note the capital I
                    red_bill_col = i
                elif header == 'Doc':
                    doc_col = i
            
            # Add credit side document data
            if bill_col is not None and bill_col < len(credit_row_data):
                transaction_data['Credit Bill'] = credit_row_data[bill_col] if credit_row_data[bill_col] else ""
                print(f"DEBUG: Credit Bill: {transaction_data['Credit Bill']}")
            if red_bill_col is not None and red_bill_col < len(credit_row_data):
                transaction_data['Credit Red Bill'] = credit_row_data[red_bill_col] if credit_row_data[red_bill_col] else ""
                print(f"DEBUG: Credit Red Bill: {transaction_data['Credit Red Bill']}")
            if doc_col is not None and doc_col < len(credit_row_data):
                transaction_data['Credit Doc'] = credit_row_data[doc_col] if credit_row_data[doc_col] else ""
                print(f"DEBUG: Credit Doc: {transaction_data['Credit Doc']}")
        
        print(f"DEBUG: Identified Debit Account: {debit_account}")
        print(f"DEBUG: Identified Credit Account: {credit_account}")
        print(f"DEBUG: Transaction found with {len(transaction_data)} fields")
        return transaction_data
        
    except Exception as e:
        print(f"ERROR: Failed to search transaction: {str(e)}")
        return None

# =============================================================================
# DOCUMENT UPDATE FUNCTIONS
# =============================================================================

def update_document_link(gc, sheet_type, transaction_number, document_type, file_url):
    """
    Update document link in Google Sheets for both debit and credit rows.
    
    Args:
        gc: Google Sheets client
        sheet_type: 'vn' for Vietnamese or 'be' for Belgian
        transaction_number: Transaction number to update
        document_type: 'bill', 'redBill', or 'documentation'
        file_url: URL of the uploaded file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"DEBUG: Updating document link for transaction: {transaction_number}")
        print(f"DEBUG: Document type: {document_type}")
        print(f"DEBUG: File URL: {file_url}")
        
        # Define sheet IDs
        sheet_ids = {
            'vn': '1Fvrld1X0OioH7AbKCiSIMNac5U9OvlKJh0OSk02bTTI',  # Vietnamese Master Ledger
            'be': '1o5RnuAmm00YAqZzLkyrhZx7CocEETBhi-snPGUzbqSk'   # Belgian Master Ledger
        }
        
        if sheet_type not in sheet_ids:
            print(f"ERROR: Invalid sheet type: {sheet_type}")
            return False
        
        sheet_id = sheet_ids[sheet_type]
        print(f"DEBUG: UPDATE FUNCTION - Using sheet ID: {sheet_id}")
        print(f"DEBUG: UPDATE FUNCTION - This should be the SAME sheet as the search function")
        
        # Open the sheet
        sheet = gc.open_by_key(sheet_id)
        worksheet = sheet.sheet1
        
        print(f"DEBUG: UPDATE FUNCTION - Opened sheet: {sheet.title}")
        print(f"DEBUG: UPDATE FUNCTION - Using worksheet: {worksheet.title}")
        print(f"DEBUG: UPDATE FUNCTION - Worksheet ID: {worksheet.id}")
        
        # Get headers to find the correct column
        headers = worksheet.row_values(1)
        print(f"DEBUG: Headers: {headers}")
        
        # Find the document column index
        document_column_map = {
            'bill': ['Bill'],
            'redBill': ['Red BIll', 'Red Bill', 'Red Bills'],  # Try different variations
            'documentation': ['Doc', 'Documentation']
        }
        
        possible_columns = document_column_map.get(document_type)
        if not possible_columns:
            print(f"ERROR: Invalid document type: {document_type}")
            return False
        
        print(f"DEBUG: Looking for columns {possible_columns} in headers: {headers}")
        
        # Find column index
        column_index = None
        target_column = None
        for i, header in enumerate(headers):
            print(f"DEBUG: Checking header {i}: '{header}'")
            if header in possible_columns:
                column_index = i
                target_column = header
                print(f"DEBUG: Found column '{target_column}' at index {i}")
                break
        
        if column_index is None:
            print(f"ERROR: None of the columns {possible_columns} found in headers")
            print(f"DEBUG: Available headers: {headers}")
            return False
        
        print(f"DEBUG: Found column '{target_column}' at index {column_index}")
        
        # Find all rows with this transaction number
        transaction_column = worksheet.col_values(1)  # Column A
        print(f"DEBUG: Searching for transaction '{transaction_number}' in column A")
        print(f"DEBUG: Transaction number type: {type(transaction_number)}")
        print(f"DEBUG: Transaction number length: {len(transaction_number)}")
        print(f"DEBUG: Total rows in sheet: {len(transaction_column)}")
        
        # Show some sample transaction numbers for debugging
        sample_transactions = [txn for txn in transaction_column[1:6] if txn]  # Skip header, get first 5 transactions
        print(f"DEBUG: Sample transaction numbers in sheet: {sample_transactions}")
        
        # Check for exact matches with detailed debugging
        row_indices = []
        found_similar = []
        for i, cell_value in enumerate(transaction_column):
            if cell_value == transaction_number:
                row_indices.append(i + 1)  # Convert to 1-based indexing
                print(f"DEBUG: EXACT MATCH found at row {i + 1}: '{cell_value}'")
            elif transaction_number in str(cell_value):
                found_similar.append((i + 1, cell_value))
        
        if found_similar:
            print(f"DEBUG: Found similar transaction numbers: {found_similar}")
        
        # Also try string comparison with strip
        if not row_indices:
            print(f"DEBUG: No exact matches, trying with stripped values...")
            for i, cell_value in enumerate(transaction_column):
                if str(cell_value).strip() == str(transaction_number).strip():
                    row_indices.append(i + 1)
                    print(f"DEBUG: STRIPPED MATCH found at row {i + 1}: '{cell_value}'")
        
        print(f"DEBUG: Found transaction at rows: {row_indices}")
        
        if not row_indices:
            print(f"ERROR: Transaction '{transaction_number}' not found in sheet")
            print(f"DEBUG: Available transaction numbers (first 10): {[txn for txn in transaction_column[1:11] if txn]}")
            print(f"DEBUG: Transaction number format should be DDMMYY-HHMMSS (e.g., 080925-180635)")
            print(f"DEBUG: You searched for: {transaction_number}")
            return False
        
        # Create HYPERLINK formula like in the main form
        hyperlink_formula = f'=HYPERLINK("{file_url}", "✔")'
        print(f"DEBUG: Created HYPERLINK formula: {hyperlink_formula}")
        
        # Map document types to column letters (same as main form)
        column_mapping = {
            'bill': 'N',      # Bill column
            'redBill': 'O',   # Red Bill column  
            'documentation': 'P'  # Doc column
        }
        
        # Get the column letter for this document type
        column_letter = column_mapping.get(document_type)
        if not column_letter:
            print(f"ERROR: Invalid document type: {document_type}")
            return False
        
        print(f"DEBUG: Using column {column_letter} for document type {document_type}")
        
        # Update all rows for this transaction with HYPERLINK formula
        for row_index in row_indices:
            print(f"DEBUG: Updating row {row_index} with HYPERLINK formula")
            
            try:
                # Update the cell with the HYPERLINK formula using USER_ENTERED (same as main form)
                cell_address = f'{column_letter}{row_index}'
                print(f"DEBUG: Updating cell {cell_address} with formula: {hyperlink_formula}")
                worksheet.update(cell_address, hyperlink_formula, value_input_option='USER_ENTERED')
                print(f"DEBUG: Successfully updated cell {cell_address}")
            except Exception as e:
                print(f"ERROR: Failed to update cell {cell_address}: {str(e)}")
                return False
        
        print(f"DEBUG: Successfully updated {len(row_indices)} rows for transaction {transaction_number} with HYPERLINK formulas")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to update document link: {str(e)}")
        return False

# =============================================================================
# ACCOUNT REFERENCE MANAGEMENT
# =============================================================================

# Get Account Reference Table
# ---------------------------
def get_account_reference_table(gc, master_sheet_id="1DE3YTidoVIQm4SxFvK2ByRahZ7qR_Kj_LDPTpIv5NQE", worksheet_title="Account - ID Worksheet"):
    """
    Get the account reference table that maps worksheet IDs to account names
    Args:
        gc: Google Sheets client
        master_sheet_id: ID of the master sheet containing the reference table
        worksheet_title: Title of the worksheet containing the reference table
    Returns: Dictionary mapping worksheet IDs to account names
    """
    try:
        print(f"DEBUG: Opening master sheet: {master_sheet_id}")
        print(f"DEBUG: Looking for worksheet: {worksheet_title}")
        
        # Open the master sheet
        master_sheet = gc.open_by_key(master_sheet_id)
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

# Get Account Name From Worksheet ID
# ----------------------------------
def get_account_name_from_worksheet_id(gc, worksheet_id, master_sheet_id="1DE3YTidoVIQm4SxFvK2ByRahZ7qR_Kj_LDPTpIv5NQE"):
    """
    Get the account name for a given worksheet ID from the reference table
    Args:
        gc: Google Sheets client
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
        
        account_mapping = get_account_reference_table(gc, master_sheet_id)
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

# Get Account Name From Worksheet Title
# ------------------------------------
def get_account_name_from_worksheet_title(gc, worksheet_title, master_sheet_id="1DE3YTidoVIQm4SxFvK2ByRahZ7qR_Kj_LDPTpIv5NQE"):
    """
    Get the account name for a given worksheet title from the reference table
    Args:
        gc: Google Sheets client
        worksheet_title: Title of the worksheet to look up
        master_sheet_id: ID of the master sheet containing the reference table
    Returns: Account name or None if not found
    """
    try:
        print(f"DEBUG: Looking up worksheet title: {worksheet_title}")
        print(f"DEBUG: Using master sheet ID: {master_sheet_id}")
        
        # Get the reference table
        master_sheet = gc.open_by_key(master_sheet_id)
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

# =============================================================================
# SHEET SELECTION AND MANAGEMENT
# =============================================================================

# Get Available Sheets
# -------------------
def get_available_sheets(gc):
    """
    Get list of available Google Sheets for dropdown selection
    Args:
        gc: Google Sheets client
    Returns: List of dictionaries with sheet info
    """
    try:
        # Get all spreadsheets you have access to
        all_sheets = gc.openall()
        sheet_list = []
        
        for sheet in all_sheets:
            sheet_list.append({
                'id': sheet.id,
                'title': sheet.title
            })
        
        return sheet_list
    except Exception as e:
        print(f"Error getting sheets: {e}")
        return []

# Get Sheet By ID
# ---------------
def get_sheet_by_id(gc, sheet_id):
    """
    Get a specific sheet by its ID
    Args:
        gc: Google Sheets client
        sheet_id: ID of the sheet to retrieve
    Returns: Sheet object or None if not found
    """
    try:
        sheet = gc.open_by_key(sheet_id)
        return sheet
    except Exception as e:
        print(f"Error getting sheet by ID: {e}")
        return None

# Get Worksheets From Sheet
# -------------------------
def get_worksheets_from_sheet(gc, sheet_id):
    """
    Get list of worksheets (subsheets) from a specific Google Sheet
    Args:
        gc: Google Sheets client
        sheet_id: ID of the specific sheet
    Returns: List of dictionaries with worksheet info including account names
    """
    try:
        # Use the centralized sheet opening function
        sheet = get_sheet_by_id(gc, sheet_id)
        if sheet is None:
            return []
        
        # Get all worksheets in this sheet
        worksheets = sheet.worksheets()
        worksheet_list = []
        
        for worksheet in worksheets:
            worksheet_title = worksheet.title
            
            print(f"DEBUG: Processing worksheet: {worksheet_title}")
            
            worksheet_list.append({
                'id': worksheet_title,  # Use worksheet title as ID
                'title': worksheet.title,
                'index': worksheet.index,
                'account_name': worksheet_title  # Use worksheet title as account name
            })
        
        return worksheet_list
    except Exception as e:
        print(f"Error getting worksheets: {e}")
        return []

# =============================================================================
# TRANSACTION MANAGEMENT
# =============================================================================

# Generate Offset Text
# --------------------
def generate_offset_text(account_name, counter_account_name):
    """
    Generate offset text for Expenses and Revenues accounts
    Args:
        account_name: The current account name
        counter_account_name: The counter account name (the other side of the transaction)
    Returns: Offset text or empty string
    """
    # Define the target accounts that should get offset text
    target_accounts = {
        'VN - Expenses': 'expense',
        'BE - Expenses': 'expense', 
        'VN - Revenues': 'revenue',
        'BE - Revenues': 'revenue'
    }
    
    # Check if this account should get offset text
    account_type = target_accounts.get(account_name)
    
    if account_type:
        if account_type == 'expense':
            return f"Paid From {counter_account_name}"
        elif account_type == 'revenue':
            return f"Received Into {counter_account_name}"
    
    # Return empty string for non-target accounts
    return ""

# Add Transaction To Selected Sheet
# --------------------------------
def add_transaction_to_selected_sheet(gc, sheet_id, worksheet_id, amount, description, fund_id, category_id, debit_account_id, credit_account_id, transaction_type, date_input, transaction_number, file_links="", origin_account="", destination_account="", transfer_type="external", payment_method="bank", reference_number=""):
    """
    Add double-entry transaction to a specific selected sheet and worksheet
    Creates TWO entries: one debit entry and one credit entry
    Args:
        gc: Google Sheets client
        sheet_id: ID of the specific sheet
        worksheet_id: ID of the specific worksheet (not title)
        amount: Amount from form (always positive)
        description: Description from form
        fund_id: ID of the fund from form
        category_id: ID of the category from form
        debit_account_id: ID of the account to be debited
        credit_account_id: ID of the account to be credited
        transaction_type: Legacy parameter (kept for compatibility)
        date_input: Date from form in DD/MM/YY format
        transaction_number: Pre-generated transaction number from form
        file_links: Optional dict of file links with keys: bills, red_bills, bank_statement, documentation
        origin_account: Legacy parameter (kept for compatibility)
        destination_account: Legacy parameter (kept for compatibility)
        transfer_type: Legacy parameter (kept for compatibility)
        payment_method: Payment method ("bank" or "cash")
        reference_number: Bank transaction reference number
    Returns: True if successful, False otherwise
    """
    try:
        print(f"DEBUG: add_transaction_to_selected_sheet called with:")
        print(f"  - sheet_id: {sheet_id}")
        print(f"  - worksheet_id: {worksheet_id}")
        print(f"  - amount: {amount}")
        print(f"  - transaction_type: {transaction_type}")
        print(f"  - transfer_type: {transfer_type}")
        print(f"  - origin_account: {origin_account}")
        print(f"  - destination_account: {destination_account}")
        print(f"  - fund_id: {fund_id}")
        print(f"  - category_id: {category_id}")
        print(f"  - date_input: {date_input}")
        print(f"  - transaction_number: {transaction_number}")
        print(f"  - file_links: {file_links}")
        print(f"  - description: {description}")
        # Use the centralized sheet opening function
        print(f"DEBUG: Opening sheet with ID: {sheet_id}")
        sheet = get_sheet_by_id(gc, sheet_id)
        if sheet is None:
            print("ERROR: Could not open sheet")
            return False
        print(f"DEBUG: Successfully opened sheet: {sheet.title}")
        
        # Get worksheet by title (since we're now passing worksheet titles)
        print(f"DEBUG: Getting worksheet by title: {worksheet_id}")
        try:
            worksheet = sheet.worksheet(worksheet_id)
            print(f"DEBUG: Found worksheet by title: {worksheet.title}")
        except Exception as e:
            print(f"ERROR: Could not get worksheet by title '{worksheet_id}': {e}")
            worksheets = sheet.worksheets()
            print(f"DEBUG: Available worksheets: {[ws.title for ws in worksheets]}")
            return False
        
        # Use the pre-generated transaction number from the form
        if not transaction_number:
            # Fallback: generate new transaction number if none provided
            now = datetime.now()
            transaction_number = now.strftime('%d%m%y-%H%M%S')
            print(f"Warning: No transaction number provided, generated: {transaction_number}")
        
        # Format the date input to DD/MM/YY format
        try:
            # Parse the date input and convert to DD/MM/YY format
            if date_input:
                # If date_input is in YYYY-MM-DD format (from HTML date picker), convert it
                if '-' in date_input and len(date_input.split('-')[0]) == 4:
                    # Parse YYYY-MM-DD and convert to DD/MM/YY
                    parsed_date = datetime.strptime(date_input, '%Y-%m-%d')
                    formatted_date = parsed_date.strftime('%d/%m/%y')
                else:
                    # If already in DD/MM/YY format, use as is
                    formatted_date = date_input
            else:
                # If no date provided, use today's date in DD/MM/YY format
                formatted_date = now.strftime('%d/%m/%y')
        except Exception as e:
            # Fallback to today's date if parsing fails
            formatted_date = now.strftime('%d/%m/%y')
            print(f"Warning: Could not parse date '{date_input}', using today's date: {formatted_date}")
        
        # Extract month and year for analysis columns
        try:
            # Parse the formatted date to extract month and year
            if '-' in date_input and len(date_input.split('-')[0]) == 4:
                # Date is in YYYY-MM-DD format
                parsed_date = datetime.strptime(date_input, '%Y-%m-%d')
            else:
                # Date is in DD/MM/YY format
                parsed_date = datetime.strptime(formatted_date, '%d/%m/%y')
            
            # Generate month, year, and month-year values
            month_name = parsed_date.strftime('%B')  # e.g., "September", "October"
            year_value = str(parsed_date.year)       # e.g., "2025", "2024"
            month_year = f"{month_name}-{year_value}"  # e.g., "September-2025", "October-2025"
            
        except Exception as e:
            # Fallback to current month/year if parsing fails
            month_name = now.strftime('%B')  # Full month name
            year_value = str(now.year)
            month_year = f"{month_name}-{year_value}"
            print(f"Warning: Could not parse date for month/year extraction, using current: {month_year}")
        
        # Convert amount to number (not string)
        try:
            numeric_amount = float(amount)
        except ValueError:
            raise Exception(f"Invalid amount: {amount}. Please enter a valid number.")
        
        # Get fund name from fund ID (or use directly if it's "Internal Transfer")
        print(f"DEBUG: Looking up fund name for fund_id: {fund_id}")
        if fund_id == "Internal Transfer":
            fund_name = "Internal Transfer"
            print(f"DEBUG: Using hardcoded fund name: {fund_name}")
        else:
            fund_name = get_fund_name_by_id(gc, fund_id)
            print(f"DEBUG: Found fund name: {fund_name}")
        
        # Get category name from category ID (or use directly if it's "Internal Transfer")
        print(f"DEBUG: Looking up category name for category_id: {category_id}")
        if category_id == "Internal Transfer":
            category_name = "Internal Transfer"
            print(f"DEBUG: Using hardcoded category name: {category_name}")
        else:
            category_name = get_category_name_by_code(gc, category_id)
            print(f"DEBUG: Found category name: {category_name}")
        
        # Get account names from account IDs
        print(f"DEBUG: Looking up debit account name for debit_account_id: {debit_account_id}")
        debit_account_name = get_account_name_by_code(gc, debit_account_id)
        print(f"DEBUG: Found debit account name: {debit_account_name}")
        
        print(f"DEBUG: Looking up credit account name for credit_account_id: {credit_account_id}")
        credit_account_name = get_account_name_by_code(gc, credit_account_id)
        print(f"DEBUG: Found credit account name: {credit_account_name}")
        
        # Handle multiple file links - create HYPERLINK formulas for each file type
        # Map file types to column names in the sheet
        file_type_mapping = {
            'bills': 'Bill',
            'red_bills': 'Red Bill', 
            'documentation': 'Doc'
        }
        
        # Initialize all file link values
        file_link_values = {}
        for file_type, column_name in file_type_mapping.items():
            file_link_values[file_type] = ""
        
        # Process each file type if provided
        if isinstance(file_links, dict):
            for file_type, file_data in file_links.items():
                if isinstance(file_data, dict) and 'filename' in file_data and 'url' in file_data:
                    # Create the HYPERLINK formula with ✔ as display text
                    file_link_values[file_type] = f'=HYPERLINK("{file_data["url"]}", "✔")'
                    print(f"DEBUG: Created link for {file_type}: {file_link_values[file_type]}")
        
        print(f"DEBUG: File link values: {file_link_values}")
        
        # Get worksheet title for reference
        worksheet_title = worksheet.title
        print(f"DEBUG: Worksheet title: {worksheet_title}")
        
        # Reference number will be stored in its own column (M)
        print(f"DEBUG: Reference number: {reference_number}")
        
        # DOUBLE-ENTRY BOOKKEEPING: Create TWO entries
        print(f"DEBUG: Creating double-entry bookkeeping entries")
        
        # Generate Offset text for Expenses and Revenues accounts
        debit_offset = generate_offset_text(debit_account_name, credit_account_name)
        credit_offset = generate_offset_text(credit_account_name, debit_account_name)
        
        print(f"DEBUG: Offset text generation:")
        print(f"  - Debit account: {debit_account_name} → Offset: '{debit_offset}'")
        print(f"  - Credit account: {credit_account_name} → Offset: '{credit_offset}'")
        
        # Entry 1: DEBIT entry (amount goes in Debit column)
        debit_row = [
            transaction_number,    # A: Transaction Number
            formatted_date,        # B: Date
            month_name,           # C: Month (e.g., "September")
            year_value,           # D: Year (e.g., "2025")
            fund_name,            # E: Funds
            debit_account_name,   # F: Account (the account being debited)
            category_name,        # G: Category
            numeric_amount,       # H: Debit (VND) - amount goes here
            "",                   # I: Credit (VND) - empty for debit entry
            debit_offset,         # J: Offset
            payment_method,       # K: Payment Method
            description,          # L: Description
            reference_number,     # M: Bank Transaction Number
            file_link_values.get('bills', ''),           # N: Bill
            file_link_values.get('red_bills', ''),       # O: Red Bill
            file_link_values.get('documentation', '')    # P: Doc
        ]
        
        # Entry 2: CREDIT entry (amount goes in Credit column)
        credit_row = [
            transaction_number,    # A: Transaction Number
            formatted_date,        # B: Date
            month_name,           # C: Month (e.g., "September")
            year_value,           # D: Year (e.g., "2025")
            fund_name,            # E: Funds
            credit_account_name,  # F: Account (the account being credited)
            category_name,        # G: Category
            "",                   # H: Debit (VND) - empty for credit entry
            numeric_amount,       # I: Credit (VND) - amount goes here
            credit_offset,        # J: Offset
            payment_method,       # K: Payment Method
            description,          # L: Description
            reference_number,     # M: Bank Transaction Number
            file_link_values.get('bills', ''),           # N: Bill
            file_link_values.get('red_bills', ''),       # O: Red Bill
            file_link_values.get('documentation', '')    # P: Doc
        ]
        
        print(f"DEBUG: Prepared DEBIT entry:")
        for i, cell in enumerate(debit_row):
            column_letter = chr(65 + i)  # A=65, B=66, etc.
            print(f"  - Column {column_letter}: '{cell}' (type: {type(cell)})")
            
        print(f"DEBUG: Prepared CREDIT entry:")
        for i, cell in enumerate(credit_row):
            column_letter = chr(65 + i)  # A=65, B=66, etc.
            print(f"  - Column {column_letter}: '{cell}' (type: {type(cell)})")
        
        # Add both entries to the worksheet
        print(f"DEBUG: Adding DEBIT entry to worksheet: {worksheet.title}")
        worksheet.append_row(debit_row)
        print(f"DEBUG: DEBIT entry successfully added")
        
        print(f"DEBUG: Adding CREDIT entry to worksheet: {worksheet.title}")
        worksheet.append_row(credit_row)
        print(f"DEBUG: CREDIT entry successfully added")
        
        # If we added any HYPERLINK formulas, we need to format them properly with USER_ENTERED for both entries
        has_hyperlinks = any(value.startswith('=HYPERLINK(') for value in file_link_values.values())
        if has_hyperlinks:
            print(f"DEBUG: Processing HYPERLINK formulas: {file_link_values}")
            # Get the current row count to find the last two rows we just added
            all_values = worksheet.get_all_values()
            last_row = len(all_values)
            
            # Update HYPERLINK formulas for all file types in both entries
            # Column mapping: N=Bill, O=Red Bill, P=Doc (updated column order with Bank Transaction Number in M)
            column_mapping = {
                'bills': 'N',
                'red_bills': 'O', 
                'documentation': 'P'
            }
            
            for file_type, column_letter in column_mapping.items():
                link_value = file_link_values.get(file_type, '')
                if link_value.startswith('=HYPERLINK('):
                    # Update HYPERLINK for debit entry (second to last row)
                    debit_cell_address = f'{column_letter}{last_row - 1}'
                    print(f"DEBUG: Updating debit entry cell {debit_cell_address} with {file_type} HYPERLINK formula")
                    worksheet.update(debit_cell_address, link_value, value_input_option='USER_ENTERED')
                    
                    # Update HYPERLINK for credit entry (last row)
                    credit_cell_address = f'{column_letter}{last_row}'
                    print(f"DEBUG: Updating credit entry cell {credit_cell_address} with {file_type} HYPERLINK formula")
                    worksheet.update(credit_cell_address, link_value, value_input_option='USER_ENTERED')
            
            print(f"DEBUG: HYPERLINK formulas updated successfully for both entries")
        
        print(f"DEBUG: Transaction completed successfully!")
        return True
    except Exception as e:
        print(f"ERROR: Exception occurred in add_transaction_to_selected_sheet:")
        print(f"  - Error message: {e}")
        print(f"  - Error type: {type(e).__name__}")
        import traceback
        print(f"  - Full traceback:")
        traceback.print_exc()
        return False

# =============================================================================
# FUNDS REFERENCE FUNCTIONS
# =============================================================================


# Get Fund Name By ID
# -------------------
def get_fund_name_by_id(gc, fund_id):
    """
    Get fund name by ID for transaction saving
    Args:
        gc: Google Sheets client (kept for compatibility but not used)
        fund_id: ID of the fund to look up
    Returns: Fund name or "Unknown Fund" if not found
    """
    try:
        print(f"DEBUG: get_fund_name_by_id called with fund_id: {fund_id}")
        
        # Load funds from JSON file instead of Google Sheets
        import json
        import os
        
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(current_dir, 'data', 'funds.json')
        
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


# =============================================================================
# ACCOUNTS REFERENCE FUNCTIONS
# =============================================================================


# Get Account Name By Code
# ------------------------
def get_account_name_by_code(gc, account_code):
    """
    Get account name by code for transaction saving
    Args:
        gc: Google Sheets client (kept for compatibility but not used)
        account_code: Code of the account to look up
    Returns: Account name or "Unknown Account" if not found
    """
    try:
        print(f"DEBUG: get_account_name_by_code called with account_code: {account_code}")
        
        # Load accounts from JSON file instead of Google Sheets
        import json
        import os
        
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(current_dir, 'data', 'accounts.json')
        
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        accounts = data.get('accounts', [])
        print(f"DEBUG: Retrieved {len(accounts)} account records from JSON")
        
        for i, acc in enumerate(accounts):
            print(f"DEBUG: Account {i}: Code='{acc.get('code')}', Name='{acc.get('name')}'")
            if str(acc.get('code', '')) == str(account_code):
                print(f"DEBUG: Found matching account: {acc.get('name')}")
                return acc.get('name', '')
        
        print(f"WARNING: Account Code {account_code} not found")
        print(f"DEBUG: Available account codes: {[str(acc.get('code', '')) for acc in accounts]}")
        return "Unknown Account"
        
    except Exception as e:
        print(f"ERROR in get_account_name_by_code: {e}")
        import traceback
        traceback.print_exc()
        return "Unknown Account"


# =============================================================================
# CATEGORIES REFERENCE FUNCTIONS
# =============================================================================


# Get Category Name By Code
# ----------------------------
def get_category_name_by_code(gc, category_code):
    """
    Get category name by code for transaction saving
    Args:
        gc: Google Sheets client (kept for compatibility but not used)
        category_code: Code of the category to look up
    Returns: Category name or "Unknown Category" if not found
    """
    try:
        print(f"DEBUG: get_category_name_by_code called with category_code: {category_code}")
        
        # Load categories from JSON file instead of Google Sheets
        import json
        import os
        
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(current_dir, 'data', 'categories.json')
        
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



