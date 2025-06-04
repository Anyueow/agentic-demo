#!/usr/bin/env python3
"""
Debug script to check what Google Drive files the service account can access
"""

import os
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

def debug_access():
    print("🔍 Debugging Google Sheets Access")
    print("=" * 50)
    
    try:
        # Set up credentials
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)
        
        print("✅ Successfully authenticated with Google Sheets API")
        
        # List all spreadsheets the service account has access to
        print("\n📋 Spreadsheets accessible by service account:")
        
        try:
            spreadsheets = client.list_permissions()
            if spreadsheets:
                for i, sheet in enumerate(spreadsheets[:5]):  # Show first 5
                    print(f"   {i+1}. {sheet.title} (ID: {sheet.id})")
            else:
                print("   No spreadsheets found")
        except:
            # Try alternative method
            print("   (Cannot list spreadsheets - trying to create a test sheet)")
            
            # Try to create a test spreadsheet
            try:
                test_sheet = client.create("ABM Test Sheet")
                print(f"✅ Created test spreadsheet: {test_sheet.title}")
                print(f"   ID: {test_sheet.id}")
                print(f"   URL: https://docs.google.com/spreadsheets/d/{test_sheet.id}/edit")
                print("\n📝 You can use this test spreadsheet for now!")
                print(f"   Update your .env file: SPREADSHEET_ID={test_sheet.id}")
                
                # Add some sample data
                worksheet = test_sheet.sheet1
                worksheet.update('A1:J1', [['lead_id', 'name', 'email', 'company', 'status', 'notes', 'timestamp', 'last_updated', 'source', 'priority']])
                worksheet.update('A2:J4', [
                    [1, 'John Doe', 'john.doe@techstartup.com', 'TechStartup Inc', 'pending', '', '', '', 'manual', 'high'],
                    [2, 'Jane Smith', 'jane.smith@enterprise.com', 'Enterprise Solutions', 'pending', '', '', '', 'manual', 'medium'],
                    [3, 'Bob Wilson', 'bob@innovation.co', 'Innovation Co', 'pending', '', '', '', 'manual', 'low']
                ])
                print("✅ Added sample data to test sheet")
                
                return test_sheet.id
                
            except Exception as e:
                print(f"❌ Cannot create test spreadsheet: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def verify_current_id():
    """Try to access the currently configured spreadsheet"""
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    print(f"\n🔍 Testing current spreadsheet ID: {spreadsheet_id}")
    
    if not spreadsheet_id or spreadsheet_id == 'your_spreadsheet_id_here':
        print("❌ No valid spreadsheet ID configured")
        return False
    
    try:
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)
        
        spreadsheet = client.open_by_key(spreadsheet_id)
        print(f"✅ Successfully opened: {spreadsheet.title}")
        return True
        
    except Exception as e:
        print(f"❌ Cannot access spreadsheet: {e}")
        print("\n💡 Possible solutions:")
        print("1. Check that the spreadsheet ID is correct")
        print("2. Make sure the spreadsheet is shared with: lead-gen-sa@lead-gen-app-461916.iam.gserviceaccount.com")
        print("3. Ensure the service account has Editor permissions")
        return False

if __name__ == "__main__":
    debug_access()
    verify_current_id() 