"""
Script to standardize worksheet column names and structure
"""

from src.core.config import Config
from src.agents.worksheet_standardizer import WorksheetStandardizer
import json

def main():
    # Initialize configuration
    config = Config()
    
    # Validate configuration
    error = config.validate()
    if error:
        print(f"Configuration error: {error}")
        return
    
    # Initialize standardizer
    standardizer = WorksheetStandardizer(config)
    
    # Test connection and print headers
    print("\nTesting connection to Google Sheet...")
    conn_result = standardizer.test_connection()
    print(json.dumps(conn_result, indent=2))
    if conn_result["status"] == "error":
        print(f"Error: {conn_result['message']}")
        return
    
    # First validate the worksheet
    print("\nValidating worksheet structure...")
    validation = standardizer.validate_worksheet()
    print(json.dumps(validation, indent=2))
    
    if validation["status"] == "error":
        print(f"Error validating worksheet: {validation['message']}")
        return
    
    # If there are issues, fix them
    if validation["has_duplicates"] or validation["missing_columns"]:
        print("\nFixing worksheet structure...")
        result = standardizer.fix_worksheet_structure()
        print(json.dumps(result, indent=2))
        
        if result["status"] == "error":
            print(f"Error fixing worksheet: {result['message']}")
            return
        
        print("\nWorksheet structure fixed successfully!")
    else:
        print("\nWorksheet structure is already correct!")

if __name__ == "__main__":
    main() 