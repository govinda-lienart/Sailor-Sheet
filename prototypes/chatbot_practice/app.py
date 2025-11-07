"""
Flask Backend for Chatbot Practice with DeepSeek Integration using LangChain
Handles AI-powered chatbot responses using LangChain with DeepSeek
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import Optional, List, Mapping, Any
from dotenv import load_dotenv
from tools import setup_router, router_response
import requests
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from frontend

# DeepSeek API Configuration from environment variables
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Validate that API key is set
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY environment variable is not set. Please add it to your .env file.")

# Load context from text file
def load_context():
    """Load the context information about Sailor Sheet"""
    try:
        context_path = os.path.join(os.path.dirname(__file__), 'context.txt')
        with open(context_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Sailor Sheet is an accounting application for small businesses."

context_info = load_context()
print(f"✅ Context loaded: {len(context_info)} characters")

# Custom LangChain LLM for DeepSeek
class DeepSeekLLM(LLM):
    """Custom LangChain LLM wrapper for DeepSeek API"""
    
    model_name: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 1000  # Increased for agent responses
    
    @property
    def _llm_type(self) -> str:
        return "deepseek"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
    ) -> str:
        """Call the DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant for Sailor Sheet, an accounting application. Be friendly, concise, and informative."},
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        try:
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            print(f"❌ Error calling DeepSeek API: {e}")
            return "I apologize, but I'm having trouble connecting right now. Please try again later."

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"model_name": self.model_name, "temperature": self.temperature}

# Initialize the DeepSeek LLM
llm = DeepSeekLLM()

# Create prompt template with LangChain
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are a helpful AI assistant for Sailor Sheet, an accounting application.

Here is information about Sailor Sheet:
{context}

Based on this information, answer the user's question in a friendly and helpful way.
Keep your response concise (2-3 sentences max) and conversational.

User question: {question}

Your answer:"""
)

# Create LangChain chain for general questions
chain = LLMChain(llm=llm, prompt=prompt_template)

# Set up router with LangChain Tools (do this once at startup)
transaction_tool, format_chain, decision_chain = setup_router(llm, context_info)
print("✅ Router with LangChain Tools initialized")

# Function to call using LangChain chain or Router
3

@app.route('/')
def index():
    """Serve the main HTML file"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handle chatbot messages with AI-powered responses
    
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
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'response': "I'm here to help! What would you like to know?"}), 400
        
        print(f"📩 Received message: {user_message}")
        
        # Get AI response from DeepSeek
        ai_response = call_deepseek_api(user_message)
        
        if ai_response:
            print(f"✅ AI response received: {ai_response[:50]}...")
            return jsonify({'response': ai_response})
        else:
            # Fallback response if API fails
            print("⚠️ API call failed, returning fallback")
            return jsonify({'response': "I apologize, but I'm having trouble connecting right now. Please try again later!"}), 503
        
    except Exception as e:
        print(f"❌ Error in /api/chat: {e}")
        return jsonify({'response': "Sorry, I encountered an error. Please try again!"}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy', 
        'service': 'Sailor Sheet Chatbot Practice',
        'context_loaded': len(context_info) > 0
    })

if __name__ == '__main__':
    print("🤖 Starting Sailor Sheet Chatbot Practice with DeepSeek AI...")
    app.run(debug=True, port=9000, host='0.0.0.0')









