"""
Tools and Router Setup for Chatbot Practice
Handles transaction search tools and simple routing
"""

from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import requests
import os
import re

# Configuration - API base URL for main Sailor Sheet app
SAILOR_SHEET_API_URL = os.getenv('SAILOR_SHEET_API_URL', 'http://localhost:8000')


def search_transaction_tool(transaction_number: str) -> str:
    """
    Search for a transaction by transaction number.
    Always searches in Vietnam (VN) sheet.
    """
    # Always use VN sheet type
    sheet_type = 'vn'
    
    try:
        response = requests.post(
            f'{SAILOR_SHEET_API_URL}/api/search_transaction',
            json={
                'sheet_type': sheet_type,
                'transaction_number': transaction_number
            },
            timeout=10
        )
        
        # Parse response
        try:
            data = response.json()
        except:
            return f"Error: Could not parse API response (Status: {response.status_code})"
        
        if response.status_code == 200:
            if data.get('success'):
                # Format transaction data for LLM
                transaction_data = data.get('data', {})
                return format_transaction_response(transaction_data)
            else:
                return f"Transaction not found: {data.get('error', 'Unknown error')}"
        elif response.status_code == 404:
            # 404 means transaction not found - return clear message
            error_msg = data.get('error', f'Transaction {transaction_number} not found')
            return f"Transaction not found: {error_msg}"
        else:
            # Other HTTP errors
            error_msg = data.get('error', f'HTTP {response.status_code}')
            return f"API error: {error_msg}"
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Sailor Sheet API: {str(e)}"


def format_transaction_response(data: dict) -> str:
    """Format transaction data into readable string for LLM"""
    # Extract key fields from transaction data
    # Format as natural language summary
    lines = [f"Transaction Details:"]
    for key, value in data.items():
        if value and value != '—' and value != '':
            lines.append(f"  {key}: {value}")
    return "\n".join(lines)


def extract_transaction_number(user_message: str) -> str:
    """
    Extract transaction number from user message.
    Looks for patterns like VN-XXX-XXX or BE-XXX-XXX
    """
    # Pattern to match transaction numbers: VN- or BE- followed by alphanumeric and hyphens
    pattern = r'(?:VN|BE)-\d+-\d+'
    match = re.search(pattern, user_message, re.IGNORECASE)
    if match:
        return match.group(0).upper()  # Return in uppercase for consistency
    return None


def setup_router(llm: LLM, context_info: str):
    """
    Set up router with formatting chain for transaction data
    
    Args:
        llm: The DeepSeekLLM instance
        context_info: Context about Sailor Sheet
        
    Returns:
        LLMChain for formatting responses
    """
    # Create prompt template for formatting transaction data
    format_template = PromptTemplate(
        input_variables=["transaction_data"],
        template="""You are a helpful assistant. Format this transaction data into a clear, readable response.
Just present the key information in simple sentences. Be concise and friendly.

Transaction data:
{transaction_data}

Format this into a clear, readable response (2-3 sentences max):"""
    )
    
    format_chain = LLMChain(llm=llm, prompt=format_template)
    return format_chain


def router_response(user_message: str, llm: LLM, context_info: str, format_chain) -> str:
    """
    Simple router: detects transaction search and routes to tool, then formats response
    
    Args:
        user_message: User's question/message
        llm: The DeepSeekLLM instance
        context_info: Context about Sailor Sheet
        format_chain: Chain for formatting responses
        
    Returns:
        Formatted response string
    """
    # Check if it's a transaction search request
    transaction_keywords = ['transaction', 'be-', 'vn-', 'search', 'find', 'lookup']
    is_transaction_query = any(keyword in user_message.lower() for keyword in transaction_keywords)
    
    if is_transaction_query:
        # Extract transaction number
        transaction_number = extract_transaction_number(user_message)
        
        if transaction_number:
            print(f"🔍 Router: Searching for transaction {transaction_number}")
            # Call the search tool
            transaction_data = search_transaction_tool(transaction_number)
            
            # Format the response using LLM
            try:
                formatted_response = format_chain.invoke({"transaction_data": transaction_data})
                return formatted_response["text"]
            except Exception as e:
                print(f"❌ Error formatting response: {e}")
                # Return raw transaction data if formatting fails
                return transaction_data
        else:
            return "I couldn't find a transaction number in your message. Please provide a transaction number like VN-151025-135926."
    
    # Not a transaction query - return None to use regular chain
    return None
