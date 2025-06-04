import gradio as gr
from abm_agent import ABMLeadGenAgent
from src.core.config import Config
import json
from typing import Dict, List
import threading
import time

class ABMLeadGenUI:
    """Gradio UI for ABM Lead Generation"""
    
    def __init__(self):
        self.config = Config()
        self.agent = ABMLeadGenAgent()
        self.processing = False
        self.logs = []
    
    def get_pending_leads(self) -> Dict:
        """Get current pending leads"""
        try:
            leads = self.agent.sheets_service.get_pending_leads()
            return {
                "pending_count": len(leads),
                "pending_leads": leads
            }
        except Exception as e:
            return {
                "error": str(e),
                "pending_count": 0,
                "pending_leads": []
            }
    
    def log_message(self, message: str):
        """Add a message to the logs"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")
        return "\n".join(self.logs[-100:])  # Keep last 100 messages
    
    def process_leads(self):
        """Process all pending leads"""
        if self.processing:
            return "Already processing leads..."
        
        self.processing = True
        self.log_message("Starting lead processing...")
        
        try:
            leads = self.agent.sheets_service.get_pending_leads()
            self.log_message(f"Found {len(leads)} pending leads")
            
            for lead in leads:
                self.log_message(f"Processing lead: {lead.get('CONTACT_PERSON')} ({lead.get('CONTACT_EMAIL')})")
                success = self.agent.process_lead(lead)
                if success:
                    self.log_message(f"✓ Successfully processed lead: {lead.get('CONTACT_EMAIL')}")
                else:
                    self.log_message(f"✗ Failed to process lead: {lead.get('CONTACT_EMAIL')}")
                time.sleep(1)  # Small delay between leads
            
            self.log_message("Lead processing completed")
            return self.get_pending_leads()
            
        except Exception as e:
            self.log_message(f"Error: {str(e)}")
            return {"error": str(e)}
        finally:
            self.processing = False
    
    def create_ui(self):
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

if __name__ == "__main__":
    ui = ABMLeadGenUI()
    app = ui.create_ui()
    app.launch(server_name="0.0.0.0", server_port=7860) 