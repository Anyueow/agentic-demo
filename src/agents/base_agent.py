"""
Base Agent Class for ABM Lead Generation System

This module provides the base agent class that all specialized agents inherit from.
It includes common functionality and integration points for the LLM SDK.
"""

from typing import Dict, Any, Optional
import logging
from abc import ABC, abstractmethod
from smolagents import CodeAgent, InferenceClientModel

# TODO: Import LLM SDK when available
# from llm_sdk import LLMClient, ModelConfig

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all ABM lead generation agents"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the base agent
        
        Args:
            config: Configuration dictionary containing agent settings
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize InferenceClientModel with Together API key
        self.llm_model = InferenceClientModel(
            model_id="mistralai/Mistral-7B-Instruct-v0.2",  # or your preferred model
            provider="together",
            token=self.config.together_api_key
        )
        self.llm_agent = CodeAgent(tools=[], model=self.llm_model)
    
    def generate_llm_response(self, prompt: str, max_tokens: int = 256, temperature: float = 0.7) -> str:
        """Generate a response from the LLM using smolagents CodeAgent."""
        return self.llm_agent.run(prompt)
    
    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the input data and return results
        
        Args:
            data: Input data for processing
            
        Returns:
            Dict containing processing results
        """
        pass
    
    def log_activity(self, message: str, level: str = 'info'):
        """Log agent activity with appropriate level"""
        log_method = getattr(self.logger, level.lower())
        log_method(message)
    
    def handle_error(self, error: Exception, context: Optional[Dict] = None):
        """Handle errors with proper logging and context"""
        self.logger.error(
            f"Error in {self.__class__.__name__}: {str(error)}",
            extra={'context': context} if context else None
        )
        raise error 