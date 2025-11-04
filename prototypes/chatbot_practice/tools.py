"""
Tools and Agent Setup for Chatbot Practice
Handles LangChain tools and agent configuration
"""

from langchain.agents import initialize_agent, AgentType, Tool
from langchain.llms.base import LLM
import requests
import os

# Configuration - API base URL for main Sailor Sheet app
SAILOR_SHEET_API_URL = os.getenv('SAILOR_SHEET_API_URL', 'http://localhost:5000')


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


def setup_agent(llm: LLM, context_info: str):
    """
    Set up AgentExecutor with tools
    
    Args:
        llm: The DeepSeekLLM instance
        context_info: Context about Sailor Sheet for the agent
        
    Returns:
        AgentExecutor instance
    """
    # Create the tool
    transaction_search_tool = Tool(
        name="search_transaction",
        func=search_transaction_tool,
        description=(
            "Search for a transaction in Sailor Sheet accounting system (Vietnam ledger). "
            "Use this tool when the user asks to find, search, or get details about a transaction. "
            "Transaction numbers start with BE or VN followed by the transaction identifier. "
            "Just pass the transaction number as provided by the user. "
            "Example: 'search for transaction VN-151025-135926' or 'find BE-131025-170514'"
        )
    )
    
    # Create tools list
    tools = [transaction_search_tool]
    
    # Initialize agent
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,  # Print agent reasoning (helpful for debugging)
        handle_parsing_errors=True,
        max_iterations=3  # Limit to prevent infinite loops
    )
    
    return agent


def get_agent_response(user_message: str, agent, context_info: str) -> str:
    """
    Get response from agent, with context about Sailor Sheet
    
    Args:
        user_message: User's question/message
        agent: The AgentExecutor instance
        context_info: Context about Sailor Sheet
        
    Returns:
        Agent's response string
    """
    # Build prompt with context and user message
    prompt = f"""You are a helpful AI assistant for Sailor Sheet, an accounting application.

Context about Sailor Sheet:
{context_info}

User question: {user_message}

Answer the user's question. If they ask about searching for a transaction, 
use the search_transaction tool. Be friendly, concise, and helpful.
"""
    
    try:
        response = agent.run(prompt)
        return response
    except Exception as e:
        print(f"❌ Error in agent execution: {e}")
        return "I apologize, but I encountered an error processing your request."
