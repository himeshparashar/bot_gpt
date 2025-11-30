from fastapi import APIRouter, UploadFile, File, HTTPException

from app.schemas.document import DocumentUploadResponse, DocumentDeleteResponse
from app.services.ingestion_service import ingestion_service

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload a document for RAG processing."""
    try:
        content = await file.read()
        result = await ingestion_service.ingest(
            content=content,
            filename=file.filename,
            content_type=file.content_type or "text/plain"
        )
        return DocumentUploadResponse(
            document_id=result.document_id,
            filename=result.filename,
            chunk_count=result.chunk_count,
            status=result.status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(document_id: str):
    """Delete a document from the vector store."""
    success = await ingestion_service.delete_document(document_id)
    return DocumentDeleteResponse(
        success=success,
        document_id=document_id,
        message="Document deleted" if success else "Delete failed"
    )
