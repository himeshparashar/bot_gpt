from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    """Response after document upload and ingestion"""
    document_id: str
    filename: str
    chunk_count: int
    status: str


class DocumentDeleteResponse(BaseModel):
    """Response after document deletion"""
    success: bool
    document_id: str
    message: str
