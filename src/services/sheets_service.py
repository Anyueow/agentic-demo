import os
from typing import Dict, List, Optional
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from src.core.config import Config
import time
import requests

class GoogleSheetsService:
    """Service for interacting with Google Sheets"""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = None
        self.spreadsheet = None
        self.worksheet = None
        self._connect()
    
    def _connect(self):
        """Connect to Google Sheets API"""
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.config.google_credentials_path,
            scope
        )
        
        self.client = gspread.authorize(credentials)
        self.spreadsheet = self.client.open_by_key(self.config.spreadsheet_id)
        
        try:
            self.worksheet = self.spreadsheet.worksheet(self.config.worksheet_name)
        except gspread.exceptions.WorksheetNotFound:
            # Create worksheet if it doesn't exist
            self.worksheet = self.spreadsheet.add_worksheet(
                title=self.config.worksheet_name,
                rows=1000,
                cols=10
            )
            # Set headers
            self.worksheet.append_row(self.config.get_worksheet_headers())
    
    def get_pending_leads(self) -> List[Dict]:
        """Get all leads with empty status, standardizing columns"""
        try:
            # Get raw values
            values = self.worksheet.get_all_values()
            if not values:
                return []
            headers = values[0]
            data_rows = values[1:]
            # Map headers to standard names
            standard_headers = []
            for h in headers:
                std = self.config.get_standard_column_name(h)
                standard_headers.append(std if std else h)
            # Build records
            all_leads = []
            for row in data_rows:
                record = {standard_headers[i]: row[i] if i < len(row) else '' for i in range(len(standard_headers))}
                all_leads.append(record)
            # Filter for pending leads
            return [lead for lead in all_leads if not lead.get('STATUS') or lead.get('STATUS') == '']
        except Exception as e:
            print(f"Error getting pending leads: {str(e)}")
            return []
    
    def update_lead_status(self, email: str, status: str = None, action: str = None, follow_up_date: str = None):
        """Update only the status, action, and follow_up_date columns of a lead"""
        try:
            # Find the row with matching email
            cell = self.worksheet.find(email)
            if not cell:
                return False
            headers = self.worksheet.row_values(1)
            # Update STATUS
            if status is not None and 'STATUS' in headers:
                col = headers.index('STATUS') + 1
                self.worksheet.update_cell(cell.row, col, status)
            # Update ACTION
            if action is not None and 'ACTION' in headers:
                col = headers.index('ACTION') + 1
                self.worksheet.update_cell(cell.row, col, action)
            # Update FOLLOW_UP_DATE
            if follow_up_date is not None and 'FOLLOW_UP_DATE' in headers:
                col = headers.index('FOLLOW_UP_DATE') + 1
                self.worksheet.update_cell(cell.row, col, follow_up_date)
            return True
        except Exception as e:
            print(f"Error updating lead status: {str(e)}")
            return False
    
    def add_lead(self, lead_data: Dict) -> bool:
        """Add a new lead to the worksheet"""
        try:
            # Ensure all required fields are present
            required_fields = ['CONTACT_PERSON', 'CONTACT_EMAIL', 'COMPANY']
            for field in required_fields:
                if field not in lead_data:
                    print(f"Missing required field: {field}")
                    return False
            
            # Add timestamp
            lead_data['TIMESTAMP'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            lead_data['LAST_UPDATED'] = lead_data['TIMESTAMP']
            
            # Prepare row data in correct order
            row_data = []
            for header in self.config.get_worksheet_headers():
                row_data.append(lead_data.get(header, ''))
            
            # Append the row
            self.worksheet.append_row(row_data)
            return True
            
        except Exception as e:
            print(f"Error adding lead: {str(e)}")
            return False
    
    def get_lead_by_email(self, email: str) -> Optional[Dict]:
        """Get a lead by email address"""
        try:
            cell = self.worksheet.find(email)
            if not cell:
                return None
            
            # Get the entire row
            row = self.worksheet.row_values(cell.row)
            headers = self.config.get_worksheet_headers()
            
            # Convert to dictionary
            return dict(zip(headers, row))
            
        except Exception as e:
            print(f"Error getting lead: {str(e)}")
            return None
    
    def retry_failed_leads(self, max_retries: int = 3):
        """Retry processing failed leads"""
        try:
            all_leads = self.worksheet.get_all_records()
            failed_leads = [
                lead for lead in all_leads
                if lead.get('STATUS') == 'Failed'
            ]
            
            for lead in failed_leads:
                # Reset status to empty
                self.update_lead_status(
                    lead['CONTACT_EMAIL'],
                    '',
                    f"Retrying after failure. Attempt {lead.get('RETRY_COUNT', 0) + 1}/{max_retries}"
                )
                
                # Update retry count
                cell = self.worksheet.find(lead['CONTACT_EMAIL'])
                self.worksheet.update_cell(cell.row, 11, str(int(lead.get('RETRY_COUNT', 0)) + 1))
                
                time.sleep(1)  # Small delay between updates
            
            return len(failed_leads)
            
        except Exception as e:
            print(f"Error retrying failed leads: {str(e)}")
            return 0
    
    def verify_email_mailboxlayer(self, email: str) -> bool:
        """Verify email using Mailboxlayer API. Returns True if valid, False otherwise."""
        api_key = self.config.mailboxlayer_api_key
        if not api_key:
            print("[WARN] No Mailboxlayer API key set.")
            return False
        url = f"https://apilayer.net/api/check?access_key={api_key}&email={email}"
        try:
            resp = requests.get(url)
            data = resp.json()
            # Consider valid if format_valid and mx_found are both True
            is_valid = data.get("format_valid") and data.get("mx_found")
            print(f"[DEBUG] Mailboxlayer result for {email}: {data} | Verified: {is_valid}")
            return bool(is_valid)
        except Exception as e:
            print(f"[ERROR] Mailboxlayer API error: {e}")
            return False 