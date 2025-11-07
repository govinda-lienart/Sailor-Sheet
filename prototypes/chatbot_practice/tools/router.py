"""
Router Logic
Handles routing user messages to appropriate tools and chains.
"""

from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.tools import Tool
import re
from .transaction_tool import search_transaction_tool
from .utils import extract_transaction_number


def setup_router(llm: LLM, context_info: str):
    """
    Set up router with LangChain Tool and helper chains.
    
    Args:
        llm: LangChain LLM instance
        context_info: Context information about Sailor Sheet
        
    Returns:
        Tuple of (transaction_tool, format_chain, decision_chain)
    """
    # Tool: transaction search
    transaction_tool = Tool(
        name="search_transaction",
        func=search_transaction_tool,
        description=(
            "Search for a transaction in Sailor Sheet (VN ledger). "
            "Use when user asks to find, get, or view a transaction. "
            "Transaction numbers start with BE or VN, e.g., VN-151025-135926."
        )
    )

    # Chain: formatting transaction data
    format_template = PromptTemplate(
        input_variables=["transaction_data"],
        template="""You are a helpful assistant. Format this transaction data clearly and naturally.
Transaction data:
{transaction_data}

Output a concise, friendly summary (2–3 sentences max):"""
    )
    format_chain = LLMChain(llm=llm, prompt=format_template)

    # Chain: decision-making (intent classification)
    decision_template = PromptTemplate(
        input_variables=["user_message"],
        template="""You are a router for an accounting chatbot. Classify the user's intent.

Available tool: search_transaction (looks up transactions like VN-151025-135926 or BE-131025-170514)

The chatbot can only SEARCH. It cannot delete, edit, or create data.

User message: {user_message}

Answer with one word only:
- SEARCH
- DESTRUCTIVE
- UNCLEAR
"""
    )
    decision_chain = LLMChain(llm=llm, prompt=decision_template)

    print("✅ Router with LangChain tools initialized")
    return transaction_tool, format_chain, decision_chain


def detect_intent(user_message: str, decision_chain: LLMChain) -> str:
    """
    Use LLM to classify intent as SEARCH, DESTRUCTIVE, or UNCLEAR.
    
    Args:
        user_message: User's input message
        decision_chain: LangChain chain for intent classification
        
    Returns:
        Intent classification string (SEARCH, DESTRUCTIVE, or UNCLEAR)
    """
    decision_response = decision_chain.invoke({"user_message": user_message})
    return decision_response["text"].strip().upper()


def handle_transaction_query(
    transaction_number: str,
    user_message: str,
    has_allowed_verb: bool,
    has_forbidden_verb: bool,
    has_additional_words: bool,
    transaction_tool: Tool,
    format_chain: LLMChain,
    decision_chain: LLMChain,
) -> str:
    """
    Handle transaction-related queries based on intent and verbs.
    
    Args:
        transaction_number: Extracted transaction number
        user_message: Original user message
        has_allowed_verb: Whether message contains allowed verbs (search, find, etc.)
        has_forbidden_verb: Whether message contains forbidden verbs (delete, update, etc.)
        has_additional_words: Whether message has words beyond transaction number
        transaction_tool: LangChain tool for searching transactions
        format_chain: Chain for formatting transaction data
        decision_chain: Chain for intent classification
        
    Returns:
        Formatted response string
    """
    if has_forbidden_verb:
        print(f"🚫 Forbidden action detected for {transaction_number}")
        return "Sorry, I can only show transaction information — not delete, update, or modify it."

    if has_allowed_verb:
        print(f"⚡ Fast path: Direct search for {transaction_number}")
        data = transaction_tool.run(transaction_number)
        try:
            return format_chain.invoke({"transaction_data": data})["text"]
        except Exception as e:
            print(f"❌ Formatting error: {e}")
            return data

    if not has_additional_words:
        print(f"❓ Transaction number only: {transaction_number}")
        return f"What would you like to do with transaction {transaction_number}? I can search and show details."

    # Unknown verbs → ask LLM to decide
    print(f"🤔 Unknown verb in query for {transaction_number}")
    decision = detect_intent(user_message, decision_chain)
    if "SEARCH" in decision:
        data = transaction_tool.run(transaction_number)
        try:
            return format_chain.invoke({"transaction_data": data})["text"]
        except Exception as e:
            print(f"❌ Formatting error: {e}")
            return data
    elif "DESTRUCTIVE" in decision:
        return "Sorry, I can only search transactions — not modify them."
    else:
        return f"I'm not sure what you'd like to do with {transaction_number}. Try saying 'search {transaction_number}'."


def router_response(
    user_message: str,
    transaction_tool: Tool,
    format_chain: LLMChain,
    decision_chain: LLMChain
) -> str | None:
    """
    Route user message through appropriate tool or fallback.
    
    Args:
        user_message: User's input message
        transaction_tool: LangChain tool for searching transactions
        format_chain: Chain for formatting transaction data
        decision_chain: Chain for intent classification
        
    Returns:
        Formatted response string or None for general queries
    """
    try:
        user_lower = user_message.lower()

        allowed_verbs = [
            'search', 'find', 'show', 'get', 'lookup', 'retrieve',
            'display', 'info', 'information', 'details', 'tell me about', 'what is'
        ]
        forbidden_verbs = [
            'delete', 'remove', 'cancel', 'void', 'update', 'edit',
            'change', 'modify', 'create', 'add', 'new', 'insert'
        ]

        has_allowed_verb = any(verb in user_lower for verb in allowed_verbs)
        has_forbidden_verb = any(verb in user_lower for verb in forbidden_verbs)

        transaction_number = extract_transaction_number(user_message)

        if transaction_number:
            # Clean message from transaction number
            message_without_txn = re.sub(transaction_number, '', user_lower, flags=re.IGNORECASE).strip()
            message_without_txn = re.sub(r'\b(the|a|an)\b', '', message_without_txn).strip()
            has_additional_words = bool(message_without_txn)

            return handle_transaction_query(
                transaction_number,
                user_message,
                has_allowed_verb,
                has_forbidden_verb,
                has_additional_words,
                transaction_tool,
                format_chain,
                decision_chain,
            )

        # No transaction number → general decision
        print("🤔 No transaction number detected — checking intent")
        decision = detect_intent(user_message, decision_chain)
        if "SEARCH" in decision or "DESTRUCTIVE" in decision:
            return "I understand you're asking about a transaction, but I couldn't find a number. Please include one like VN-151025-135926."
        else:
            print("💬 General query — hand off to main chain")
            return None

    except Exception as e:
        print(f"❌ Router error: {e}")
        txn = extract_transaction_number(user_message)
        if txn:
            try:
                data = transaction_tool.run(txn)
                return format_chain.invoke({"transaction_data": data})["text"]
            except Exception:
                return "I encountered an error processing your request. Please try again."
        return None

