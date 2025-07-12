#!/usr/bin/env python3
"""
Relaxed automation - less restrictive filtering for Continue button detection.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.button_finder import ButtonFinder
from scripts.continuous_automation import ContinuousAutomation


def main():
    """Run automation with relaxed filtering."""
    print("🔧 RELAXED AUTOMATION: Less Restrictive Continue Button Detection")
    print("=" * 70)
    print("⚠️  This uses more permissive filtering and may click more buttons")
    print("✅ But it's more likely to find Continue buttons")
    print()
    
    # Monkey patch the button finder to use relaxed filtering
    original_filter = ButtonFinder._is_in_chat_panel_area
    
    def relaxed_chat_filter(self, x, y, image_width, image_height):
        """More permissive chat panel detection."""
        # Right 50% of screen (instead of 45%)
        right_area = x > image_width * 0.5
        
        # Bottom 50% of screen (instead of 25%)  
        bottom_area = y > image_height * 0.5
        
        # Avoid very top (menu bars)
        not_top = y > image_height * 0.1
        
        return right_area and bottom_area and not_top
    
    ButtonFinder._is_in_chat_panel_area = relaxed_chat_filter
    
    try:
        print("🚀 Starting relaxed automation...")
        print("   - Targeting computer-vision window")
        print("   - Using relaxed position filtering")
        print("   - Press Ctrl+C to stop")
        print()
        
        automation = ContinuousAutomation()
        automation.run()
        
    finally:
        # Restore original filter
        ButtonFinder._is_in_chat_panel_area = original_filter
        print("🔧 Restored original filtering")


if __name__ == "__main__":
    main()
