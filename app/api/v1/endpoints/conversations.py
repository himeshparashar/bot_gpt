"""
Conversation Endpoints
Operations:
- POST /conversations - Create new conversation with first message
- GET /conversations - List all conversations for a user
- GET /conversations/{id} - Get conversation detail with messages
- POST /conversations/{id}/messages - Add message to conversation (Update)
- DELETE /conversations/{id} - Delete conversation and messages
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.services.chat_service import ChatService, chat_service
from app.schemas.chat import (
    CreateConversationRequest,
    CreateConversationResponse,
    AddMessageRequest,
    AddMessageResponse,
    ConversationDetail,
    PaginatedConversations,
    MessageResponse
)
from app.core.exceptions import ChatException, LLMException

router = APIRouter()


def get_chat_service() -> ChatService:
    return chat_service


@router.post(
    "/",
    response_model=CreateConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new conversation",
    description="Start a new conversation with the first message. Returns the conversation ID and both user and assistant messages."
)
async def create_conversation(
    request: CreateConversationRequest,
    db: Session = Depends(get_db),
    service: ChatService = Depends(get_chat_service)
):
    """
    Create a new conversation with the first message.
    
    - user_id: Identifier for the user
    - message: The first message content
    - title: Optional title for the conversation
    - system_prompt: Optional system prompt to guide the AI
    - mode: Conversation mode (open_chat or rag)
    """
    try:
        response = await service.create_conversation(db, request)
        return response
    except ChatException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.detail))
    except LLMException as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e.detail))


@router.get(
    "/",
    response_model=PaginatedConversations,
    summary="List conversations",
    description="Get all conversations for a user with pagination support."
)
async def list_conversations(
    user_id: str = Query(..., description="User identifier"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    service: ChatService = Depends(get_chat_service)
):
    """
    List all conversations for a user.
    
    Returns paginated results with conversation summaries including:
    - Conversation ID and title
    - Message count
    - Last message preview
    - Token usage
    """
    return service.list_conversations(db, user_id, skip, limit)


@router.get(
    "/{conversation_id}",
    response_model=ConversationDetail,
    summary="Get conversation details",
    description="Get full conversation details including all messages."
)
async def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    service: ChatService = Depends(get_chat_service)
):
    """
    Get detailed information about a specific conversation.
    
    Returns:
    - Conversation metadata
    - Full message history in order
    - Token usage statistics
    """
    try:
        return service.get_conversation(db, conversation_id)
    except ChatException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e.detail))


@router.get(
    "/{conversation_id}/messages",
    response_model=List[MessageResponse],
    summary="Get conversation messages",
    description="Get messages for a conversation with pagination."
)
async def get_conversation_messages(
    conversation_id: str,
    skip: int = Query(0, ge=0, description="Number of messages to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum messages to return"),
    db: Session = Depends(get_db),
    service: ChatService = Depends(get_chat_service)
):
    """
    Get message history for a specific conversation.
    
    Messages are returned in chronological order (oldest first).
    """
    try:
        return service.get_conversation_history(db, conversation_id, skip, limit)
    except ChatException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e.detail))


@router.post(
    "/{conversation_id}/messages",
    response_model=AddMessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add message to conversation",
    description="Add a new message to an existing conversation and get AI response."
)
async def add_message(
    conversation_id: str,
    request: AddMessageRequest,
    db: Session = Depends(get_db),
    service: ChatService = Depends(get_chat_service)
):
    """
    Add a message to an existing conversation.
    
    This endpoint:
    1. Adds the user's message to the conversation
    2. Builds context using sliding window approach
    3. Calls the LLM to generate a response
    4. Stores and returns both messages
    
    - message: The message content to send
    """
    try:
        response = await service.add_message(db, conversation_id, request)
        return response
    except ChatException as e:
        if "not found" in str(e.detail).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e.detail))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.detail))
    except LLMException as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e.detail))


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete conversation",
    description="Delete a conversation and all its messages."
)
async def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    service: ChatService = Depends(get_chat_service)
):
    """
    Delete a conversation and all associated messages.
    
    """
    try:
        service.delete_conversation(db, conversation_id)
        return None
    except ChatException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e.detail))