"""
Groq LLM Provider Implementation
"""
from typing import List, Dict
import httpx

from app.services.llm.base import BaseLLMProvider
from app.core.config import settings


class GroqProvider(BaseLLMProvider):
    """Groq LLM provider implementation"""
    
    def __init__(self, model: str = "llama-3.1-70b-versatile"):
        self.api_key = settings.GROQ_API_KEY
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1"
    
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a response using Groq API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    **kwargs
                }
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
    
    async def generate_stream(self, messages: List[Dict[str, str]], **kwargs):
        """Generate a streaming response using Groq API"""
        # TODO: Implement streaming
        pass
