#!/usr/bin/env python3
"""Test actual VS Code window and button detection."""

import sys
from pathlib import Path

# Add src to path
src_path = str(Path(__file__).parent / "src")
sys.path.insert(0, src_path)

import subprocess
import time

from core.config_manager import ConfigManager
from core.window_detector import WindowDetector


def test_vs_code_detection():
    """Test if we can detect VS Code windows and their content."""
    print("🔍 Testing VS Code Window Detection...")

    # Initialize components
    config_manager = ConfigManager()
    window_detector = WindowDetector()

    print("\n1. Looking for VS Code windows...")
    windows = window_detector.get_vscode_windows()

    if not windows:
        print("❌ No VS Code windows found!")
        print("Please make sure VS Code is running with a Copilot Chat session.")
        return False

    print(f"✅ Found {len(windows)} VS Code window(s)")

    for i, window in enumerate(windows, 1):
        print(f"\n   Window {i}:")
        print(f"   Title: {window.title}")
        print(f"   Size: {window.width}x{window.height}")
        print(f"   Position: ({window.x}, {window.y})")
        print(f"   Window ID: {window.window_id}")

    print("\n2. Checking window content for Continue buttons...")

    # Try to find actual button text using xdotool or wmctrl
    for window in windows:
        print(f"\n   Analyzing window: {window.title[:50]}...")

        # Try to get window text content using xdotool
        try:
            # Get window properties
            result = subprocess.run(
                ["xprop", "-id", str(window.window_id)], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                props = result.stdout.lower()
                if any(keyword in props for keyword in ["continue", "chat", "copilot"]):
                    print("   🎯 Window contains chat/continue-related content!")
                else:
                    print("   ⚠️  No continue/chat keywords found in window properties")
            else:
                print("   ⚠️  Could not read window properties")

        except Exception as e:
            print(f"   ⚠️  Error reading window content: {e}")

    print("\n3. Testing alternative detection methods...")

    # Test if we can find Continue buttons using text searching
    try:
        # Use xdotool to search for text in all windows
        result = subprocess.run(
            ["xdotool", "search", "--name", ".*[Cc]ontinue.*"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0 and result.stdout.strip():
            window_ids = result.stdout.strip().split("\n")
            print(f"   🎯 Found {len(window_ids)} windows with 'Continue' in title/content")
            for wid in window_ids:
                if wid.strip():
                    try:
                        # Get window title
                        title_result = subprocess.run(
                            ["xdotool", "getwindowname", wid.strip()],
                            capture_output=True,
                            text=True,
                            timeout=3,
                        )
                        if title_result.returncode == 0:
                            title = title_result.stdout.strip()
                            print(f"      Window {wid}: {title}")
                    except:
                        pass
        else:
            print("   ❌ No windows found with 'Continue' text")

    except Exception as e:
        print(f"   ⚠️  Text search failed: {e}")

    print("\n4. Testing manual button detection...")

    # Try to simulate what a real detection would do
    try:
        # Look for typical VS Code chat button locations
        for window in windows:
            if "code" in window.title.lower():
                print(f"   Testing VS Code window: {window.title[:30]}...")

                # Calculate likely button positions (bottom of chat area)
                # VS Code typically has Continue buttons in the bottom-right of chat
                likely_x = window.x + window.width - 150  # 150px from right edge
                likely_y = window.y + window.height - 100  # 100px from bottom

                print(f"   Likely Continue button position: ({likely_x}, {likely_y})")
                print("   (This is where automation would attempt to click)")

    except Exception as e:
        print(f"   ⚠️  Button position calculation failed: {e}")

    return True


def test_click_simulation():
    """Test if we can simulate clicks without screenshots."""
    print("\n🖱️  Testing Click Simulation...")

    try:
        import pyautogui

        # Just test if we can move mouse (don't actually click)
        current_pos = pyautogui.position()
        print(f"   Current mouse position: {current_pos}")
        print("   ✅ Mouse control available")
        return True
    except Exception as e:
        print(f"   ❌ Mouse control failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("VS Code Continue Button Detection Test")
    print("=" * 60)

    # Test VS Code detection
    vs_code_ok = test_vs_code_detection()

    # Test click capability
    click_ok = test_click_simulation()

    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"VS Code Detection: {'✅ Working' if vs_code_ok else '❌ Failed'}")
    print(f"Click Simulation:  {'✅ Working' if click_ok else '❌ Failed'}")

    if vs_code_ok and click_ok:
        print("\n🎉 Basic detection capabilities are working!")
        print("The issue is likely in the screenshot-based button detection.")
        print("Recommendation: Implement coordinate-based clicking for known button positions.")
    else:
        print("\n⚠️  There are fundamental issues with the detection system.")

    print("=" * 60)
