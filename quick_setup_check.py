#!/usr/bin/env python3
"""
Quick setup verification script
"""

import os
import json
from dotenv import load_dotenv

def check_setup():
    print("🔍 ABM Lead Gen Setup Check")
    print("=" * 40)
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("   Create .env file with:")
        print("   GOOGLE_APPLICATION_CREDENTIALS=./lead-gen-app-461916-a2961efb0da6.json")
        print("   SPREADSHEET_ID=your_spreadsheet_id_here")
        print("   WORKSHEET_NAME=Leads")
        return False
    
    # Load environment variables
    load_dotenv()
    
    # Check credentials file
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not creds_path or not os.path.exists(creds_path):
        print("❌ Service account file not found")
        return False
    
    # Check if it's a valid service account
    try:
        with open(creds_path, 'r') as f:
            creds = json.load(f)
        
        if creds.get('type') != 'service_account':
            print("❌ Invalid service account file")
            return False
            
        print("✅ Service account file found")
        print(f"   Email: {creds['client_email']}")
        
    except Exception as e:
        print(f"❌ Error reading service account: {e}")
        return False
    
    # Check spreadsheet ID
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    if not spreadsheet_id or spreadsheet_id == 'your_spreadsheet_id_here':
        print("❌ SPREADSHEET_ID not set")
        print("   Update .env with your actual Google Sheet ID")
        return False
    
    print("✅ SPREADSHEET_ID configured")
    print(f"   ID: {spreadsheet_id}")
    
    print("\n🎉 Setup looks good!")
    print("\n📝 Next: Run 'python test_sheets_setup.py' to test the connection")
    return True

if __name__ == "__main__":
    check_setup() 