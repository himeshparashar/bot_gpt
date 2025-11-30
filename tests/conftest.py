"""
Pytest Configuration and Fixtures
"""
from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.models.conversation import Conversation, Message, MessageRole


# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Create a fresh database session for each test.
    Tables are created before each test and dropped after.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_conversation(db_session: Session) -> Conversation:
    """Create a sample conversation for testing"""
    conversation = Conversation(title="Test Conversation")
    db_session.add(conversation)
    db_session.commit()
    db_session.refresh(conversation)
    return conversation


@pytest.fixture
def sample_message(db_session: Session, sample_conversation: Conversation) -> Message:
    """Create a sample message for testing"""
    message = Message(
        conversation_id=sample_conversation.id,
        role=MessageRole.USER,
        content="Hello, this is a test message"
    )
    db_session.add(message)
    db_session.commit()
    db_session.refresh(message)
    return message
