

# =============================================================================

# Import required libraries
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify  # Web framework
import os
import json

# Import custom modules
from config import initialize_sheets
from sheets_manager import get_available_sheets, get_worksheets_from_sheet, add_transaction_to_selected_sheet
import file_upload_manager

# Create Flask web application
app = Flask(__name__)

# =============================================================================
# ENVIRONMENT CONFIGURATION
# =============================================================================

# Get environment (development or production)
FLASK_ENV = os.environ.get('FLASK_ENV', 'development')

# Set debug mode based on environment
DEBUG_MODE = FLASK_ENV == 'development'

# Set maximum file size for uploads (16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Add secret key for flash messages and sessions
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

# =============================================================================
# INITIALIZE GOOGLE SHEETS
# =============================================================================

# Initialize Google Sheets connection
gc = initialize_sheets()

# =============================================================================
# JSON DATA LOADING FUNCTIONS - EFFICIENT ALTERNATIVE TO GOOGLE SHEETS
# =============================================================================

def load_json_data(filename):
    """
    Load data from JSON file in the data directory
    """
    try:
        file_path = os.path.join('data', filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            print(f"DEBUG: Successfully loaded {filename}")
            return data
    except FileNotFoundError:
        print(f"ERROR: JSON file {filename} not found")
        return {}
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {filename}: {e}")
        return {}
    except Exception as e:
        print(f"ERROR: Unexpected error loading {filename}: {e}")
        return {}

def get_funds_from_json():
    """
    Get funds list from JSON file instead of Google Sheets
    Returns list of fund dictionaries with id, name, color, active
    """
    try:
        data = load_json_data('funds.json')
        funds = data.get('funds', [])
        # Filter only active funds
        active_funds = [fund for fund in funds if fund.get('active', True)]
        print(f"DEBUG: Loaded {len(active_funds)} active funds from JSON")
        return active_funds
    except Exception as e:
        print(f"ERROR: Failed to load funds from JSON: {e}")
        return []

def get_categories_from_json():
    """
    Get categories list from JSON file instead of Google Sheets
    Returns list of category dictionaries with code, name, category, active
    """
    try:
        data = load_json_data('categories.json')
        categories = data.get('categories', [])
        # Filter only active categories
        active_categories = [cat for cat in categories if cat.get('active', True)]
        print(f"DEBUG: Loaded {len(active_categories)} active categories from JSON")
        return active_categories
    except Exception as e:
        print(f"ERROR: Failed to load categories from JSON: {e}")
        return []

def get_accounts_from_json():
    """
    Get accounts list from JSON file instead of Google Sheets
    Returns list of account dictionaries with code, name, type, active
    """
    try:
        data = load_json_data('accounts.json')
        accounts = data.get('accounts', [])
        # Filter only active accounts
        active_accounts = [acc for acc in accounts if acc.get('active', True)]
        print(f"DEBUG: Loaded {len(active_accounts)} active accounts from JSON")
        return active_accounts
    except Exception as e:
        print(f"ERROR: Failed to load accounts from JSON: {e}")
        return []

# =============================================================================
# API ROUTES - AJAX Endpoints
# =============================================================================

@app.route('/api/submit_transaction', methods=['POST'])
def api_submit_transaction():
    """
    API endpoint for AJAX form submission
    Returns JSON response instead of redirecting
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Extract data from the JSON request
        selected_sheet_id = data.get('sheet_id')
        selected_worksheet_title = data.get('worksheet_name')
        amount = data.get('amount')
        description = data.get('description')
        fund_id = data.get('fund_id')
        category_id = data.get('category_id')
        transaction_type = data.get('transaction_type', 'external')
        
        # Get account IDs based on transaction type
        if transaction_type == 'interbanking_transfer':
            debit_account_id = data.get('debit_account_id')
            credit_account_id = data.get('credit_account_id')
        else:
            debit_account_id = data.get('regular_debit_account_id')
            credit_account_id = data.get('regular_credit_account_id')
        
        date_input = data.get('date_input', '')
        transaction_number = data.get('transaction_number', '')
        reference_number = data.get('reference_number', '')
        payment_method = data.get('payment_method', 'bank')
        include_bank_fees = data.get('include_bank_fees', False)
        
        # Handle file links
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
        
        # Validate required fields
        if not all([selected_sheet_id, selected_worksheet_title, amount, description, fund_id, category_id, debit_account_id, credit_account_id]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        # Handle interbanking transfers (dual-entry)
        if transaction_type == 'interbanking_transfer':
            # Get Master Ledger data
            master_ledger_a_sheet_id = data.get('master_ledger_a_sheet_id')
            master_ledger_a_worksheet_id = data.get('master_ledger_a_worksheet_id')
            master_ledger_a_debit = data.get('master_ledger_a_debit_account_id')
            master_ledger_a_credit = data.get('master_ledger_a_credit_account_id')
            master_ledger_b_sheet_id = data.get('master_ledger_b_sheet_id')
            master_ledger_b_worksheet_id = data.get('master_ledger_b_worksheet_id')
            master_ledger_b_debit = data.get('master_ledger_b_debit_account_id')
            master_ledger_b_credit = data.get('master_ledger_b_credit_account_id')
            transfer_type = data.get('transfer_type', 'internal')
            interbanking_payment_method = data.get('interbanking_payment_method', 'bank')
            
            # Validate Master Ledger fields
            if not all([master_ledger_a_sheet_id, master_ledger_a_worksheet_id, master_ledger_a_debit, master_ledger_a_credit,
                       master_ledger_b_sheet_id, master_ledger_b_worksheet_id, master_ledger_b_debit, master_ledger_b_credit]):
                return jsonify({
                    'success': False,
                    'error': 'Please fill in all Master Ledger A and B fields for interbanking transfer!'
                }), 400
            
            # Create Master Ledger A entry
            master_ledger_a_result = add_transaction_to_selected_sheet(
                gc, master_ledger_a_sheet_id, master_ledger_a_worksheet_id, amount, 
                f"Interbanking Transfer - {description}", 
                fund_id, category_id, master_ledger_a_debit, master_ledger_a_credit, 
                transaction_type, date_input, transaction_number, file_links, 
                master_ledger_a_debit, master_ledger_a_credit, transfer_type, interbanking_payment_method, reference_number
            )
            
            # Create Master Ledger B entry
            master_ledger_b_result = add_transaction_to_selected_sheet(
                gc, master_ledger_b_sheet_id, master_ledger_b_worksheet_id, amount, 
                f"Interbanking Transfer - {description}", 
                fund_id, category_id, master_ledger_b_debit, master_ledger_b_credit, 
                transaction_type, date_input, transaction_number, file_links, 
                master_ledger_b_debit, master_ledger_b_credit, transfer_type, interbanking_payment_method, reference_number
            )
            
            if master_ledger_a_result and master_ledger_b_result:
                return jsonify({
                    'success': True,
                    'message': 'Interbanking transfer recorded in both Master Ledger A and B accounting systems!',
                    'data': {
                        'transaction_number': transaction_number,
                        'amount': amount,
                        'type': 'interbanking_transfer'
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Error creating dual-entry transaction! Please check both Master Ledger systems.'
                }), 500
        
        else:
            # Regular single-entry transaction
            transfer_type = data.get('transfer_type', 'external')
            origin_account = data.get('origin_account', '')
            destination_account = data.get('destination_account', '')
            
            transaction_result = add_transaction_to_selected_sheet(
                gc, selected_sheet_id, selected_worksheet_title, amount, description, 
                fund_id, category_id, debit_account_id, credit_account_id, 
                transaction_type, date_input, transaction_number, file_links, 
                origin_account, destination_account, transfer_type, payment_method, reference_number
            )
            
            if transaction_result:
                # Handle bank fee transactions if checkbox is checked
                bank_fee_results = []
                if include_bank_fees:
                    print(f"🏦 Creating bank fee transactions for main transaction: {transaction_number}")
                    
                    # Bank fee amounts
                    bank_fee_amounts = [5000, 500]
                    bank_fee_category = "8001"  # Bank Fee category code
                    
                    for i, bank_fee_amount in enumerate(bank_fee_amounts, 1):
                        # Generate new transaction number for bank fee
                        from datetime import datetime
                        bank_fee_txn_number = f"{datetime.now().strftime('%d%m%y')}-{datetime.now().strftime('%H%M%S')}{i}"
                        
                        # Bank fee description (same as main transaction)
                        bank_fee_description = description
                        
                        # Create bank fee transaction
                        bank_fee_result = add_transaction_to_selected_sheet(
                            gc, selected_sheet_id, selected_worksheet_title, bank_fee_amount, bank_fee_description, 
                            fund_id, bank_fee_category, debit_account_id, credit_account_id, 
                            transaction_type, date_input, bank_fee_txn_number, file_links, 
                            origin_account, destination_account, transfer_type, payment_method, reference_number
                        )
                        
                        bank_fee_results.append({
                            'amount': bank_fee_amount,
                            'transaction_number': bank_fee_txn_number,
                            'success': bank_fee_result
                        })
                        
                        if bank_fee_result:
                            print(f"✅ Bank fee transaction {i} created: {bank_fee_amount} VND - {bank_fee_txn_number}")
                        else:
                            print(f"❌ Failed to create bank fee transaction {i}: {bank_fee_amount} VND")
                
                # Prepare response message
                if include_bank_fees:
                    successful_bank_fees = [r for r in bank_fee_results if r['success']]
                    message = f'Transaction submitted successfully! Main transaction: {transaction_number}'
                    if successful_bank_fees:
                        message += f', Bank fees: {len(successful_bank_fees)} transactions created'
                else:
                    message = 'Transaction submitted successfully!'
                
                return jsonify({
                    'success': True,
                    'message': message,
                    'data': {
                        'transaction_number': transaction_number,
                        'amount': amount,
                        'type': transaction_type,
                        'bank_fees_created': len([r for r in bank_fee_results if r['success']]) if include_bank_fees else 0
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Error adding transaction!'
                }), 500
                
    except Exception as e:
        print(f"❌ ERROR in API submit_transaction: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =============================================================================
# MAIN WEB ROUTE - Sheet Selection Form
# =============================================================================

# Main Index Route
# ----------------
@app.route('/', methods=['GET'])
def index():
    """
    Main function that shows the web form with sheet selection
    GET: Shows the form to the user
    POST: Now handled by /api/submit_transaction endpoint
    """
    
    # =====================================================================
    # SHOW THE FORM WITH SHEET SELECTION (GET request)
    # =====================================================================
    
    # Get available sheets for dropdown (still from Google Sheets for worksheet selection)
    available_sheets = get_available_sheets(gc)
    
    # Get available funds, categories, and accounts from JSON files (MUCH FASTER!)
    print("DEBUG: Loading dropdown data from JSON files...")
    funds = get_funds_from_json()
    categories = get_categories_from_json()
    accounts = get_accounts_from_json()
    
    print(f"DEBUG: JSON data loaded - Funds: {len(funds)}, Categories: {len(categories)}, Accounts: {len(accounts)}")
    
    # Show the form with sheet selection, funds, categories, and accounts
    return render_template('index.html', sheets=available_sheets, funds=funds, categories=categories, accounts=accounts)

# =============================================================================
# AJAX ROUTE FOR WORKSHEET SELECTION
# =============================================================================

# Get Worksheets Route
# --------------------
@app.route('/get_worksheets/<sheet_id>')
def get_worksheets(sheet_id):
    """
    AJAX route to get worksheets for a selected sheet
    """
    try:
        print(f"\n" + "="*50)
        print(f"DEBUG: GET_WORKSHEETS CALLED")
        print(f"  - Sheet ID: {sheet_id}")
        print(f"="*50)
        
        worksheets = get_worksheets_from_sheet(gc, sheet_id)
        print(f"DEBUG: Found {len(worksheets)} worksheets:")
        for i, ws in enumerate(worksheets):
            print(f"  {i+1}. ID: '{ws.get('id')}', Title: '{ws.get('title')}'")
        print(f"="*50)
        
        return jsonify(worksheets)
    except Exception as e:
        print(f"ERROR in get_worksheets: {e}")
        return jsonify({'error': str(e)}), 500

# Upload File Route
# -----------------
@app.route('/upload_file', methods=['POST'])
def upload_file():
    """
    AJAX route to upload file first, before form submission
    """
    try:
        file = request.files.get('file')
        transaction_number = request.form.get('transaction_number', '')
        file_type = request.form.get('file_type', 'bills')
        
        # Use the file upload manager to handle the upload
        result = file_upload_manager.handle_web_upload(file, transaction_number, file_type)
        
        return jsonify(result)
            
    except Exception as e:
        print(f"DEBUG: Error in upload_file route: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Refresh Form Data Route
# ------------------------
@app.route('/refresh_form_data', methods=['POST'])
def refresh_form_data():
    """
    AJAX route to refresh form data when transaction type changes
    """
    try:
        data = request.get_json()
        transaction_type = data.get('transaction_type', 'donation')
        
        print(f"\n" + "="*50)
        print(f"DEBUG: REFRESH_FORM_DATA CALLED")
        print(f"  - Transaction Type: {transaction_type}")
        print(f"="*50)
        
        # Get fresh data from JSON files (MUCH FASTER than Google Sheets!)
        accounts = get_accounts_from_json()
        categories = get_categories_from_json()
        funds = get_funds_from_json()
        
        print(f"DEBUG: Retrieved fresh data:")
        print(f"  - Accounts: {len(accounts)} items")
        print(f"  - Categories: {len(categories)} items")
        print(f"  - Funds: {len(funds)} items")
        print(f"="*50)
        
        return jsonify({
            'success': True,
            'accounts': accounts,
            'categories': categories,
            'funds': funds,
            'transaction_type': transaction_type
        })
        
    except Exception as e:
        print(f"ERROR in refresh_form_data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# TRANSACTION SEARCH API
# =============================================================================

@app.route('/api/search_transaction', methods=['POST'])
def api_search_transaction():
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
        
        # Call the search tool
        from sheets_manager import search_transaction_tool
        result = search_transaction_tool(gc, sheet_type, transaction_number)
        
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

# =============================================================================
# DOCUMENT UPDATE API
# =============================================================================

@app.route('/api/update_document', methods=['POST'])
def api_update_document():
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
        
        # Call the update function
        from sheets_manager import update_document_link
        result = update_document_link(gc, sheet_type, transaction_number, document_type, file_url)
        
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

# =============================================================================
# GOOGLE DRIVE LINK PROCESSING API
# =============================================================================

@app.route('/api/process_google_drive_link', methods=['POST'])
def api_process_google_drive_link():
    """
    API endpoint for processing Google Drive links.
    
    Receives: JSON with google_drive_url and document_type
    Downloads the file and re-uploads it to the correct folder
    Returns: JSON with new file URL and name
    """
    try:
        # Get data from request
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        google_drive_url = data.get('google_drive_url')
        document_type = data.get('document_type')
        transaction_number = data.get('transaction_number')
        
        # Validate required fields
        if not all([google_drive_url, document_type]):
            return jsonify({
                'success': False,
                'error': 'Google Drive URL and document type are required'
            }), 400
        
        print(f"\n" + "="*50)
        print(f"DEBUG: PROCESS GOOGLE DRIVE LINK API CALLED")
        print(f"  - Google Drive URL: {google_drive_url}")
        print(f"  - Document Type: {document_type}")
        print(f"  - Transaction Number: {transaction_number}")
        print(f"="*50)
        
        # Call the processing function with transaction number for proper naming
        from file_upload_manager import process_google_drive_link
        result = process_google_drive_link(google_drive_url, document_type, transaction_number)
        
        if result and result.get('success'):
            print(f"DEBUG: Google Drive link processed successfully")
            return jsonify({
                'success': True,
                'file_url': result['file_url'],
                'file_name': result['file_name'],
                'message': f'File downloaded and uploaded to {document_type} folder successfully'
            })
        else:
            print(f"DEBUG: Google Drive link processing failed")
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to process Google Drive link')
            }), 500
                
    except Exception as e:
        print(f"ERROR in api_process_google_drive_link: {e}")
        return jsonify({
            'success': False,
            'error': f'Google Drive link processing failed: {str(e)}'
        }), 500

# =============================================================================
# START THE APPLICATION
# =============================================================================

if __name__ == '__main__':
    # Run the Flask app with environment-based debug mode
    # Bind to 0.0.0.0 to make it accessible from the internet
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))