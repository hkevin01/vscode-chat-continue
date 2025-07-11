#!/usr/bin/env python3
"""
Quick test to verify MainWindow class exists and can be imported.
"""

import os
import sys
from pathlib import Path

# Set up environment
os.environ['DISPLAY'] = ':0'
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_mainwindow():
    """Test MainWindow import and creation."""
    try:
        print("Testing MainWindow class...")
        
        # Test import
        from src.gui.main_window import MainWindow
        print("✅ MainWindow imported successfully")
        
        # Test basic instantiation (without actually showing)
        from PyQt6.QtWidgets import QApplication
        app = QApplication([])
        
        # Test creation
        window = MainWindow()
        print("✅ MainWindow created successfully")
        
        # Test that menu bar exists
        menubar = window.menuBar()
        actions = menubar.actions()
        print(f"✅ Menu bar has {len(actions)} menus")
        
        for action in actions:
            print(f"   - {action.text()}")
        
        print("\n✅ SUCCESS: MainWindow class is properly defined and functional!")
        print("The 'NameError: name 'MainWindow' is not defined' should be fixed.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_mainwindow()
    if success:
        print("\n🎉 GUI should now work properly!")
        print("Run: DISPLAY=:0 python src/gui/main_window.py")
    else:
        print("\n❌ There are still issues to fix.")
