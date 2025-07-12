#!/usr/bin/env python3
"""
Simple test to manually click where the Continue button should be based on your screenshot.
"""

import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.click_automator import ClickAutomator


def manual_click_test():
    """Manually click where the Continue button appears to be in your screenshot."""
    print("🎯 Manual Continue Button Click Test")
    print("=" * 40)
    
    # From your screenshot, the Continue button appears to be approximately at:
    # - Right side of the screen 
    # - In the Copilot chat area
    # Let's try some likely coordinates
    
    click_automator = ClickAutomator()
    
    # Coordinates to try (based on typical VS Code layout)
    # These are rough estimates from where Continue buttons typically appear
    test_coordinates = [
        (1400, 500),  # Right side, middle height
        (1350, 450),  # Slightly left and up
        (1450, 550),  # Slightly right and down
        (1380, 480),  # Another variation
    ]
    
    print("🖱️  Testing manual clicks at estimated Continue button locations...")
    print("   (Watch your screen to see if any clicks hit the button)")
    
    for i, (x, y) in enumerate(test_coordinates):
        print(f"\n   Attempt {i+1}: Clicking at ({x}, {y})")
        
        try:
            result = click_automator.click(x, y, restore_position=True)
            if result.success:
                print(f"   ✅ Click successful using {result.method}")
            else:
                print(f"   ❌ Click failed: {result.error}")
        except Exception as e:
            print(f"   ❌ Click error: {e}")
        
        # Wait between clicks to see the effect
        time.sleep(2)
    
    print("\n💡 If any of these clicks worked, we know clicking is functional!")
    print("   The issue is then just with button detection coordinates.")

if __name__ == "__main__":
    manual_click_test()
