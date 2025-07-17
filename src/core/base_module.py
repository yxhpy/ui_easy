"""
Base module class for all core functionality modules
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
from PyQt5.QtCore import QObject, pyqtSignal

class QObjectMeta(type(QObject), type(ABC)):
    """Metaclass that combines QObject and ABC"""
    pass

class BaseModule(QObject, ABC, metaclass=QObjectMeta):
    """Base class for all core modules in UI Easy"""
    
    # Signals
    progress_updated = pyqtSignal(int)  # Progress percentage
    status_updated = pyqtSignal(str)    # Status message
    error_occurred = pyqtSignal(str)    # Error message
    completed = pyqtSignal(object)      # Result object
    streaming_text_updated = pyqtSignal(str)  # Streaming text chunk
    
    def __init__(self, name: str, config: Optional[Union['Config', Dict[str, Any]]] = None):
        super().__init__()
        self.name = name
        self.config = config or {}
        self._is_running = False
        self._result = None
    
    @property
    def is_running(self) -> bool:
        """Check if module is currently running"""
        return self._is_running
    
    @property
    def result(self) -> Any:
        """Get the last result"""
        return self._result
    
    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """Process input data and return result"""
        pass
    
    def run(self, input_data: Any) -> None:
        """Run the module processing"""
        try:
            self._is_running = True
            self.status_updated.emit(f"Starting {self.name}...")
            self.progress_updated.emit(0)
            
            result = self.process(input_data)
            
            self._result = result
            self.progress_updated.emit(100)
            self.status_updated.emit(f"{self.name} completed successfully")
            self.completed.emit(result)
            
        except Exception as e:
            self.error_occurred.emit(f"Error in {self.name}: {str(e)}")
            
        finally:
            self._is_running = False
    
    def update_progress(self, percentage: int, message: str = ""):
        """Update progress during processing"""
        self.progress_updated.emit(percentage)
        if message:
            self.status_updated.emit(message)
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input data before processing"""
        return True
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)