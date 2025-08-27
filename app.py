from flask import Flask, render_template, request, redirect, url_for
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os

app = Flask(__name__)

# Google Sheets setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
credentials = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
gc = gspread.authorize(credentials)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        amount = request.form['amount']
        description = request.form['description']
        
        # Write to Google Sheets
        try:
            sheet = gc.open('Test_Sheet').sheet1
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Add data to next row
            row = [name, amount, description, timestamp]
            sheet.append_row(row)
            
            return "Data saved successfully!"
        except Exception as e:
            return f"Error: {str(e)}"
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)