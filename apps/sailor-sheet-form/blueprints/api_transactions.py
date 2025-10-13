"""
Transaction API endpoints.
Handles transaction-related API routes.
"""

from flask import Blueprint, request, jsonify
from services.transaction_service import TransactionService
from services.sheets_service import SheetsService

# Create blueprint
api_transactions_bp = Blueprint('api_transactions', __name__, url_prefix='/api')

# Initialize services
transaction_service = TransactionService()
sheets_service = SheetsService()


@api_transactions_bp.route('/submit_transaction', methods=['POST'])
def submit_transaction():
    """
    API endpoint for AJAX form submission
    Returns JSON response instead of redirecting
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Use transaction service to handle the submission
        result = transaction_service.submit_transaction(data)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
                
    except Exception as e:
        print(f"❌ ERROR in API submit_transaction: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_transactions_bp.route('/search_transaction', methods=['POST'])
def search_transaction():
    """
    API endpoint for searching transactions in Google Sheets.
    
    Receives: JSON with sheet_type and transaction_number
    Returns: JSON with transaction data or error message
    """
    try:
        # Get data from request
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        sheet_type = data.get('sheet_type', 'vn')
        transaction_number = data.get('transaction_number')
        
        # Validate required fields
        if not transaction_number:
            return jsonify({
                'success': False,
                'error': 'Transaction number is required'
            }), 400
        
        print(f"\n" + "="*50)
        print(f"DEBUG: SEARCH TRANSACTION API CALLED")
        print(f"  - Sheet Type: {sheet_type}")
        print(f"  - Transaction Number: {transaction_number}")
        print(f"="*50)
        
        # Use sheets service to search
        result = sheets_service.search_transaction(sheet_type, transaction_number)
        
        if result:
            print(f"DEBUG: Transaction found with {len(result)} fields")
            return jsonify({
                'success': True,
                'data': result,
                'message': 'Transaction found successfully'
            })
        else:
            print(f"DEBUG: Transaction not found")
            return jsonify({
                'success': False,
                'error': f'Transaction {transaction_number} not found in {sheet_type.upper()} sheet'
            }), 404
            
    except Exception as e:
        print(f"ERROR in api_search_transaction: {e}")
        return jsonify({
            'success': False,
            'error': f'Search failed: {str(e)}'
        }), 500


@api_transactions_bp.route('/update_document', methods=['POST'])
def update_document():
    """
    API endpoint for updating document links in Google Sheets.
    
    Receives: JSON with sheet_type, transaction_number, document_type, and file_url
    Returns: JSON with success status
    """
    try:
        # Get data from request
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        sheet_type = data.get('sheet_type', 'vn')
        transaction_number = data.get('transaction_number')
        document_type = data.get('document_type')  # 'bill', 'redBill', 'documentation'
        file_url = data.get('file_url')
        
        # Validate required fields
        if not all([transaction_number, document_type, file_url]):
            return jsonify({
                'success': False,
                'error': 'Transaction number, document type, and file URL are required'
            }), 400
        
        print(f"\n" + "="*50)
        print(f"DEBUG: UPDATE DOCUMENT API CALLED")
        print(f"  - Sheet Type: {sheet_type}")
        print(f"  - Transaction Number: {transaction_number}")
        print(f"  - Document Type: {document_type}")
        print(f"  - File URL: {file_url}")
        print(f"="*50)
        
        # Use sheets service to update document
        result = sheets_service.update_document_link(sheet_type, transaction_number, document_type, file_url)
        
        if result:
            print(f"DEBUG: Document updated successfully")
            return jsonify({
                'success': True,
                'message': f'{document_type} updated successfully for transaction {transaction_number}'
            })
        else:
            print(f"DEBUG: Document update failed")
            return jsonify({
                'success': False,
                'error': f'Failed to update {document_type} for transaction {transaction_number}. Check server logs for details.'
            }), 500
                
    except Exception as e:
        print(f"ERROR in api_update_document: {e}")
        return jsonify({
            'success': False,
            'error': f'Document update failed: {str(e)}'
        }), 500
