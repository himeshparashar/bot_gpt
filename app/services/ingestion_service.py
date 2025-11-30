import uuid
from dataclasses import dataclass
from typing import Optional

from app.core.config import settings
from app.services.embeddings import EmbeddingFactory, BaseEmbeddingProvider
from app.services.vectorstore import VectorStoreFactory, BaseVectorStore
from app.services.vectorstore.base import DocumentChunk
from app.services.document_processor import DocumentProcessor, TextChunker


@dataclass
class IngestionResult:
    """Result of document ingestion"""
    document_id: str
    filename: str
    chunk_count: int
    status: str


class IngestionService:
    """Orchestrates the document ingestion pipeline"""
    
    def __init__(
        self,
        embedding_provider: BaseEmbeddingProvider = None,
        vector_store: BaseVectorStore = None,
        chunk_size: int = None,
        chunk_overlap: int = None
    ):
        # Lazy initialization - don't create providers if not explicitly passed
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        self._document_processor = DocumentProcessor()
        self._chunker = TextChunker(
            chunk_size=chunk_size or settings.CHUNK_SIZE,
            chunk_overlap=chunk_overlap or settings.CHUNK_OVERLAP
        )
        self._initialized = embedding_provider is not None and vector_store is not None
    
    def _ensure_initialized(self):
        """Lazy initialization of embedding provider and vector store"""
        if not self._initialized:
            if self._embedding_provider is None:
                self._embedding_provider = EmbeddingFactory.create()
                if self._embedding_provider is None:
                    raise ValueError("No API key configured for embedding provider. Set GOOGLE_API_KEY or OPENAI_API_KEY.")
            if self._vector_store is None:
                self._vector_store = VectorStoreFactory.create()
            self._initialized = True
    
    async def ingest(self, content: bytes, filename: str, content_type: str) -> IngestionResult:
        self._ensure_initialized()
        document_id = str(uuid.uuid4())
        
        text, file_type = await self._document_processor.process(content, filename, content_type)
        
        text_chunks = self._chunker.chunk_text(text)
        if not text_chunks:
            return IngestionResult(
                document_id=document_id,
                filename=filename,
                chunk_count=0,
                status="empty"
            )
        
        embeddings = await self._embedding_provider.embed_texts(
            [chunk.content for chunk in text_chunks]
        )
        
        document_chunks = [
            DocumentChunk(
                id=f"{document_id}_{chunk.chunk_index}",
                content=chunk.content,
                embedding=embeddings[i],
                metadata={
                    "document_id": document_id,
                    "filename": filename,
                    "chunk_index": chunk.chunk_index,
                    "start_index": chunk.start_index,
                    "file_type": file_type
                }
            )
            for i, chunk in enumerate(text_chunks)
        ]
        
        await self._vector_store.add_documents(document_chunks)
        
        return IngestionResult(
            document_id=document_id,
            filename=filename,
            chunk_count=len(document_chunks),
            status="completed"
        )
    
    async def delete_document(self, document_id: str) -> bool:
        self._ensure_initialized()
        return await self._vector_store.delete_by_document_id(document_id)


ingestion_service = IngestionService()
