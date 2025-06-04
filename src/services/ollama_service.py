"""
Ollama Service

This service handles interactions with the Ollama API for LLM operations.
"""

import aiohttp
import asyncio
from typing import Dict, Any, Optional
from ..config.llm_config import LLM_CONFIGS, OLLAMA_API_CONFIG

class OllamaService:
    """Service for interacting with Ollama API"""
    
    def __init__(self):
        self.base_url = OLLAMA_API_CONFIG['base_url']
        self.timeout = OLLAMA_API_CONFIG['timeout']
        self.retry_attempts = OLLAMA_API_CONFIG['retry_attempts']
        self.retry_delay = OLLAMA_API_CONFIG['retry_delay']
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """Initialize the HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def cleanup(self):
        """Cleanup the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def generate(self, 
                      prompt: str, 
                      use_case: str,
                      context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a response from the LLM
        
        Args:
            prompt: The input prompt
            use_case: The specific use case (e.g., 'company_analysis')
            context: Additional context for the generation
            
        Returns:
            Dictionary containing the generated response
        """
        if not self.session:
            await self.initialize()
        
        config = LLM_CONFIGS[use_case]
        
        # Prepare the request payload
        payload = {
            "model": config.model_name,
            "prompt": prompt,
            "system": config.system_prompt,
            "options": {
                "temperature": config.temperature,
                "top_p": config.top_p,
                "frequency_penalty": config.frequency_penalty,
                "presence_penalty": config.presence_penalty,
                "max_tokens": config.max_tokens
            }
        }
        
        if context:
            payload["context"] = context
        
        # Retry logic for API calls
        for attempt in range(self.retry_attempts):
            try:
                async with self.session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            'text': result.get('response', ''),
                            'context': result.get('context', None)
                        }
                    else:
                        error_text = await response.text()
                        raise Exception(f"API error: {response.status} - {error_text}")
                        
            except Exception as e:
                if attempt == self.retry_attempts - 1:
                    raise
                await asyncio.sleep(self.retry_delay)
    
    async def stream_generate(self, 
                            prompt: str, 
                            use_case: str,
                            context: Optional[Dict[str, Any]] = None):
        """
        Stream a response from the LLM
        
        Args:
            prompt: The input prompt
            use_case: The specific use case
            context: Additional context for the generation
            
        Yields:
            Chunks of the generated response
        """
        if not self.session:
            await self.initialize()
        
        config = LLM_CONFIGS[use_case]
        
        payload = {
            "model": config.model_name,
            "prompt": prompt,
            "system": config.system_prompt,
            "stream": True,
            "options": {
                "temperature": config.temperature,
                "top_p": config.top_p,
                "frequency_penalty": config.frequency_penalty,
                "presence_penalty": config.presence_penalty,
                "max_tokens": config.max_tokens
            }
        }
        
        if context:
            payload["context"] = context
        
        async with self.session.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=self.timeout
        ) as response:
            if response.status == 200:
                async for line in response.content:
                    if line:
                        try:
                            chunk = await response.json()
                            yield chunk.get('response', '')
                        except:
                            continue
            else:
                error_text = await response.text()
                raise Exception(f"API error: {response.status} - {error_text}") 