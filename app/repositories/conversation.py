"""
Conversation Repository - Chat History Queries
"""
from typing import List
from sqlalchemy.orm import Session

from app.repositories.base import CRUDBase
from app.models.conversation import Conversation, Message


class ConversationRepository(CRUDBase[Conversation]):
    """Repository for conversation operations"""
    
    def __init__(self):
        super().__init__(Conversation)
    
    def get_messages(self, db: Session, conversation_id: str) -> List[Message]:
        """Get all messages for a conversation"""
        return db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).all()
    
    def add_message(self, db: Session, conversation_id: str, role: str, content: str) -> Message:
        """Add a message to a conversation"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message


conversation_repository = ConversationRepository()
