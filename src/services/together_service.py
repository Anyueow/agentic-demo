"""
Together.ai Service

This service handles interactions with Together.ai API for LLM operations.
"""

import os
from typing import Dict, Any, Optional, List
import together
from ..config.llm_config import TOGETHER_CONFIG, AVAILABLE_MODELS

class TogetherService:
    """Service for interacting with Together.ai API"""
    
    def __init__(self):
        self.api_key = os.getenv('TOGETHER_API_KEY', TOGETHER_CONFIG.api_key)
        self.model = TOGETHER_CONFIG.model
        self.temperature = TOGETHER_CONFIG.temperature
        self.max_tokens = TOGETHER_CONFIG.max_tokens
        self.top_p = TOGETHER_CONFIG.top_p
        self.frequency_penalty = TOGETHER_CONFIG.frequency_penalty
        self.presence_penalty = TOGETHER_CONFIG.presence_penalty
        
        # Initialize Together.ai client
        together.api_key = self.api_key
    
    def set_model(self, model_name: str) -> None:
        """Set the model to use"""
        if model_name in AVAILABLE_MODELS:
            self.model = AVAILABLE_MODELS[model_name]
        else:
            raise ValueError(f"Model {model_name} not available. Choose from: {list(AVAILABLE_MODELS.keys())}")
    
    def generate(self, 
                prompt: str,
                system_prompt: Optional[str] = None,
                temperature: Optional[float] = None,
                max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate a response from the LLM
        
        Args:
            prompt: The input prompt
            system_prompt: Optional system prompt
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            
        Returns:
            Dictionary containing the generated response
        """
        try:
            response = together.Complete.create(
                prompt=prompt,
                model=self.model,
                system_prompt=system_prompt,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty
            )
            
            return {
                'text': response['output']['choices'][0]['text'],
                'usage': response['output']['usage']
            }
            
        except Exception as e:
            raise Exception(f"Together.ai API error: {str(e)}")
    
    def stream_generate(self,
                       prompt: str,
                       system_prompt: Optional[str] = None,
                       temperature: Optional[float] = None,
                       max_tokens: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Stream a response from the LLM
        
        Args:
            prompt: The input prompt
            system_prompt: Optional system prompt
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            
        Returns:
            List of response chunks
        """
        try:
            response = together.Complete.create(
                prompt=prompt,
                model=self.model,
                system_prompt=system_prompt,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty,
                stream=True
            )
            
            return response
            
        except Exception as e:
            raise Exception(f"Together.ai API error: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return list(AVAILABLE_MODELS.keys())
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        if model_name not in AVAILABLE_MODELS:
            raise ValueError(f"Model {model_name} not available")
            
        return {
            'name': model_name,
            'id': AVAILABLE_MODELS[model_name],
            'provider': 'Together.ai'
        } 