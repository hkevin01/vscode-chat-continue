#!/usr/bin/env python3
"""
Debug import issues
"""

import os
import sys


def test_imports():
    """Test all imports"""
    print("Testing imports...")
    
    # Test basic Python
    print("✓ Python working")
    
    # Test PyQt6
    try:
        import PyQt6
        print("✓ PyQt6 import successful")
        
        from PyQt6.QtWidgets import QApplication
        print("✓ PyQt6.QtWidgets import successful")
        
        from PyQt6.QtCore import QThread, pyqtSignal
        print("✓ PyQt6.QtCore import successful")
        
    except ImportError as e:
        print(f"✗ PyQt6 import failed: {e}")
        return False
    
    # Test our modules
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
    
    try:
        from core.config_manager import ConfigManager
        print("✓ ConfigManager import successful")
        
        from core.automation_engine import AutomationEngine
        print("✓ AutomationEngine import successful")
        
        from utils.logger import setup_logging
        print("✓ Logger import successful")
        
    except ImportError as e:
        print(f"✗ Core module import failed: {e}")
        return False
    
    print("All imports successful!")
    return True

def test_display():
    """Test display environment"""
    print("\nTesting display environment...")
    
    display = os.environ.get('DISPLAY')
    wayland_display = os.environ.get('WAYLAND_DISPLAY')
    xdg_session_type = os.environ.get('XDG_SESSION_TYPE')
    
    print(f"DISPLAY: {display}")
    print(f"WAYLAND_DISPLAY: {wayland_display}")
    print(f"XDG_SESSION_TYPE: {xdg_session_type}")
    
    if not display and not wayland_display:
        print("✗ No display environment detected")
        return False
    
    print("✓ Display environment detected")
    return True

def test_qapplication():
    """Test creating QApplication"""
    print("\nTesting QApplication creation...")
    
    try:
        from PyQt6.QtWidgets import QApplication

        # Try to create QApplication
        app = QApplication([])
        print("✓ QApplication created successfully")
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"✗ QApplication creation failed: {e}")
        return False

if __name__ == '__main__':
    print("=== Import and Display Debug ===")
    
    success = True
    success &= test_imports()
    success &= test_display()
    success &= test_qapplication()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    sys.exit(0 if success else 1)
