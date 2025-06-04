"""
Main application entry point for the ABM Lead Generation System.
"""

import os
from dotenv import load_dotenv
from pathlib import Path
import logging
from src.agents.process_leads_agent import ProcessLeadsAgent
from src.services.together_service import TogetherService
from src.services.sheets_service import GoogleSheetsService
from src.ui.gradio_interface import GradioInterface
from src.config.llm_config import TOGETHER_CONFIG, AGENT_CONFIGS
from src.core.config import Config
import gradio as gr

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def setup_environment():
    """Setup environment and create necessary directories"""
    # Create required directories
    for dir_name in ['logs', 'data']:
        Path(dir_name).mkdir(exist_ok=True)
    
    # Load environment variables
    load_dotenv()
    
    # Validate required environment variables
    required_vars = [
        'TOGETHER_API_KEY',
        'GOOGLE_APPLICATION_CREDENTIALS',
        'SPREADSHEET_ID',
        'TEXTFULLY_API_KEY',
        'FROM_EMAIL'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

def create_app():
    """Create and configure the application"""
    try:
        # Initialize services
        together_service = TogetherService()
        
        # Create configuration for sheets service
        config = Config()
        sheets_service = GoogleSheetsService(config)
        
        # Initialize agent with configuration
        agent_config = {
            'together_service': together_service,
            'sheets_service': sheets_service,
            'agent_configs': AGENT_CONFIGS
        }
        agent = ProcessLeadsAgent(agent_config)
        
        # Create Gradio interface
        interface = GradioInterface(agent, sheets_service)
        app = interface.create_ui()
        
        return app
        
    except Exception as e:
        logger.error(f"Failed to create application: {str(e)}")
        raise

def main():
    """Main application entry point"""
    try:
        # Setup environment
        setup_environment()
        logger.info("Environment setup completed")
        
        # Create application
        app = create_app()
        logger.info("Application created successfully")
        
        # Launch Gradio interface
        app.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False
        )
        
    except Exception as e:
        logger.error(f"Application failed to start: {str(e)}")
        raise

if __name__ == "__main__":
    main() 