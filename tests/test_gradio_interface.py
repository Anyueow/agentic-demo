import unittest
from unittest.mock import Mock, patch
import gradio as gr
from src.ui.gradio_interface import GradioInterface
import time

class TestGradioInterface(unittest.TestCase):
    """Test cases for GradioInterface"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_agent_service = Mock()
        self.mock_sheets_service = Mock()
        self.interface = GradioInterface(
            self.mock_agent_service,
            self.mock_sheets_service
        )
    
    def test_get_pending_leads_success(self):
        """Test successful retrieval of pending leads"""
        # Setup mock
        mock_leads = [
            {'CONTACT_PERSON': 'Test User', 'CONTACT_EMAIL': 'test@example.com'}
        ]
        self.mock_sheets_service.get_pending_leads.return_value = mock_leads
        
        # Call method
        result = self.interface.get_pending_leads()
        
        # Assertions
        self.assertEqual(result['pending_count'], 1)
        self.assertEqual(result['pending_leads'], mock_leads)
        self.mock_sheets_service.get_pending_leads.assert_called_once()
    
    def test_get_pending_leads_error(self):
        """Test error handling in get_pending_leads"""
        # Setup mock
        self.mock_sheets_service.get_pending_leads.side_effect = Exception("Test error")
        
        # Call method
        result = self.interface.get_pending_leads()
        
        # Assertions
        self.assertEqual(result['pending_count'], 0)
        self.assertEqual(result['pending_leads'], [])
        self.assertIn('error', result)
    
    def test_log_message(self):
        """Test log message functionality"""
        # Call method
        result = self.interface.log_message("Test message")
        
        # Assertions
        self.assertIn("Test message", result)
        self.assertEqual(len(self.interface.logs), 1)
    
    def test_process_leads_already_processing(self):
        """Test process_leads when already processing"""
        # Setup
        self.interface.processing = True
        
        # Call method
        result, message = self.interface.process_leads()
        
        # Assertions
        self.assertEqual(message, "Already processing leads...")
        self.assertEqual(self.mock_sheets_service.get_pending_leads.call_count, 1)
    
    def test_process_leads_success(self):
        """Test successful lead processing"""
        # Setup mocks
        mock_leads = [
            {
                'CONTACT_PERSON': 'Test User',
                'CONTACT_EMAIL': 'test@example.com'
            }
        ]
        self.mock_sheets_service.get_pending_leads.return_value = mock_leads
        self.mock_agent_service.process_lead.return_value = True
        
        # Call method
        result, _ = self.interface.process_leads()
        
        # Assertions
        self.assertEqual(result['pending_count'], 1)
        self.assertEqual(self.mock_sheets_service.get_pending_leads.call_count, 2)
        self.mock_agent_service.process_lead.assert_called_once_with(mock_leads[0])
    
    def test_process_leads_error(self):
        """Test error handling in process_leads"""
        # Setup mock
        self.mock_sheets_service.get_pending_leads.side_effect = Exception("Test error")
        
        # Call method
        result, message = self.interface.process_leads()
        
        # Assertions
        self.assertIn('error', result)
        self.assertIn('Test error', message)
        self.assertFalse(self.interface.processing)
    
    def test_create_ui(self):
        """Test UI creation"""
        # Call method
        ui = self.interface.create_ui()
        
        # Assertions
        self.assertIsInstance(ui, gr.Blocks)
        # Add more specific UI element checks if needed

if __name__ == '__main__':
    unittest.main() 