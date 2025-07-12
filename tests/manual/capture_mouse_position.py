#!/usr/bin/env python3
"""
Mouse position capture tool.
Hover over the Continue button and press Enter to capture coordinates.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.click_automator import ClickAutomator


def main():
    print("🖱️ Mouse Position Capture Tool")
    print("=" * 40)
    print()
    print("Instructions:")
    print("1. Hover your mouse over the Continue button in VS Code")
    print("2. Press Enter to capture the current mouse position")
    print("3. The coordinates will be saved and tested")
    print()
    
    input("Hover over the Continue button and press Enter...")
    
    # Get current mouse position
    automator = ClickAutomator()
    position = automator.get_mouse_position()
    
    if position:
        x, y = position
        print(f"\n📍 Captured mouse position: ({x}, {y})")
        
        # Save coordinates to file
        coords_file = "tmp/continue_button_coords.txt"
        Path("tmp").mkdir(exist_ok=True)
        
        with open(coords_file, "w") as f:
            f.write(f"{x},{y}\n")
        print(f"💾 Coordinates saved to: {coords_file}")
        
        # Ask if user wants to test click immediately
        test_now = input("\nTest click at this position now? (y/n): ").lower().strip()
        
        if test_now == 'y':
            print(f"\n🎯 Testing click at ({x}, {y})...")
            
            # Small delay to let user move mouse away if needed
            print("Clicking in 2 seconds...")
            time.sleep(2)
            
            result = automator.click(x, y)
            
            if result.success:
                print("✅ Click successful!")
                print("🔇 (No audio feedback - beeps disabled)")
                print("\nCheck VS Code to see if the Continue button was clicked!")
            else:
                print(f"❌ Click failed: {result}")
        else:
            print("\nCoordinates saved. You can test later with:")
            print(f"python -c \"")
            print(f"import sys; sys.path.insert(0, 'src')")
            print(f"from core.click_automator import ClickAutomator")
            print(f"automator = ClickAutomator()")
            print(f"result = automator.click({x}, {y})")
            print(f"print('Success!' if result.success else f'Failed: {{result}}')\"")
    
    else:
        print("❌ Could not get mouse position")

if __name__ == "__main__":
    main()
