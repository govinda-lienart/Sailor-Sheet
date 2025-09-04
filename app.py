# Created: 2025-09-04 16:37:37
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-04 15:18:55
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-04 14:57:08
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-04 14:49:11
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-04 14:26:30
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-04 14:23:56
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-04 14:01:24
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-04 04:52:11
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-04 04:50:11
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-04 04:49:54
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-04 04:26:36
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-03 22:51:02
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-03 19:28:04
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-03 19:13:13
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-03 16:09:02
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-03 15:20:50
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-03 11:28:57
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-03 11:27:32
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-02 21:17:10
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-02 12:20:13
# Status: ✅ WORKING - Ready for GitHub commit

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
# MAIN WEB ROUTE - Sheet Selection Form
# =============================================================================

# Main Index Route
# ----------------
@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Main function that handles the web form with sheet selection
    GET: Shows the form to the user
    POST: Processes form data and saves to selected Google Sheet
    """
    
    if request.method == 'POST':
        # =====================================================================
        # PROCESS FORM SUBMISSION WITH SHEET SELECTION
        # =====================================================================
        
        # Extract data from the web form
        try:
            selected_sheet_id = request.form['sheet_id']
            selected_worksheet_title = request.form['worksheet_name']  # This is the worksheet title
            amount = request.form['amount']
            description = request.form['description']
            fund_id = request.form['fund_id']
            category_id = request.form['category_id']
            # Get account IDs based on transaction type
            transaction_type = request.form.get('transaction_type', 'external')
            
            if transaction_type == 'interbanking_transfer':
                # For interbanking transfers, use the destination account fields
                debit_account_id = request.form['debit_account_id']
                credit_account_id = request.form['credit_account_id']
            else:
                # For regular transactions, use the regular account fields
                debit_account_id = request.form['regular_debit_account_id']
                credit_account_id = request.form['regular_credit_account_id']
            date_input = request.form.get('date_input', '')  # Date in DD/MM/YYYY format
            transaction_number = request.form.get('transaction_number', '')  # Pre-generated transaction number
        except KeyError as e:
            print(f"ERROR: Missing required form field: {e}")
            print(f"DEBUG: Available form fields: {list(request.form.keys())}")
            flash(f'Missing required field: {e}', 'error')
            available_sheets = get_available_sheets(gc)
            funds = get_funds_from_json()
            categories = get_categories_from_json()
            accounts = get_accounts_from_json()
            return render_template('index.html', sheets=available_sheets, funds=funds, categories=categories, accounts=accounts)
        
        # Debug: Show what we're working with
        print(f"\n" + "="*50)
        print(f"DEBUG: FORM SUBMISSION STARTED")
        print(f"="*50)
        print(f"DEBUG: Form data extracted:")
        print(f"  - Sheet ID: '{selected_sheet_id}' (type: {type(selected_sheet_id)})")
        print(f"  - Worksheet Title: '{selected_worksheet_title}' (type: {type(selected_worksheet_title)})")
        print(f"  - Amount: {amount}")
        print(f"  - Description: {description}")
        print(f"  - Fund ID: {fund_id}")
        print(f"  - Category ID: {category_id}")
        print(f"  - Debit Account ID: {debit_account_id}")
        print(f"  - Credit Account ID: {credit_account_id}")
        print(f"  - Transaction Type: {transaction_type}")
        print(f"  - Date: {date_input}")
        print(f"  - Transaction Number: {transaction_number}")
        print(f"="*50)
        
        # Handle file link (file was already uploaded separately)
        file_link = request.form.get('file_link', '')
        file_name = request.form.get('file_name', '')
        
        if file_link and file_name:
            print(f"DEBUG: File link from form: {file_link}")
            print(f"DEBUG: File name from form: {file_name}")
            
            # Create the file link dict for the sheets manager
            file_link_dict = {
                'url': file_link,
                'filename': file_name
            }
            
            flash(f'Transaction submitted with file link!', 'success')
        else:
            print("DEBUG: No file link in form")
            file_link_dict = ""
        
        # Validate that a sheet and worksheet were selected
        if not selected_sheet_id:
            flash('Please select a sheet!', 'error')
            available_sheets = get_available_sheets(gc)
            funds = get_funds_from_json()
            categories = get_categories_from_json()
            accounts = get_accounts_from_json()
            return render_template('index.html', sheets=available_sheets, funds=funds, categories=categories, accounts=accounts)
                                                                                        # ↑ HTML name ↑ Python data

        if not selected_worksheet_title:
            flash('Please select a worksheet!', 'error')
            available_sheets = get_available_sheets(gc)
            funds = get_funds_from_json()
            categories = get_categories_from_json()
            accounts = get_accounts_from_json()
            return render_template('index.html', sheets=available_sheets, funds=funds, categories=categories, accounts=accounts)
        
        # Use the worksheet title directly as the account name
        print(f"DEBUG: Using worksheet title as account name: {selected_worksheet_title}")
        account_name = selected_worksheet_title  # The worksheet title is the account name
        
        # Add transaction to selected sheet and worksheet with file link and fund
        print(f"DEBUG: About to call add_transaction_to_selected_sheet with:")
        print(f"  - selected_sheet_id: {selected_sheet_id}")
        print(f"  - selected_worksheet_title: {selected_worksheet_title}")
        print(f"  - amount: {amount}")
        print(f"  - description: {description}")
        print(f"  - fund_id: {fund_id}")
        print(f"  - category_id: {category_id}")
        print(f"  - debit_account_id: {debit_account_id}")
        print(f"  - credit_account_id: {credit_account_id}")
        print(f"  - transaction_type: {transaction_type}")
        print(f"  - date_input: {date_input}")
        print(f"  - transaction_number: {transaction_number}")
        
        # Get transfer type and account details from form
        transfer_type = request.form.get('transfer_type', 'external')
        destination_account = request.form.get('destination_account', '')
        
        # For internal transfers, use selected worksheet as origin account
        if transfer_type == 'internal':
            origin_account = selected_worksheet_title  # Use selected sheet as origin
            fund_id = 'Internal Transfer'
            category_id = 'Internal Transfer'
            print(f"DEBUG: Internal transfer - using selected worksheet as origin account")
            print(f"DEBUG: Internal transfer - overriding fund and category to 'Internal Transfer'")
        else:
            origin_account = ''  # Not used for external transactions
        
        print(f"DEBUG: Transfer details:")
        print(f"  - transfer_type: {transfer_type}")
        print(f"  - origin_account: {origin_account}")
        print(f"  - destination_account: {destination_account}")
        print(f"  - fund_id: {fund_id}")
        print(f"  - category_id: {category_id}")
        
        # Get the actual transaction type from the form
        form_transaction_type = request.form.get('transaction_category', transaction_type)
        print(f"DEBUG: Form transaction type: {form_transaction_type}")
        
        # Check if this is an interbanking transfer that needs dual-entry
        if form_transaction_type == 'interbanking_transfer':
            print("🔄 Processing INTERBANKING TRANSFER with dual-entry accounting...")
            
            # Get origin account selections from form
            origin_debit = request.form.get('origin_debit_account_id', '')
            origin_credit = request.form.get('origin_credit_account_id', '')
            
            # Destination accounts are the regular debit/credit fields
            destination_debit = debit_account_id
            destination_credit = credit_account_id
            
            print(f"📋 Dual form data:")
            print(f"  - Origin Debit: {origin_debit}")
            print(f"  - Origin Credit: {origin_credit}")
            print(f"  - Destination Debit: {destination_debit}")
            print(f"  - Destination Credit: {destination_credit}")
            
            # Validate that all dual fields are filled
            if not all([origin_debit, origin_credit, destination_debit, destination_credit]):
                print("❌ Missing dual account selections")
                flash('Please fill in all origin and destination account fields for interbanking transfer!', 'error')
                available_sheets = get_available_sheets(gc)
                funds = get_funds_from_json()
                categories = get_categories_from_json()
                accounts = get_accounts_from_json()
                return render_template('index.html', sheets=available_sheets, funds=funds, categories=categories, accounts=accounts)
            
            # Create Origin entry (typically Belgium)
            belgium_sheet_id = "1o5RnuAmm00YAqZzLkyrhZx7CocEETBhi-snPGUzbqSk"  # Belgium Master Ledger
            belgium_worksheet = "BE - Master Ledger"
            
            print(f"📍 Creating Origin entry: Debit {origin_debit}, Credit {origin_credit}")
            origin_result = add_transaction_to_selected_sheet(
                gc, belgium_sheet_id, belgium_worksheet, amount, 
                f"Interbanking Transfer - {description}", 
                fund_id, category_id, origin_debit, origin_credit, 
                transaction_type, date_input, transaction_number, file_link_dict, 
                origin_account, destination_account, transfer_type
            )
            
            # Create Destination entry (typically Vietnam) using selected sheet
            print(f"🎯 Creating Destination entry: Debit {destination_debit}, Credit {destination_credit}")
            destination_result = add_transaction_to_selected_sheet(
                gc, selected_sheet_id, selected_worksheet_title, amount, description, 
                fund_id, category_id, destination_debit, destination_credit, 
                transaction_type, date_input, transaction_number, file_link_dict, 
                origin_account, destination_account, transfer_type
            )
            
            print(f"📍 Origin transaction result: {origin_result}")
            print(f"🎯 Destination transaction result: {destination_result}")
            
            if origin_result and destination_result:
                print("✅ DUAL-ENTRY SUCCESS: Both Origin and Destination entries created!")
                flash('Interbanking transfer recorded in both Origin and Destination accounting systems!', 'success')
                return redirect(url_for('thank_you'))
            else:
                print("❌ DUAL-ENTRY FAILED: One or both entries failed")
                flash('Error creating dual-entry transaction! Please check both accounting systems.', 'error')
                available_sheets = get_available_sheets(gc)
                funds = get_funds_from_json()
                categories = get_categories_from_json()
                accounts = get_accounts_from_json()
                return render_template('index.html', sheets=available_sheets, funds=funds, categories=categories, accounts=accounts)
        else:
            # Regular single-entry transaction
            transaction_result = add_transaction_to_selected_sheet(gc, selected_sheet_id, selected_worksheet_title, amount, description, fund_id, category_id, debit_account_id, credit_account_id, transaction_type, date_input, transaction_number, file_link_dict, origin_account, destination_account, transfer_type)
            print(f"DEBUG: Transaction result: {transaction_result}")
            
            if transaction_result:
                print("DEBUG: Transaction successful! Redirecting to thank you page")
                # Transaction successful! Redirect to thank you page
                return redirect(url_for('thank_you'))
            else:
                print("ERROR: Transaction failed!")
                flash('Error adding transaction!', 'error')
                available_sheets = get_available_sheets(gc)
                funds = get_funds_from_json()
                categories = get_categories_from_json()
                accounts = get_accounts_from_json()
                return render_template('index.html', sheets=available_sheets, funds=funds, categories=categories, accounts=accounts)
    
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
        
        # Use the file upload manager to handle the upload
        result = file_upload_manager.handle_web_upload(file, transaction_number)
        
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
# THANK YOU PAGE ROUTE
# =============================================================================

# Thank You Route
# ---------------
@app.route('/thank-you')
def thank_you():
    """
    Thank you page after successful submission
    """
    return render_template('thank_you.html')

# =============================================================================
# START THE APPLICATION
# =============================================================================

if __name__ == '__main__':
    # Run the Flask app with environment-based debug mode
    # Bind to 0.0.0.0 to make it accessible from the internet
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))