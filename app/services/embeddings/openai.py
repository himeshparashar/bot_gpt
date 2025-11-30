from typing import List
from langchain_openai import OpenAIEmbeddings

from app.core.config import settings
from app.services.embeddings.base import BaseEmbeddingProvider


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """OpenAI embedding provider"""
    
    MODEL_NAME = "text-embedding-3-small"
    DIMENSION = 1536
    
    def __init__(self):
        self._client = OpenAIEmbeddings(
            model=self.MODEL_NAME,
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    async def embed_text(self, text: str) -> List[float]:
        return self._client.embed_query(text)
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return self._client.embed_documents(texts)
    
    @property
    def dimension(self) -> int:
        return self.DIMENSION
