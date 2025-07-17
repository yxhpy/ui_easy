"""
OpenAI model implementation
"""

import json
from typing import Dict, Any, List
from .base_model import BaseModel

class OpenAIModel(BaseModel):
    """OpenAI model implementation"""
    
    def _initialize_client(self):
        """Initialize OpenAI client"""
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                timeout=self.config.timeout
            )
        except ImportError:
            raise ImportError("OpenAI library not installed. Run: pip install openai")
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt"""
        try:
            response = self.client.chat.completions.create(
                model=self.config.model_id,
                messages=[{"role": "user", "content": prompt}],
                # max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                temperature=kwargs.get('temperature', self.config.temperature),
                timeout=kwargs.get('timeout', self.config.timeout)
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def generate_text_stream(self, prompt: str, **kwargs):
        """Generate text from prompt with streaming"""
        try:
            stream = self.client.chat.completions.create(
                model=self.config.model_id,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get('temperature', self.config.temperature),
                timeout=kwargs.get('timeout', self.config.timeout),
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content is not None:
                        yield delta.content
                        
        except Exception as e:
            raise Exception(f"OpenAI stream API error: {str(e)}")
    
    def generate_stream(self, prompt: str, **kwargs):
        """Generate text with streaming (implementation for base class)"""
        return self.generate_text_stream(prompt, **kwargs)
    
    def analyze_image(self, image_data: str, prompt: str, **kwargs) -> str:
        """Analyze image with prompt"""
        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ]
            
            response = self.client.chat.completions.create(
                model=self.config.model_id,
                messages=messages,
                # max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                temperature=kwargs.get('temperature', self.config.temperature),
                timeout=kwargs.get('timeout', self.config.timeout)
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI vision API error: {str(e)}")
    
    def analyze_image_stream(self, image_data: str, prompt: str, **kwargs):
        """Analyze image with prompt and stream response"""
        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ]
            
            stream = self.client.chat.completions.create(
                model=self.config.model_id,
                messages=messages,
                # max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                temperature=kwargs.get('temperature', self.config.temperature),
                timeout=kwargs.get('timeout', self.config.timeout),
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content is not None:
                        yield delta.content
                    
        except Exception as e:
            raise Exception(f"OpenAI vision stream API error: {str(e)}")
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat with the model using message history"""
        try:
            response = self.client.chat.completions.create(
                model=self.config.model_id,
                messages=messages,
                # max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                temperature=kwargs.get('temperature', self.config.temperature),
                timeout=kwargs.get('timeout', self.config.timeout)
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI chat API error: {str(e)}")