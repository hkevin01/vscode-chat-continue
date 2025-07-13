#!/usr/bin/env python3
"""
Test script to verify beep suppression is working during screenshot capture.
"""

import os
import subprocess
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.config_manager import ConfigManager
from src.utils.screen_capture import ScreenCapture


def disable_system_bell():
    """Disable system bell using multiple methods."""
    print("🔇 Disabling system bell...")
    
    try:
        # Method 1: setterm
        os.system('setterm -blength 0 2>/dev/null || true')
        print("   ✓ setterm bell disabled")
    except Exception as e:
        print(f"   ✗ setterm failed: {e}")
    
    try:
        # Method 2: xset
        result = subprocess.run(['xset', 'b', 'off'], 
                              capture_output=True, check=False)
        if result.returncode == 0:
            print("   ✓ X11 bell disabled")
        else:
            print(f"   ✗ X11 bell disable failed: {result.stderr.decode()}")
    except Exception as e:
        print(f"   ✗ xset failed: {e}")
    
    # Method 3: Environment variables
    os.environ.update({
        'TERM_BELL': 'off',
        'PULSE_DISABLE': '1',
        'ALSA_DISABLE': '1',
        'GNOME_SCREENSHOT_DISABLE': '1',
        'NO_GNOME_SCREENSHOT': '1'
    })
    print("   ✓ Environment variables set")


def test_screenshot_capture():
    """Test screenshot capture to see if beeps occur."""
    print("\n📸 Testing screenshot capture...")
    
    # Initialize screen capture
    capture = ScreenCapture()
    
    # Test 1: Full screen capture
    print("   Testing full screen capture...")
    full_screen = capture.capture_screen()
    if full_screen:
        print(f"   ✓ Full screen captured: {full_screen.size}")
    else:
        print("   ✗ Full screen capture failed")
    
    # Test 2: Region capture
    print("   Testing region capture...")
    region = capture.capture_region(100, 100, 400, 300)
    if region:
        print(f"   ✓ Region captured: {region.size}")
    else:
        print("   ✗ Region capture failed")
    
    # Test 3: Multiple rapid captures (stress test)
    print("   Testing rapid captures (should be silent)...")
    for i in range(3):
        print(f"     Capture {i+1}/3...")
        test_region = capture.capture_region(50 + i*10, 50 + i*10, 200, 150)
        if test_region:
            print(f"       ✓ Size: {test_region.size}")
        else:
            print("       ✗ Failed")


def main():
    """Main test function."""
    print("🔇 Beep Suppression Test")
    print("=" * 40)
    
    print("📋 Before running this test:")
    print("   • Listen for any beeps/sounds during capture")
    print("   • The automation should be completely silent")
    print("   • If you hear beeps, the suppression isn't working")
    print()
    
    # Disable system bell
    disable_system_bell()
    
    # Test screenshot captures
    test_screenshot_capture()
    
    print("\n✅ Test completed!")
    print("💡 If you heard any beeps during the test, please report it.")
    print("   The automation should now run silently.")


if __name__ == "__main__":
    main()
