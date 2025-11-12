"""
Flask Backend for Chatbot Practice
Main entry point - handles routes and coordinates LLM + tools.
"""

# IMPORTANT: Load environment variables FIRST, before any imports that need them
from dotenv import load_dotenv
import os

# Load .env file from project root (two levels up from this file)
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(env_path)

# Now import everything else
from typing import Dict

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.tools import Tool

# Import from new modular structure
from llm import DeepSeekLLM
from tools import extract_transaction_number, route_message, setup_router

# ------------------------------------------------------------
# 🌍 Environment & Configuration
# ------------------------------------------------------------

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from frontend

# ------------------------------------------------------------
# 📘 Context Loader
# ------------------------------------------------------------

def load_context() -> str:
    """Load context information about Sailor Sheet from text file."""
    try:
        context_path = os.path.join(os.path.dirname(__file__), "context.txt")
        with open(context_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Could not load context file."


context_info = load_context()
print(f"✅ Context loaded: {len(context_info)} characters")

# ------------------------------------------------------------
# 🤖 LLM & Chains Setup
# ------------------------------------------------------------

# Initialize DeepSeek LLM
llm = DeepSeekLLM()

# General question answering prompt
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are a helpful AI assistant for Sailor Sheet, an accounting application.

Here is information about Sailor Sheet:
{context}

Based on this information, answer the user's question in a friendly and helpful way.
Keep your response concise (2–3 sentences max) and conversational.

User question: {question}

Your answer:"""
)

# General-purpose LangChain chain
chain = LLMChain(llm=llm, prompt=prompt_template)

# Initialize router and tools for transaction queries
transaction_tool, format_chain, router_chain = setup_router(llm)

DEFAULT_DESTRUCTIVE_REPLY = "Sorry, I can only show transaction information — not delete, update, or modify it."
DEFAULT_UNCLEAR_REPLY = "Please include a transaction number like VN-151025-135926 or clarify what you need."


def _format_transaction_search(transaction_number: str) -> str:
    """Run the search tool and format the response for the user."""
    data = transaction_tool.run(transaction_number)
    try:
        return format_chain.invoke({"transaction_data": data})["text"]
    except Exception as exc:
        print(f"❌ Formatting error: {exc}")
        return data


def _run_general_chain(user_message: str) -> str:
    """Fallback to the general Sailor Sheet chain."""
    try:
        result = chain.invoke({"context": context_info, "question": user_message})
        return result["text"]
    except Exception as exc:
        print(f"❌ Error in general chain: {exc}")
        return "Sorry, I couldn't process your request right now. Please try again later."


def _build_action_tools() -> Dict[str, Tool]:
    """Wrap each action as a LangChain Tool for consistent dispatching."""

    def search_action(transaction_number: str) -> str:
        txn = (transaction_number or "").strip()
        if not txn:
            return "I need a transaction number like VN-151025-135926 to search."
        return _format_transaction_search(txn)

    def general_chat_action(message: str) -> str:
        return _run_general_chain(message)

    def reject_destructive_action(reason: str) -> str:
        return reason or DEFAULT_DESTRUCTIVE_REPLY

    def reject_unclear_action(reason: str) -> str:
        return reason or DEFAULT_UNCLEAR_REPLY

    return {
        "search_transaction": Tool(
            name="search_transaction",
            func=search_action,
            description="Read-only lookup of a Sailor Sheet transaction by its BE/VN identifier.",
        ),
        "general_chat": Tool(
            name="general_chat",
            func=general_chat_action,
            description="Friendly Q&A about Sailor Sheet that does not require transaction data.",
        ),
        "reject_destructive": Tool(
            name="reject_destructive",
            func=reject_destructive_action,
            description="Politely refuse requests to delete, edit, or modify accounting records.",
        ),
        "reject_unclear": Tool(
            name="reject_unclear",
            func=reject_unclear_action,
            description="Ask the user to clarify or include a transaction number before continuing.",
        ),
    }


ACTION_TOOLS = _build_action_tools()


# ------------------------------------------------------------
# 🧩 Helper Functions
# ------------------------------------------------------------

def call_deepseek_api(user_message: str) -> str:
    """Decide whether to use a structured tool or the general chat chain."""
    try:
        decision = route_message(user_message, router_chain)
    except Exception as exc:
        print(f"❌ Router invocation failed: {exc}")
        return _run_general_chain(user_message)

    action = (decision.tool or "general_chat").lower()
    tool = ACTION_TOOLS.get(action)

    if not tool:
        print(f"⚠️ Unknown router action '{action}', using general chat.")
        return _run_general_chain(user_message)

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

    # Fallback just in case
    print(f"⚠️ Unhandled router action '{action}', defaulting to general chat.")
    return _run_general_chain(user_message)


# ------------------------------------------------------------
# 🌐 Flask Routes
# ------------------------------------------------------------

@app.route("/")
def index():
    """Serve the main HTML interface."""
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Handle chatbot messages with AI-powered responses.

    Expected JSON:
    {
        "message": "user's message"
    }

    Returns:
    {
        "response": "AI-generated response"
    }
    """
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"response": "I'm here to help! What would you like to know?"}), 400

        print(f"📩 Received message: {user_message}")
        ai_response = call_deepseek_api(user_message)

        if ai_response:
            print(f"✅ AI response: {ai_response[:60]}...")
            return jsonify({"response": ai_response})
        else:
            print("⚠️ Empty AI response, returning fallback.")
            return jsonify({"response": "I'm having trouble right now, please try again later!"}), 503

    except Exception as e:
        print(f"❌ Error in /api/chat: {e}")
        return jsonify({"response": "Sorry, I encountered an error. Please try again!"}), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint for monitoring."""
    return jsonify({
        "status": "healthy",
        "service": "Sailor Sheet Chatbot Practice",
        "context_loaded": len(context_info) > 0
    })


# ------------------------------------------------------------
# 🚀 Application Entry Point
# ------------------------------------------------------------

if __name__ == "__main__":
    print("🤖 Starting Sailor Sheet Chatbot Practice with DeepSeek AI...")
    app.run(debug=True, port=9000, host="0.0.0.0")
