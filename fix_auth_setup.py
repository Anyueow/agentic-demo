#!/usr/bin/env python3
"""
Script to help fix Google authentication setup.
The user has OAuth2 client credentials but needs service account credentials.
"""

import json
import os

def analyze_credentials_file():
    """Analyze the current credentials file"""
    filename = "client_secret_842043796505-mpmubln13p3or44adrkhe8a10obhlm22.apps.googleusercontent.com.json"
    
    if not os.path.exists(filename):
        print(f"❌ File {filename} not found")
        return
    
    try:
        with open(filename, 'r') as f:
            creds = json.load(f)
        
        print("🔍 Analyzing your credentials file...")
        print(f"📁 File: {filename}")
        print()
        
        if "web" in creds:
            print("📋 Type: OAuth2 Client Credentials (Web Application)")
            print("   - client_id:", creds["web"].get("client_id", "N/A"))
            print("   - project_id:", creds["web"].get("project_id", "N/A"))
            print()
            
            print("⚠️  ISSUE: This is an OAuth2 client secret file")
            print("   We need a SERVICE ACCOUNT key for server-to-server access")
            print()
            
            print("🔧 How to fix this:")
            print("1. Go to Google Cloud Console:")
            print("   https://console.cloud.google.com/")
            print()
            print("2. Select your project:", creds["web"].get("project_id", "your-project"))
            print()
            print("3. Navigate to: IAM & Admin → Service Accounts")
            print()
            print("4. Create a new service account:")
            print("   - Name: lead-gen-service-account")
            print("   - Description: For ABM lead generation app")
            print("   - No roles needed (we'll share the sheet directly)")
            print()
            print("5. Create a JSON key:")
            print("   - Click on the service account")
            print("   - Go to 'Keys' tab")
            print("   - 'Add Key' → 'Create new key' → JSON")
            print("   - Download the JSON file")
            print()
            print("6. Share your Google Sheet with the service account:")
            print("   - Open your Google Sheet")
            print("   - Click 'Share'")
            print("   - Add the service account email (looks like: name@project.iam.gserviceaccount.com)")
            print("   - Give it 'Editor' permission")
            print()
            
        elif "type" in creds and creds["type"] == "service_account":
            print("✅ Type: Service Account Key")
            print("   - client_email:", creds.get("client_email", "N/A"))
            print("   - project_id:", creds.get("project_id", "N/A"))
            print()
            print("✅ This is the correct type of credentials!")
            
        else:
            print("❓ Unknown credentials format")
            print("Raw data:", creds)
            
    except Exception as e:
        print(f"❌ Error reading credentials file: {e}")

def create_temp_env_file():
    """Create a temporary .env file with instructions"""
    env_content = """# ABM Lead Generation Environment Variables
# 
# IMPORTANT: You need to replace the credentials file with a SERVICE ACCOUNT key
# Current file is OAuth2 client credentials, not service account

# Google Sheets Configuration
# TODO: Replace with service account JSON key path
GOOGLE_APPLICATION_CREDENTIALS=./client_secret_842043796505-mpmubln13p3or44adrkhe8a10obhlm22.apps.googleusercontent.com.json

# TODO: Add your Google Spreadsheet ID from the URL
# Example: https://docs.google.com/spreadsheets/d/1AbCdEfGhIJK.../edit
#                                               ^^^^^^^^^^
SPREADSHEET_ID=

# Worksheet/tab name (default: Leads)
WORKSHEET_NAME=Leads

# Optional APIs (uncomment and fill when you have them)
# TEXTFULLY_API_KEY=
# VERIFY_API_KEY=
# FROM_EMAIL=
# HF_TOKEN=
"""
    
    with open(".env.template", "w") as f:
        f.write(env_content)
    
    print("📄 Created .env.template file")
    print("   Copy this to .env and update the values")

def main():
    print("🚨 Google Authentication Setup Fix")
    print("=" * 50)
    print()
    
    analyze_credentials_file()
    create_temp_env_file()
    
    print()
    print("📝 Quick Summary:")
    print("- You have OAuth2 client credentials")
    print("- You need service account credentials")
    print("- Follow the steps above to create proper credentials")
    print("- Then update .env with the new service account JSON file path")

if __name__ == "__main__":
    main() 