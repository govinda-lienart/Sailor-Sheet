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

from .helpers.transaction_tool import search_transaction_tool


@dataclass
class RouterCall:
    """Structured tool call returned by the LLM router."""

    tool: str
    tool_input: Optional[str] = None
    reason: Optional[str] = None


ROUTER_TEMPLATE = """You route messages for the Sailor Sheet assistant.

Available tools:
1. search_transaction → READ ONLY lookup. Requires a transaction_number in the form BE-XXXXXXXX or VN-XXXXXXXX (letters+digits with dashes). Never use this to edit or delete anything.
2. general_chat → Friendly chit-chat or questions about Sailor Sheet that do not need a specific transaction lookup.
3. reject_destructive → When the user asks to delete, edit, modify, add, create, insert, or otherwise change accounting data.
4. reject_unclear → When the request is ambiguous, missing a transaction number, or you cannot determine intent confidently.

Rules:
- If a transaction is mentioned but the number is missing, call reject_unclear.
- If the user requests any destructive action (delete/update/etc.), call reject_destructive.
- Respond with raw JSON ONLY using keys: tool, tool_input, reason.
- tool must be one of: search_transaction, general_chat, reject_destructive, reject_unclear.
- tool_input must contain the transaction number for search_transaction, or the user message / explanation for other tools.
- reason is a short sentence explaining why you chose that tool.

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


def parse_router_output(raw_output: str) -> RouterCall:
    """
    Convert the LLM output into a RouterCall object.

    Falls back to general_chat when parsing fails.
    """
    cleaned = _strip_json_snippet(raw_output)
    try:
        data = json.loads(cleaned)
        return RouterCall(
            tool=data.get("tool", "general_chat"),
            tool_input=data.get("tool_input"),
            reason=data.get("reason"),
        )
    except json.JSONDecodeError:
        print("⚠️ Router output was not valid JSON, defaulting to general_chat")
        return RouterCall(
            tool="general_chat",
            reason="Router output could not be parsed.",
        )


def route_message(user_message: str, router_chain: LLMChain) -> RouterCall:
    """Invoke the router chain and parse its structured decision."""
    response = router_chain.invoke({"user_message": user_message})
    raw_text = response["text"]
    print(f"🧭 Router raw output: {raw_text}")
    return parse_router_output(raw_text)
