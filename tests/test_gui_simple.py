#!/usr/bin/env python3
"""
Simple GUI test to identify menu issues.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set DISPLAY
os.environ['DISPLAY'] = ':0'

print("Testing GUI import...")
try:
    from PyQt6.QtWidgets import QApplication, QMainWindow
    print("✅ PyQt6 import successful")
    
    # Create a minimal application to test
    app = QApplication(sys.argv)
    
    print("✅ QApplication created")
    
    # Create a test window
    window = QMainWindow()
    window.setWindowTitle("Test Menu Window")
    
    # Add a menu bar
    menubar = window.menuBar()
    file_menu = menubar.addMenu('&File')
    file_menu.addAction('&Test Action')
    
    print("✅ Menu bar created")
    
    window.show()
    print("✅ Window shown")
    
    # Don't actually run the event loop, just test setup
    print("Menu test successful - GUI components working")
    
except Exception as e:
    print(f"❌ GUI test failed: {e}")
    import traceback
    traceback.print_exc()
