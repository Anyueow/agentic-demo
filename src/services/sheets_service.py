import os
from typing import Dict, List, Optional
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from config import Config
import time

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
        """Get all leads with empty status"""
        try:
            all_leads = self.worksheet.get_all_records()
            return [
                lead for lead in all_leads
                if not lead.get('STATUS') or lead.get('STATUS') == ''
            ]
        except Exception as e:
            print(f"Error getting pending leads: {str(e)}")
            return []
    
    def update_lead_status(self, email: str, status: str, notes: str = None):
        """Update the status of a lead"""
        try:
            # Find the row with matching email
            cell = self.worksheet.find(email)
            if not cell:
                return False
            
            # Update status and notes
            self.worksheet.update_cell(cell.row, 5, status)  # STATUS column
            if notes:
                self.worksheet.update_cell(cell.row, 6, notes)  # NOTES column
            
            # Update last_updated timestamp
            self.worksheet.update_cell(
                cell.row,
                8,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
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