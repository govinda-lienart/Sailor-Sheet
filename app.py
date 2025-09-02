# =============================================================================
# Created: 2025-09-02 21:17:10
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-02 12:20:13
# Status: ✅ WORKING - Ready for GitHub commit

# =============================================================================

# Import required libraries
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify  # Web framework
import os

# Import custom modules
from config import initialize_sheets
from sheets_manager import get_available_sheets, get_worksheets_from_sheet, add_transaction_to_selected_sheet, get_funds_list, get_cost_centers_list
from file_upload_manager import upload_file_to_drive

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
        selected_sheet_id = request.form['sheet_name']
        selected_worksheet_title = request.form['worksheet_name']  # This is the worksheet title
        amount = request.form['amount']
        description = request.form['description']
        fund_id = request.form['fund_id']
        cost_center_id = request.form['cost_center_id']
        transaction_type = request.form['transaction_type']  # 'debit' or 'credit'
        date_input = request.form.get('date_input', '')  # Date in DD/MM/YYYY format
        transaction_number = request.form.get('transaction_number', '')  # Pre-generated transaction number
        
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
        print(f"  - Cost Center ID: {cost_center_id}")
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
            funds = get_funds_list(gc)
            cost_centers = get_cost_centers_list(gc)
            return render_template('index.html', sheets=available_sheets, funds=funds, cost_centers=cost_centers)
                                                                                        # ↑ HTML name ↑ Python data

        if not selected_worksheet_title:
            flash('Please select a worksheet!', 'error')
            available_sheets = get_available_sheets(gc)
            funds = get_funds_list(gc)
            cost_centers = get_cost_centers_list(gc)
            return render_template('index.html', sheets=available_sheets, funds=funds, cost_centers=cost_centers)
        
        # Use the worksheet title directly as the account name
        print(f"DEBUG: Using worksheet title as account name: {selected_worksheet_title}")
        account_name = selected_worksheet_title  # The worksheet title is the account name
        
        # Add transaction to selected sheet and worksheet with file link and fund
        print(f"DEBUG: About to call add_transaction_to_selected_sheet with:")
        print(f"  - selected_sheet_id: {selected_sheet_id}")
        print(f"  - selected_worksheet_title: {selected_worksheet_title}")
        print(f"  - account_name: {account_name}")
        print(f"  - amount: {amount}")
        print(f"  - description: {description}")
        print(f"  - fund_id: {fund_id}")
        print(f"  - cost_center_id: {cost_center_id}")
        print(f"  - transaction_type: {transaction_type}")
        print(f"  - date_input: {date_input}")
        print(f"  - transaction_number: {transaction_number}")
        
        transaction_result = add_transaction_to_selected_sheet(gc, selected_sheet_id, selected_worksheet_title, amount, description, fund_id, cost_center_id, transaction_type, date_input, transaction_number, file_link_dict, account_name)
        print(f"DEBUG: Transaction result: {transaction_result}")
        
        if transaction_result:
            print("DEBUG: Transaction successful! Redirecting to thank you page")
            # Transaction successful! Redirect to thank you page
            return redirect(url_for('thank_you'))
        else:
            print("ERROR: Transaction failed!")
            flash('Error adding transaction!', 'error')
            available_sheets = get_available_sheets(gc)
            funds = get_funds_list(gc)
            cost_centers = get_cost_centers_list(gc)
            return render_template('index.html', sheets=available_sheets, funds=funds, cost_centers=cost_centers)
    
    # =====================================================================
    # SHOW THE FORM WITH SHEET SELECTION (GET request)
    # =====================================================================
    
    # Get available sheets for dropdown
    available_sheets = get_available_sheets(gc)
    
    # Get available funds for dropdown
    funds = get_funds_list(gc)
    
    # Get available cost centers for dropdown
    cost_centers = get_cost_centers_list(gc)
    
    # Show the form with sheet selection, funds, and cost centers
    return render_template('index.html', sheets=available_sheets, funds=funds, cost_centers=cost_centers)

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
        print("DEBUG: upload_file route called")
        file = request.files.get('file')
        transaction_number = request.form.get('transaction_number', '')  # Get transaction number if provided
        
        print(f"DEBUG: File received: {file.filename if file else 'None'}")
        print(f"DEBUG: Transaction number received: '{transaction_number}'")
        print(f"DEBUG: Transaction number type: {type(transaction_number)}")
        print(f"DEBUG: Transaction number length: {len(transaction_number) if transaction_number else 0}")
        
        if not file or not file.filename:
            print("DEBUG: No file in request")
            return jsonify({'success': False, 'error': 'No file selected'})
        
        print(f"DEBUG: Uploading file: {file.filename}")
        print(f"DEBUG: Transaction number: {transaction_number}")
        print(f"DEBUG: File size: {len(file.read())} bytes")
        file.seek(0)  # Reset file pointer after reading
        
        # Upload file to Google Drive using our working upload manager
        result = upload_file_to_drive(file, transaction_number)
        
        if result['success']:
            print(f"DEBUG: File uploaded successfully: {result}")
            return jsonify({
                'success': True,
                'file_name': result['file_name'],
                'file_url': result['file_url'],
                'file_id': result['file_id']
            })
        else:
            print(f"DEBUG: File upload failed: {result['error']}")
            return jsonify({'success': False, 'error': result['error']})
            
    except Exception as e:
        print(f"DEBUG: Error in upload_file route: {e}")
        import traceback
        traceback.print_exc()
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