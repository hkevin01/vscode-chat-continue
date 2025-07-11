#!/usr/bin/env python3
"""
Menu functionality diagnostic that writes to a file.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set DISPLAY
os.environ['DISPLAY'] = ':0'

def test_menu_functionality():
    """Test menu functionality and write results to file."""
    results = []
    results.append("=== Menu Functionality Test ===")
    results.append(f"DISPLAY: {os.environ.get('DISPLAY', 'Not set')}")
    
    try:
        results.append("\n1. Testing PyQt6 imports...")
        from PyQt6.QtWidgets import QApplication, QMainWindow
        results.append("   ✅ PyQt6 imports successful")
        
        results.append("\n2. Testing application creation...")
        app = QApplication(sys.argv)
        results.append("   ✅ QApplication created")
        
        results.append("\n3. Testing window creation...")
        window = QMainWindow()
        window.setWindowTitle("Menu Test")
        results.append("   ✅ Main window created")
        
        results.append("\n4. Testing menu bar creation...")
        menubar = window.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction('&Test Action')
        results.append("   ✅ Menu bar and actions created")
        
        results.append("\n5. Testing window display...")
        window.show()
        results.append("   ✅ Window shown (GUI components working)")
        
        # Don't run the event loop, just test setup
        results.append("\n✅ All menu tests passed - GUI functionality is working!")
        
    except Exception as e:
        results.append(f"\n❌ Menu test failed: {e}")
        import traceback
        results.append(traceback.format_exc())
    
    # Write results to tmp directory
    tmp_dir = Path(__file__).parent.parent / "tmp"
    tmp_dir.mkdir(exist_ok=True)
    output_file = tmp_dir / "menu_test_results.txt"
    
    with open(output_file, 'w') as f:
        f.write('\n'.join(results))
    
    print(f"Menu test results written to: {output_file}")
    return output_file

if __name__ == '__main__':
    output_file = test_menu_functionality()
    print(f"Check {output_file} for test results")
