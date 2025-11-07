"""
Utility Functions for Tools
Helper functions for transaction processing and data formatting.
"""

import re


def extract_transaction_number(user_message: str) -> str | None:
    """
    Extract transaction number from user message.
    Looks for patterns like VN-XXX-XXX or BE-XXX-XXX.
    
    Args:
        user_message: User's input message
        
    Returns:
        Transaction number in uppercase (e.g., 'VN-151025-135926') or None
    """
    pattern = r'(?:VN|BE)-\d+-\d+'
    match = re.search(pattern, user_message, re.IGNORECASE)
    return match.group(0).upper() if match else None


def format_transaction_response(data: dict) -> str:
    """
    Format transaction data into readable text for LLM.
    Skips empty or placeholder fields.
    
    Args:
        data: Dictionary containing transaction data
        
    Returns:
        Formatted string with transaction details
    """
    lines = ["Transaction Details:"]
    for key, value in data.items():
        if value and value not in ('—', ''):
            lines.append(f"  {key}: {value}")
    return "\n".join(lines)

