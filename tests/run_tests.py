import unittest
import sys
from pathlib import Path

def run_tests():
    """Run all tests in the tests directory"""
    # Add src directory to Python path
    src_path = str(Path(__file__).parent.parent / 'src')
    if src_path not in sys.path:
        sys.path.append(src_path)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests()) 