#!/usr/bin/env python3
"""
Coordinate-based Continue button clicking (fallback when OCR fails)
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def coordinate_based_continue_clicking():
    """Click Continue buttons using coordinate estimation"""
    try:
        import pyautogui

        from core.click_automator import ClickAutomator
        from core.window_detector import WindowDetector
        
        print("Using coordinate-based Continue button detection...")
        
        # Get VS Code windows
        detector = WindowDetector()
        windows = detector.get_vscode_windows()
        print(f"Found {len(windows)} VS Code windows")
        
        if not windows:
            print("No VS Code windows found")
            return
        
        automator = ClickAutomator()
        
        for i, window in enumerate(windows):
            print(f"Processing window {i+1}: {window.title}")
            
            # Calculate likely Continue button positions
            # Typically in bottom-right area of chat panel
            possible_positions = [
                # Bottom right area (common for Continue buttons)
                (window.x + window.width - 100, window.y + window.height - 50),
                (window.x + window.width - 150, window.y + window.height - 50),
                (window.x + window.width - 200, window.y + window.height - 50),
                
                # Middle right area
                (window.x + window.width - 100, window.y + window.height // 2),
                (window.x + window.width - 150, window.y + window.height // 2),
                
                # Chat area bottom
                (window.x + window.width // 2, window.y + window.height - 100),
                (window.x + window.width // 2 + 100, window.y + window.height - 100),
            ]
            
            print(f"Trying {len(possible_positions)} potential Continue button locations...")
            
            for j, (x, y) in enumerate(possible_positions):
                # Check if coordinates are reasonable
                if (0 <= x <= 3000 and 0 <= y <= 2000):  # Reasonable screen bounds
                    print(f"  Trying position {j+1}: ({x}, {y})")
                    
                    # In dry-run mode, just log what we would click
                    print(f"    Would click at ({x}, {y})")
                    
                    # Uncomment to actually click:
                    # automator.click_button_at(x, y)
                    
                else:
                    print(f"  Skipping invalid position: ({x}, {y})")
        
        print("Coordinate-based clicking complete")
        
    except Exception as e:
        print(f"Coordinate-based clicking failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    coordinate_based_continue_clicking()
