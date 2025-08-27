# NGO Accounting System

A Flask-based web application for NGO financial management with Google Sheets integration.

## 🚀 Features

- **Simple Data Entry**: Web form for transaction input
- **Google Sheets Integration**: Automatic data storage
- **Clean Interface**: Professional web forms
- **Environment Support**: Development and production configurations

## 📁 Project Structure

```
📁 ngo-accounting/
├── app.py                    # Main Flask application
├── config.py                 # Google Sheets authentication
├── sheets_manager.py         # Data operations
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
├── README.md                # Project documentation
├── templates/               # HTML templates
│   ├── index.html           # Main form
│   └── thank_you.html       # Success page
├── static/                  # Static files
│   ├── css/                 # Stylesheets
│   ├── js/                  # JavaScript files
│   └── images/              # Image assets
└── .env                     # Environment variables (local)
```

## 🛠️ Installation

### Prerequisites
- Python 3.7+
- Google Sheets API credentials

### Setup
1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd ngo-accounting
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google Sheets API**
   - Create a Google Cloud project
   - Enable Google Sheets API
   - Create service account credentials
   - Download `credentials.json`

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

## 🌐 Usage

1. **Access the application**: `http://localhost:8000`
2. **Fill out the form**: Enter name, amount, and description
3. **Submit**: Data is automatically saved to Google Sheets
4. **View results**: Check your Google Sheet for the new entry

## 🔧 Configuration

### Environment Variables
- `FLASK_ENV`: Development or production mode
- `SHEET_NAME`: Google Sheet name for data storage
- `GOOGLE_CREDENTIALS`: Google API credentials (production)

### Google Sheets Setup
1. Create a new Google Sheet
2. Share with your service account email
3. Update `SHEET_NAME` in environment variables

## 🚀 Deployment

### Render (Recommended)
1. Push code to GitHub
2. Connect repository to Render
3. Set environment variables
4. Deploy automatically

### Environment Variables for Production
```
FLASK_ENV=production
SHEET_NAME=Your_Sheet_Name
GOOGLE_CREDENTIALS={"type": "service_account", ...}
```

## 📊 Data Structure

### Google Sheets Format
| Column | Description |
|--------|-------------|
| A | Name |
| B | Amount |
| C | Description |
| D | Timestamp |

## 🔒 Security

- **Credentials**: Stored in environment variables
- **API Keys**: Never committed to repository
- **HTTPS**: Automatic SSL in production

## 🛠️ Development

### Local Development
```bash
# Run in development mode
FLASK_ENV=development python app.py
```

### File Structure
- **`app.py`**: Main Flask application and routes
- **`config.py`**: Google Sheets authentication
- **`sheets_manager.py`**: Data operations
- **`templates/`**: HTML templates
- **`static/`**: CSS, JS, and images

## 📝 Version History

- **v1.0.0**: Initial working version with basic functionality
  - Simple form data entry
  - Google Sheets integration
  - Clean separation of concerns

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support, please contact the development team or create an issue in the repository.

---

**Version**: 1.0.0  
**Last Updated**: 2025-01-27  
**Status**: ✅ Production Ready
