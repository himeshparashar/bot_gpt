from typing import List, Optional, Dict
from sqlalchemy.orm import Session
import logging

from app.services.llm.base import BaseLLMProvider
from app.services.llm.gemini import GeminiProvider
from app.services.llm.groq import GroqProvider
from app.services.llm.openai import OpenAIProvider
from app.services.context_manager import ContextManager, ContextWindowStrategy, create_context_manager
from app.services.prompt_manager import PromptManager, PromptType, prompt_manager
from app.repositories.conversation import ConversationRepository, MessageRepository
from app.models.conversation import Conversation, Message, MessageRole, ConversationMode
from app.schemas.chat import (
    CreateConversationRequest,
    CreateConversationResponse,
    AddMessageRequest,
    AddMessageResponse,
    ConversationDetail,
    ConversationSummary,
    MessageResponse,
    PaginatedConversations
)
from app.core.exceptions import ChatException, LLMException
from app.core.config import settings


logger = logging.getLogger(__name__)


class LLMProviderFactory:
    
    _providers: Dict[str, type] = {
        "gemini": GeminiProvider,
        "groq": GroqProvider,
        "openai": OpenAIProvider,
    }
    
    @classmethod
    def create(cls, provider_name: str, **kwargs) -> BaseLLMProvider:
        """Create an LLM provider instance"""
        provider_class = cls._providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Unknown provider: {provider_name}")
        return provider_class(**kwargs)
    
    @classmethod
    def register(cls, name: str, provider_class: type) -> None:
        """Register a new provider type"""
        cls._providers[name.lower()] = provider_class
    
    @classmethod
    def get_default_provider(cls) -> BaseLLMProvider:
        """Get the default provider based on available API keys"""
        if settings.GOOGLE_API_KEY:
            return GeminiProvider()
        elif settings.GROQ_API_KEY:
            return GroqProvider()
        elif settings.OPENAI_API_KEY:
            return OpenAIProvider()
        else:
            raise LLMException("No LLM API key configured. Please set GOOGLE_API_KEY, GROQ_API_KEY, or OPENAI_API_KEY.")


class ChatService:
    """
    Service for handling chat operations.
    
    Orchestrates:
    - Conversation and message persistence
    - LLM provider calls
    - Context window management
    - System prompt management via PromptManager
    """
    
    def __init__(
        self,
        conversation_repo: Optional[ConversationRepository] = None,
        message_repo: Optional[MessageRepository] = None,
        llm_provider: Optional[BaseLLMProvider] = None,
        context_manager: Optional[ContextManager] = None,
        prompt_mgr: Optional[PromptManager] = None,
    ):
        self.conversation_repo = conversation_repo or ConversationRepository()
        self.message_repo = message_repo or MessageRepository()
        self._llm_provider = llm_provider
        self.context_manager = context_manager or create_context_manager()
        self.prompt_manager = prompt_mgr or prompt_manager
    
    @property
    def llm_provider(self) -> BaseLLMProvider:
        """Lazy initialization of LLM provider"""
        if self._llm_provider is None:
            self._llm_provider = LLMProviderFactory.get_default_provider()
        return self._llm_provider
    
    def set_provider(self, provider: BaseLLMProvider) -> None:
        """Set the LLM provider (Strategy Pattern)"""
        self._llm_provider = provider
    
    def _get_system_prompt_for_mode(self, mode: ConversationMode, **kwargs) -> str:
        """Get the appropriate system prompt based on conversation mode"""
        mode_value = mode.value if isinstance(mode, ConversationMode) else mode
        return self.prompt_manager.get_prompt_for_mode(mode_value, **kwargs)
    
    async def create_conversation(
        self, 
        db: Session, 
        request: CreateConversationRequest
    ) -> CreateConversationResponse:
        """
        Create a new conversation with the first message.
        """
        try:
            conv_mode = ConversationMode.OPEN_CHAT if request.mode.value == "open_chat" else ConversationMode.RAG
            
            conversation_data = {
                "user_id": request.user_id,
                "title": request.title or self._generate_title(request.message),
                "mode": conv_mode,
            }
            conversation = self.conversation_repo.create(db, conversation_data)
            
            user_token_count = self.context_manager.count_tokens(request.message)
            user_message = self.conversation_repo.add_message(
                db=db,
                conversation_id=conversation.id,
                role=MessageRole.USER,
                content=request.message,
                token_count=user_token_count
            )
            
            system_prompt = self._get_system_prompt_for_mode(conv_mode)
            
            messages_for_llm = self._build_llm_messages(
                messages=[user_message],
                system_prompt=system_prompt
            )
            
            assistant_content = await self._call_llm(messages_for_llm)
            
            assistant_token_count = self.context_manager.count_tokens(assistant_content)
            assistant_message = self.conversation_repo.add_message(
                db=db,
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT,
                content=assistant_content,
                token_count=assistant_token_count
            )
            
            total_tokens = user_token_count + assistant_token_count
            self.conversation_repo.update_total_tokens(db, conversation.id, total_tokens)
            
            return CreateConversationResponse(
                conversation_id=conversation.id,
                title=conversation.title,
                user_message=self._message_to_response(user_message),
                assistant_message=self._message_to_response(assistant_message)
            )
            
        except LLMException:
            raise
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            raise ChatException(f"Failed to create conversation: {str(e)}")
    
    async def add_message(
        self,
        db: Session,
        conversation_id: str,
        request: AddMessageRequest
    ) -> AddMessageResponse:
        """
        Add a message to an existing conversation.
        """
        conversation = self.conversation_repo.get(db, conversation_id)
        if not conversation:
            raise ChatException(f"Conversation not found: {conversation_id}")
        
        try:
            existing_messages = self.conversation_repo.get_messages(db, conversation_id)
            
            user_token_count = self.context_manager.count_tokens(request.message)
            user_message = self.conversation_repo.add_message(
                db=db,
                conversation_id=conversation_id,
                role=MessageRole.USER,
                content=request.message,
                token_count=user_token_count
            )
            
            system_prompt = self._get_system_prompt_for_mode(conversation.mode)
            
            all_messages = existing_messages + [user_message]
            messages_for_llm = self._build_llm_messages(
                messages=all_messages,
                system_prompt=system_prompt
            )
            
            assistant_content = await self._call_llm(messages_for_llm)
            
            assistant_token_count = self.context_manager.count_tokens(assistant_content)
            assistant_message = self.conversation_repo.add_message(
                db=db,
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content=assistant_content,
                token_count=assistant_token_count
            )
            
            total_tokens = user_token_count + assistant_token_count
            self.conversation_repo.update_total_tokens(db, conversation_id, total_tokens)
            
            return AddMessageResponse(
                conversation_id=conversation_id,
                user_message=self._message_to_response(user_message),
                assistant_message=self._message_to_response(assistant_message)
            )
            
        except LLMException:
            raise
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            raise ChatException(f"Failed to add message: {str(e)}")
    
    def get_conversation(self, db: Session, conversation_id: str) -> ConversationDetail:
        """Get detailed conversation with all messages"""
        conversation = self.conversation_repo.get_with_messages(db, conversation_id)
        if not conversation:
            raise ChatException(f"Conversation not found: {conversation_id}")
        
        return self._conversation_to_detail(conversation)
    
    def list_conversations(
        self,
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> PaginatedConversations:
        """List all conversations for a user with pagination"""
        conversations, total = self.conversation_repo.get_by_user(db, user_id, skip, limit)
        
        items = [self._conversation_to_summary(db, conv) for conv in conversations]
        
        return PaginatedConversations(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + len(items)) < total
        )
    
    def delete_conversation(self, db: Session, conversation_id: str) -> bool:
        """Delete a conversation and all its messages"""
        conversation = self.conversation_repo.get(db, conversation_id)
        if not conversation:
            raise ChatException(f"Conversation not found: {conversation_id}")
        
        return self.conversation_repo.delete(db, conversation_id)
    
    def get_conversation_history(
        self, 
        db: Session, 
        conversation_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[MessageResponse]:
        """Get message history for a conversation"""
        conversation = self.conversation_repo.get(db, conversation_id)
        if not conversation:
            raise ChatException(f"Conversation not found: {conversation_id}")
        
        messages = self.conversation_repo.get_messages(db, conversation_id, skip, limit)
        return [self._message_to_response(msg) for msg in messages]
    
    def _build_llm_messages(
        self, 
        messages: List[Message], 
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Build messages for LLM with sliding window context management.
        Converts Message models to LLM-compatible format.
        """
        message_dicts = [msg.to_llm_format() for msg in messages]
        
        context = self.context_manager.build_context(
            messages=message_dicts,
            system_prompt=system_prompt,
            strategy=ContextWindowStrategy.SLIDING_WINDOW
        )
        
        return context
    
    async def _call_llm(self, messages: List[Dict[str, str]]) -> str:
        """Call the LLM provider with error handling"""
        try:
            response = await self.llm_provider.generate(messages)
            return response
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise LLMException(f"LLM service error: {str(e)}")
    
    def _generate_title(self, first_message: str, max_length: int = 50) -> str:
        """Generate a title from the first message"""
        title = first_message[:max_length]
        if len(first_message) > max_length:
            title = title.rsplit(' ', 1)[0] + "..."
        return title
    
    def _message_to_response(self, message: Message) -> MessageResponse:
        """Convert Message model to MessageResponse schema"""
        return MessageResponse(
            id=message.id,
            role=message.role.value if isinstance(message.role, MessageRole) else message.role,
            content=message.content,
            sequence_number=message.sequence_number,
            token_count=message.token_count,
            is_summary=message.is_summary,
            created_at=message.created_at
        )
    
    def _conversation_to_detail(self, conversation: Conversation) -> ConversationDetail:
        """Convert Conversation model to ConversationDetail schema"""
        return ConversationDetail(
            id=conversation.id,
            user_id=conversation.user_id,
            title=conversation.title,
            mode=conversation.mode.value if isinstance(conversation.mode, ConversationMode) else conversation.mode,
            total_tokens=conversation.total_tokens,
            is_active=conversation.is_active,
            messages=[self._message_to_response(msg) for msg in conversation.messages],
            created_at=conversation.created_at,
            updated_at=conversation.updated_at
        )
    
    def _conversation_to_summary(self, db: Session, conversation: Conversation) -> ConversationSummary:
        """Convert Conversation model to ConversationSummary schema"""
        message_count = self.conversation_repo.get_message_count(db, conversation.id)
        last_message = self.conversation_repo.get_last_message(db, conversation.id)
        
        last_message_preview = None
        if last_message:
            last_message_preview = last_message.content[:100]
            if len(last_message.content) > 100:
                last_message_preview += "..."
        
        return ConversationSummary(
            id=conversation.id,
            user_id=conversation.user_id,
            title=conversation.title,
            mode=conversation.mode.value if isinstance(conversation.mode, ConversationMode) else conversation.mode,
            total_tokens=conversation.total_tokens,
            is_active=conversation.is_active,
            message_count=message_count,
            last_message_preview=last_message_preview,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at
        )

# singleton instance
chat_service = ChatService()
