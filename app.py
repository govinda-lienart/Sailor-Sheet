# =============================================================================
# NGO ACCOUNTING APP - Simple Flask Web Application
# Purpose: Collect data from web form and save to Google Sheets
# =============================================================================

# Import required libraries
from flask import Flask, render_template, request, redirect, url_for  # Web framework
import gspread  # Google Sheets API library
from google.oauth2.service_account import Credentials  # Google authentication
from datetime import datetime  # For timestamps
import os  # Operating system functions
from config import Config  # Configuration settings

# Create Flask web application
app = Flask(__name__)
app.config.from_object(Config)  # Load configuration from config.py

# =============================================================================
# GOOGLE SHEETS SETUP
# =============================================================================

# Define API permissions (scopes) - what our app can do
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',  # Read/write Google Sheets
    'https://www.googleapis.com/auth/drive'          # Access Google Drive
]

# Load service account credentials from JSON file
# This is like giving our app a "login card" for Google
credentials = Credentials.from_service_account_file(
    app.config['GOOGLE_SHEETS_CREDENTIALS_FILE'],  # Path to credentials.json
    scopes=SCOPES  # What permissions our app has
)

# Authorize our app to use Google Sheets
gc = gspread.authorize(credentials)

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
            # Open the Google Sheet named 'Test_Sheet'
            sheet = gc.open('Test_Sheet').sheet1
            
            # Create timestamp for when data was submitted
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Prepare data row: [Name, Amount, Description, Timestamp]
            row = [name, amount, description, timestamp]
            
            # Add the new row to the Google Sheet
            sheet.append_row(row)
            
            # Show success message to user
            return "Data saved successfully!"
            
        except Exception as e:
            # If something goes wrong, show error message
            return f"Error: {str(e)}"
    
    # =====================================================================
    # SHOW THE WEB FORM (GET request)
    # =====================================================================
    
    # If it's a GET request, show the HTML form
    return render_template('index.html')

# =============================================================================
# START THE APPLICATION
# =============================================================================

if __name__ == '__main__':
    # Run the Flask app in debug mode (shows errors, auto-reloads)
    app.run(debug=True)