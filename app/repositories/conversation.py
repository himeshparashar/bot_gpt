from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.repositories.base import CRUDBase
from app.models.conversation import Conversation, Message, MessageRole


class IConversationRepository(ABC):
    
    @abstractmethod
    def get_by_user(self, db: Session, user_id: str, skip: int = 0, limit: int = 20) -> Tuple[List[Conversation], int]:
        """Get all conversations for a specific user with pagination"""
        pass
    
    @abstractmethod
    def get_messages(self, db: Session, conversation_id: str, skip: int = 0, limit: int = 100) -> List[Message]:
        """Get all messages for a conversation"""
        pass
    
    @abstractmethod
    def get_recent_messages(self, db: Session, conversation_id: str, limit: int = 10) -> List[Message]:
        """Get most recent messages for a conversation"""
        pass
    
    @abstractmethod
    def add_message(self, db: Session, conversation_id: str, role: MessageRole, content: str, token_count: int = 0) -> Message:
        """Add a message to a conversation"""
        pass
    
    @abstractmethod
    def get_next_sequence_number(self, db: Session, conversation_id: str) -> int:
        """Get the next sequence number for a conversation"""
        pass


class IMessageRepository(ABC):
    """Interface for message-specific operations"""
    
    @abstractmethod
    def get_messages_within_token_limit(self, db: Session, conversation_id: str, max_tokens: int) -> List[Message]:
        """Get messages within token limit (for sliding window)"""
        pass
    
    @abstractmethod
    def update_token_count(self, db: Session, message_id: str, token_count: int) -> Optional[Message]:
        """Update token count for a message"""
        pass


class ConversationRepository(CRUDBase[Conversation], IConversationRepository):

    
    def __init__(self):
        super().__init__(Conversation)
    
    def get_by_user(self, db: Session, user_id: str, skip: int = 0, limit: int = 20) -> Tuple[List[Conversation], int]:
        """Get all conversations for a specific user with pagination"""
        query = db.query(Conversation).filter(Conversation.user_id == user_id)
        total = query.count()
        conversations = query.order_by(desc(Conversation.updated_at)).offset(skip).limit(limit).all()
        return conversations, total
    
    def get_with_messages(self, db: Session, conversation_id: str) -> Optional[Conversation]:
        """Get conversation with all its messages"""
        return db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    def get_messages(self, db: Session, conversation_id: str, skip: int = 0, limit: int = 100) -> List[Message]:
        """Get all messages for a conversation ordered by sequence"""
        return db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.sequence_number).offset(skip).limit(limit).all()
    
    def get_recent_messages(self, db: Session, conversation_id: str, limit: int = 10) -> List[Message]:
        """Get most recent messages for a conversation"""
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(desc(Message.sequence_number)).limit(limit).all()
        return list(reversed(messages))
    
    def get_next_sequence_number(self, db: Session, conversation_id: str) -> int:
        """Get the next sequence number for a conversation"""
        result = db.query(func.max(Message.sequence_number)).filter(
            Message.conversation_id == conversation_id
        ).scalar()
        return (result or 0) + 1
    
    def add_message(
        self, 
        db: Session, 
        conversation_id: str, 
        role: MessageRole, 
        content: str, 
        token_count: int = 0
    ) -> Message:
        """Add a message to a conversation with proper sequencing"""
        sequence_number = self.get_next_sequence_number(db, conversation_id)
        
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            sequence_number=sequence_number,
            token_count=token_count
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    
    def update_total_tokens(self, db: Session, conversation_id: str, tokens_to_add: int) -> None:
        """Update total token count for a conversation"""
        conversation = self.get(db, conversation_id)
        if conversation:
            conversation.total_tokens += tokens_to_add
            db.commit()
    
    def get_message_count(self, db: Session, conversation_id: str) -> int:
        """Get total message count for a conversation"""
        return db.query(Message).filter(Message.conversation_id == conversation_id).count()
    
    def get_last_message(self, db: Session, conversation_id: str) -> Optional[Message]:
        """Get the last message in a conversation"""
        return db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(desc(Message.sequence_number)).first()


class MessageRepository(CRUDBase[Message], IMessageRepository):   
    def __init__(self):
        super().__init__(Message)
    
    def get_messages_within_token_limit(
        self, 
        db: Session, 
        conversation_id: str, 
        max_tokens: int
    ) -> List[Message]:
        """
        Get messages within token limit using sliding window approach.
        Returns most recent messages that fit within the token budget.
        """
        all_messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(desc(Message.sequence_number)).all()
        
        selected_messages = []
        current_tokens = 0
        
        for message in all_messages:
            if current_tokens + message.token_count <= max_tokens:
                selected_messages.append(message)
                current_tokens += message.token_count
            else:
                break
        
        return list(reversed(selected_messages))
    
    def update_token_count(self, db: Session, message_id: str, token_count: int) -> Optional[Message]:
        """Update token count for a message"""
        message = self.get(db, message_id)
        if message:
            message.token_count = token_count
            db.commit()
            db.refresh(message)
        return message


# singleton instance
conversation_repository = ConversationRepository()
message_repository = MessageRepository()
