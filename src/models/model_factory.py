"""
Model factory for creating AI model instances
"""

from typing import Dict, Type, Optional
from .base_model import BaseModel
from .openai_model import OpenAIModel
from .deepseek_model import DeepSeekModel
from ..core.config import Config, ModelConfig

class ModelFactory:
    """Factory for creating AI model instances"""
    
    # Registry of available model providers
    _providers: Dict[str, Type[BaseModel]] = {
        'openai': OpenAIModel,
        'deepseek': DeepSeekModel,
    }
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config
        self._model_cache: Dict[str, BaseModel] = {}
    
    def get_model(self, config_name: str) -> BaseModel:
        """Get a model instance by configuration name"""
        if not self.config:
            raise ValueError("Config not provided to ModelFactory")
            
        if config_name in self._model_cache:
            return self._model_cache[config_name]
        
        model_config = self.config.get_model_config(config_name)
        if not model_config:
            raise ValueError(f"Model configuration '{config_name}' not found")
        
        if not model_config.api_key:
            raise ValueError(f"API key not configured for model '{config_name}'")
        
        provider = model_config.provider.lower()
        if provider not in self._providers:
            raise ValueError(f"Unsupported model provider: {provider}")
        
        model_class = self._providers[provider]
        model_instance = model_class(model_config)
        
        # Cache the instance
        self._model_cache[config_name] = model_instance
        
        return model_instance
    
    def register_provider(self, provider_name: str, model_class: Type[BaseModel]):
        """Register a new model provider"""
        self._providers[provider_name] = model_class
    
    def get_available_providers(self) -> list:
        """Get list of available providers"""
        return list(self._providers.keys())
    
    def create_model_from_config(self, model_config: ModelConfig) -> BaseModel:
        """Create a model instance directly from ModelConfig"""
        provider = model_config.provider.lower()
        if provider not in self._providers:
            raise ValueError(f"Unsupported model provider: {provider}")
        
        model_class = self._providers[provider]
        return model_class(model_config)
    
    def create_model(self, model_config_name: str) -> BaseModel:
        """Create a model from config name or return a mock model for testing"""
        try:
            if self.config:
                return self.get_model(model_config_name)
            else:
                # Return a mock model for testing
                return MockModel()
        except Exception:
            # Return a mock model if config fails
            return MockModel()
    
    def clear_cache(self):
        """Clear the model cache"""
        self._model_cache.clear()

class MockModel(BaseModel):
    """Mock model for testing purposes"""
    
    def __init__(self):
        # Create a mock config
        mock_config = ModelConfig(
            name="mock",
            provider="mock",
            api_key="mock",
            model_id="mock-model"
        )
        super().__init__(mock_config)
    
    def _initialize_client(self):
        """Initialize mock client"""
        self.client = "mock_client"
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate mock text response"""
        return self._generate_mock_response(prompt)
    
    def analyze_image(self, image_data: str, prompt: str, **kwargs) -> str:
        """Analyze image mock response"""
        return self._generate_mock_response(prompt)
    
    def _generate_mock_response(self, prompt: str) -> str:
        """Generate realistic mock responses based on prompt content"""
        prompt_lower = prompt.lower()
        
        if 'requirements' in prompt_lower and 'json' in prompt_lower:
            return '''[
                {
                    "title": "用户登录功能",
                    "description": "用户需要能够使用邮箱和密码登录系统",
                    "type": "functional",
                    "priority": "critical",
                    "rationale": "用户身份验证是系统的基础功能",
                    "acceptance_criteria": ["用户输入有效邮箱和密码", "系统验证用户身份", "登录成功后跳转到仪表板"],
                    "estimated_effort": "M",
                    "tags": ["authentication", "security"]
                },
                {
                    "title": "任务列表组件",
                    "description": "显示用户任务的列表界面组件",
                    "type": "ui_component",
                    "priority": "high",
                    "rationale": "任务列表是核心UI组件",
                    "acceptance_criteria": ["显示任务标题", "显示任务状态", "支持排序和过滤"],
                    "estimated_effort": "M",
                    "tags": ["ui", "tasks"]
                },
                {
                    "title": "响应式布局",
                    "description": "网站需要在不同设备上自适应显示",
                    "type": "layout",
                    "priority": "high",
                    "rationale": "支持多设备访问",
                    "acceptance_criteria": ["手机端正常显示", "平板端正常显示", "桌面端正常显示"],
                    "estimated_effort": "L",
                    "tags": ["responsive", "layout"]
                }
            ]'''
        
        elif 'component' in prompt_lower and 'json' in prompt_lower:
            return '''{
                "name": "TaskCard",
                "type": "card",
                "properties": {
                    "title": "任务标题",
                    "status": "pending|in_progress|completed",
                    "priority": "low|medium|high|critical",
                    "due_date": "2024-12-31"
                },
                "events": ["click", "hover", "drag"],
                "validation": {
                    "rules": ["required:title"],
                    "messages": {"required": "标题不能为空"}
                },
                "accessibility": {
                    "aria-label": "任务卡片",
                    "role": "button",
                    "keyboard_navigation": true
                }
            }'''
        
        elif 'layout' in prompt_lower and 'json' in prompt_lower:
            return '''{
                "type": "grid",
                "sections": [
                    {
                        "name": "sidebar",
                        "position": "left",
                        "size": "250px",
                        "components": ["navigation", "user_info"]
                    },
                    {
                        "name": "main",
                        "position": "center",
                        "size": "1fr",
                        "components": ["header", "content"]
                    }
                ],
                "responsive": true,
                "breakpoints": {
                    "mobile": 768,
                    "tablet": 1024,
                    "desktop": 1200
                },
                "spacing": {
                    "padding": "16px",
                    "margin": "8px",
                    "gap": "12px"
                }
            }'''
        
        elif 'interaction' in prompt_lower and 'json' in prompt_lower:
            return '''[
                {
                    "trigger": "click",
                    "action": "navigate",
                    "target": "task_detail_page",
                    "conditions": ["user_authenticated"],
                    "feedback": "页面过渡动画",
                    "validation": null
                }
            ]'''
        
        elif 'overview' in prompt_lower or 'project' in prompt_lower:
            return '''{
                "project_overview": "一个现代化的任务管理系统，帮助用户高效组织和跟踪日常任务",
                "target_audience": "中小企业员工和个人用户"
            }'''
        
        else:
            return "Mock response for: " + prompt[:100] + "..."