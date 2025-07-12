#!/usr/bin/env python3
"""Test script to verify imports work correctly."""

import sys
from pathlib import Path

# Add the project root to Python path for proper imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

try:
    from src.utils.gnome_screenshot_fix import setup_screenshot_environment
    setup_screenshot_environment()
    
    from src.core.automation_engine import AutomationEngine
    from src.core.config_manager import ConfigManager
    from src.utils.logger import setup_logging
    
    print("✓ All imports successful!")
    
    # Test basic initialization
    config_manager = ConfigManager()
    print("✓ ConfigManager initialized")
    
    automation_engine = AutomationEngine(config_manager)
    print("✓ AutomationEngine initialized")
    
    print("All components working correctly!")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Other error: {e}")
    sys.exit(1)
