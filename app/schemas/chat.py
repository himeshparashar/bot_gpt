"""
Chat Schemas - Request/Response DTOs
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    """Chat request schema"""
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response schema"""
    message: str
    conversation_id: str


class MessageHistory(BaseModel):
    """Message history schema"""
    id: str
    role: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True
