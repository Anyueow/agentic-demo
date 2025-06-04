"""
LLM Configuration Settings

This module contains configuration settings for different LLM models and their use cases.
"""

from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class ModelConfig:
    """Configuration for a specific LLM model"""
    model_name: str
    temperature: float
    max_tokens: int
    top_p: float
    frequency_penalty: float
    presence_penalty: float
    system_prompt: str

# Mistral configuration for company analysis and value proposition generation
MISTRAL_CONFIG = ModelConfig(
    model_name="mistral",
    temperature=0.7,  # Balanced between creativity and consistency
    max_tokens=2000,  # Sufficient for detailed analysis
    top_p=0.9,       # High diversity in responses
    frequency_penalty=0.3,  # Reduce repetition
    presence_penalty=0.3,   # Encourage diverse topics
    system_prompt="""You are Axel, an expert B2B Sales Development Agent specializing in EXIM and Supply Chain technology.
Your task is to analyze company websites and generate personalized value propositions for Expodite.
Focus on identifying export operations, compliance needs, and potential pain points.
Be precise, professional, and data-driven in your analysis."""
)

# Configuration for different use cases
LLM_CONFIGS: Dict[str, ModelConfig] = {
    'company_analysis': MISTRAL_CONFIG,
    'value_proposition': MISTRAL_CONFIG,
    'message_personalization': MISTRAL_CONFIG
}

# Ollama API settings
OLLAMA_API_CONFIG = {
    'base_url': 'http://localhost:11434',
    'timeout': 30,  # seconds
    'retry_attempts': 3,
    'retry_delay': 1  # seconds
}

@dataclass
class TogetherConfig:
    """Configuration for Together.ai"""
    api_key: str
    model: str = "mistralai/Mistral-7B-Instruct-v0.2"  # Default model
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 0.9
    frequency_penalty: float = 0.3
    presence_penalty: float = 0.3

@dataclass
class AgentConfig:
    """Configuration for smolagents"""
    name: str
    description: str
    system_prompt: str
    tools: list[str]
    memory: bool = True
    max_turns: int = 10

# Together.ai configuration
TOGETHER_CONFIG = TogetherConfig(
    api_key="${TOGETHER_API_KEY}",  # Will be loaded from environment
    model="mistralai/Mistral-7B-Instruct-v0.2",
    temperature=0.7,
    max_tokens=2000,
    top_p=0.9,
    frequency_penalty=0.3,
    presence_penalty=0.3
)

# Agent configurations
AGENT_CONFIGS: Dict[str, AgentConfig] = {
    'company_analyzer': AgentConfig(
        name="Company Analyzer",
        description="Analyzes company websites and generates insights",
        system_prompt="""You are Axel, an expert B2B Sales Development Agent specializing in EXIM and Supply Chain technology.
Your task is to analyze company websites and generate personalized value propositions for Expodite.
Focus on identifying export operations, compliance needs, and potential pain points.
Be precise, professional, and data-driven in your analysis.""",
        tools=['web_search', 'content_analysis'],
        memory=True,
        max_turns=10
    ),
    'value_proposition_generator': AgentConfig(
        name="Value Proposition Generator",
        description="Generates personalized value propositions based on company analysis",
        system_prompt="""You are a value proposition expert for Expodite.
Your task is to create compelling value propositions based on company analysis.
Focus on connecting identified pain points with Expodite's features.
Be specific, relevant, and persuasive in your propositions.""",
        tools=['analysis_review', 'proposition_generator'],
        memory=True,
        max_turns=5
    ),
    'message_personalizer': AgentConfig(
        name="Message Personalizer",
        description="Creates personalized outreach messages",
        system_prompt="""You are a B2B communication expert.
Your task is to create personalized outreach messages based on value propositions.
Focus on being professional, engaging, and action-oriented.
Adapt the tone and content for different channels (email, SMS).""",
        tools=['message_formatter', 'channel_adapter'],
        memory=True,
        max_turns=3
    )
}

# Available Together.ai models
AVAILABLE_MODELS = {
    'mistral-7b': 'mistralai/Mistral-7B-Instruct-v0.2',
    'llama-2-70b': 'meta-llama/Llama-2-70b-chat-hf',
    'mixtral-8x7b': 'mistralai/Mixtral-8x7B-Instruct-v0.1',
    'codellama-34b': 'codellama/CodeLlama-34b-Instruct-hf'
} 