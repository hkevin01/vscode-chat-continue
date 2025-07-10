"""Basic test to verify the testing setup."""

import sys
import unittest
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestBasic(unittest.TestCase):
    """Basic test to verify testing setup."""
    
    def test_basic_functionality(self):
        """Test basic Python functionality."""
        self.assertEqual(1 + 1, 2)
        self.assertTrue(True)
        self.assertFalse(False)
    
    def test_path_setup(self):
        """Test that project paths are set up correctly."""
        self.assertTrue(project_root.exists())
        self.assertTrue((project_root / 'src').exists())
        self.assertTrue((project_root / 'src' / 'core').exists())
    
    def test_imports(self):
        """Test that core modules can be imported."""
        try:
            from src.core.automation_engine import AutomationEngine
            from src.core.config_manager import ConfigManager
            self.assertTrue(True, "Imports successful")
        except ImportError as e:
            self.fail(f"Import failed: {e}")


if __name__ == '__main__':
    print("Running basic tests...")
    unittest.main(verbosity=2)
