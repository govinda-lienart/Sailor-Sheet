"""
Data API endpoints.
Handles data loading and country selection API routes.
"""

from flask import Blueprint, request, jsonify, session
from services.sheets_service import SheetsService
from utils.data_loader import DataLoader

# Create blueprint
api_data_bp = Blueprint('api_data', __name__, url_prefix='/api')

# Initialize services
sheets_service = SheetsService()
data_loader = DataLoader()


@api_data_bp.route('/get_worksheets/<sheet_id>')
def get_worksheets(sheet_id):
    """
    AJAX route to get worksheets for a selected sheet
    """
    try:
        print(f"\n" + "="*50)
        print(f"DEBUG: GET_WORKSHEETS CALLED")
        print(f"  - Sheet ID: {sheet_id}")
        print(f"="*50)
        
        worksheets = sheets_service.get_worksheets_from_sheet(sheet_id)
        print(f"DEBUG: Found {len(worksheets)} worksheets:")
        for i, ws in enumerate(worksheets):
            print(f"  {i+1}. ID: '{ws.get('id')}', Title: '{ws.get('title')}'")
        print(f"="*50)
        
        return jsonify(worksheets)
    except Exception as e:
        print(f"ERROR in get_worksheets: {e}")
        return jsonify({'error': str(e)}), 500


@api_data_bp.route('/refresh_form_data', methods=['POST'])
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
        
        # Get fresh data from JSON files
        accounts = data_loader.get_accounts()
        categories = data_loader.get_categories()
        funds = data_loader.get_funds()
        sub_categories = data_loader.get_sub_categories()
        
        print(f"DEBUG: Retrieved fresh data:")
        print(f"  - Accounts: {len(accounts)} items")
        print(f"  - Categories: {len(categories)} items")
        print(f"  - Funds: {len(funds)} items")
        print(f"  - Sub-Categories: {len(sub_categories)} items")
        print(f"="*50)
        
        return jsonify({
            'success': True,
            'accounts': accounts,
            'categories': categories,
            'funds': funds,
            'sub_categories': sub_categories,
            'transaction_type': transaction_type
        })
        
    except Exception as e:
        print(f"ERROR in refresh_form_data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_data_bp.route('/countries', methods=['GET'])
def get_countries():
    """
    API endpoint to get available countries
    """
    try:
        countries_data = data_loader.load_json_data('countries.json')
        return jsonify({
            'success': True,
            'countries': countries_data.get('countries', {})
        })
    except Exception as e:
        print(f"ERROR in api_get_countries: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to load countries: {str(e)}'
        }), 500


@api_data_bp.route('/select_country', methods=['POST'])
def select_country():
    """
    API endpoint to select a country and get country-specific data
    """
    try:
        data = request.get_json()
        country_code = data.get('country_code')
        
        if not country_code:
            return jsonify({
                'success': False,
                'error': 'Country code is required'
            }), 400
        
        # Load countries configuration
        countries_data = data_loader.load_json_data('countries.json')
        countries = countries_data.get('countries', {})
        
        if country_code not in countries:
            return jsonify({
                'success': False,
                'error': f'Invalid country code: {country_code}'
            }), 400
        
        country_info = countries[country_code]
        
        # Store selected country in session
        session['selected_country'] = country_code
        
        # Load country-specific accounts
        accounts_data = data_loader.load_json_data(country_info['accounts_file'])
        
        print(f"DEBUG: Country selected: {country_code}")
        print(f"DEBUG: Sheet: {country_info['sheet_name']}")
        print(f"DEBUG: Worksheet: {country_info['worksheet_name']}")
        
        return jsonify({
            'success': True,
            'country': country_info,
            'accounts': accounts_data.get('accounts', []),
            'message': f'Country switched to {country_info["name"]}'
        })
        
    except Exception as e:
        print(f"ERROR in api_select_country: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to select country: {str(e)}'
        }), 500
