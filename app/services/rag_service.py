from typing import List, Optional
import logging

from app.services.embeddings import EmbeddingFactory, BaseEmbeddingProvider
from app.services.vectorstore import VectorStoreFactory, BaseVectorStore

logger = logging.getLogger(__name__)


class RAGService:
    """Service for RAG operations - retrieves relevant document context"""
    
    def __init__(
        self,
        embedding_provider: BaseEmbeddingProvider = None,
        vector_store: BaseVectorStore = None
    ):
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        self._initialized = embedding_provider is not None and vector_store is not None
    
    def _ensure_initialized(self):
        """Lazy initialization of embedding provider and vector store"""
        if not self._initialized:
            if self._embedding_provider is None:
                self._embedding_provider = EmbeddingFactory.create()
                if self._embedding_provider is None:
                    raise ValueError("No API key configured for embedding provider.")
            if self._vector_store is None:
                self._vector_store = VectorStoreFactory.create()
            self._initialized = True
    
    async def retrieve_context(self, query: str, top_k: int = 5) -> str:
        """
        Retrieve relevant document context for a query.
        
        Args:
            query: The user's query to find relevant context for
            top_k: Number of top results to retrieve
            
        Returns:
            Formatted string containing relevant document chunks
        """
        try:
            self._ensure_initialized()
            
            # Generate embedding for the query
            query_embedding = await self._embedding_provider.embed_text(query)
            
            # Search vector store for relevant chunks
            results = await self._vector_store.search(query_embedding, top_k=top_k)
            
            if not results:
                logger.info(f"No relevant documents found for query: {query[:50]}...")
                return ""
            
            # Format the context from retrieved chunks
            context_parts = []
            for i, result in enumerate(results, 1):
                source = result.metadata.get("filename", "Unknown") if result.metadata else "Unknown"
                context_parts.append(f"[Source: {source}]\n{result.content}")
            
            context = "\n\n---\n\n".join(context_parts)
            logger.info(f"Retrieved {len(results)} relevant chunks for query")
            logger.debug(f"Retrieved context length: {len(context)} chars")
            logger.debug(f"Context preview: {context[:500]}...")
            
            return context
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return ""
    
    async def retrieve_context_chunks(self, query: str, top_k: int = 5) -> List[dict]:
        """
        Retrieve relevant document chunks with metadata.
        
        Returns:
            List of dicts with content, score, and metadata
        """
        try:
            self._ensure_initialized()
            
            query_embedding = await self._embedding_provider.embed_text(query)
            results = await self._vector_store.search(query_embedding, top_k=top_k)
            
            return [
                {
                    "content": r.content,
                    "score": r.score,
                    "metadata": r.metadata
                }
                for r in results
            ]
            
        except Exception as e:
            logger.error(f"Error retrieving context chunks: {e}")
            return []


# Singleton instance - lazy initialized
rag_service = RAGService()
