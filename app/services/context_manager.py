from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import tiktoken


class TokenCounterStrategy(ABC):
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string"""
        pass
    
    @abstractmethod
    def count_messages_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Count total tokens in a list of messages"""
        pass


class TiktokenCounter(TokenCounterStrategy):
    """
    Token counter using tiktoken library (for OpenAI-compatible models).
    """
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")
        
        # Token overhead per message (role, content separators, etc.)
        self.tokens_per_message = 4  # Approximate overhead per message
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string"""
        return len(self.encoding.encode(text))
    
    def count_messages_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Count total tokens in a list of messages"""
        total = 0
        for message in messages:
            total += self.tokens_per_message
            total += self.count_tokens(message.get("role", ""))
            total += self.count_tokens(message.get("content", ""))
        total += 3  
        return total


class SimpleTokenCounter(TokenCounterStrategy):
    
    def count_tokens(self, text: str) -> int:
        """Approximate tokens using character count / 4"""
        return len(text) // 4 + 1
    
    def count_messages_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Count total tokens in a list of messages"""
        total = 0
        for message in messages:
            total += 4  # Overhead per message
            total += self.count_tokens(message.get("role", ""))
            total += self.count_tokens(message.get("content", ""))
        return total + 3


@dataclass
class ContextConfig:
    """Configuration for context management"""
    max_context_tokens: int = 4096  
    max_response_tokens: int = 1024  
    sliding_window_messages: int = 20  
    system_prompt_token_budget: int = 500  

class ContextWindowStrategy(Enum):
    """Strategies for handling context window limits"""
    SLIDING_WINDOW = "sliding_window"
    TRUNCATE_OLDEST = "truncate_oldest"
    SUMMARIZE = "summarize"


class ContextManager:
    """
    Manages LLM context with sliding window approach.
    """
    
    def __init__(
        self, 
        config: Optional[ContextConfig] = None,
        token_counter: Optional[TokenCounterStrategy] = None
    ):
        self.config = config or ContextConfig()
        self.token_counter = token_counter or self._create_default_counter()
    
    def _create_default_counter(self) -> TokenCounterStrategy:
        """Create default token counter, fallback to simple if tiktoken unavailable"""
        try:
            return TiktokenCounter()
        except Exception:
            return SimpleTokenCounter()
    
    @property
    def available_context_tokens(self) -> int:
        """Calculate available tokens for conversation context"""
        return self.config.max_context_tokens - self.config.max_response_tokens
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string"""
        return self.token_counter.count_tokens(text)
    
    def count_messages_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Count total tokens in messages"""
        return self.token_counter.count_messages_tokens(messages)
    
    def build_context(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        strategy: ContextWindowStrategy = ContextWindowStrategy.SLIDING_WINDOW
    ) -> List[Dict[str, str]]:
        """
        Build context for LLM call with sliding window approach.
        
        Args:
            messages: List of messages in conversation
            system_prompt: Optional system prompt to include
            strategy: Strategy for handling context limits
            
        Returns:
            List of messages that fit within token limits
        """
        context = []
        available_tokens = self.available_context_tokens
        
        # Add system prompt first if provided
        if system_prompt:
            system_message = {"role": "system", "content": system_prompt}
            system_tokens = self.token_counter.count_messages_tokens([system_message])
            
            if system_tokens <= self.config.system_prompt_token_budget:
                context.append(system_message)
                available_tokens -= system_tokens
        
        if strategy == ContextWindowStrategy.SLIDING_WINDOW:
            context.extend(self._apply_sliding_window(messages, available_tokens))
        elif strategy == ContextWindowStrategy.TRUNCATE_OLDEST:
            context.extend(self._truncate_oldest(messages, available_tokens))
        else:
            # Default to sliding window
            context.extend(self._apply_sliding_window(messages, available_tokens))
        
        return context
    
    def _apply_sliding_window(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: int
    ) -> List[Dict[str, str]]:
        """
        Apply sliding window to keep most recent messages within token limit.
        """
        if not messages:
            return []
        
        # Limit to max sliding window size first
        recent_messages = messages[-self.config.sliding_window_messages:]
        
        selected = []
        current_tokens = 0
        
        for message in reversed(recent_messages):
            message_tokens = self.token_counter.count_messages_tokens([message])
            
            if current_tokens + message_tokens <= max_tokens:
                selected.insert(0, message) 
                current_tokens += message_tokens
            else:
                if not selected and messages:
                    selected = [messages[-1]]
                break
        
        return selected
    
    def _truncate_oldest(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: int
    ) -> List[Dict[str, str]]:
        """
        Truncate oldest messages to fit within token limit.
        """
        if not messages:
            return []
        
        result = list(messages)
        
        while result and self.token_counter.count_messages_tokens(result) > max_tokens:
            result.pop(0)
        
        return result
    
    def add_message_to_context(
        self,
        context: List[Dict[str, str]],
        role: str,
        content: str
    ) -> List[Dict[str, str]]:
        """
        Add a new message to existing context, maintaining token limits.
        """
        new_message = {"role": role, "content": content}
        updated_context = context + [new_message]
        
        total_tokens = self.token_counter.count_messages_tokens(updated_context)
        
        if total_tokens > self.available_context_tokens:
            system_message = None
            if updated_context and updated_context[0].get("role") == "system":
                system_message = updated_context[0]
                updated_context = updated_context[1:]
            
            # Apply sliding window
            updated_context = self._apply_sliding_window(
                updated_context, 
                self.available_context_tokens - (
                    self.token_counter.count_messages_tokens([system_message]) 
                    if system_message else 0
                )
            )
            
            # Prepend system message if it existed
            if system_message:
                updated_context.insert(0, system_message)
        
        return updated_context
    
    def get_context_stats(self, messages: List[Dict[str, str]]) -> Dict:
        """
        Get statistics about the current context.
        
        Returns:
            Dict with token counts and utilization info
        """
        total_tokens = self.token_counter.count_messages_tokens(messages)
        available = self.available_context_tokens
        
        return {
            "total_tokens": total_tokens,
            "max_tokens": self.config.max_context_tokens,
            "available_tokens": available,
            "used_percentage": (total_tokens / available * 100) if available > 0 else 0,
            "message_count": len(messages),
            "can_add_more": total_tokens < available
        }


def create_context_manager(
    model: str = "gpt-3.5-turbo",
    max_context_tokens: int = 4096,
    max_response_tokens: int = 1024
) -> ContextManager:
    """
    Factory function to create ContextManager with model-specific settings.
    
    Args:
        model: LLM model name (affects token counting)
        max_context_tokens: Maximum context window size
        max_response_tokens: Tokens reserved for response
        
    Returns:
        Configured ContextManager instance
    """
    config = ContextConfig(
        max_context_tokens=max_context_tokens,
        max_response_tokens=max_response_tokens
    )
    
    try:
        token_counter = TiktokenCounter(model)
    except Exception:
        token_counter = SimpleTokenCounter()
    
    return ContextManager(config=config, token_counter=token_counter)


default_context_manager = ContextManager()
