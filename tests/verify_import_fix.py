#!/usr/bin/env python3
"""
Replicate the exact import pattern from main.py to verify the fix.
This mimics line 24 in main.py that was causing the error.
"""

import sys
from pathlib import Path

# This replicates the exact setup in main.py
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("Testing the exact import that was failing...")
print("Import path:", sys.path[:3])

try:
    # This was line 24 in main.py that was failing:
    from src.core.automation_engine import AutomationEngine
    print("✅ SUCCESS: AutomationEngine import works!")
    
    # Test a few more critical imports
    from src.core.config_manager import ConfigManager
    print("✅ SUCCESS: ConfigManager import works!")
    
    from src.utils.screen_capture import ScreenCapture
    print("✅ SUCCESS: ScreenCapture import works!")
    
    print("\n🎉 All imports fixed! The relative import error should be resolved.")
    
except ImportError as e:
    print(f"❌ FAILED: {e}")
    
except Exception as e:
    print(f"❌ UNEXPECTED ERROR: {e}")
