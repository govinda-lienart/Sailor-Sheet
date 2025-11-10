"""
Sheets Operations Service
Handles Google Sheets search, document updates, and sheet management operations.
"""

from datetime import datetime

class SheetsOperations:
    """Service for Google Sheets operations like search and document updates."""
    
    def __init__(self, gc):
        """Initialize with Google Sheets client."""
        self.gc = gc
    
    def search_transaction_tool(self, sheet_type, transaction_number):
        """
        Efficiently search for a transaction by number without downloading all data.
        
        Method 1: Get only transaction number column first, then fetch specific row.
        This avoids downloading all rows and columns.
        
        Args:
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
            sheet = self.gc.open_by_key(sheet_id)
            
            # Find the Master Ledger worksheet based on sheet type
            worksheet = None
            all_worksheets = sheet.worksheets()
            
            # Determine the expected worksheet name based on sheet type
            if sheet_type == 'vn':
                expected_worksheet_name = 'VN - Master Ledger'
            elif sheet_type == 'be':
                expected_worksheet_name = 'BE - Master Ledger'
            else:
                expected_worksheet_name = 'Master Ledger'
            
            # Search for the Master Ledger worksheet
            for ws in all_worksheets:
                if ws.title == expected_worksheet_name or 'Master Ledger' in ws.title:
                    worksheet = ws
                    print(f"DEBUG: Found Master Ledger worksheet: {ws.title}")
                    break
            
            # If not found, fall back to first worksheet
            if worksheet is None:
                worksheet = sheet.sheet1
                print(f"DEBUG: Master Ledger worksheet '{expected_worksheet_name}' not found, using first worksheet")
            
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

    def update_document_link(self, sheet_type, transaction_number, document_type, file_url):
        """
        Update document link in Google Sheets for both debit and credit rows.
        
        Args:
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
            sheet = self.gc.open_by_key(sheet_id)
            
            # Find the Master Ledger worksheet based on sheet type (same logic as search function)
            worksheet = None
            all_worksheets = sheet.worksheets()
            
            # Determine the expected worksheet name based on sheet type
            if sheet_type == 'vn':
                expected_worksheet_name = 'VN - Master Ledger'
            elif sheet_type == 'be':
                expected_worksheet_name = 'BE - Master Ledger'
            else:
                expected_worksheet_name = 'Master Ledger'
            
            # Search for the Master Ledger worksheet
            for ws in all_worksheets:
                if ws.title == expected_worksheet_name or 'Master Ledger' in ws.title:
                    worksheet = ws
                    print(f"DEBUG: UPDATE FUNCTION - Found Master Ledger worksheet: {ws.title}")
                    break
            
            # If not found, fall back to first worksheet
            if worksheet is None:
                worksheet = sheet.sheet1
                print(f"DEBUG: UPDATE FUNCTION - Master Ledger worksheet '{expected_worksheet_name}' not found, using first worksheet")
            
            print(f"DEBUG: UPDATE FUNCTION - Opened sheet: {sheet.title}")
            print(f"DEBUG: UPDATE FUNCTION - Using worksheet: {worksheet.title}")
            print(f"DEBUG: UPDATE FUNCTION - Worksheet ID: {worksheet.id}")
            
            # Get headers to find the correct column
            headers = worksheet.row_values(1)
            print(f"DEBUG: Headers: {headers}")
            
            # Find the document column index
            # IMPORTANT: Belgium and Vietnam have DIFFERENT column structures!
            # BELGIUM: N=Bank Transaction Number, O=Bill, P=Bank Statement, Q=Doc
            # VIETNAM: N=Bank Transaction, O=Bill, P=Red Bill, Q=Doc
            document_column_map = {
                'bill': ['Bill', 'bill', 'BILL'],
                'redBill': ['Red Bill', 'Red BIll', 'Red Bills', 'red bill', 'RED BILL', 'Red Bill '],
                'bankStatement': ['Bank Statement', 'bank statement', 'BANK STATEMENT'],  # Belgium only
                'documentation': ['Doc', 'Documentation', 'doc', 'DOC', 'Documentation ']
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
                
                # Fallback: Use known column positions - COUNTRY SPECIFIC!
                # BELGIUM: O=Bill, P=Bank Statement, Q=Doc
                # VIETNAM: O=Bill, P=Red Bill, Q=Doc
                if sheet_type.lower() == 'be':
                    fallback_columns = {
                        'bill': 14,              # Column O (0-indexed)
                        'bankStatement': 15,     # Column P (0-indexed) - Belgium only
                        'documentation': 16      # Column Q (0-indexed)
                    }
                else:  # Vietnam
                    fallback_columns = {
                        'bill': 14,              # Column O (0-indexed)
                        'redBill': 15,           # Column P (0-indexed) - Vietnam only
                        'documentation': 16      # Column Q (0-indexed)
                    }
                
                if document_type in fallback_columns:
                    column_index = fallback_columns[document_type]
                    target_column = f"Column {chr(65 + column_index)}"  # Convert to letter (O, P, Q)
                    print(f"DEBUG: Using fallback column {target_column} (index {column_index}) for {document_type}")
                else:
                    print(f"ERROR: No fallback available for document type: {document_type}")
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
            
            # Create HYPERLINK formula using semicolon separator (working format)
            hyperlink_formula = f'=HYPERLINK("{file_url}"; "✔")'
            print(f"DEBUG: Created HYPERLINK formula: {hyperlink_formula}")
            
            # Map document types to column letters - COUNTRY SPECIFIC!
            # BELGIUM: O=Bill, P=Bank Statement, Q=Doc
            # VIETNAM: O=Bill, P=Red Bill, Q=Doc
            if sheet_type.lower() == 'be':
                column_mapping = {
                    'bill': 'O',
                    'bankStatement': 'P',     # Belgium: Bank Statement in column P
                    'documentation': 'Q'
                }
            else:  # Vietnam
                column_mapping = {
                    'bill': 'O',
                    'redBill': 'P',           # Vietnam: Red Bill in column P
                    'documentation': 'Q'
                }
            
            # Get the column letter for this document type
            column_letter = column_mapping.get(document_type)
            if not column_letter:
                print(f"ERROR: Invalid document type '{document_type}' for sheet '{sheet_type}'")
                print(f"DEBUG: Valid types for {sheet_type}: {list(column_mapping.keys())}")
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

    def get_available_sheets(self):
        """
        Get list of available Google Sheets for dropdown selection
        Returns: List of dictionaries with sheet info
        """
        try:
            # Get all spreadsheets you have access to
            all_sheets = self.gc.openall()
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

    def get_sheet_by_id(self, sheet_id):
        """
        Get a specific sheet by its ID
        Args:
            sheet_id: ID of the sheet to retrieve
        Returns: Sheet object or None if not found
        """
        try:
            sheet = self.gc.open_by_key(sheet_id)
            return sheet
        except Exception as e:
            print(f"Error getting sheet by ID: {e}")
            return None

    def get_worksheets_from_sheet(self, sheet_id):
        """
        Get list of worksheets (subsheets) from a specific Google Sheet
        Args:
            sheet_id: ID of the specific sheet
        Returns: List of dictionaries with worksheet info including account names
        """
        try:
            # Use the centralized sheet opening function
            sheet = self.get_sheet_by_id(sheet_id)
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
