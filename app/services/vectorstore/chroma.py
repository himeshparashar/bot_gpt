from typing import List
import chromadb

from app.core.config import settings
from app.services.vectorstore.base import BaseVectorStore, DocumentChunk, SearchResult


class ChromaVectorStore(BaseVectorStore):
    """Chroma vector store implementation"""
    
    COLLECTION_NAME = "documents"
    
    def __init__(self, persist_directory: str = None):
        persist_dir = persist_directory or settings.CHROMA_PERSIST_DIR
        self._client = chromadb.PersistentClient(path=persist_dir)
        self._collection = self._client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
    
    async def add_documents(self, chunks: List[DocumentChunk]) -> List[str]:
        if not chunks:
            return []
        
        self._collection.add(
            ids=[chunk.id for chunk in chunks],
            embeddings=[chunk.embedding for chunk in chunks],
            documents=[chunk.content for chunk in chunks],
            metadatas=[chunk.metadata or {} for chunk in chunks]
        )
        return [chunk.id for chunk in chunks]
    
    async def search(self, query_embedding: List[float], top_k: int = 5) -> List[SearchResult]:
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        search_results = []
        if results["ids"] and results["ids"][0]:
            for i, chunk_id in enumerate(results["ids"][0]):
                search_results.append(SearchResult(
                    chunk_id=chunk_id,
                    content=results["documents"][0][i],
                    score=1 - results["distances"][0][i],
                    metadata=results["metadatas"][0][i] if results["metadatas"] else None
                ))
        return search_results
    
    async def delete_by_document_id(self, document_id: str) -> bool:
        try:
            self._collection.delete(where={"document_id": document_id})
            return True
        except Exception:
            return False
