import os
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from typing import Dict, List, Optional
import smolagents
from smolagents import CodeAgent, PythonInterpreterTool, DuckDuckGoSearchTool, InferenceClientModel
import re
import time
from datetime import datetime
import json
from src.core.config import Config
from sheets_service import GoogleSheetsService
from messaging_service import MessagingService

# Load environment variables
load_dotenv()

class ABMLeadGenAgent:
    """Main agent class for ABM lead generation"""
    
    def __init__(self):
        # Initialize configuration
        self.config = Config()
        
        # Initialize services
        self.sheets_service = GoogleSheetsService(self.config)
        self.messaging_service = MessagingService(self.config)
        
        # Initialize smolagents
        self.model = InferenceClientModel(
            model_id="microsoft/DialoGPT-medium"
        )
        self.agent = CodeAgent(
            model=self.model,
            tools=[
                PythonInterpreterTool(),
                DuckDuckGoSearchTool()
            ]
        )
        print("✓ Smolagents CodeAgent initialized successfully")
    
    def verify_email(self, email: str) -> bool:
        """Verify email validity using regex and optional API"""
        if not email:
            return False
        
        # Basic regex validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False
        
        # If we have a verification API key, use it
        verify_api_key = os.getenv('VERIFY_API_KEY')
        if verify_api_key:
            try:
                response = requests.get(
                    'https://api.hunter.io/v2/email-verifier',
                    params={
                        'email': email,
                        'api_key': verify_api_key
                    }
                )
                data = response.json()
                return data.get('data', {}).get('status') == 'valid'
            except Exception as e:
                print(f"Error verifying email with API: {str(e)}")
                return False
        
        return True
    
    def process_lead(self, lead: Dict) -> bool:
        """Process a single lead through the pipeline"""
        try:
            email = lead.get('CONTACT_EMAIL')
            if not email:
                print(f"Warning: No email found for lead {lead.get('CONTACT_PERSON')}")
                return False
            
            # Verify email
            if not self.verify_email(email):
                self.sheets_service.update_lead_status(
                    email=email,
                    status=self.config.status_values.INVALID
                )
                self.sheets_service.add_remark(
                    email=email,
                    remark="Invalid email format"
                )
                return False
            
            # Update status to verified
            self.sheets_service.update_lead_status(
                email=email,
                status=self.config.status_values.EMAIL_VERIFIED
            )
            
            # Send messages
            email_sent, sms_sent, action = self.messaging_service.send_messages(lead)
            
            if email_sent or sms_sent:
                self.sheets_service.update_lead_status(
                    email=email,
                    status=self.config.status_values.EMAIL_VERIFIED,
                    action=action
                )
                self.sheets_service.add_remark(
                    email=email,
                    remark=f"Messages sent: Email={email_sent}, SMS={sms_sent}"
                )
                return True
            else:
                self.sheets_service.update_lead_status(
                    email=email,
                    status=self.config.status_values.FAILED
                )
                self.sheets_service.add_remark(
                    email=email,
                    remark="Failed to send messages"
                )
                return False
                
        except Exception as e:
            print(f"Error processing lead: {str(e)}")
            if email:
                self.sheets_service.update_lead_status(
                    email=email,
                    status=self.config.status_values.FAILED
                )
                self.sheets_service.add_remark(
                    email=email,
                    remark=f"Error: {str(e)}"
                )
            return False
    
    def run(self):
        """Main execution loop"""
        while True:
            try:
                # Get pending leads
                pending_leads = self.sheets_service.get_pending_leads()
                if not pending_leads:
                    print("No pending leads found. Waiting...")
                    time.sleep(300)  # Wait 5 minutes
                    continue
                
                # Process each lead
                for lead in pending_leads:
                    print(f"Processing lead: {lead.get('CONTACT_PERSON')} ({lead.get('CONTACT_EMAIL')})")
                    self.process_lead(lead)
                    time.sleep(60)  # Wait 1 minute between leads
                
            except Exception as e:
                print(f"Error in main loop: {str(e)}")
                time.sleep(300)  # Wait 5 minutes before retrying

if __name__ == "__main__":
    agent = ABMLeadGenAgent()
    agent.run() 