"""
Unit Tests for Conversation Repository
"""
import pytest
from sqlalchemy.orm import Session

from app.models.conversation import Conversation, Message, MessageRole
from app.repositories.conversation import ConversationRepository, conversation_repository


class TestConversationRepository:
    """Test cases for the ConversationRepository class"""
    
    @pytest.fixture
    def repo(self) -> ConversationRepository:
        """Create a fresh repository instance"""
        return ConversationRepository()
    
    def test_create_conversation(self, db_session: Session, repo: ConversationRepository):
        """Test creating a conversation through repository"""
        conversation = repo.create(db_session, {"title": "New Conversation"})
        
        assert conversation is not None
        assert conversation.id is not None
        assert conversation.title == "New Conversation"
    
    def test_get_conversation_by_id(self, db_session: Session, repo: ConversationRepository, sample_conversation: Conversation):
        """Test retrieving a conversation by ID"""
        found = repo.get(db_session, sample_conversation.id)
        
        assert found is not None
        assert found.id == sample_conversation.id
        assert found.title == sample_conversation.title
    
    def test_get_nonexistent_conversation(self, db_session: Session, repo: ConversationRepository):
        """Test retrieving a non-existent conversation returns None"""
        found = repo.get(db_session, "nonexistent-id")
        
        assert found is None
    
    def test_get_all_conversations(self, db_session: Session, repo: ConversationRepository):
        """Test retrieving all conversations"""
        # Create multiple conversations
        repo.create(db_session, {"title": "Conversation 1"})
        repo.create(db_session, {"title": "Conversation 2"})
        repo.create(db_session, {"title": "Conversation 3"})
        
        conversations = repo.get_all(db_session)
        
        assert len(conversations) == 3
    
    def test_get_all_with_pagination(self, db_session: Session, repo: ConversationRepository):
        """Test pagination when retrieving conversations"""
        # Create 5 conversations
        for i in range(5):
            repo.create(db_session, {"title": f"Conversation {i+1}"})
        
        # Get first 2
        first_page = repo.get_all(db_session, skip=0, limit=2)
        assert len(first_page) == 2
        
        # Get next 2
        second_page = repo.get_all(db_session, skip=2, limit=2)
        assert len(second_page) == 2
        
        # Get remaining
        third_page = repo.get_all(db_session, skip=4, limit=2)
        assert len(third_page) == 1
    
    def test_delete_conversation(self, db_session: Session, repo: ConversationRepository, sample_conversation: Conversation):
        """Test deleting a conversation"""
        conversation_id = sample_conversation.id
        
        result = repo.delete(db_session, conversation_id)
        
        assert result is True
        assert repo.get(db_session, conversation_id) is None
    
    def test_delete_nonexistent_conversation(self, db_session: Session, repo: ConversationRepository):
        """Test deleting a non-existent conversation returns False"""
        result = repo.delete(db_session, "nonexistent-id")
        
        assert result is False
    
    def test_add_message(self, db_session: Session, repo: ConversationRepository, sample_conversation: Conversation):
        """Test adding a message to a conversation"""
        message = repo.add_message(
            db_session,
            sample_conversation.id,
            role="user",
            content="Hello, world!"
        )
        
        assert message is not None
        assert message.id is not None
        assert message.conversation_id == sample_conversation.id
        assert message.role == "user"
        assert message.content == "Hello, world!"
    
    def test_get_messages(self, db_session: Session, repo: ConversationRepository, sample_conversation: Conversation):
        """Test retrieving messages for a conversation"""
        # Add multiple messages
        repo.add_message(db_session, sample_conversation.id, "user", "Message 1")
        repo.add_message(db_session, sample_conversation.id, "assistant", "Message 2")
        repo.add_message(db_session, sample_conversation.id, "user", "Message 3")
        
        messages = repo.get_messages(db_session, sample_conversation.id)
        
        assert len(messages) == 3
        assert messages[0].content == "Message 1"
        assert messages[1].content == "Message 2"
        assert messages[2].content == "Message 3"
    
    def test_get_messages_empty_conversation(self, db_session: Session, repo: ConversationRepository, sample_conversation: Conversation):
        """Test retrieving messages from a conversation with no messages"""
        messages = repo.get_messages(db_session, sample_conversation.id)
        
        assert messages == []
    
    def test_get_messages_ordered_by_created_at(self, db_session: Session, repo: ConversationRepository, sample_conversation: Conversation):
        """Test that messages are returned in chronological order"""
        import time
        
        # Add messages with slight delays to ensure different timestamps
        repo.add_message(db_session, sample_conversation.id, "user", "First")
        repo.add_message(db_session, sample_conversation.id, "assistant", "Second")
        repo.add_message(db_session, sample_conversation.id, "user", "Third")
        
        messages = repo.get_messages(db_session, sample_conversation.id)
        
        # Verify order
        assert messages[0].content == "First"
        assert messages[1].content == "Second"
        assert messages[2].content == "Third"
        
        # Verify timestamps are in order
        for i in range(len(messages) - 1):
            assert messages[i].created_at <= messages[i + 1].created_at


class TestConversationRepositorySingleton:
    """Test the singleton instance of ConversationRepository"""
    
    def test_singleton_exists(self):
        """Test that the singleton instance is available"""
        assert conversation_repository is not None
        assert isinstance(conversation_repository, ConversationRepository)
    
    def test_singleton_uses_conversation_model(self):
        """Test that the singleton uses the correct model"""
        assert conversation_repository.model == Conversation
