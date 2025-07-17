"""
Base model class for all AI model providers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from ..core.config import ModelConfig

class BaseModel(ABC):
    """Base class for all AI model implementations"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.client = None
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """Initialize the model client"""
        pass
    
    @abstractmethod
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt"""
        pass
    
    @abstractmethod
    def analyze_image(self, image_data: str, prompt: str, **kwargs) -> str:
        """Analyze image with prompt"""
        pass
    
    def analyze_image_stream(self, image_data: str, prompt: str, **kwargs):
        """Analyze image with prompt and stream response"""
        # Default implementation falls back to non-streaming
        result = self.analyze_image(image_data, prompt, **kwargs)
        yield result
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt (alias for generate_text)"""
        return self.generate_text(prompt, **kwargs)
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat with the model using message history"""
        # Default implementation converts to simple prompt
        prompt = self._messages_to_prompt(messages)
        return self.generate_text(prompt, **kwargs)
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert message history to single prompt"""
        prompt_parts = []
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            if role == 'system':
                prompt_parts.append(f"System: {content}")
            elif role == 'user':
                prompt_parts.append(f"User: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")
        
        return '\n'.join(prompt_parts)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            'name': self.config.name,
            'provider': self.config.provider,
            'model_id': self.config.model_id,
            'max_tokens': self.config.max_tokens,
            'temperature': self.config.temperature
        }