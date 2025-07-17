"""
Configuration management for UI Easy
"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class ModelConfig:
    """Configuration for a specific model"""
    name: str
    provider: str  # openai, deepseek, anthropic, etc.
    api_key: str
    base_url: Optional[str] = None
    model_id: str = ""
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout: int = 30

@dataclass
class ModuleConfig:
    """Configuration for a module"""
    enabled: bool = True
    model_config: str = "default"  # Reference to model config
    custom_prompts: Dict[str, str] = None
    
    def __post_init__(self):
        if self.custom_prompts is None:
            self.custom_prompts = {}

class Config:
    """Main configuration manager"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.models: Dict[str, ModelConfig] = {}
        self.modules: Dict[str, ModuleConfig] = {}
        self.app_settings: Dict[str, Any] = {}
        
        # Set default configurations
        self._set_defaults()
        
        # Load from file - required for configuration
        if self.config_file.exists():
            self.load()
        else:
            raise FileNotFoundError(f"Configuration file {config_file} not found. Please create it with your API keys and settings.")
    
    def _set_defaults(self):
        """Set default configurations"""
        # Initialize empty configurations - will be loaded from config.json
        self.models = {}
        self.modules = {}
        self.app_settings = {}
    
    def get_model_config(self, name: str) -> Optional[ModelConfig]:
        """Get model configuration by name"""
        return self.models.get(name)
    
    def get_module_config(self, name: str) -> Optional[ModuleConfig]:
        """Get module configuration by name"""
        return self.modules.get(name)
    
    def get_app_setting(self, key: str, default: Any = None) -> Any:
        """Get application setting"""
        return self.app_settings.get(key, default)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value (generic method for compatibility)"""
        # Check if it's a model config request
        if key == 'model_config':
            # For model_config, return the config name (default parameter), not the config object
            # This is because create_model() expects a config name, not a config object
            return default if default is not None else 'default'
        # Otherwise treat as app setting
        else:
            return self.get_app_setting(key, default)
    
    def set_model_config(self, name: str, config: ModelConfig):
        """Set model configuration"""
        self.models[name] = config
    
    def set_module_config(self, name: str, config: ModuleConfig):
        """Set module configuration"""
        self.modules[name] = config
    
    def set_app_setting(self, key: str, value: Any):
        """Set application setting"""
        self.app_settings[key] = value
    
    def save(self):
        """Save configuration to file"""
        config_data = {
            "models": {name: asdict(config) for name, config in self.models.items()},
            "modules": {name: asdict(config) for name, config in self.modules.items()},
            "app_settings": self.app_settings
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    def load(self):
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Load models
            if "models" in config_data:
                for name, model_data in config_data["models"].items():
                    self.models[name] = ModelConfig(**model_data)
            
            # Load modules
            if "modules" in config_data:
                for name, module_data in config_data["modules"].items():
                    self.modules[name] = ModuleConfig(**module_data)
            
            # Load app settings
            if "app_settings" in config_data:
                self.app_settings.update(config_data["app_settings"])
                
        except Exception as e:
            print(f"Error loading config: {e}")
            # Keep defaults if loading fails