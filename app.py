# =============================================================================
# Created: 2025-09-01 12:57:34
# Status: ✅ WORKING - Ready for GitHub commit
# Created: 2025-09-01 10:45:48
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

# Add secret key for flash messages
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

# Set maximum file size for uploads (16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# =============================================================================
# INITIALIZE GOOGLE SHEETS
# =============================================================================

# Initialize Google Sheets connection
gc = initialize_sheets()

# =============================================================================
# MAIN WEB ROUTE - Sheet Selection Form
# =============================================================================

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
        selected_worksheet = request.form['worksheet_name']
        amount = request.form['amount']
        description = request.form['description']
        fund_id = request.form['fund_id']
        cost_center_id = request.form['cost_center_id']
        transaction_type = request.form['transaction_type']  # 'debit' or 'credit'
        
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
        
        if not selected_worksheet:
            flash('Please select a worksheet!', 'error')
            available_sheets = get_available_sheets(gc)
            funds = get_funds_list(gc)
            cost_centers = get_cost_centers_list(gc)
            return render_template('index.html', sheets=available_sheets, funds=funds, cost_centers=cost_centers)
        
        # Add transaction to selected sheet and worksheet with file link and fund
        if add_transaction_to_selected_sheet(gc, selected_sheet_id, selected_worksheet, amount, description, fund_id, cost_center_id, transaction_type, file_link_dict):
            flash('Transaction added successfully!', 'success')
            return redirect(url_for('thank_you'))
        else:
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

@app.route('/get_worksheets/<sheet_id>')
def get_worksheets(sheet_id):
    """
    AJAX route to get worksheets for a selected sheet
    """
    try:
        worksheets = get_worksheets_from_sheet(gc, sheet_id)
        return jsonify(worksheets)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload_file', methods=['POST'])
def upload_file():
    """
    AJAX route to upload file first, before form submission
    """
    try:
        print("DEBUG: upload_file route called")
        file = request.files.get('file')
        if not file or not file.filename:
            print("DEBUG: No file in request")
            return jsonify({'success': False, 'error': 'No file selected'})
        
        print(f"DEBUG: Uploading file: {file.filename}")
        print(f"DEBUG: File size: {len(file.read())} bytes")
        file.seek(0)  # Reset file pointer after reading
        
        # Upload file to Google Drive using our working upload manager
        result = upload_file_to_drive(file)
        
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