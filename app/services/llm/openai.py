"""
OpenAI LLM Provider Implementation
"""
from typing import List, Dict
from openai import AsyncOpenAI

from app.services.llm.base import BaseLLMProvider
from app.core.config import settings


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider implementation"""
    
    def __init__(self, model: str = "gpt-4"):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = model
    
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a response using OpenAI API"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content
    
    async def generate_stream(self, messages: List[Dict[str, str]], **kwargs):
        """Generate a streaming response using OpenAI API"""
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
            **kwargs
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
