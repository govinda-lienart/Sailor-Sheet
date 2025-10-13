"""
Main blueprint for the Sailor Sheet application.
Handles the main web routes and form display.
"""

from flask import Blueprint, render_template
from services.sheets_service import SheetsService
from utils.data_loader import DataLoader

# Create blueprint
main_bp = Blueprint('main', __name__)

# Initialize services
sheets_service = SheetsService()
data_loader = DataLoader()


@main_bp.route('/', methods=['GET'])
def index():
    """
    Main function that shows the web form with sheet selection
    GET: Shows the form to the user
    """
    try:
        # Get available sheets for dropdown
        available_sheets = sheets_service.get_available_sheets()
        
        # Get available funds, categories, accounts, and sub-categories from JSON files
        print("DEBUG: Loading dropdown data from JSON files...")
        funds = data_loader.get_funds()
        categories = data_loader.get_categories()
        accounts = data_loader.get_accounts('BE')  # Default to Belgium accounts
        sub_categories = data_loader.get_sub_categories()
        
        print(f"DEBUG: JSON data loaded - Funds: {len(funds)}, Categories: {len(categories)}, Accounts: {len(accounts)}, Sub-Categories: {len(sub_categories)}")
        
        # Show the form with sheet selection, funds, categories, accounts, and sub-categories
        return render_template('index.html', 
                             sheets=available_sheets, 
                             funds=funds, 
                             categories=categories, 
                             accounts=accounts, 
                             sub_categories=sub_categories)
    except Exception as e:
        print(f"ERROR in main index route: {e}")
        return render_template('index.html', 
                             sheets=[], 
                             funds=[], 
                             categories=[], 
                             accounts=[], 
                             sub_categories=[])
