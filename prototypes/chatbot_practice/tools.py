"""
Tools and Router Setup for Chatbot Practice
Handles transaction search tools and simple routing using LangChain Tools
"""

from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.tools import Tool
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
    Set up router with LangChain Tool and formatting chain
    
    Args:
        llm: The DeepSeekLLM instance
        context_info: Context about Sailor Sheet
        
    Returns:
        Tuple of (transaction_tool, format_chain, decision_chain)
    """
    # Wrap search_transaction_tool in LangChain Tool
    transaction_tool = Tool(
        name="search_transaction",
        func=search_transaction_tool,
        description=(
            "Search for a transaction in Sailor Sheet accounting system (Vietnam ledger). "
            "Use this when the user asks to find, search, or get details about a transaction. "
            "Transaction numbers start with BE or VN followed by numbers and hyphens (e.g., VN-151025-135926)."
        )
    )
    
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
    
    # Create decision chain: asks LLM to classify intent (fast, single call)
    decision_template = PromptTemplate(
        input_variables=["user_message"],
        template="""You are a router for an accounting chatbot. Classify what the user wants to do with a transaction.

Available tool: search_transaction (searches for transactions by transaction number like VN-151025-135926 or BE-131025-170514)

The chatbot can only SEARCH for transactions. It CANNOT delete, update, modify, or create transactions.

User message: {user_message}

Classify the user's intent. Answer with ONLY one word:
- SEARCH: if the user wants to search, find, get info, view, see details, investigate, check, etc.
- DESTRUCTIVE: if the user wants to delete, remove, update, edit, modify, create, add, change, etc.
- UNCLEAR: if the intent is unclear or neither search nor destructive

Answer:"""
    )
    
    decision_chain = LLMChain(llm=llm, prompt=decision_template)
    
    return transaction_tool, format_chain, decision_chain


def router_response(user_message: str, transaction_tool: Tool, format_chain: LLMChain, decision_chain: LLMChain) -> str:
    """
    Router using LangChain Tools with verb-based routing:
    - Transaction number + allowed verb → fast path
    - Transaction number + forbidden verb → error immediately
    - Transaction number only → ask for clarification
    - Transaction number + unknown verb → LLM decision
    - No transaction number → LLM decision for general queries
    
    Args:
        user_message: User's question/message
        transaction_tool: LangChain Tool for searching transactions
        format_chain: Chain for formatting transaction data
        decision_chain: Chain for deciding if tool should be used
        
    Returns:
        Formatted response string, or None if not a transaction query
    """
    try:
        user_lower = user_message.lower()
        
        # Define verb categories
        allowed_verbs = ['search', 'find', 'show', 'get', 'lookup', 'retrieve', 'display', 'info', 'information', 'details', 'tell me about', 'what is']
        forbidden_verbs = ['delete', 'remove', 'cancel', 'void', 'update', 'edit', 'change', 'modify', 'create', 'add', 'new', 'insert']
        
        # Check for verbs in message
        has_allowed_verb = any(verb in user_lower for verb in allowed_verbs)
        has_forbidden_verb = any(verb in user_lower for verb in forbidden_verbs)
        
        # Extract transaction number
        transaction_number = extract_transaction_number(user_message)
        
        # CASE 1: Transaction number found
        if transaction_number:
            # Check if message has additional words beyond the transaction number (indicates a verb/action)
            # Remove transaction number from message and check if anything remains
            message_without_txn = user_lower.replace(transaction_number.lower(), '').strip()
            # Remove common words that might appear with transaction numbers
            message_without_txn = message_without_txn.replace('the', '').replace('a', '').replace('an', '').strip()
            has_additional_words = len(message_without_txn.split()) > 0
            
            # A) Transaction number + FORBIDDEN verb → block immediately
            if has_forbidden_verb:
                print(f"🚫 Blocked: Forbidden action detected for transaction {transaction_number}")
                return "Sorry, I can't assist with that request. I can only search for and provide information about transactions. I cannot delete, update, or modify transactions."
            
            # B) Transaction number + ALLOWED verb → fast path
            elif has_allowed_verb:
                print(f"⚡ Fast path: Transaction {transaction_number} with allowed verb, calling tool directly")
                transaction_data = transaction_tool.run(transaction_number)
                
                # Format the response using LLM
                try:
                    formatted_response = format_chain.invoke({"transaction_data": transaction_data})
                    return formatted_response["text"]
                except Exception as e:
                    print(f"❌ Error formatting response: {e}")
                    return transaction_data
            
            # C) Transaction number ONLY (no additional words) → ask what they want
            elif not has_additional_words:
                print(f"❓ Transaction number only: {transaction_number}, asking for clarification")
                return f"What would you like to do with transaction {transaction_number}? I can search for and show you the transaction details. Please specify what you need (e.g., 'search {transaction_number}' or 'show details for {transaction_number}')."
            
            # D) Transaction number + UNKNOWN verb/words → use LLM decision
            else:
                print(f"🤔 Transaction {transaction_number} with unknown verb/words, using LLM to classify intent...")
                decision_response = decision_chain.invoke({"user_message": user_message})
                decision = decision_response["text"].strip().upper()
                
                if "SEARCH" in decision:
                    print(f"🔍 LLM classified as SEARCH: Searching for transaction {transaction_number}")
                    transaction_data = transaction_tool.run(transaction_number)
                    try:
                        formatted_response = format_chain.invoke({"transaction_data": transaction_data})
                        return formatted_response["text"]
                    except Exception as e:
                        print(f"❌ Error formatting response: {e}")
                        return transaction_data
                elif "DESTRUCTIVE" in decision:
                    print(f"🚫 LLM classified as DESTRUCTIVE for transaction {transaction_number}")
                    return "Sorry, I can't assist with that request. I can only search for and provide information about transactions. I cannot delete, update, or modify transactions."
                else:
                    # UNCLEAR or anything else
                    print(f"❓ LLM classified as UNCLEAR for transaction {transaction_number}")
                    return f"I'm not sure what you'd like to do with transaction {transaction_number}. I can search for and show you the transaction details. Please specify what you need (e.g., 'search {transaction_number}' or 'show details for {transaction_number}')."
        
        # CASE 2: No transaction number → use LLM decision for general queries
        else:
            print("🤔 No transaction number found, using LLM to check if transaction-related...")
            decision_response = decision_chain.invoke({"user_message": user_message})
            decision = decision_response["text"].strip().upper()
            
            if "SEARCH" in decision or "DESTRUCTIVE" in decision:
                # LLM thinks it's a transaction query but no number found
                return "I understand you're asking about a transaction, but I couldn't find a transaction number in your message. Please provide a transaction number like VN-151025-135926 or BE-131025-170514."
            else:
                # Not a transaction query - return None to use regular chain
                print("💬 Not a transaction query, using regular chain")
                return None
            
    except Exception as e:
        print(f"❌ Error in router: {e}")
        # Fallback: try extracting transaction number directly
        transaction_number = extract_transaction_number(user_message)
        if transaction_number:
            print(f"🔄 Fallback: Direct tool call for {transaction_number}")
            try:
                transaction_data = transaction_tool.run(transaction_number)
                formatted_response = format_chain.invoke({"transaction_data": transaction_data})
                return formatted_response["text"]
            except:
                return "I encountered an error processing your request. Please try again."
        return None
