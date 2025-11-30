from typing import Tuple
from langchain_community.document_loaders import PyPDFLoader
import tempfile
import os


class DocumentProcessor:
    """Process different document types and extract text"""
    
    SUPPORTED_TYPES = {
        "application/pdf": "pdf",
        "text/plain": "txt",
        "text/markdown": "md",
    }
    
    async def process(self, content: bytes, filename: str, content_type: str) -> Tuple[str, str]:
        """
        Process document and extract text.
        Returns (extracted_text, file_type)
        """
        file_type = self._get_file_type(filename, content_type)
        
        if file_type == "pdf":
            text = await self._process_pdf(content)
        else:
            text = await self._process_text(content)
        
        return text, file_type
    
    def _get_file_type(self, filename: str, content_type: str) -> str:
        if content_type in self.SUPPORTED_TYPES:
            return self.SUPPORTED_TYPES[content_type]
        
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext in ["pdf"]:
            return "pdf"
        return "txt"
    
    async def _process_pdf(self, content: bytes) -> str:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            loader = PyPDFLoader(tmp_path)
            pages = loader.load()
            return "\n\n".join(page.page_content for page in pages)
        finally:
            os.unlink(tmp_path)
    
    async def _process_text(self, content: bytes) -> str:
        return content.decode("utf-8")
