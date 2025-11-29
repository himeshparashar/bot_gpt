"""
Document Model - For RAG Knowledge Base
"""
from sqlalchemy import Column, String, Text, Integer
import uuid

from app.models.base import Base, TimestampMixin


class Document(Base, TimestampMixin):
    """Document table for RAG"""
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    chunk_count = Column(Integer, default=0)
    status = Column(String(50), default="pending")
