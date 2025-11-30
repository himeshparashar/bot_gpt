"""
API v1 router - aggregates all endpoint routers
v1 for versioning
"""
from fastapi import APIRouter

from app.api.v1.endpoints import conversations, documents

api_router = APIRouter()

api_router.include_router(
    conversations.router, 
    prefix="/conversations", 
    tags=["Conversations"]
)

# document endpoints for RAG
api_router.include_router(
    documents.router, 
    prefix="/documents", 
    tags=["Documents"]
)
