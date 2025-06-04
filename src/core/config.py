from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

@dataclass
class ColumnMapping:
    """Standard column names and their possible variations"""
    COMPANY = ['Company', 'Name of the Exporter', 'Business Name']
    CONTACT_PERSON = ['Contact Person', 'Name of the person', 'Contact Name']
    CONTACT_DESIGNATION = ['Contact Person Designation', 'Designation', 'Title']
    CONTACT_NUMBER = ['Contact Number', 'Phone', 'Mobile']
    CONTACT_EMAIL = ['Contact Email', 'E-Mail', 'Email']
    LOCATION = ['Location', 'Base Location', 'City']
    INDUSTRY = ['Industry', 'Category', 'Business Type']
    STATUS = ['Status']
    ACTION = ['Action']
    REMARKS = ['Remarks', 'Notes']
    FOLLOW_UP_DATE = ['Follow Up Date', 'Next Follow Up']

@dataclass
class StatusValues:
    """Standard status values"""
    PENDING = ""
    EMAIL_VERIFIED = "Email Verified"
    FAILED = "Failed"
    INVALID = "Invalid"

@dataclass
class ActionValues:
    """Standard action values"""
    EMAILED = "Emailed"
    TEXTED = "Texted"
    EMAILED_AND_TEXTED = "Emailed & texted"

class Config:
    """Configuration management for the ABM Lead Generation system"""
    
    def __init__(self):
        load_dotenv()
        
        # Google Sheets configuration
        self.google_credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        self.spreadsheet_id = os.getenv('SPREADSHEET_ID')
        self.worksheet_name = os.getenv('WORKSHEET_NAME', 'Leads')
        
        # API Keys
        self.textfully_api_key = os.getenv('TEXTFULLY_API_KEY')
        self.verify_api_key = os.getenv('VERIFY_API_KEY')
        
        # Email configuration
        self.from_email = os.getenv('FROM_EMAIL')
        
        # Processing settings
        self.delay_between_leads = int(os.getenv('DELAY_BETWEEN_LEADS', '60'))  # seconds
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        self.batch_size = int(os.getenv('BATCH_SIZE', '10'))
        
        # Message templates
        self.email_template = os.getenv('EMAIL_TEMPLATE', """
        Hi {name},
        
        I noticed {company} is doing great work in {industry}. I'd love to connect and discuss how we might help you {value_proposition}.
        
        Would you be open to a quick chat?
        
        Best regards,
        {sender_name}
        """)
        
        self.sms_template = os.getenv('SMS_TEMPLATE', """
        Hi {name}, I'm {sender_name} from {company}. Would you be open to a quick chat about {value_proposition}? Reply STOP to opt out.
        """)
    
    def validate(self) -> Optional[str]:
        """Validate the configuration and return any error message"""
        required_vars = [
            ('GOOGLE_APPLICATION_CREDENTIALS', self.google_credentials_path),
            ('SPREADSHEET_ID', self.spreadsheet_id),
            ('TEXTFULLY_API_KEY', self.textfully_api_key),
            ('FROM_EMAIL', self.from_email)
        ]
        
        for name, value in required_vars:
            if not value:
                return f"Missing required environment variable: {name}"
        
        if not os.path.exists(self.google_credentials_path):
            return f"Google credentials file not found: {self.google_credentials_path}"
        
        return None
    
    def get_worksheet_headers(self) -> list:
        """Get the expected worksheet headers"""
        return [
            'CONTACT_PERSON',
            'CONTACT_EMAIL',
            'CONTACT_PHONE',
            'COMPANY',
            'STATUS',
            'NOTES',
            'TIMESTAMP',
            'LAST_UPDATED',
            'SOURCE',
            'PRIORITY'
        ]

    def get_standard_column_name(self, column_name: str) -> Optional[str]:
        """Convert any variation of column name to standard name"""
        column_name = column_name.strip()
        for standard_name, variations in self.column_mapping.__dict__.items():
            if column_name in variations:
                return standard_name
        return None

    def get_follow_up_date(self) -> str:
        """Get follow-up date (3 weeks from now)"""
        return (datetime.now() + timedelta(days=self.follow_up_days)).strftime("%Y-%m-%d")

    @staticmethod
    def get_required_columns() -> List[str]:
        """Get list of required columns in standard format"""
        return [
            'COMPANY',
            'CONTACT_PERSON',
            'CONTACT_DESIGNATION',
            'CONTACT_NUMBER',
            'CONTACT_EMAIL',
            'LOCATION',
            'INDUSTRY',
            'STATUS',
            'ACTION',
            'REMARKS',
            'FOLLOW_UP_DATE'
        ] 