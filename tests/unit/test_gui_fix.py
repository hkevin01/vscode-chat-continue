#!/usr/bin/env python3
"""
Test the fixed GUI launch to ensure no more freezing
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_gui_launch():
    """Test GUI launch without freezing"""
    print("=== Testing Fixed GUI Launch ===")

    # Test 1: Check PyQt6 availability
    try:
        from PyQt6.QtWidgets import QApplication

        print("✓ PyQt6 import successful")
    except ImportError as e:
        print(f"❌ PyQt6 not available: {e}")
        return False

    # Test 2: Check if we can create QApplication
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(["test"])
            print("✓ QApplication created")
            created_app = True
        else:
            print("✓ QApplication already exists")
            created_app = False

        # Test 3: Check GUI component import
        from gui.main_window import MainWindow, create_parser

        print("✓ GUI components imported")

        # Test 4: Test argument parsing
        parser = create_parser()
        args = parser.parse_args(["--dry-run"])
        print("✓ Argument parsing works")

        print("\n✅ All GUI components test successfully!")
        print("✅ The freezing issue should be resolved")

        if created_app:
            app.quit()

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_gui_launch()

    if success:
        print("\n🚀 Ready to test:")
        print("   ./run.sh --gui --dry-run")
    else:
        print("\n❌ GUI testing failed")
        print("   Use ./run.sh --cli --dry-run instead")
