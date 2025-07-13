#!/usr/bin/env python3
"""Test coordinate-based button detection."""

import sys
from pathlib import Path

# Add src to path
src_path = str(Path(__file__).parent / "src")
sys.path.insert(0, src_path)

from PIL import Image

from core.button_finder import ButtonFinder
from core.window_detector import WindowDetector


def test_coordinate_detection():
    """Test the coordinate-based fallback detection."""
    print("🎯 Testing Coordinate-Based Button Detection...")
    
    # Initialize components
    button_finder = ButtonFinder()
    window_detector = WindowDetector()
    
    # Get VS Code windows
    windows = window_detector.get_vscode_windows()
    if not windows:
        print("❌ No VS Code windows found!")
        return
    
    print(f"✅ Found {len(windows)} VS Code window(s)")
    
    # Create a mock image (simulating Wayland scenario)
    mock_image = Image.new('RGB', (100, 100), color='black')
    print(f"📸 Created mock image: {mock_image.width}x{mock_image.height}")
    
    # Test button detection on each window
    for i, window in enumerate(windows, 1):
        print(f"\n🔍 Testing window {i}: {window.title[:50]}...")
        print(f"   Window position: ({window.x}, {window.y})")
        print(f"   Window size: {window.width}x{window.height}")
        
        # Find buttons using coordinate fallback
        buttons = button_finder.find_continue_buttons(
            mock_image, window.x, window.y
        )
        
        print(f"   🎯 Found {len(buttons)} coordinate-based buttons:")
        for j, button in enumerate(buttons, 1):
            print(f"      Button {j}: ({button.x}, {button.y}) "
                  f"{button.width}x{button.height}")
            print(f"         Method: {button.method}")
            print(f"         Confidence: {button.confidence}")
            print(f"         Text: {button.text}")
            print(f"         Center: ({button.center_x}, {button.center_y})")

if __name__ == "__main__":
    test_coordinate_detection()
