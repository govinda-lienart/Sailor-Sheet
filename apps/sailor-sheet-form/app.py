"""
Sailor Sheet Flask Application - Fully Refactored Industry Standard Version
Main application entry point with proper separation of concerns.
"""

import os
from flask import Flask
from flask_cors import CORS

# Import blueprints
from blueprints.main import main_bp
from blueprints.api_transactions import api_transactions_bp
from blueprints.api_data import api_data_bp
from blueprints.api_files import api_files_bp

# Import configuration
from config import initialize_sheets

# =============================================================================
# APPLICATION FACTORY PATTERN
# =============================================================================

def create_app():
    """
    Application factory pattern for creating Flask app.
    This is the industry standard way to create Flask applications.
    """
    # Create Flask web application
    app = Flask(__name__)
    
    # =============================================================================
    # CORS CONFIGURATION
    # =============================================================================
    
    # Enable CORS for API endpoints to allow cross-origin requests
    # This allows practice tools and external apps to call our APIs
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5001", "http://localhost:5000", "http://127.0.0.1:5001", "http://127.0.0.1:5000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
            "expose_headers": ["Content-Type"],
            "supports_credentials": True,
            "send_wildcard": False,
            "max_age": 3600
        }
    })
    
    # =============================================================================
    # CONFIGURATION
    # =============================================================================
    
    # Get environment (development or production)
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    
    # Set debug mode based on environment
    DEBUG_MODE = FLASK_ENV == 'development'
    
    # Set maximum file size for uploads (16MB)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    
    # Add secret key for flash messages and sessions
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
    
    # Set debug mode in Flask config
    app.config['DEBUG'] = DEBUG_MODE
    
    # =============================================================================
    # INITIALIZE GOOGLE SHEETS
    # =============================================================================
    
    # Initialize Google Sheets connection
    gc = initialize_sheets()
    
    # =============================================================================
    # REGISTER BLUEPRINTS
    # =============================================================================
    
    # Register main blueprint (handles main web routes)
    app.register_blueprint(main_bp)
    
    # Register API blueprints (organized by functionality)
    app.register_blueprint(api_transactions_bp)  # Transaction operations
    app.register_blueprint(api_data_bp)          # Data loading & country selection
    app.register_blueprint(api_files_bp)         # File uploads & Google Drive
    
    # =============================================================================
    # APPLICATION CONTEXT
    # =============================================================================
    
    # Make Google Sheets connection available to all blueprints
    app.config['GOOGLE_SHEETS_GC'] = gc
    
    return app

# =============================================================================
# CREATE APPLICATION INSTANCE
# =============================================================================

# Create the application instance
app = create_app()

# =============================================================================
# START THE APPLICATION
# =============================================================================

if __name__ == '__main__':
    # Run the Flask app with environment-based debug mode
    # Bind to 0.0.0.0 to make it accessible from the internet
    print(f"🚀 Starting Sailor Sheet application...")
    print(f"🔧 Debug mode: {'ON' if app.config['DEBUG'] else 'OFF'}")
    print(f"🌍 Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"🌐 Server will be available at: http://0.0.0.0:{os.environ.get('PORT', 8000)}")
    
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
