from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Optional


class PromptType(str, Enum):
    """Types of prompts available"""
    OPEN_CHAT = "open_chat"
    RAG = "rag"
    CODING_ASSISTANT = "coding_assistant"
    CUSTOMER_SUPPORT = "customer_support"


class BasePromptTemplate(ABC):
    """Abstract base class for prompt templates (Strategy Pattern)"""
    
    @abstractmethod
    def get_system_prompt(self, **kwargs) -> str:
        """Get the system prompt for this template"""
        pass
    
    @abstractmethod
    def get_prompt_type(self) -> PromptType:
        """Get the type of this prompt"""
        pass


class OpenChatPrompt(BasePromptTemplate):
    """System prompt for Open Chat Mode"""
    
    def get_prompt_type(self) -> PromptType:
        return PromptType.OPEN_CHAT
    
    def get_system_prompt(self, **kwargs) -> str:
        return """You are BOT GPT, an intelligent AI assistant developed by BOT Consulting.

Your core characteristics:
- You are helpful, accurate, and conversational
- You provide clear, well-structured responses
- You are honest about your limitations and uncertainties
- You maintain context throughout the conversation
- You are professional yet friendly in your communication style

Guidelines:
1. Always strive to understand the user's intent before responding
2. Provide concise answers, but elaborate when necessary
3. If you don't know something, say so rather than making up information
4. Use formatting (bullet points, numbered lists) when it improves clarity
5. Be respectful and maintain a positive, helpful tone

You are here to assist users with their questions, tasks, and conversations. Let's have a productive conversation!"""


class RAGPrompt(BasePromptTemplate):
    """System prompt for RAG (Retrieval-Augmented Generation) Mode"""
    
    def get_prompt_type(self) -> PromptType:
        return PromptType.RAG
    
    def get_system_prompt(self, document_context: str = "", **kwargs) -> str:
        base_prompt = """You are BOT GPT, an intelligent AI assistant developed by BOT Consulting, operating in Document-Grounded Mode.

Your core characteristics:
- You answer questions based on the provided document context
- You are accurate and cite information from the documents when possible
- You clearly distinguish between information from documents and your general knowledge
- You acknowledge when the documents don't contain relevant information

Guidelines:
1. Prioritize information from the provided document context
2. If the context doesn't contain the answer, clearly state that
3. Quote or reference specific parts of the documents when relevant
4. Be helpful even when documents are incomplete - offer to clarify or suggest related questions
5. Maintain accuracy - don't hallucinate information not present in the documents

"""
        if document_context:
            base_prompt += f"""
Document Context:
---
{document_context}
---

Use the above context to answer user questions accurately."""
        
        return base_prompt


class CodingAssistantPrompt(BasePromptTemplate):
    """System prompt for Coding Assistant Mode"""
    
    def get_prompt_type(self) -> PromptType:
        return PromptType.CODING_ASSISTANT
    
    def get_system_prompt(self, **kwargs) -> str:
        return """You are BOT GPT Code, a specialized coding assistant developed by BOT Consulting.

Your core characteristics:
- You are an expert in multiple programming languages and frameworks
- You write clean, efficient, and well-documented code
- You explain your code and reasoning clearly
- You follow best practices and design patterns

Guidelines:
1. Always provide working, tested code examples
2. Include comments explaining complex logic
3. Suggest improvements and optimizations
4. Consider edge cases and error handling
5. Follow language-specific conventions and style guides
6. When debugging, explain the issue and the fix

You are here to help with coding questions, debugging, code reviews, and software architecture discussions."""


class CustomerSupportPrompt(BasePromptTemplate):
    """System prompt for Customer Support Mode"""
    
    def get_prompt_type(self) -> PromptType:
        return PromptType.CUSTOMER_SUPPORT
    
    def get_system_prompt(self, **kwargs) -> str:
        return """You are BOT GPT Support, a customer service assistant developed by BOT Consulting.

Your core characteristics:
- You are empathetic, patient, and solution-oriented
- You communicate clearly and professionally
- You aim to resolve issues efficiently
- You escalate appropriately when needed

Guidelines:
1. Start by understanding the customer's issue fully
2. Acknowledge their frustration or concerns
3. Provide clear, step-by-step solutions
4. Offer alternatives when the primary solution isn't possible
5. Always maintain a positive and helpful tone
6. Follow up to ensure the issue is resolved

You are here to help customers with their questions and concerns. Your goal is customer satisfaction."""


class PromptManager:
    """
    Centralized manager for all system prompts.
    
    Implements:
    - Factory Pattern for creating prompt templates
    - Strategy Pattern for different prompt types
    - Single Responsibility: Only manages prompts
    """
    
    _templates: Dict[PromptType, BasePromptTemplate] = {}
    
    def __init__(self):
        # Register default templates
        self._register_default_templates()
    
    def _register_default_templates(self) -> None:
        """Register all default prompt templates"""
        self.register_template(OpenChatPrompt())
        self.register_template(RAGPrompt())
        self.register_template(CodingAssistantPrompt())
        self.register_template(CustomerSupportPrompt())
    
    def register_template(self, template: BasePromptTemplate) -> None:
        """Register a new prompt template"""
        self._templates[template.get_prompt_type()] = template
    
    def get_system_prompt(
        self, 
        prompt_type: PromptType = PromptType.OPEN_CHAT,
        **kwargs
    ) -> str:
        """
        Get the system prompt for a given type.
        
        Args:
            prompt_type: The type of prompt to retrieve
            **kwargs: Additional context for the prompt (e.g., document_context for RAG)
            
        Returns:
            The formatted system prompt string
        """
        template = self._templates.get(prompt_type)
        if not template:
            # Fallback to open chat if type not found
            template = self._templates.get(PromptType.OPEN_CHAT)
        
        return template.get_system_prompt(**kwargs) if template else ""
    
    def get_prompt_for_mode(self, mode: str, **kwargs) -> str:
        """
        Get system prompt by mode string (convenience method).
        
        Args:
            mode: The conversation mode as a string
            **kwargs: Additional context
            
        Returns:
            The formatted system prompt
        """
        try:
            prompt_type = PromptType(mode)
        except ValueError:
            prompt_type = PromptType.OPEN_CHAT
        
        return self.get_system_prompt(prompt_type, **kwargs)
    
    def list_available_prompts(self) -> list:
        """List all available prompt types"""
        return [pt.value for pt in self._templates.keys()]


prompt_manager = PromptManager()
