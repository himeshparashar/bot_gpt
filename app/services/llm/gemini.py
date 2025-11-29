"""
Gemini LLM Provider Implementation
"""
from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage

from app.services.llm.base import BaseLLMProvider
from app.core.config import settings


class GeminiProvider(BaseLLMProvider):
    """Gemini LLM provider implementation"""
    
    def __init__(self, model: str = "gemini-1.5-flash"):
        self.model = model
        self.client = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=settings.GOOGLE_API_KEY,
            convert_system_message_to_human=True
        )
    
    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[BaseMessage]:
        """Convert dict messages to LangChain messages"""
        converted_messages = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")
            if role == "user":
                converted_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                converted_messages.append(AIMessage(content=content))
            elif role == "system":
                converted_messages.append(SystemMessage(content=content))
        return converted_messages

    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a response using Gemini"""
        langchain_messages = self._convert_messages(messages)
        response = await self.client.ainvoke(langchain_messages)
        return response.content
    
    async def generate_stream(self, messages: List[Dict[str, str]], **kwargs):
        """Generate a streaming response using Gemini"""
        langchain_messages = self._convert_messages(messages)
        async for chunk in self.client.astream(langchain_messages):
            if chunk.content:
                yield chunk.content