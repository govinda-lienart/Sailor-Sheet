"""
Transaction Search Tool
Handles searching for transactions via Sailor Sheet API.
"""

import requests
import os
from .utils import format_transaction_response

# Configuration - API base URL for main Sailor Sheet app
SAILOR_SHEET_API_URL = os.getenv('SAILOR_SHEET_API_URL', 'http://localhost:8000')


def search_transaction_tool(transaction_number: str) -> str:
    """
    Search for a transaction by number using Sailor Sheet API (VN ledger).
    
    Args:
        transaction_number: Transaction number to search for (e.g., 'VN-151025-135926')
        
    Returns:
        Formatted transaction data string or error message
    """
    try:
        response = requests.post(
            f"{SAILOR_SHEET_API_URL}/api/search_transaction",
            json={"sheet_type": "vn", "transaction_number": transaction_number},
            timeout=10
        )

        try:
            data = response.json()
        except Exception:
            return f"Error: Could not parse API response (Status: {response.status_code})"

        if response.status_code == 200:
            if data.get("success"):
                return format_transaction_response(data.get("data", {}))
            return f"Transaction not found: {data.get('error', 'Unknown error')}"
        elif response.status_code == 404:
            return f"Transaction not found: {data.get('error', f'Transaction {transaction_number} not found')}"
        else:
            return f"API error: {data.get('error', f'HTTP {response.status_code}')}"
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Sailor Sheet API: {str(e)}"

