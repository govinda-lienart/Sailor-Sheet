"""
General Chat Tool
Wraps the fallback Sailor Sheet chat chain as a Tool.
"""

from typing import Callable

from langchain.tools import Tool


def build_general_chat_tool(general_chat_callback: Callable[[str], str]) -> Tool:
    """Create a Tool for conversational Sailor Sheet questions."""

    def general_chat_action(message: str) -> str:
        return general_chat_callback(message)

    return Tool(
        name="general_chat",
        func=general_chat_action,
        description="Friendly Q&A about Sailor Sheet that does not require transaction data.",
    )


__all__ = ["build_general_chat_tool"]
