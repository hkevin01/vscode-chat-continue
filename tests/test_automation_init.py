#!/usr/bin/env python3
"""Simple direct test of the automation engine."""

import os
import sys
from pathlib import Path

# Ensure proper paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

print(f"Testing from: {project_root}")
print(f"Python version: {sys.version}")

try:
    # Import and setup
    from src.utils.gnome_screenshot_fix import setup_screenshot_environment
    setup_screenshot_environment()
    print("✓ gnome-screenshot fix applied")
    
    from src.core.config_manager import ConfigManager
    config_manager = ConfigManager()
    print("✓ ConfigManager initialized")
    
    from src.core.automation_engine import AutomationEngine
    automation_engine = AutomationEngine(config_manager)
    print("✓ AutomationEngine initialized")
    
    # Test basic functionality
    print("\n--- Testing basic functionality ---")
    print(f"Config loaded: {config_manager.config}")
    
    print("\n--- All imports and initialization successful! ---")
    print("The automation engine should now be ready to run.")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
