"""
Router Logic
Uses a single LLM router to choose between actions like transaction search,
general chat, or rejecting destructive/unclear intents.
"""

from dataclasses import dataclass
import json
from typing import Optional, Tuple

from langchain.chains import LLMChain
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain.tools import Tool

from .transaction_tool import search_transaction_tool


@dataclass
class RouterDecision:
    """Structured decision returned by the LLM router."""

    action: str
    transaction_number: Optional[str] = None
    reason: Optional[str] = None


ROUTER_TEMPLATE = """You route messages for the Sailor Sheet assistant.

Available actions:
1. search_transaction: Use only to READ/LOOK UP a transaction. Requires a transaction_number in the form BE-XXXXXXXX or VN-XXXXXXXX (letters+digits with dashes). Never use this to edit or delete anything.
2. general_chat: Use for greetings, chit-chat, or any question about Sailor Sheet that does not require looking up a specific transaction.
3. reject_destructive: Use when the user wants to delete, edit, modify, add, create, insert, or otherwise change accounting data.
4. reject_unclear: Use when the request is ambiguous, missing a transaction number, or you cannot determine the intent confidently.

Rules:
- If a transaction is mentioned but the number is missing, choose reject_unclear.
- If the user requests any destructive action (delete/update/etc.), choose reject_destructive.
- Your response must be raw JSON with keys action, transaction_number, and reason.
- transaction_number must be null when not needed.
- reason is a short sentence explaining the choice.

User message: {user_message}

JSON:"""


def setup_router(llm: LLM) -> Tuple[Tool, LLMChain, LLMChain]:
    """
    Build the LangChain tool, formatter chain, and intent router chain.

    Returns:
        Tuple of (transaction_tool, format_chain, router_chain)
    """
    transaction_tool = Tool(
        name="search_transaction",
        func=search_transaction_tool,
        description=(
            "Search for a transaction in Sailor Sheet (VN ledger). "
            "Use when the user asks to find, get, or view a transaction. "
            "Transaction numbers start with BE or VN, e.g., VN-151025-135926."
        ),
    )

    format_template = PromptTemplate(
        input_variables=["transaction_data"],
        template="""You are a helpful assistant. Format this transaction data clearly and naturally.
Transaction data:
{transaction_data}

Output a concise, friendly summary (2–3 sentences max):""",
    )
    format_chain = LLMChain(llm=llm, prompt=format_template)

    router_template = PromptTemplate(
        input_variables=["user_message"],
        template=ROUTER_TEMPLATE,
    )
    router_chain = LLMChain(llm=llm, prompt=router_template)

    print("✅ LLM intent router initialized")
    return transaction_tool, format_chain, router_chain


def _strip_json_snippet(raw_text: str) -> str:
    """Remove code fences or leading text so json.loads succeeds."""
    text = raw_text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        # Remove possible language hint like json\n
        lines = text.splitlines()
        if lines and lines[0].lower().startswith("json"):
            lines = lines[1:]
        text = "\n".join(lines).strip()
    return text


def parse_router_output(raw_output: str) -> RouterDecision:
    """
    Convert the LLM output into a RouterDecision object.

    Falls back to general_chat when parsing fails.
    """
    cleaned = _strip_json_snippet(raw_output)
    try:
        data = json.loads(cleaned)
        return RouterDecision(
            action=data.get("action", "general_chat"),
            transaction_number=data.get("transaction_number"),
            reason=data.get("reason"),
        )
    except json.JSONDecodeError:
        print("⚠️ Router output was not valid JSON, defaulting to general_chat")
        return RouterDecision(
            action="general_chat",
            reason="Router output could not be parsed.",
        )


def route_message(user_message: str, router_chain: LLMChain) -> RouterDecision:
    """Invoke the router chain and parse its structured decision."""
    response = router_chain.invoke({"user_message": user_message})
    raw_text = response["text"]
    return parse_router_output(raw_text)
