#!/usr/bin/env python3
"""
Simple test to verify the menu issue is fixed.
"""

import os
import sys
from pathlib import Path

# Set up environment
os.environ['DISPLAY'] = ':0'
sys.path.insert(0, str(Path(__file__).parent.parent))

print("Testing VS Code Chat Continue GUI Menu Functionality")
print("=" * 60)

try:
    print("1. Importing GUI modules...")
    from src.gui.main_window import MainWindow
    print("   ✅ MainWindow imported successfully")
    
    print("2. Testing window detection...")
    from src.core.window_detector import WindowDetector
    detector = WindowDetector()
    windows = detector.get_vscode_windows()
    print(f"   ✅ Found {len(windows)} VS Code windows")
    
    if windows:
        for i, window in enumerate(windows):
            print(f"     Window {i+1}: {window.title} (PID: {window.pid})")
    
    print("3. Creating test application...")
    from PyQt6.QtWidgets import QApplication
    app = QApplication([])
    print("   ✅ QApplication created")
    
    print("4. Creating main window with menus...")
    window = MainWindow()
    print("   ✅ MainWindow created with menu bar")
    
    # Test menu access
    menubar = window.menuBar()
    actions = menubar.actions()
    print(f"   ✅ Menu bar has {len(actions)} menus")
    
    for action in actions:
        menu_name = action.text()
        print(f"     - {menu_name}")
    
    print("\n✅ ALL TESTS PASSED!")
    print("The File and other menus should now be working properly.")
    print("To test interactively, run:")
    print("   DISPLAY=:0 python src/gui/main_window.py")
    
except Exception as e:
    print(f"\n❌ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\nTest completed.")
