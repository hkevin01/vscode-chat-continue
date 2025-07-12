#!/usr/bin/env python3
"""Simple debug script to test import issues."""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Write to a log file so we can see the results
log_file = project_root / "debug_import.log"

try:
    with open(log_file, "w") as f:
        f.write("=== Import Debug Test ===\n")
        f.write(f"Project root: {project_root}\n")
        f.write(f"Python version: {sys.version}\n")
        f.write(f"Python path entries: {sys.path[:5]}\n\n")
        
        f.write("Testing imports...\n")
        
        # Test gnome-screenshot fix
        from src.utils.gnome_screenshot_fix import setup_screenshot_environment
        setup_screenshot_environment()
        f.write("✓ gnome-screenshot fix imported and setup\n")
        
        # Test config manager
        from src.core.config_manager import ConfigManager
        config_manager = ConfigManager()
        f.write("✓ ConfigManager imported and initialized\n")
        
        # Test automation engine - this is where the original error occurred
        from src.core.automation_engine import AutomationEngine
        f.write("✓ AutomationEngine imported successfully\n")
        
        automation_engine = AutomationEngine(config_manager)
        f.write("✓ AutomationEngine initialized successfully\n")
        
        # Test main module
        import src.main
        f.write("✓ src.main imported successfully\n")
        
        f.write("\n=== ALL TESTS PASSED ===\n")
        
    print(f"Debug completed. Results written to: {log_file}")
    
except Exception as e:
    with open(log_file, "a") as f:
        f.write(f"\n✗ ERROR: {e}\n")
        import traceback
        f.write(traceback.format_exc())
    print(f"Debug failed. Error logged to: {log_file}")
