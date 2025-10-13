"""
File API endpoints.
Handles file upload and Google Drive link processing API routes.
"""

from flask import Blueprint, request, jsonify
from services.file_service import FileService

# Create blueprint
api_files_bp = Blueprint('api_files', __name__, url_prefix='/api')

# Initialize services
file_service = FileService()


@api_files_bp.route('/upload_file', methods=['POST'])
def upload_file():
    """
    AJAX route to upload file first, before form submission
    """
    try:
        file = request.files.get('file')
        transaction_number = request.form.get('transaction_number', '')
        file_type = request.form.get('file_type', 'bills')
        country_code = request.form.get('country_code')
        
        # Use the file service to handle the upload
        result = file_service.handle_web_upload(file, transaction_number, file_type, country_code)
        
        return jsonify(result)
            
    except Exception as e:
        print(f"DEBUG: Error in upload_file route: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_files_bp.route('/process_google_drive_link', methods=['POST'])
def process_google_drive_link():
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
        country_code = data.get('country_code')
        
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
        print(f"  - Country Code: {country_code}")
        print(f"="*50)
        
        # Use file service to process the Google Drive link
        result = file_service.process_google_drive_link(google_drive_url, document_type, transaction_number, country_code)
        
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
