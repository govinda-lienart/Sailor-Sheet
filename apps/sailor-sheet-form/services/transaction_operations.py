"""
Transaction Operations Service
Handles transaction creation, management, and offset text generation.
"""

from datetime import datetime

class TransactionOperations:
    """Service for transaction-related operations."""
    
    def __init__(self, gc):
        """Initialize with Google Sheets client."""
        self.gc = gc
        # Import here to avoid circular imports
        from .reference_lookups import ReferenceLookups
        from .worksheet_operations import WorksheetOperations
        self.reference_lookups = ReferenceLookups(gc)
        self.worksheet_ops = WorksheetOperations(gc)
    
    def generate_offset_text(self, account_name, counter_account_name):
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

    def add_transaction_to_selected_sheet(self, sheet_id, worksheet_id, amount, description, fund_id, category_id, debit_account_id, credit_account_id, transaction_type, date_input, transaction_number, file_links="", origin_account="", destination_account="", transfer_type="external", payment_method="bank", reference_number="", sub_category_id=""):
        """
        Add double-entry transaction to a specific selected sheet and worksheet
        Creates TWO entries: one debit entry and one credit entry
        Args:
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
            print(f"  - file_links type: {type(file_links)}")
            if isinstance(file_links, dict):
                for key, value in file_links.items():
                    print(f"    - {key}: {value}")
            print(f"  - description: {description}")
            
            # Use the centralized sheet opening function
            print(f"DEBUG: Opening sheet with ID: {sheet_id}")
            sheet = self.worksheet_ops.get_sheet_by_id(sheet_id)
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
                fund_name = self.reference_lookups.get_fund_name_by_id(fund_id)
                print(f"DEBUG: Found fund name: {fund_name}")
            
            # Get category name from category ID (or use directly if it's "Internal Transfer")
            print(f"DEBUG: Looking up category name for category_id: {category_id}")
            if category_id == "Internal Transfer":
                category_name = "Internal Transfer"
                print(f"DEBUG: Using hardcoded category name: {category_name}")
            else:
                category_name = self.reference_lookups.get_category_name_by_code(category_id)
                print(f"DEBUG: Found category name: {category_name}")
            
            # Get sub-category name from sub-category ID
            print(f"DEBUG: Looking up sub-category name for sub_category_id: {sub_category_id}")
            sub_category_name = self.reference_lookups.get_sub_category_name_by_id(sub_category_id)
            print(f"DEBUG: Found sub-category name: {sub_category_name}")
            
            # Get account names from account IDs
            print(f"DEBUG: Looking up debit account name for debit_account_id: {debit_account_id}")
            debit_account_name = self.reference_lookups.get_account_name_by_code(debit_account_id)
            print(f"DEBUG: Found debit account name: {debit_account_name}")
            
            print(f"DEBUG: Looking up credit account name for credit_account_id: {credit_account_id}")
            credit_account_name = self.reference_lookups.get_account_name_by_code(credit_account_id)
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
                print(f"DEBUG: Processing file_links dict with {len(file_links)} items")
                for file_type, file_data in file_links.items():
                    print(f"DEBUG: Processing file_type: {file_type}, file_data: {file_data}")
                    if isinstance(file_data, dict) and 'filename' in file_data and 'url' in file_data:
                        # Create the HYPERLINK formula with ✔ as display text (using semicolon separator)
                        url = file_data["url"].strip()
                        # Make sure the URL doesn't have any quotes or special characters that could break the formula
                        if '"' in url:
                            url = url.replace('"', '')
                        file_link_values[file_type] = f'=HYPERLINK("{url}"; "✔")'
                        print(f"DEBUG: Created HYPERLINK for {file_type}")
                        print(f"DEBUG:   URL: {url}")
                        print(f"DEBUG:   Formula: {file_link_values[file_type]}")
                    else:
                        print(f"DEBUG: Skipping {file_type} - invalid file_data format")
            
            print(f"DEBUG: File link values: {file_link_values}")
            
            # Get worksheet title for reference
            worksheet_title = worksheet.title
            print(f"DEBUG: Worksheet title: {worksheet_title}")
            
            # Reference number will be stored in its own column (M)
            print(f"DEBUG: Reference number: {reference_number}")
            
            # DOUBLE-ENTRY BOOKKEEPING: Create TWO entries
            print(f"DEBUG: Creating double-entry bookkeeping entries")
            
            # Generate Offset text for Expenses and Revenues accounts
            debit_offset = self.generate_offset_text(debit_account_name, credit_account_name)
            credit_offset = self.generate_offset_text(credit_account_name, debit_account_name)
            
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
                sub_category_name,    # H: Sub-Category
                numeric_amount,       # I: Debit (VND) - amount goes here
                "",                   # J: Credit (VND) - empty for debit entry
                debit_offset,         # K: Offset
                payment_method,       # L: Payment Method
                description,          # M: Description
                reference_number,     # N: Bank Transaction Number
                file_link_values.get('bills', ''),           # O: Bill
                file_link_values.get('red_bills', ''),       # P: Red Bill
                file_link_values.get('documentation', '')    # Q: Doc
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
                sub_category_name,    # H: Sub-Category
                "",                   # I: Debit (VND) - empty for credit entry
                numeric_amount,       # J: Credit (VND) - amount goes here
                credit_offset,        # K: Offset
                payment_method,       # L: Payment Method
                description,          # M: Description
                reference_number,     # N: Bank Transaction Number
                file_link_values.get('bills', ''),           # O: Bill
                file_link_values.get('red_bills', ''),       # P: Red Bill
                file_link_values.get('documentation', '')    # Q: Doc
            ]
            
            print(f"DEBUG: Prepared DEBIT entry:")
            column_names = ['Transaction', 'Date', 'Month', 'Year', 'Funds', 'Account', 'Category', 'Sub-Category', 
                           'Debit (VND)', 'Credit (VND)', 'Offset', 'Payment', 'Description', 'Bank Transaction', 'Bill', 'Red Bill', 'Doc']
            for i, cell in enumerate(debit_row):
                column_letter = chr(65 + i)  # A=65, B=66, etc.
                column_name = column_names[i] if i < len(column_names) else f'Column{i}'
                if 'HYPERLINK' in str(cell):
                    print(f"  - Column {column_letter} ({column_name}): HYPERLINK FORMULA - {cell[:100]}...")
                else:
                    print(f"  - Column {column_letter} ({column_name}): '{cell}' (type: {type(cell).__name__})")
                
            print(f"DEBUG: Prepared CREDIT entry:")
            for i, cell in enumerate(credit_row):
                column_letter = chr(65 + i)  # A=65, B=66, etc.
                column_name = column_names[i] if i < len(column_names) else f'Column{i}'
                if 'HYPERLINK' in str(cell):
                    print(f"  - Column {column_letter} ({column_name}): HYPERLINK FORMULA - {cell[:100]}...")
                else:
                    print(f"  - Column {column_letter} ({column_name}): '{cell}' (type: {type(cell).__name__})")
            
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
                # Column mapping: O=Bill, P=Red Bill, Q=Doc (MUST MATCH update_document_link function!)
                # A=Transaction, B=Date, C=Month, D=Year, E=Funds, F=Account, G=Category, H=Sub-Category,
                # I=Debit, J=Credit, K=Offset, L=Payment, M=Description, N=Bank Transaction, O=Bill, P=Red Bill, Q=Doc
                column_mapping = {
                    'bills': 'O',           # Bill column - MATCHES update_document_link
                    'red_bills': 'P',       # Red Bill column - MATCHES update_document_link  
                    'documentation': 'Q'    # Doc column - MATCHES update_document_link
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
