import os
from typing import Dict, Optional, Tuple
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.core.config import Config
import json

class MessagingService:
    """Service for handling email and SMS communications"""
    
    def __init__(self, config: Config):
        self.config = config
        self.textfully_api_key = config.textfully_api_key
        self.from_email = config.from_email
    
    def create_email_message(self, lead: Dict) -> str:
        """Create a personalized email message for the lead"""
        return f"""Hi {lead.get('CONTACT_PERSON', 'there')},

I noticed you're with {lead.get('COMPANY', 'your company')} and thought you might be interested in our solutions.

Would you be open to a quick chat about how we could help?

Best regards,
Your Name"""
    
    def create_sms_message(self, lead: Dict) -> str:
        """Create a personalized SMS message for the lead"""
        return f"Hi {lead.get('CONTACT_PERSON', 'there')}, I'm reaching out about {lead.get('COMPANY', 'your company')}. Would you be open to a quick chat?"
    
    def send_sms(self, phone: str, message: str) -> Dict:
        """Send SMS via Textfully API"""
        if not phone or not message:
            return {"success": False, "error": "Missing phone or message"}
        
        try:
            # Format phone number (remove spaces, ensure + prefix)
            phone = phone.strip().replace(" ", "")
            if not phone.startswith("+"):
                phone = "+" + phone
            
            # Prepare API request
            url = "https://api.textfully.com/v1/messages"
            headers = {
                "Authorization": f"Bearer {self.textfully_api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "to": phone,
                "message": message,
                "from": "ABM Agent"  # Your Textfully sender ID
            }
            
            # Send request
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            return {
                "success": True,
                "message_id": response.json().get("id"),
                "status": response.json().get("status")
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send SMS: {str(e)}"
            }
    
    def send_email(self, to_email: str, subject: str, message: str) -> Dict:
        """Send email using SMTP"""
        if not to_email or not subject or not message:
            return {"success": False, "error": "Missing required email fields"}
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add message body
            msg.attach(MIMEText(message, 'plain'))
            
            # Connect to SMTP server (using Gmail as example)
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            
            # Login (you'll need to set up app-specific password)
            server.login(self.from_email, os.getenv('EMAIL_PASSWORD'))
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            return {
                "success": True,
                "message": "Email sent successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send email: {str(e)}"
            }
    
    def send_multi_channel(self, lead: Dict, message: str) -> Dict:
        """Send message via both email and SMS if available"""
        results = {
            "email": None,
            "sms": None,
            "success": False
        }
        
        # Send email if available
        if lead.get('CONTACT_EMAIL'):
            email_result = self.send_email(
                to_email=lead['CONTACT_EMAIL'],
                subject="Quick question about your business",
                message=message
            )
            results['email'] = email_result
        
        # Send SMS if available
        if lead.get('CONTACT_PHONE'):
            sms_result = self.send_sms(
                phone=lead['CONTACT_PHONE'],
                message=message
            )
            results['sms'] = sms_result
        
        # Overall success if at least one channel succeeded
        results['success'] = (
            (results['email'] and results['email']['success']) or
            (results['sms'] and results['sms']['success'])
        )
        
        return results
    
    def format_message(self, template: str, lead: Dict) -> str:
        """Format message template with lead data"""
        try:
            # Add some default values if not present
            context = {
                'name': lead.get('CONTACT_PERSON', 'there'),
                'company': lead.get('COMPANY', 'your company'),
                'industry': lead.get('INDUSTRY', 'your industry'),
                'value_proposition': lead.get('VALUE_PROPOSITION', 'how we can help'),
                'sender_name': lead.get('SENDER_NAME', 'Your Name')
            }
            
            # Format the message
            return template.format(**context)
            
        except Exception as e:
            print(f"Error formatting message: {str(e)}")
            return template  # Return original template if formatting fails
    
    def send_messages(self, lead: Dict) -> Tuple[bool, bool, str]:
        """Send both email and SMS to a lead"""
        email = lead.get('CONTACT_EMAIL')
        phone = lead.get('CONTACT_NUMBER')
        
        if not email and not phone:
            return False, False, "No contact information available"
        
        email_sent = False
        sms_sent = False
        
        # Send email if available
        if email:
            email_message = self.create_email_message(lead)
            email_sent = self.send_email(
                to_email=email,
                subject=f"Quick question for {lead.get('COMPANY', 'your company')}",
                message=email_message
            )
        
        # Send SMS if available
        if phone:
            sms_message = self.create_sms_message(lead)
            sms_sent = self.send_sms(phone=phone, message=sms_message)
        
        # Determine action taken
        if email_sent and sms_sent:
            action = self.config.action_values.EMAILED_AND_TEXTED
        elif email_sent:
            action = self.config.action_values.EMAILED
        elif sms_sent:
            action = self.config.action_values.TEXTED
        else:
            action = None
        
        return email_sent, sms_sent, action 