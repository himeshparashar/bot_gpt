from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class DocumentChunk:
    """Represents a document chunk with metadata"""
    id: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Optional[dict] = None


@dataclass
class SearchResult:
    """Search result from vector store"""
    chunk_id: str
    content: str
    score: float
    metadata: Optional[dict] = None


class BaseVectorStore(ABC):
    """Abstract base class for vector stores (Strategy Pattern)"""
    
    @abstractmethod
    async def add_documents(self, chunks: List[DocumentChunk]) -> List[str]:
        """Add document chunks with embeddings to the store"""
        pass
    
    @abstractmethod
    async def search(self, query_embedding: List[float], top_k: int = 5) -> List[SearchResult]:
        """Search for similar documents"""
        pass
    
    @abstractmethod
    async def delete_by_document_id(self, document_id: str) -> bool:
        """Delete all chunks for a document"""
        pass
