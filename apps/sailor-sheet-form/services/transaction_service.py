"""
Transaction service for handling transaction-related business logic.
"""

from datetime import datetime
from services.sheets_service import SheetsService


class TransactionService:
    """Service class for transaction operations."""
    
    def __init__(self):
        """Initialize the transaction service."""
        self.sheets_service = SheetsService()
    
    def submit_transaction(self, data):
        """
        Submit a transaction with all business logic.
        """
        try:
            # Extract data from the JSON request
            selected_sheet_id = data.get('sheet_id')
            selected_worksheet_title = data.get('worksheet_name')
            amount = data.get('amount')
            description = data.get('description')
            fund_id = data.get('fund_id')
            category_id = data.get('category_id')
            sub_category_id = data.get('sub_category_id')
            transaction_type = data.get('transaction_type', 'external')
            
            # Get account IDs for regular transactions
            debit_account_id = data.get('regular_debit_account_id')
            credit_account_id = data.get('regular_credit_account_id')
            
            date_input = data.get('date_input', '')
            transaction_number = data.get('transaction_number', '')
            reference_number = data.get('reference_number', '')
            payment_method = data.get('payment_method', 'bank')
            include_bank_fees = data.get('include_bank_fees', False)
            
            # Handle file links
            file_links = self._extract_file_links(data)
            
            # Validate required fields
            if not all([selected_sheet_id, selected_worksheet_title, amount, description, fund_id, category_id, debit_account_id, credit_account_id]):
                return {
                    'success': False,
                    'error': 'Missing required fields'
                }
            
            # Regular single-entry transaction
            transfer_type = data.get('transfer_type', 'external')
            origin_account = data.get('origin_account', '')
            destination_account = data.get('destination_account', '')
            
            # Prepare transaction data
            transaction_data = {
                'sheet_id': selected_sheet_id,
                'worksheet_name': selected_worksheet_title,
                'amount': amount,
                'description': description,
                'fund_id': fund_id,
                'category_id': category_id,
                'debit_account_id': debit_account_id,
                'credit_account_id': credit_account_id,
                'transaction_type': transaction_type,
                'date_input': date_input,
                'transaction_number': transaction_number,
                'file_links': file_links,
                'origin_account': origin_account,
                'destination_account': destination_account,
                'transfer_type': transfer_type,
                'payment_method': payment_method,
                'reference_number': reference_number,
                'sub_category_id': sub_category_id
            }
            
            # Submit main transaction
            transaction_result = self.sheets_service.add_transaction(transaction_data)
            
            if not transaction_result:
                return {
                    'success': False,
                    'error': 'Error adding transaction!'
                }
            
            # Handle bank fee transactions if checkbox is checked
            bank_fee_results = []
            if include_bank_fees:
                bank_fee_results = self._create_bank_fee_transactions(
                    transaction_data, transaction_number
                )
            
            # Prepare response message
            message = self._prepare_success_message(transaction_number, include_bank_fees, bank_fee_results)
            
            return {
                'success': True,
                'message': message,
                'data': {
                    'transaction_number': transaction_number,
                    'amount': amount,
                    'type': transaction_type,
                    'bank_fees_created': len([r for r in bank_fee_results if r['success']]) if include_bank_fees else 0
                }
            }
                
        except Exception as e:
            print(f"❌ ERROR in submit_transaction: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_file_links(self, data):
        """Extract file links from form data."""
        file_links = {}
        
        if data.get('bills_file_link') and data.get('bills_file_name'):
            file_links['bills'] = {
                'url': data.get('bills_file_link'),
                'filename': data.get('bills_file_name')
            }
        if data.get('red_bills_file_link') and data.get('red_bills_file_name'):
            file_links['red_bills'] = {
                'url': data.get('red_bills_file_link'),
                'filename': data.get('red_bills_file_name')
            }
        if data.get('documentation_file_link') and data.get('documentation_file_name'):
            file_links['documentation'] = {
                'url': data.get('documentation_file_link'),
                'filename': data.get('documentation_file_name')
            }
        
        return file_links
    
    def _create_bank_fee_transactions(self, transaction_data, main_transaction_number):
        """Create bank fee transactions."""
        print(f"🏦 Creating bank fee transactions for main transaction: {main_transaction_number}")
        
        bank_fee_results = []
        bank_fee_amounts = [5000, 500]
        bank_fee_category = "8001"  # Bank Fee category code
        
        for i, bank_fee_amount in enumerate(bank_fee_amounts, 1):
            # Generate new transaction number for bank fee with country prefix
            country_prefix = main_transaction_number.split('-')[0] if '-' in main_transaction_number else 'BE'
            bank_fee_txn_number = f"{country_prefix}-{datetime.now().strftime('%d%m%y')}-{datetime.now().strftime('%H%M%S')}{i}"
            
            # Create bank fee transaction data
            bank_fee_data = transaction_data.copy()
            bank_fee_data['transaction_number'] = bank_fee_txn_number
            bank_fee_data['category_id'] = bank_fee_category
            bank_fee_data['amount'] = bank_fee_amount
            bank_fee_data['description'] = transaction_data['description']
            
            # Create bank fee transaction
            bank_fee_result = self.sheets_service.add_transaction(bank_fee_data)
            
            bank_fee_results.append({
                'amount': bank_fee_amount,
                'transaction_number': bank_fee_txn_number,
                'success': bank_fee_result
            })
            
            if bank_fee_result:
                print(f"✅ Bank fee transaction {i} created: {bank_fee_amount} VND - {bank_fee_txn_number}")
            else:
                print(f"❌ Failed to create bank fee transaction {i}: {bank_fee_amount} VND")
        
        return bank_fee_results
    
    def _prepare_success_message(self, transaction_number, include_bank_fees, bank_fee_results):
        """Prepare success message for transaction submission."""
        if include_bank_fees:
            successful_bank_fees = [r for r in bank_fee_results if r['success']]
            message = f'Transaction submitted successfully! Main transaction: {transaction_number}'
            if successful_bank_fees:
                message += f', Bank fees: {len(successful_bank_fees)} transactions created'
        else:
            message = 'Transaction submitted successfully!'
        
        return message
