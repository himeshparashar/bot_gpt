from enum import Enum
from typing import Dict, Type

from app.services.vectorstore.base import BaseVectorStore
from app.services.vectorstore.chroma import ChromaVectorStore


class VectorStoreType(str, Enum):
    CHROMA = "chroma"


class VectorStoreFactory:
    """Factory for creating vector store instances"""
    
    _stores: Dict[VectorStoreType, Type[BaseVectorStore]] = {
        VectorStoreType.CHROMA: ChromaVectorStore,
    }
    
    _instance: BaseVectorStore = None
    
    @classmethod
    def create(cls, store_type: VectorStoreType = VectorStoreType.CHROMA) -> BaseVectorStore:
        if cls._instance is None:
            store_class = cls._stores.get(store_type)
            if not store_class:
                raise ValueError(f"Unknown vector store type: {store_type}")
            cls._instance = store_class()
        return cls._instance
