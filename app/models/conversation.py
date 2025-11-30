from sqlalchemy import Column, String, Text, ForeignKey, Enum, Integer, Boolean
from sqlalchemy.orm import relationship
import enum
import uuid

from app.models.base import Base, TimestampMixin


class MessageRole(str, enum.Enum):
    """Enum for message roles in a conversation"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationMode(str, enum.Enum):
    """Enum for conversation modes"""
    OPEN_CHAT = "open_chat"
    RAG = "rag"


class Conversation(Base, TimestampMixin):
    """
    Conversation table - represents a chat session.
    
    Follows Single Responsibility Principle: Only handles conversation metadata.
    Messages are handled through relationship.
    System prompts are managed by PromptManager based on mode.
    """
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True) 
    title = Column(String(255), nullable=True)
    mode = Column(Enum(ConversationMode), default=ConversationMode.OPEN_CHAT, nullable=False)
    
    # Context management metadata
    total_tokens = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    messages = relationship(
        "Message", 
        back_populates="conversation", 
        cascade="all, delete-orphan",
        order_by="Message.sequence_number"  # Ensure proper ordering
    )
    
    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, user_id={self.user_id}, title={self.title})>"


class Message(Base, TimestampMixin):
    """
    Message table - represents a single message in a conversation.
    """
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    
    sequence_number = Column(Integer, nullable=False, index=True)
    
    token_count = Column(Integer, default=0)
    
    is_summary = Column(Boolean, default=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role}, sequence={self.sequence_number})>"
    
    def to_llm_format(self) -> dict:
        """Convert message to LLM-compatible format"""
        return {
            "role": self.role.value if isinstance(self.role, MessageRole) else self.role,
            "content": self.content
        }
