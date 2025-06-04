"""
Test suite for LLM integration with Ollama

This module contains tests for:
1. OllamaService functionality
2. ProcessLeadsAgent LLM operations
3. Error handling and edge cases
"""

import pytest
import asyncio
import aiohttp
from typing import Dict, Any
from src.services.ollama_service import OllamaService
from src.agents.process_leads_agent import ProcessLeadsAgent

# Test configuration
TEST_CONFIG = {
    'ollama': {
        'base_url': 'http://localhost:11434',
        'timeout': 5,
        'retry_attempts': 2,
        'retry_delay': 0.1
    }
}

# Sample test data
SAMPLE_COMPANY_DATA = {
    'name': 'Test Export Co',
    'website': 'https://example.com',
    'industry': 'Manufacturing'
}

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def ollama_service(event_loop):
    """Fixture for OllamaService"""
    service = OllamaService()
    await service.initialize()
    try:
        yield service
    finally:
        await service.cleanup()

@pytest.fixture
async def process_agent(event_loop):
    """Fixture for ProcessLeadsAgent"""
    agent = ProcessLeadsAgent(TEST_CONFIG)
    await agent.initialize()
    try:
        yield agent
    finally:
        await agent.cleanup()

@pytest.mark.asyncio
async def test_ollama_service_initialization(ollama_service):
    """Test OllamaService initialization"""
    assert ollama_service.session is not None
    assert ollama_service.base_url == 'http://localhost:11434'
    assert isinstance(ollama_service.session, aiohttp.ClientSession)

@pytest.mark.asyncio
async def test_ollama_generate(ollama_service):
    """Test basic text generation"""
    prompt = "What is the capital of France?"
    try:
        response = await ollama_service.generate(prompt, 'company_analysis')
        
        assert isinstance(response, dict)
        assert 'text' in response
        assert len(response['text']) > 0
        assert 'Paris' in response['text']
    except Exception as e:
        pytest.fail(f"Test failed with error: {str(e)}")

@pytest.mark.asyncio
async def test_ollama_stream_generate(ollama_service):
    """Test streaming text generation"""
    prompt = "Count from 1 to 5"
    chunks = []
    
    try:
        async for chunk in ollama_service.stream_generate(prompt, 'company_analysis'):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        assert any(str(i) in ''.join(chunks) for i in range(1, 6))
    except Exception as e:
        pytest.fail(f"Test failed with error: {str(e)}")

@pytest.mark.asyncio
async def test_process_agent_company_analysis(process_agent):
    """Test company analysis functionality"""
    try:
        analysis = await process_agent.analyze_company(SAMPLE_COMPANY_DATA)
        
        assert isinstance(analysis, (dict, str))
        if isinstance(analysis, dict):
            assert 'error' not in analysis
        else:
            assert 'company_profile' in analysis.lower()
            assert 'export_evidence' in analysis.lower()
    except Exception as e:
        pytest.fail(f"Test failed with error: {str(e)}")

@pytest.mark.asyncio
async def test_process_agent_value_proposition(process_agent):
    """Test value proposition generation"""
    analysis = {
        'company_profile': 'Test company in manufacturing',
        'export_evidence': ['Exports to Europe', 'ISO certified'],
        'inferred_pain_points': ['Documentation', 'Compliance']
    }
    
    try:
        value_prop = await process_agent.generate_value_proposition(analysis)
        
        assert isinstance(value_prop, (dict, str))
        if isinstance(value_prop, dict):
            assert 'error' not in value_prop
        else:
            assert 'value_proposition' in value_prop.lower()
            assert 'outreach_hook' in value_prop.lower()
    except Exception as e:
        pytest.fail(f"Test failed with error: {str(e)}")

@pytest.mark.asyncio
async def test_process_agent_message_creation(process_agent):
    """Test message creation functionality"""
    company_data = SAMPLE_COMPANY_DATA
    value_proposition = {
        'company_profile': 'Test company',
        'pain_points': ['Documentation'],
        'value_proposition': 'Streamline export docs',
        'outreach_hook': 'Simplify your exports'
    }
    
    try:
        messages = await process_agent.create_outreach_message(company_data, value_proposition)
        
        assert isinstance(messages, (dict, str))
        if isinstance(messages, dict):
            assert 'error' not in messages
        else:
            assert 'email' in messages.lower()
            assert 'sms' in messages.lower()
    except Exception as e:
        pytest.fail(f"Test failed with error: {str(e)}")

@pytest.mark.asyncio
async def test_error_handling_invalid_url(process_agent):
    """Test error handling for invalid website URL"""
    invalid_data = SAMPLE_COMPANY_DATA.copy()
    invalid_data['website'] = 'invalid-url'
    
    try:
        result = await process_agent.analyze_company(invalid_data)
        assert isinstance(result, dict)
        assert 'error' in result
    except Exception as e:
        pytest.fail(f"Test failed with error: {str(e)}")

@pytest.mark.asyncio
async def test_error_handling_missing_data(process_agent):
    """Test error handling for missing company data"""
    try:
        result = await process_agent.analyze_company({})
        assert isinstance(result, dict)
        assert 'error' in result
    except Exception as e:
        pytest.fail(f"Test failed with error: {str(e)}")

if __name__ == '__main__':
    pytest.main(['-v', __file__]) 