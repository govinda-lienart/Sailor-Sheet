"""
Rejection Tools
Helpers that create tools for destructive and unclear intents.
"""

from typing import Callable

from langchain.tools import Tool


def build_reject_destructive_tool(reply_callback: Callable[[str], str]) -> Tool:
    """Create a Tool that politely refuses destructive requests."""

    def reject_destructive_action(reason: str) -> str:
        return reply_callback(reason or "")

    return Tool(
        name="reject_destructive",
        func=reject_destructive_action,
        description="Politely refuse requests to delete, edit, or modify accounting records.",
    )


def build_reject_unclear_tool(reply_callback: Callable[[str], str]) -> Tool:
    """Create a Tool that asks the user to clarify their intent."""

    def reject_unclear_action(reason: str) -> str:
        return reply_callback(reason or "")

    return Tool(
        name="reject_unclear",
        func=reject_unclear_action,
        description="Ask the user to clarify or include a transaction number before continuing.",
    )


__all__ = ["build_reject_destructive_tool", "build_reject_unclear_tool"]
