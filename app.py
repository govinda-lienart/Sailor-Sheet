# =============================================================================
# Created: 2025-08-30 14:05:01
# Status: ✅ WORKING - Ready for GitHub commit
# NGO ACCOUNTING APP - Main Flask Application
# Purpose: Main web application with clean, organized structure
# Version: 1.0.0 - Working Version
# Created: 2025-01-27 19:30:00
# Status: ✅ WORKING - Ready for deployment
# =============================================================================

# Import required libraries
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify  # Web framework
import os

# Import custom modules
from config import initialize_sheets
from sheets_manager import get_available_sheets, get_worksheets_from_sheet, add_transaction_to_selected_sheet
from file_upload_manager import upload_file_to_drive, list_folder_files

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
        name = request.form['name']
        amount = request.form['amount']
        description = request.form['description']
        
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
            return render_template('index.html', sheets=available_sheets)
        
        if not selected_worksheet:
            flash('Please select a worksheet!', 'error')
            available_sheets = get_available_sheets(gc)
            return render_template('index.html', sheets=available_sheets)
        
        # Add transaction to selected sheet and worksheet with file link
        if add_transaction_to_selected_sheet(gc, selected_sheet_id, selected_worksheet, name, amount, description, file_link_dict):
            flash('Transaction added successfully!', 'success')
            return redirect(url_for('thank_you'))
        else:
            flash('Error adding transaction!', 'error')
            available_sheets = get_available_sheets(gc)
            return render_template('index.html', sheets=available_sheets)
    
    # =====================================================================
    # SHOW THE FORM WITH SHEET SELECTION (GET request)
    # =====================================================================
    
    # Get available sheets for dropdown
    available_sheets = get_available_sheets(gc)
    
    # Show the form with sheet selection
    return render_template('index.html', sheets=available_sheets)

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