"""
Search Transaction Tool
Provides a helper to build the read-only Sailor Sheet search tool.
"""

from typing import Callable

from langchain.tools import Tool


def build_search_tool(search_callback: Callable[[str], str]) -> Tool:
    """Create a Tool wrapper around the transaction search callback."""

    def search_action(transaction_number: str) -> str:
        txn = (transaction_number or "").strip()
        if not txn:
            return "I need a transaction number like VN-151025-135926 to search."
        return search_callback(txn)

    return Tool(
        name="search_transaction",
        func=search_action,
        description="Read-only lookup of a Sailor Sheet transaction by its BE/VN identifier.",
    )


__all__ = ["build_search_tool"]
