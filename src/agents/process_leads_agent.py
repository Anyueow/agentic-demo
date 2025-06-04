"""
Process Leads Agent

This agent is responsible for:
1. Analyzing company data and website content
2. Generating personalized value propositions
3. Creating tailored outreach messages

The agent uses smolagents with Together.ai for LLM operations.
"""

from typing import Dict, Any, Optional
import aiohttp
from bs4 import BeautifulSoup
import re
from smolagents.agents import ToolCallingAgent
from smolagents.tools import Tool
from ..services.together_service import TogetherService
from ..config.llm_config import AGENT_CONFIGS
import asyncio

# --- Tool Classes ---
class WebSearchTool(Tool):
    name = "web_search"
    description = "Search and analyze company website content."
    inputs = {"url": {"type": "string", "description": "The URL of the company website."}}
    output_type = "object"
    def forward(self, url: str):
        return self.agent.fetch_website_content(url)

class ContentAnalysisTool(Tool):
    name = "content_analysis"
    description = "Analyze website content for export operations and pain points."
    inputs = {"content": {"type": "object", "description": "Website content sections."}}
    output_type = "object"
    def forward(self, content: dict):
        return self.agent._analyze_content(content)

class AnalysisReviewTool(Tool):
    name = "analysis_review"
    description = "Review and validate company analysis."
    inputs = {"analysis": {"type": "object", "description": "Company analysis."}}
    output_type = "object"
    def forward(self, analysis: dict):
        return self.agent._review_analysis(analysis)

class PropositionGeneratorTool(Tool):
    name = "proposition_generator"
    description = "Generate value propositions based on analysis."
    inputs = {"analysis": {"type": "object", "description": "Company analysis."}}
    output_type = "object"
    def forward(self, analysis: dict):
        return self.agent._generate_proposition(analysis)

class MessageFormatterTool(Tool):
    name = "message_formatter"
    description = "Format messages for different channels."
    inputs = {
        "company_data": {"type": "object", "description": "Company data."},
        "value_proposition": {"type": "object", "description": "Value proposition."}
    }
    output_type = "object"
    def forward(self, company_data: dict, value_proposition: dict):
        return self.agent._format_message(company_data, value_proposition)

class ChannelAdapterTool(Tool):
    name = "channel_adapter"
    description = "Adapt message tone and content for different channels."
    inputs = {
        "message": {"type": "object", "description": "Message to adapt."},
        "channel": {"type": "string", "description": "Channel name (email, sms, etc)."}
    }
    output_type = "string"
    def forward(self, message: dict, channel: str):
        return self.agent._adapt_for_channel(message, channel)

class ProcessLeadsAgent:
    """Agent for processing leads and generating value propositions"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = None
        self.together = TogetherService()
        
        # Initialize smolagents
        self.company_analyzer = ToolCallingAgent(
            name="company_analyzer",
            description=AGENT_CONFIGS['company_analyzer'].description,
            tools=[
                WebSearchTool(),
                ContentAnalysisTool()
            ],
            model=self.together
        )
        for tool in self.company_analyzer.tools.values():
            tool.agent = self
        
        self.value_proposition_generator = ToolCallingAgent(
            name="value_proposition_generator",
            description=AGENT_CONFIGS['value_proposition_generator'].description,
            tools=[
                AnalysisReviewTool(),
                PropositionGeneratorTool()
            ],
            model=self.together
        )
        for tool in self.value_proposition_generator.tools.values():
            tool.agent = self
        
        self.message_personalizer = ToolCallingAgent(
            name="message_personalizer",
            description=AGENT_CONFIGS['message_personalizer'].description,
            tools=[
                MessageFormatterTool(),
                ChannelAdapterTool()
            ],
            model=self.together
        )
        for tool in self.message_personalizer.tools.values():
            tool.agent = self
    
    async def initialize(self):
        """Initialize async resources"""
        self.session = aiohttp.ClientSession()
    
    async def cleanup(self):
        """Cleanup async resources"""
        if self.session:
            await self.session.close()
    
    async def fetch_website_content(self, url: str) -> Dict[str, str]:
        """Fetch and parse website content"""
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return {'error': f'Failed to fetch website: {response.status}'}
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                content = {
                    'homepage': self._extract_main_content(soup),
                    'about': await self._fetch_page_content(f"{url}/about"),
                    'products': await self._fetch_page_content(f"{url}/products"),
                    'contact': await self._fetch_page_content(f"{url}/contact")
                }
                
                return content
                
        except Exception as e:
            return {'error': str(e)}
    
    async def _fetch_page_content(self, url: str) -> str:
        """Fetch content from a specific page"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    return self._extract_main_content(soup)
                return ""
        except:
            return ""
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from a page"""
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    async def _analyze_content(self, content: Dict[str, str]) -> Dict[str, Any]:
        """Analyze website content"""
        prompt = f"""Analyze the following website content:
        
        Homepage: {content['homepage']}
        About: {content['about']}
        Products: {content['products']}
        
        Provide analysis in JSON format with:
        1. Company Profile
        2. Export Evidence
        3. Inferred Pain Points
        4. Feature Matches"""
        
        response = await self.together.generate(prompt)
        return response['text']
    
    async def _review_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Review and validate company analysis"""
        prompt = f"""Review this company analysis:
        
        {analysis}
        
        Validate and enhance the analysis with:
        1. Additional insights
        2. Confidence scores
        3. Missing information"""
        
        response = await self.together.generate(prompt)
        return response['text']
    
    async def _generate_proposition(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate value proposition"""
        prompt = f"""Based on this analysis:
        
        {analysis}
        
        Generate a value proposition with:
        1. Company Profile
        2. Pain Points
        3. Value Proposition
        4. Outreach Hook"""
        
        response = await self.together.generate(prompt)
        return response['text']
    
    async def _format_message(self, 
                            company_data: Dict[str, Any],
                            value_proposition: Dict[str, Any]) -> Dict[str, str]:
        """Format messages for different channels"""
        prompt = f"""Create messages based on:
        
        Company: {company_data}
        Value Proposition: {value_proposition}
        
        Format for:
        1. Email (subject and body)
        2. SMS"""
        
        response = await self.together.generate(prompt)
        return response['text']
    
    async def _adapt_for_channel(self, 
                               message: Dict[str, str],
                               channel: str) -> str:
        """Adapt message for specific channel"""
        prompt = f"""Adapt this message for {channel}:
        
        {message}
        
        Make it:
        1. Channel-appropriate
        2. Concise
        3. Action-oriented"""
        
        response = await self.together.generate(prompt)
        return response['text']
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a lead through the complete pipeline"""
        try:
            await self.initialize()
            
            # Analyze company
            content = await self.fetch_website_content(data['website'])
            if 'error' in content:
                return {'error': content['error']}
            
            analysis = await self.company_analyzer.run({
                'content': content,
                'company_data': data
            })
            
            # Generate value proposition
            value_proposition = await self.value_proposition_generator.run({
                'analysis': analysis
            })
            
            # Create messages
            messages = await self.message_personalizer.run({
                'company_data': data,
                'value_proposition': value_proposition
            })
            
            return {
                'analysis': analysis,
                'value_proposition': value_proposition,
                'messages': messages,
                'status': 'success'
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
            
        finally:
            await self.cleanup()

    def process_lead(self, lead: dict) -> bool:
        """Synchronous wrapper for async process method, returns True on success, False on error."""
        try:
            # Use asyncio.run if no event loop is running, else use run_until_complete
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None
            if loop and loop.is_running():
                result = asyncio.ensure_future(self.process(lead))
                # This is not ideal, but for Gradio sync context, we block until done
                while not result.done():
                    pass
                output = result.result()
            else:
                output = asyncio.run(self.process(lead))
            return output.get('status') == 'success'
        except Exception as e:
            return False 