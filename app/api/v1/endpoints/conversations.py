"""
Conversation Endpoints - Handle chat interactions
"""
from fastapi import APIRouter
from typing import List

from app.schemas.chat import ChatRequest, ChatResponse, MessageHistory

router = APIRouter()