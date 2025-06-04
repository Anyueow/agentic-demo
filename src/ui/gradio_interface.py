import gradio as gr
from typing import Dict, List, Optional
import time
from datetime import datetime
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ui.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class GradioInterface:
    """Gradio interface for ABM Lead Generation"""
    
    def __init__(self, agent_service, sheets_service):
        """
        Initialize the Gradio interface
        
        Args:
            agent_service: Service for lead processing
            sheets_service: Service for Google Sheets operations
        """
        self.agent_service = agent_service
        self.sheets_service = sheets_service
        self.processing = False
        self.logs = []
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        self.log_file = log_dir / f'ui_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)
    
    def get_pending_leads(self) -> Dict:
        """Get current pending leads"""
        try:
            leads = self.sheets_service.get_pending_leads()
            logger.info(f"Retrieved {len(leads)} pending leads")
            return {
                "pending_count": len(leads),
                "pending_leads": leads
            }
        except Exception as e:
            logger.error(f"Error getting pending leads: {str(e)}")
            return {
                "error": str(e),
                "pending_count": 0,
                "pending_leads": []
            }
    
    def log_message(self, message: str) -> str:
        """Add a message to the logs"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        logger.info(message)
        return "\n".join(self.logs[-100:])  # Keep last 100 messages
    
    def process_leads(self) -> tuple:
        """Process all pending leads"""
        if self.processing:
            return self.get_pending_leads(), "Already processing leads..."
        
        self.processing = True
        self.log_message("Starting lead processing...")
        
        try:
            leads = self.sheets_service.get_pending_leads()
            self.log_message(f"Found {len(leads)} pending leads")
            
            for lead in leads:
                self.log_message(
                    f"Processing lead: {lead.get('CONTACT_PERSON')} "
                    f"({lead.get('CONTACT_EMAIL')})"
                )
                success = self.agent_service.process_lead(lead)
                
                if success:
                    self.log_message(
                        f"✓ Successfully processed lead: {lead.get('CONTACT_EMAIL')}"
                    )
                else:
                    self.log_message(
                        f"✗ Failed to process lead: {lead.get('CONTACT_EMAIL')}"
                    )
                time.sleep(1)  # Small delay between leads
            
            self.log_message("Lead processing completed")
            return self.get_pending_leads(), self.logs[-1]
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            logger.error(error_msg)
            self.log_message(error_msg)
            return {"error": str(e)}, error_msg
        finally:
            self.processing = False
    
    def create_ui(self) -> gr.Blocks:
        """Create the Gradio interface"""
        with gr.Blocks(title="ABM Lead Generation Agent") as ui:
            gr.Markdown("# ABM Lead Generation Agent")
            
            with gr.Row():
                with gr.Column():
                    pending_info = gr.JSON(label="Current Pending Leads")
                    refresh_btn = gr.Button("🔄 Refresh Pending Leads")
                    refresh_btn.click(
                        fn=self.get_pending_leads,
                        inputs=[],
                        outputs=pending_info
                    )
                
                with gr.Column():
                    run_btn = gr.Button("▶️ Run Agent on Pending Leads")
                    logs = gr.Textbox(
                        label="Processing Logs",
                        lines=20,
                        max_lines=20,
                        interactive=False
                    )
                    run_btn.click(
                        fn=self.process_leads,
                        inputs=[],
                        outputs=[pending_info, logs]
                    )
            
            gr.Markdown("""
            ## How to Use
            
            1. Click "Refresh Pending Leads" to see leads awaiting outreach
            2. Click "Run Agent" to process all pending leads
            3. Watch the logs to see progress
            
            ## Status Meanings
            
            - **Empty**: Lead not yet processed
            - **Email Verified**: Email validated, ready for outreach
            - **Failed**: Error during processing
            - **Invalid**: Invalid email format
            
            ## Action Types
            
            - **Emailed**: Email sent successfully
            - **Texted**: SMS sent successfully
            - **Emailed & texted**: Both channels used
            """)
        
        return ui 