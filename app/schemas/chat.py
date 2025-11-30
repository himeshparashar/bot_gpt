from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ConversationMode(str, Enum):
    OPEN_CHAT = "open_chat"
    RAG = "rag"



class CreateConversationRequest(BaseModel):
    """Request schema for creating a new conversation with first message"""
    user_id: str = Field(..., description="User identifier")
    message: str = Field(..., min_length=1, description="First message content")
    title: Optional[str] = Field(None, max_length=255, description="Optional conversation title")
    mode: ConversationMode = Field(default=ConversationMode.OPEN_CHAT, description="Conversation mode (open_chat or rag)")


class AddMessageRequest(BaseModel):
    """Request schema for adding a message to existing conversation"""
    message: str = Field(..., min_length=1, description="Message content")



class MessageResponse(BaseModel):
    """Response schema for a single message"""
    id: str
    role: str
    content: str
    sequence_number: int
    token_count: int
    is_summary: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationSummary(BaseModel):
    """Summary schema for listing conversations"""
    id: str
    user_id: str
    title: Optional[str]
    mode: str
    total_tokens: int
    is_active: bool
    message_count: int
    last_message_preview: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ConversationDetail(BaseModel):
    """Detailed schema for a single conversation with all messages"""
    id: str
    user_id: str
    title: Optional[str]
    mode: str
    total_tokens: int
    is_active: bool
    messages: List[MessageResponse]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CreateConversationResponse(BaseModel):
    """Response schema for conversation creation"""
    conversation_id: str
    title: Optional[str]
    user_message: MessageResponse
    assistant_message: MessageResponse
    

class AddMessageResponse(BaseModel):
    """Response schema for adding a message"""
    conversation_id: str
    user_message: MessageResponse
    assistant_message: MessageResponse



class MessageHistory(BaseModel):
    """Message history schema for backward compatibility"""
    id: str
    role: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True



class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class PaginatedConversations(BaseModel):
    """Paginated list of conversations"""
    items: List[ConversationSummary]
    total: int
    skip: int
    limit: int
    has_more: bool
