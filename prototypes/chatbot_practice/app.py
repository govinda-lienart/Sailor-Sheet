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
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Import from new modular structure
from llm import DeepSeekLLM
from services import ChatService
from tools import setup_router

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

chat_service = ChatService(
    context_info=context_info,
    general_chain=chain,
    router_chain=router_chain,
    transaction_tool=transaction_tool,
    format_chain=format_chain,
)


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
        ai_response = chat_service.handle_message(user_message)

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
