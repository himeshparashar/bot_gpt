"""
Unit Tests for Conversation and Message Models
"""
import pytest
from sqlalchemy.orm import Session

from app.models.conversation import Conversation, Message, MessageRole


class TestConversationModel:
    """Test cases for the Conversation model"""
    
    def test_create_conversation(self, db_session: Session):
        """Test creating a new conversation"""
        conversation = Conversation(user_id="test-user-123", title="Test Conversation")
        db_session.add(conversation)
        db_session.commit()
        db_session.refresh(conversation)
        
        assert conversation.id is not None
        assert conversation.title == "Test Conversation"
        assert conversation.user_id == "test-user-123"
        assert conversation.created_at is not None
        assert conversation.updated_at is not None
    
    def test_create_conversation_without_title(self, db_session: Session):
        """Test creating a conversation without a title (nullable)"""
        conversation = Conversation(user_id="test-user-123")
        db_session.add(conversation)
        db_session.commit()
        db_session.refresh(conversation)
        
        assert conversation.id is not None
        assert conversation.title is None
        assert conversation.user_id == "test-user-123"
    
    def test_conversation_generates_uuid(self, db_session: Session):
        """Test that conversation ID is auto-generated as UUID"""
        conversation = Conversation(user_id="test-user-123", title="UUID Test")
        db_session.add(conversation)
        db_session.commit()
        
        # UUID v4 format: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
        assert len(conversation.id) == 36
        assert conversation.id.count("-") == 4
    
    def test_conversation_messages_relationship(self, db_session: Session):
        """Test the relationship between conversation and messages"""
        conversation = Conversation(user_id="test-user-123", title="Relationship Test")
        db_session.add(conversation)
        db_session.commit()
        
        # Add messages
        message1 = Message(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content="Hello",
            sequence_number=1
        )
        message2 = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content="Hi there!",
            sequence_number=2
        )
        db_session.add_all([message1, message2])
        db_session.commit()
        
        # Refresh and check relationship
        db_session.refresh(conversation)
        assert len(conversation.messages) == 2
    
    def test_cascade_delete_messages(self, db_session: Session):
        """Test that deleting a conversation also deletes its messages"""
        conversation = Conversation(user_id="test-user-123", title="Cascade Delete Test")
        db_session.add(conversation)
        db_session.commit()
        
        # Add a message
        message = Message(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content="Test message",
            sequence_number=1
        )
        db_session.add(message)
        db_session.commit()
        
        message_id = message.id
        
        # Delete conversation
        db_session.delete(conversation)
        db_session.commit()
        
        # Verify message is also deleted
        deleted_message = db_session.query(Message).filter(Message.id == message_id).first()
        assert deleted_message is None


class TestMessageModel:
    """Test cases for the Message model"""
    
    def test_create_message(self, db_session: Session, sample_conversation: Conversation):
        """Test creating a new message"""
        message = Message(
            conversation_id=sample_conversation.id,
            role=MessageRole.USER,
            content="Test message content",
            sequence_number=1
        )
        db_session.add(message)
        db_session.commit()
        db_session.refresh(message)
        
        assert message.id is not None
        assert message.conversation_id == sample_conversation.id
        assert message.role == MessageRole.USER
        assert message.content == "Test message content"
        assert message.sequence_number == 1
        assert message.created_at is not None
    
    def test_message_roles(self, db_session: Session, sample_conversation: Conversation):
        """Test different message roles"""
        roles = [MessageRole.USER, MessageRole.ASSISTANT, MessageRole.SYSTEM]
        
        for i, role in enumerate(roles):
            message = Message(
                conversation_id=sample_conversation.id,
                role=role,
                content=f"Message with role {role.value}",
                sequence_number=i + 1
            )
            db_session.add(message)
            db_session.commit()
            db_session.refresh(message)
            
            assert message.role == role
    
    def test_message_conversation_relationship(self, db_session: Session, sample_conversation: Conversation):
        """Test the relationship from message to conversation"""
        message = Message(
            conversation_id=sample_conversation.id,
            role=MessageRole.USER,
            content="Relationship test",
            sequence_number=1
        )
        db_session.add(message)
        db_session.commit()
        db_session.refresh(message)
        
        assert message.conversation is not None
        assert message.conversation.id == sample_conversation.id
        assert message.conversation.title == sample_conversation.title
    
    def test_message_generates_uuid(self, db_session: Session, sample_conversation: Conversation):
        """Test that message ID is auto-generated as UUID"""
        message = Message(
            conversation_id=sample_conversation.id,
            role=MessageRole.USER,
            content="UUID test",
            sequence_number=1
        )
        db_session.add(message)
        db_session.commit()
        
        assert len(message.id) == 36
        assert message.id.count("-") == 4


class TestMessageRoleEnum:
    """Test cases for MessageRole enum"""
    
    def test_role_values(self):
        """Test that role enum has correct values"""
        assert MessageRole.USER.value == "user"
        assert MessageRole.ASSISTANT.value == "assistant"
        assert MessageRole.SYSTEM.value == "system"
    
    def test_role_is_string_enum(self):
        """Test that MessageRole is a string enum"""
        assert isinstance(MessageRole.USER, str)
        assert MessageRole.USER == "user"
