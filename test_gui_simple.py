#!/usr/bin/env python3
"""
Simple GUI test to check PyQt6 and display
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_gui():
    """Test if GUI can be displayed"""
    try:
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import (
            QApplication,
            QLabel,
            QMainWindow,
            QVBoxLayout,
            QWidget,
        )
        
        print("PyQt6 imported successfully")
        
        # Create application
        app = QApplication(sys.argv)
        
        # Create a simple test window
        window = QMainWindow()
        window.setWindowTitle("Test Window")
        window.setGeometry(300, 300, 400, 200)
        
        # Add a simple widget
        central_widget = QWidget()
        layout = QVBoxLayout()
        label = QLabel("GUI Test - If you see this, PyQt6 is working!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        central_widget.setLayout(layout)
        window.setCentralWidget(central_widget)
        
        print("Test window created")
        
        # Show window
        window.show()
        print("Window shown")
        
        # Run for a few seconds then close
        import time
        time.sleep(3)
        print("Test completed")
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"GUI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_display():
    """Test display environment"""
    import os
    print("Display environment:")
    print(f"  DISPLAY: {os.environ.get('DISPLAY', 'Not set')}")
    print(f"  XDG_SESSION_TYPE: {os.environ.get('XDG_SESSION_TYPE', 'Not set')}")
    print(f"  WAYLAND_DISPLAY: {os.environ.get('WAYLAND_DISPLAY', 'Not set')}")

if __name__ == "__main__":
    print("=== GUI Test ===")
    test_display()
    print("\nTesting PyQt6 GUI...")
    if test_gui():
        print("✅ GUI test passed")
    else:
        print("❌ GUI test failed")
