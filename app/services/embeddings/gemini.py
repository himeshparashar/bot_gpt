from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core.config import settings
from app.services.embeddings.base import BaseEmbeddingProvider


class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    """Google Gemini embedding provider"""
    
    MODEL_NAME = "models/embedding-001"
    DIMENSION = 768
    
    def __init__(self):
        self._client = GoogleGenerativeAIEmbeddings(
            model=self.MODEL_NAME,
            google_api_key=settings.GOOGLE_API_KEY
        )
    
    async def embed_text(self, text: str) -> List[float]:
        return self._client.embed_query(text)
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return self._client.embed_documents(texts)
    
    @property
    def dimension(self) -> int:
        return self.DIMENSION
