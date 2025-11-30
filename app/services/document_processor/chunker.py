from typing import List
from dataclasses import dataclass
from langchain_text_splitters import RecursiveCharacterTextSplitter


@dataclass
class TextChunk:
    """Represents a chunk of text with position info"""
    content: str
    start_index: int
    chunk_index: int


class TextChunker:
    """Text chunking service using LangChain splitters"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            add_start_index=True,
            length_function=len,
        )
    
    def chunk_text(self, text: str) -> List[TextChunk]:
        docs = self._splitter.create_documents([text])
        return [
            TextChunk(
                content=doc.page_content,
                start_index=doc.metadata.get("start_index", 0),
                chunk_index=i
            )
            for i, doc in enumerate(docs)
        ]
