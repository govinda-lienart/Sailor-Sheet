"""
DeepSeek LLM Integration
Custom LangChain LLM wrapper for DeepSeek API.
"""

from langchain.llms.base import LLM
from typing import Optional, List, Mapping, Any
import requests
import os

# DeepSeek API Configuration
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Validate API key
if not DEEPSEEK_API_KEY:
    raise ValueError(
        "DEEPSEEK_API_KEY environment variable is not set. "
        "Please add it to your .env file."
    )


class DeepSeekLLM(LLM):
    """Custom LangChain LLM wrapper for DeepSeek API."""

    model_name: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 1000

    @property
    def _llm_type(self) -> str:
        """Return LLM type identifier for LangChain."""
        return "deepseek"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
    ) -> str:
        """Send prompt to DeepSeek API and return model response."""
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful AI assistant for Sailor Sheet, an accounting application. "
                        "Be friendly, concise, and informative."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        try:
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"❌ Error calling DeepSeek API: {e}")
            return "I apologize, but I'm having trouble connecting right now. Please try again later."

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Return identifying parameters for LangChain."""
        return {"model_name": self.model_name, "temperature": self.temperature}

