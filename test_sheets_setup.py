#!/usr/bin/env python3
"""
Test script to verify Google Sheets API setup and create initial sheet structure.
Run this after setting up your service account and environment variables.
"""

import os
import sys
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Load environment variables
load_dotenv()

def check_environment_variables():
    """Check if all required environment variables are set"""
    required_vars = [
        'GOOGLE_APPLICATION_CREDENTIALS',
        'SPREADSHEET_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these in your .env file:")
        print("GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json")
        print("SPREADSHEET_ID=your_google_sheet_id")
        print("WORKSHEET_NAME=All  # Optional, defaults to 'All'")
        return False
    
    # Check if credentials file exists
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not os.path.exists(creds_path):
        print(f"❌ Credentials file not found: {creds_path}")
        return False
    
    print("✅ All required environment variables are set")
    return True

def test_google_sheets_connection():
    """Test connection to Google Sheets"""
    try:
        print("\n🔐 Testing Google Sheets authentication...")
        
        # Set up credentials
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)
        
        print("✅ Successfully authenticated with Google Sheets API")
        
        # Test opening the spreadsheet
        spreadsheet_id = os.getenv('SPREADSHEET_ID')
        worksheet_name = os.getenv('WORKSHEET_NAME', 'All')
        
        print(f"\n📊 Opening spreadsheet: {spreadsheet_id}")
        spreadsheet = client.open_by_key(spreadsheet_id)
        print(f"✅ Successfully opened spreadsheet: '{spreadsheet.title}'")
        
        # Try to open the worksheet
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
            print(f"✅ Successfully opened worksheet: '{worksheet_name}'")
            
            # Get current data
            all_values = worksheet.get_all_values()
            print(f"📋 Current worksheet has {len(all_values)} rows")
            
            if len(all_values) > 0:
                print(f"📋 Headers: {all_values[0]}")
            
            return client, worksheet
            
        except gspread.WorksheetNotFound:
            print(f"❌ Worksheet '{worksheet_name}' not found")
            print(f"📋 Available worksheets: {[ws.title for ws in spreadsheet.worksheets()]}")
            
            # Offer to create the worksheet
            create = input(f"\n❓ Would you like to create the '{worksheet_name}' worksheet? (y/n): ")
            if create.lower() == 'y':
                worksheet = create_leads_worksheet(spreadsheet, worksheet_name)
                return client, worksheet
            else:
                return None, None
                
    except Exception as e:
        print(f"❌ Error connecting to Google Sheets: {e}")
        return None, None

def create_leads_worksheet(spreadsheet, worksheet_name):
    """Create a new worksheet with proper headers for leads"""
    try:
        print(f"\n🆕 Creating new worksheet: '{worksheet_name}'")
        
        # Create the worksheet
        worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows="1000", cols="10")
        
        # Set up headers
        headers = [
            'lead_id',
            'name', 
            'email',
            'company',
            'status',
            'notes',
            'timestamp',
            'last_updated',
            'source',
            'priority'
        ]
        
        worksheet.append_row(headers)
        print("✅ Added headers to the new worksheet")
        
        # Add some sample data
        sample_data = [
            [1, 'John Doe', 'john.doe@techstartup.com', 'TechStartup Inc', 'pending', '', datetime.now().isoformat(), '', 'manual', 'high'],
            [2, 'Jane Smith', 'jane.smith@enterprise.com', 'Enterprise Solutions', 'pending', '', datetime.now().isoformat(), '', 'manual', 'medium'],
            [3, 'Bob Wilson', 'bob@innovation.co', 'Innovation Co', 'pending', '', datetime.now().isoformat(), '', 'manual', 'low']
        ]
        
        for row in sample_data:
            worksheet.append_row(row)
        
        print("✅ Added sample data to the worksheet")
        return worksheet
        
    except Exception as e:
        print(f"❌ Error creating worksheet: {e}")
        return None

def test_read_write_operations(worksheet):
    """Test basic read and write operations"""
    if not worksheet:
        return False
        
    try:
        print("\n🧪 Testing read/write operations...")
        
        # Test reading all records
        records = worksheet.get_all_records()
        print(f"✅ Successfully read {len(records)} records")
        
        # Test writing a new record
        test_lead = [
            999,  # lead_id
            'Test User',  # name
            'test@example.com',  # email
            'Test Company',  # company
            'testing',  # status
            'Added by test script',  # notes
            datetime.now().isoformat(),  # timestamp
            datetime.now().isoformat(),  # last_updated
            'test_script',  # source
            'low'  # priority
        ]
        
        worksheet.append_row(test_lead)
        print("✅ Successfully added test record")
        
        # Test updating a cell
        last_row = len(worksheet.get_all_values())
        worksheet.update_cell(last_row, 5, 'test_completed')  # Update status column
        print("✅ Successfully updated test record")
        
        # Clean up - remove the test record
        worksheet.delete_rows(last_row)
        print("✅ Successfully cleaned up test record")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during read/write test: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Google Sheets Setup Test")
    print("=" * 50)
    
    # Check environment variables
    if not check_environment_variables():
        sys.exit(1)
    
    # Test connection
    client, worksheet = test_google_sheets_connection()
    
    if not client or not worksheet:
        print("\n❌ Could not establish connection to Google Sheets")
        sys.exit(1)
    
    # Test operations
    if test_read_write_operations(worksheet):
        print("\n🎉 All tests passed! Your Google Sheets integration is ready.")
        print("\n📝 Next steps:")
        print("1. Update your .env file with any missing variables")
        print("2. Run 'python abm_agent.py' to test the full ABM workflow")
        print("3. Check your Google Sheet to see the results")
    else:
        print("\n❌ Some tests failed. Please check your setup.")
        sys.exit(1)

if __name__ == "__main__":
    main() 