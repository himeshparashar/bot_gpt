"""
Base LLM Provider - Abstract Base Class
"""
from abc import ABC, abstractmethod
from typing import List, Dict


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers (Strategy Pattern)"""
    
    @abstractmethod
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a response from the LLM"""
        pass
    
    @abstractmethod
    async def generate_stream(self, messages: List[Dict[str, str]], **kwargs):
        """Generate a streaming response from the LLM"""
        pass
