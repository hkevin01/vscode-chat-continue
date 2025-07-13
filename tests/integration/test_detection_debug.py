#!/usr/bin/env python3
"""
Quick test to see what buttons are being detected and why search buttons might be clicked.
"""

import logging

from src.core.automation_engine import AutomationEngine
from src.core.config_manager import ConfigManager

# Set up logging to see what's happening
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

# Create config manager
config = ConfigManager()
config.set('automation.dry_run', True)  # Don't actually click anything

# Create automation engine
engine = AutomationEngine(config)

print("🔍 Testing current button detection...")
print("=" * 60)

# Get VS Code windows
windows = engine.window_detector.get_vscode_windows()
print(f"Found {len(windows)} VS Code windows")

for i, window in enumerate(windows):
    print(f"\nWindow {i+1}: {window.title}")
    print(f"  Position: ({window.x}, {window.y})")
    print(f"  Size: {window.width}x{window.height}")
    
    # Capture screenshot
    image = engine.screen_capture.capture_window(
        window.window_id, window.x, window.y, window.width, window.height
    )
    
    if image:
        print(f"  📸 Captured screenshot: {image.width}x{image.height}")
        
        # Find buttons
        buttons = engine.button_finder.find_continue_buttons(image, window.x, window.y)
        print(f"  🔍 Found {len(buttons)} button candidates:")
        
        for j, button in enumerate(buttons):
            print(f"    {j+1}. Method: {button.method}")
            print(f"       Text: '{button.text}'")
            print(f"       Position: ({button.x}, {button.y})")
            print(f"       Size: {button.width}x{button.height}")
            print(f"       Confidence: {button.confidence:.2f}")
            print(f"       Center: ({button.center_x}, {button.center_y})")
            print()
    else:
        print("  ❌ Failed to capture screenshot")

print("\n🎯 Test complete!")
