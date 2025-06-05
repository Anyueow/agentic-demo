"""
Worksheet Standardizer Agent

This agent is responsible for:
1. Reading current worksheet headers
2. Mapping them to standard column names
3. Updating the worksheet with standardized headers
4. Ensuring data alignment with new headers
"""

from typing import Dict, List, Optional
from ..services.sheets_service import GoogleSheetsService
from ..core.config import Config
import time

class WorksheetStandardizer:
    """Agent for standardizing worksheet column names and structure"""
    
    def __init__(self, config: Config):
        self.config = config
        self.sheets_service = GoogleSheetsService(config)
    
    def test_connection(self) -> Dict:
        """Test connection to the Google Sheet and print worksheet title and headers"""
        try:
            worksheet = self.sheets_service.worksheet
            if not worksheet:
                print("[DEBUG] Worksheet not found.")
                return {"status": "error", "message": "Worksheet not found"}
            print(f"[DEBUG] Connected to worksheet: {worksheet.title}")
            headers = worksheet.row_values(1)
            print(f"[DEBUG] Current headers: {headers}")
            return {"status": "success", "worksheet_title": worksheet.title, "headers": headers}
        except Exception as e:
            print(f"[DEBUG] Error connecting to worksheet: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def standardize_worksheet(self) -> Dict:
        """Overwrite the worksheet headers with the required standard headers"""
        try:
            worksheet = self.sheets_service.worksheet
            if not worksheet:
                print("[DEBUG] Worksheet not found.")
                return {"status": "error", "message": "Worksheet not found"}
            required_headers = [
                "COMPANY",
                "CONTACT_PERSON",
                "CONTACT_DESIGNATION",
                "CONTACT_NUMBER",
                "CONTACT_EMAIL",
                "LOCATION",
                "INDUSTRY",
                "STATUS",
                "ACTION",
                "REMARKS",
                "FOLLOW_UP_DATE"
            ]
            print(f"[DEBUG] Overwriting headers with: {required_headers}")
            worksheet.update('A1', [required_headers])
            print("[DEBUG] Worksheet headers overwritten.")
            return {
                "status": "success",
                "message": "Worksheet headers overwritten with required standard headers.",
                "new_headers": required_headers
            }
        except Exception as e:
            print(f"[DEBUG] Error overwriting worksheet headers: {str(e)}")
            return {
                "status": "error",
                "message": f"Error overwriting worksheet headers: {str(e)}"
            }
    
    def validate_worksheet(self) -> Dict:
        """Validate worksheet structure and headers"""
        try:
            worksheet = self.sheets_service.worksheet
            if not worksheet:
                return {"status": "error", "message": "Worksheet not found"}
            
            # Get current headers
            all_values = worksheet.get_all_values()
            if not all_values:
                return {"status": "error", "message": "Worksheet is empty"}
            
            current_headers = all_values[0]
            
            # Check for duplicate headers
            duplicates = set([h for h in current_headers if current_headers.count(h) > 1])
            
            # Check for required columns
            required_columns = self.config.get_required_columns()
            missing_columns = [col for col in required_columns if not any(
                self.config.get_standard_column_name(h) == col for h in current_headers
            )]
            
            return {
                "status": "success",
                "has_duplicates": len(duplicates) > 0,
                "duplicate_headers": list(duplicates),
                "missing_columns": missing_columns,
                "current_headers": current_headers
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error validating worksheet: {str(e)}"
            }
    
    def fix_worksheet_structure(self) -> Dict:
        """Fix worksheet structure issues"""
        try:
            # First validate
            validation = self.validate_worksheet()
            if validation["status"] == "error":
                return validation
            
            # If no issues, return success
            if not validation["has_duplicates"] and not validation["missing_columns"]:
                return {
                    "status": "success",
                    "message": "Worksheet structure is already correct"
                }
            
            # Standardize headers
            standardization = self.standardize_worksheet()
            if standardization["status"] == "error":
                return standardization
            
            # Add missing columns if any
            if validation["missing_columns"]:
                worksheet = self.sheets_service.worksheet
                current_headers = worksheet.row_values(1)
                
                # Add missing columns at the end
                for col in validation["missing_columns"]:
                    if col not in current_headers:
                        last_col = len(current_headers) + 1
                        worksheet.update_cell(1, last_col, col)
                        time.sleep(1)  # Avoid rate limiting
            
            return {
                "status": "success",
                "message": "Worksheet structure fixed successfully",
                "changes": {
                    "standardized": standardization["changes"],
                    "added_columns": validation["missing_columns"]
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error fixing worksheet structure: {str(e)}"
            } 