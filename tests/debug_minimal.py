#!/usr/bin/env python3
"""Ultra simple test to find the hanging issue."""

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

print("Starting test...")

try:
    print("1. Testing imports...")
    from src.core.config_manager import ConfigManager
    print("   ✅ ConfigManager imported")
    
    from src.core.window_detector import WindowDetector  
    print("   ✅ WindowDetector imported")
    
    print("2. Testing config creation...")
    config = ConfigManager()
    print("   ✅ Config created")
    
    print("3. Testing window detector creation...")
    detector = WindowDetector()
    print("   ✅ WindowDetector created")
    
    print("4. Testing window detection...")
    windows = detector.get_vscode_windows()
    print(f"   ✅ Found {len(windows)} windows")
    
    for window in windows:
        print(f"     - {window.title[:50]}...")
    
    print("5. All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
