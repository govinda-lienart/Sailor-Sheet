# =============================================================================
# NGO ACCOUNTING APP - Main Flask Application
# Purpose: Main web application with clean, organized structure
# Version: 1.0.0 - Working Version
# Created: 2025-01-27 19:30:00
# Status: ✅ WORKING - Ready for deployment
# =============================================================================

# Import required libraries
from flask import Flask, render_template, request, redirect, url_for  # Web framework
import os

# Import custom modules
from config import initialize_sheets
from sheets_manager import add_transaction

# Create Flask web application
app = Flask(__name__)

# =============================================================================
# ENVIRONMENT CONFIGURATION
# =============================================================================

# Get environment (development or production)
FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
SHEET_NAME = os.environ.get('SHEET_NAME', 'Test_Sheet')

# Set debug mode based on environment
DEBUG_MODE = FLASK_ENV == 'development'

# =============================================================================
# INITIALIZE GOOGLE SHEETS
# =============================================================================

# Initialize Google Sheets connection
gc = initialize_sheets()

# =============================================================================
# MAIN WEB ROUTE - Handles both GET and POST requests
# =============================================================================

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Main function that handles the web form
    GET: Shows the form to the user
    POST: Processes form data and saves to Google Sheets
    """
    
    if request.method == 'POST':
        # =====================================================================
        # PROCESS FORM SUBMISSION
        # =====================================================================
        
        # Extract data from the web form
        name = request.form['name']           # Get name from form
        amount = request.form['amount']       # Get amount from form
        description = request.form['description']  # Get description from form
        
        # =====================================================================
        # SAVE DATA TO GOOGLE SHEETS
        # =====================================================================
        
        try:
            # Add transaction to Google Sheets (uses environment sheet name)
            sheet = add_transaction(gc, SHEET_NAME, name, amount, description)
            
            # Redirect to thank you page
            return redirect(url_for('thank_you'))
            
        except Exception as e:
            # If something goes wrong, show error message
            if DEBUG_MODE:
                return f"Error: {str(e)}"
            else:
                return "An error occurred. Please try again."
    
    # =====================================================================
    # SHOW THE WEB FORM (GET request)
    # =====================================================================
    
    # If it's a GET request, show the HTML form
    return render_template('index.html')

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