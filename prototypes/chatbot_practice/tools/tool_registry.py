"""
Action Tool Registry Builder
Assembles individual tool definitions into a single dictionary.
"""

from typing import Callable, Dict

from langchain.tools import Tool

from .general_chat_tool import build_general_chat_tool
from .reject_action_tools import build_reject_destructive_tool, build_reject_unclear_tool
from .search_action_tool import build_search_tool


def build_action_tools(
    search_callback: Callable[[str], str],
    general_chat_callback: Callable[[str], str],
    destructive_reply_callback: Callable[[str], str],
    unclear_reply_callback: Callable[[str], str],
) -> Dict[str, Tool]:
    """
    Build the dictionary of Tool objects keyed by router action name.

    Args:
        search_callback: Handles transaction lookup formatting.
        general_chat_callback: Handles Sailor Sheet conversational answers.
        destructive_reply_callback: Returns copy for destructive refusals.
        unclear_reply_callback: Returns copy for unclear intent replies.
    """
    return {
        "search_transaction": build_search_tool(search_callback),
        "general_chat": build_general_chat_tool(general_chat_callback),
        "reject_destructive": build_reject_destructive_tool(destructive_reply_callback),
        "reject_unclear": build_reject_unclear_tool(unclear_reply_callback),
    }


__all__ = ["build_action_tools"]
