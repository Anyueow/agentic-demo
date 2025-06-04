import os
from dotenv import load_dotenv
from src.core.config import Config
from src.services.sheets_service import GoogleSheetsService
from src.services.messaging_service import MessagingService
import time
import unittest
from unittest.mock import Mock, patch

def test_config():
    """Test configuration loading"""
    print("\n=== Testing Configuration ===")
    config = Config()
    error = config.validate()
    if error:
        print(f"❌ Configuration error: {error}")
        return False
    
    print("✓ All required environment variables are set")
    print("✓ Google credentials file exists")
    return True

def test_sheets_connection():
    """Test Google Sheets connection"""
    print("\n=== Testing Google Sheets Connection ===")
    try:
        config = Config()
        sheets = GoogleSheetsService(config)
        
        # Test worksheet access
        headers = sheets.worksheet.row_values(1)
        print(f"✓ Successfully connected to worksheet: {sheets.worksheet.title}")
        print(f"✓ Found headers: {headers}")
        
        # Test adding a test lead
        test_lead = {
            'CONTACT_PERSON': 'Test User',
            'CONTACT_EMAIL': f'test_{int(time.time())}@example.com',
            'COMPANY': 'Test Company',
            'STATUS': 'Test'
        }
        
        if sheets.add_lead(test_lead):
            print("✓ Successfully added test lead")
        else:
            print("❌ Failed to add test lead")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Google Sheets error: {str(e)}")
        return False

def test_messaging():
    """Test messaging service"""
    print("\n=== Testing Messaging Service ===")
    try:
        config = Config()
        messaging = MessagingService(config)
        
        # Test message formatting
        test_lead = {
            'CONTACT_PERSON': 'Test User',
            'COMPANY': 'Test Company',
            'INDUSTRY': 'Technology',
            'VALUE_PROPOSITION': 'improve efficiency'
        }
        
        formatted = messaging.format_message(config.email_template, test_lead)
        print("✓ Message formatting successful")
        print(f"Sample formatted message:\n{formatted}")
        
        return True
        
    except Exception as e:
        print(f"❌ Messaging service error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("Starting ABM Lead Generation System Tests...")
    
    # Load environment variables
    load_dotenv()
    
    # Run tests
    config_ok = test_config()
    sheets_ok = test_sheets_connection()
    messaging_ok = test_messaging()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Configuration: {'✓' if config_ok else '❌'}")
    print(f"Google Sheets: {'✓' if sheets_ok else '❌'}")
    print(f"Messaging: {'✓' if messaging_ok else '❌'}")
    
    if all([config_ok, sheets_ok, messaging_ok]):
        print("\n✓ All systems are ready!")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1

class TestSetup(unittest.TestCase):
    """Test cases for setup functionality"""
    
    def test_config_initialization(self):
        """Test that Config can be initialized"""
        config = Config()
        self.assertIsNotNone(config)
        self.assertIsNotNone(config.google_credentials_path)
        self.assertIsNotNone(config.spreadsheet_id)
        self.assertIsNotNone(config.worksheet_name)

if __name__ == "__main__":
    exit(main()) 