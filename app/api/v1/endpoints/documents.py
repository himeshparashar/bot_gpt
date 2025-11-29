"""
Document Endpoints - Handle document uploads for RAG
"""
from fastapi import APIRouter, UploadFile, File

from app.schemas.common import StatusResponse

router = APIRouter()


@router.post("/upload", response_model=StatusResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document for RAG processing.
    """
    # TODO: Implement document processing
    return StatusResponse(
        success=True,
        message=f"Document '{file.filename}' uploaded successfully"
    )
