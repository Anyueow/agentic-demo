import os
import signal
import subprocess
import gradio as gr
from src.agents.process_leads_agent import ProcessLeadsAgent
from src.core.config import Config
from src.services.sheets_service import GoogleSheetsService
import json
from typing import Dict, List
import threading
import time

def kill_port(port):
    """Kill any process using the specified port (macOS/Linux)."""
    try:
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"], capture_output=True, text=True
        )
        pids = result.stdout.strip().split("\n")
        for pid in pids:
            if pid:
                print(f"Killing process on port {port}: PID {pid}")
                os.kill(int(pid), signal.SIGKILL)
    except Exception as e:
        print(f"[WARN] Could not kill process on port {port}: {e}")

def check_and_standardize_headers():
    """Check worksheet headers and standardize if needed."""
    config = Config()
    sheets_service = GoogleSheetsService(config)
    worksheet = sheets_service.worksheet
    required_headers = [
        "COMPANY",
        "COMPANY_URL",
        "CONTACT_PERSON",
        "CONTACT_DESIGNATION",
        "CONTACT_NUMBER",
        "CONTACT_EMAIL",
        "LOCATION",
        "INDUSTRY",
        "STATUS",
        "ACTION",
        "REMARKS",
        "FOLLOW_UP_DATE"
    ]
    headers = worksheet.row_values(1)
    if headers != required_headers:
        print("[INFO] Worksheet headers do not match required format. Standardizing...")
        result = subprocess.run([
            "python", "/Users/anyueow/Desktop/coding projects/agentic-demo/standardize_worksheet.py"
        ])
        if result.returncode != 0:
            print("[ERROR] Failed to standardize worksheet headers. Exiting.")
            exit(1)
        else:
            print("[INFO] Worksheet headers standardized.")
    else:
        print("[INFO] Worksheet headers already standardized.")

def check_and_fill_company_urls():
    """Run the company URL finder script to fill missing COMPANY_URL values."""
    print("[INFO] Ensuring COMPANY_URL values are filled...")
    result = subprocess.run([
        "python", "find_company_urls.py"
    ])
    if result.returncode != 0:
        print("[ERROR] Failed to fill COMPANY_URL values. Exiting.")
        exit(1)
    else:
        print("[INFO] COMPANY_URL values filled.")

class ABMLeadGenUI:
    """Gradio UI for ABM Lead Generation"""
    
    def __init__(self):
        self.config = Config()
        self.sheets_service = GoogleSheetsService(self.config)
        self.agent = ProcessLeadsAgent(self.config)
        self.processing = False
        self.logs = []
    
    def get_pending_leads(self) -> Dict:
        """Get current pending leads"""
        try:
            pending_leads = self.sheets_service.get_pending_leads()
            return {
                "pending_count": len(pending_leads),
                "pending_leads": pending_leads
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
            return "Already processing leads...", self.log_message("Already processing leads...")
        
        self.processing = True
        self.log_message("Starting lead processing...")
        
        try:
            pending_leads = self.sheets_service.get_pending_leads()
            self.log_message(f"Found {len(pending_leads)} pending leads")
            
            for lead in pending_leads:
                self.log_message(f"Processing lead: {lead.get('CONTACT_PERSON')} ({lead.get('CONTACT_EMAIL')})")
                success = self.agent.process_lead(lead)
                if success:
                    self.sheets_service.update_lead_status(
                        lead['CONTACT_EMAIL'],
                        'Processed',
                        'Successfully processed by agent'
                    )
                    self.log_message(f"✓ Successfully processed lead: {lead.get('CONTACT_EMAIL')}")
                else:
                    self.sheets_service.update_lead_status(
                        lead['CONTACT_EMAIL'],
                        'Failed',
                        'Failed to process lead'
                    )
                    self.log_message(f"✗ Failed to process lead: {lead.get('CONTACT_EMAIL')}")
            
            self.log_message("Lead processing completed")
            return self.get_pending_leads(), self.log_message("Processing completed successfully")
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.log_message(error_msg)
            return {"error": str(e)}, self.log_message(error_msg)
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
            - **Processed**: Successfully processed by agent
            - **Failed**: Error during processing
            
            ## Action Types
            
            - **Emailed**: Email sent successfully
            - **Texted**: SMS sent successfully
            - **Emailed & texted**: Both channels used
            """)
        
        return ui

if __name__ == "__main__":
    kill_port(7865)
    check_and_standardize_headers()
    check_and_fill_company_urls()
    ui = ABMLeadGenUI()
    app = ui.create_ui()
    app.launch(server_name="localhost", server_port=7865) 