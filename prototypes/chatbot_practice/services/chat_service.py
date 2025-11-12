"""
Chat Service
Encapsulates routing logic, tool dispatch, and fallbacks for the chatbot.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from langchain.chains import LLMChain
from langchain.tools import Tool

from tools import build_action_tools, extract_transaction_number, route_message

DEFAULT_DESTRUCTIVE_REPLY = "Sorry, I can only show transaction information — not delete, update, or modify it."
DEFAULT_UNCLEAR_REPLY = "Please include a transaction number like VN-151025-135926 or clarify what you need."


@dataclass
class ChatService:
    """Coordinates router decisions and tool execution."""

    context_info: str
    general_chain: LLMChain
    router_chain: LLMChain
    transaction_tool: Tool
    format_chain: LLMChain

    def __post_init__(self) -> None:
        self.action_tools: Dict[str, Tool] = build_action_tools(
            search_callback=self._format_transaction_search,
            general_chat_callback=self._run_general_chain,
            destructive_reply_callback=self._destructive_reply,
            unclear_reply_callback=self._unclear_reply,
        )

    def handle_message(self, user_message: str) -> str:
        """Entry point used by Flask route to answer a chat message."""
        try:
            decision = route_message(user_message, self.router_chain)
        except Exception as exc:
            print(f"❌ Router invocation failed: {exc}")
            return self._run_general_chain(user_message)

        action = (decision.tool or "general_chat").lower()
        tool = self.action_tools.get(action)

        if not tool:
            print(f"⚠️ Unknown router action '{action}', using general chat.")
            return self._run_general_chain(user_message)

        if action == "search_transaction":
            transaction_number = (decision.tool_input or "").strip() or extract_transaction_number(user_message)
            if not transaction_number:
                return decision.reason or "I need a transaction number like VN-151025-135926 to search."
            print(f"🔎 Router selected transaction lookup for {transaction_number}")
            return tool.run(transaction_number)

        if action == "general_chat":
            print("💬 Router selected general chat flow")
            payload = decision.tool_input or user_message
            return tool.run(payload)

        if action in {"reject_destructive", "reject_unclear"}:
            payload = decision.tool_input or decision.reason or ""
            return tool.run(payload)

        print(f"⚠️ Unhandled router action '{action}', defaulting to general chat.")
        return self._run_general_chain(user_message)

    def _format_transaction_search(self, transaction_number: str) -> str:
        """Run the search tool and format the response for the user."""
        data = self.transaction_tool.run(transaction_number)
        try:
            return self.format_chain.invoke({"transaction_data": data})["text"]
        except Exception as exc:
            print(f"❌ Formatting error: {exc}")
            return data

    def _run_general_chain(self, user_message: str) -> str:
        """Fallback to the general Sailor Sheet chain."""
        try:
            result = self.general_chain.invoke({"context": self.context_info, "question": user_message})
            return result["text"]
        except Exception as exc:
            print(f"❌ Error in general chain: {exc}")
            return "Sorry, I couldn't process your request right now. Please try again later."

    @staticmethod
    def _destructive_reply(reason: str) -> str:
        return reason or DEFAULT_DESTRUCTIVE_REPLY

    @staticmethod
    def _unclear_reply(reason: str) -> str:
        return reason or DEFAULT_UNCLEAR_REPLY
