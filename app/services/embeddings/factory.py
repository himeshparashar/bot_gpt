from enum import Enum
from typing import Dict, Type

from app.core.config import settings
from app.services.embeddings.base import BaseEmbeddingProvider
from app.services.embeddings.gemini import GeminiEmbeddingProvider
from app.services.embeddings.openai import OpenAIEmbeddingProvider


class EmbeddingProviderType(str, Enum):
    GEMINI = "gemini"
    OPENAI = "openai"


class EmbeddingFactory:
    """Factory for creating embedding providers"""
    
    _providers: Dict[EmbeddingProviderType, Type[BaseEmbeddingProvider]] = {
        EmbeddingProviderType.GEMINI: GeminiEmbeddingProvider,
        EmbeddingProviderType.OPENAI: OpenAIEmbeddingProvider,
    }
    
    @classmethod
    def create(cls, provider_type: EmbeddingProviderType = None) -> BaseEmbeddingProvider:
        if provider_type is None:
            provider_type = cls._get_default_provider()
            if provider_type is None:
                return None
        
        provider_class = cls._providers.get(provider_type)
        if not provider_class:
            raise ValueError(f"Unknown embedding provider: {provider_type}")
        
        return provider_class()
    
    @classmethod
    def _get_default_provider(cls) -> EmbeddingProviderType:
        if settings.GOOGLE_API_KEY:
            return EmbeddingProviderType.GEMINI
        if settings.OPENAI_API_KEY:
            return EmbeddingProviderType.OPENAI
        return None  # No API key configured, return None instead of raising
