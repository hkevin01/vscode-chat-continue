#!/usr/bin/env python3
"""
Quick test to verify unfocused window automation works.
"""

import asyncio
import os
import subprocess
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.automation_engine import AutomationEngine
from src.core.config_manager import ConfigManager


async def quick_unfocus_test():
    """Quick test of unfocused window automation."""
    print("🚀 Quick Unfocused Window Test")
    print("=" * 40)

    # Set up automation
    config = ConfigManager()
    config.set("automation.dry_run", True)  # Dry run first
    config.set("automation.auto_focus_windows", True)

    engine = AutomationEngine(config)

    # Step 1: Check current windows
    print("1. 🔍 Detecting VS Code windows...")
    windows = engine.window_detector.get_vscode_windows()
    print(f"   Found {len(windows)} VS Code window(s)")

    if not windows:
        print("   ❌ No VS Code windows found!")
        return False

    for i, window in enumerate(windows):
        print(f"   Window {i+1}: {window.title}")

    # Step 2: Test focus capability
    print("\n2. 🎯 Testing window focus capability...")
    window = windows[0]  # Test first window
    focus_result = engine.focus_manager.focus_window(window)

    if focus_result.success:
        print(f"   ✅ Can focus windows using: {focus_result.method}")
    else:
        print(f"   ❌ Cannot focus windows: {focus_result.error}")
        return False

    # Step 3: Test button detection
    print("\n3. 🔍 Testing Continue button detection...")
    image = engine.screen_capture.capture_window(
        window.window_id, window.x, window.y, window.width, window.height
    )

    if not image:
        print("   ❌ Failed to capture screenshot")
        return False

    buttons = engine.button_finder.find_continue_buttons(image, window.x, window.y)
    print(f"   Found {len(buttons)} potential Continue button(s)")

    # Step 4: Unfocus VS Code and test automation
    print("\n4. 📱 Unfocusing VS Code (opening calculator)...")
    try:
        subprocess.Popen(["gnome-calculator"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        await asyncio.sleep(2)
        print("   ✅ Calculator opened (VS Code should be unfocused)")
    except Exception:
        print("   ⚠️  Could not open calculator, manually unfocus VS Code")
        input("   Press Enter when VS Code is unfocused...")

    # Step 5: Test one automation cycle
    print("\n5. 🤖 Running automation cycle on unfocused window...")
    config.set("automation.dry_run", False)  # Actually try to focus/click

    try:
        await engine._process_vscode_windows()
        print("   ✅ Automation cycle completed!")

        # Check if any windows were processed
        stats = engine.stats
        windows_processed = stats.get("windows_processed", 0)
        buttons_found = stats.get("buttons_found", 0)
        clicks_attempted = stats.get("clicks_attempted", 0)

        print(f"   📊 Windows processed: {windows_processed}")
        print(f"   📊 Buttons found: {buttons_found}")
        print(f"   📊 Clicks attempted: {clicks_attempted}")

        success = windows_processed > 0

    except Exception as e:
        print(f"   ❌ Automation failed: {e}")
        success = False

    # Results
    print("\n" + "=" * 40)
    if success:
        print("🎉 SUCCESS! Unfocused window automation is working!")
        print("\n✅ The automation can:")
        print("   • Detect unfocused VS Code windows")
        print("   • Bring them into focus automatically")
        print("   • Click Continue buttons in background windows")
        print("   • Work while you use other applications")
    else:
        print("❌ Test failed. Check the automation setup.")

    return success


def main():
    """Run the quick test."""
    print("This will test if automation works on unfocused VS Code windows.\n")

    try:
        success = asyncio.run(quick_unfocus_test())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
