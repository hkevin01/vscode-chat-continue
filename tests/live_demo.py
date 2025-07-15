#!/usr/bin/env python3
"""
Live demo of unfocused window automation.
Opens test Continue button and demonstrates automation clicking it
while VS Code is in the background.
"""

import asyncio
import os
import subprocess
import webbrowser

from src.core.automation_engine import AutomationEngine
from src.core.config_manager import ConfigManager


async def run_live_demo():
    """Run a live demonstration of unfocused window automation."""
    print("🎭 LIVE DEMO: Unfocused Window Automation")
    print("=" * 50)

    # Step 1: Open the test Continue button page
    print("1. 📄 Opening test Continue button page...")
    test_file = os.path.abspath("test_continue_button.html")

    if not os.path.exists(test_file):
        print("   ❌ test_continue_button.html not found!")
        print("   Please run this script from the project root directory.")
        return False

    # Open in VS Code
    try:
        subprocess.run(["code", test_file], check=True)
        await asyncio.sleep(3)
        print("   ✅ Test page opened in VS Code")
    except Exception as e:
        print(f"   ❌ Failed to open in VS Code: {e}")
        return False

    # Step 2: Set up automation
    print("\n2. 🤖 Setting up automation...")
    config = ConfigManager()
    config.set("automation.dry_run", False)  # Actually click buttons
    config.set("automation.auto_focus_windows", True)
    config.set("automation.max_clicks_per_window", 1)
    config.set("automation.cycle_delay", 3.0)  # Slower for demo

    engine = AutomationEngine(config)
    print("   ✅ Automation engine ready")

    # Step 3: Show current VS Code windows
    print("\n3. 🔍 Detecting VS Code windows...")
    windows = engine.window_detector.get_vscode_windows()
    print(f"   Found {len(windows)} VS Code window(s):")

    for i, window in enumerate(windows):
        print(f"     {i+1}. {window.title}")
        print(f"        Position: ({window.x}, {window.y})")
        print(f"        Size: {window.width}x{window.height}")

    if not windows:
        print("   ❌ No VS Code windows found!")
        return False

    # Step 4: Open another application to unfocus VS Code
    print("\n4. 📱 Opening browser to put VS Code in background...")
    try:
        webbrowser.open("https://www.google.com")
        await asyncio.sleep(3)
        print("   ✅ Browser opened - VS Code should now be unfocused")
    except Exception:
        print("   ⚠️  Please manually open another application to unfocus VS Code")
        input("   Press Enter when VS Code is in the background...")

    # Step 5: Demonstrate automation
    print("\n5. 🎯 DEMONSTRATION: Watch automation work on unfocused window!")
    print("   The automation will now:")
    print("     • Detect the test Continue button in the background VS Code")
    print("     • Automatically bring VS Code window into focus")
    print("     • Click the Continue button")
    print("     • Return focus to the previous application")
    print()

    input("   Press Enter to start the demonstration...")

    # Run automation cycles
    demo_cycles = 3
    for cycle in range(1, demo_cycles + 1):
        print(f"\n   🔄 Demo Cycle {cycle}/{demo_cycles}")

        # Check if any Continue buttons are available
        buttons_found = 0
        for window in engine.window_detector.get_vscode_windows():
            image = engine.screen_capture.capture_window(
                window.window_id, window.x, window.y, window.width, window.height
            )
            if image:
                buttons = engine.button_finder.find_continue_buttons(image, window.x, window.y)
                buttons_found += len(buttons)

        if buttons_found > 0:
            print(f"     🔍 Found {buttons_found} Continue button(s)")
            print("     🎯 Attempting to focus window and click...")

            # Run one automation cycle
            await engine._process_vscode_windows()

            # Show results
            stats = engine.stats
            clicks = stats.get("clicks_attempted", 0)
            successful = stats.get("clicks_successful", 0)

            if successful > 0:
                print(f"     ✅ Successfully clicked {successful} button(s)!")
                print("     🎉 Demo successful!")
                break
            elif clicks > 0:
                print(f"     ⚠️  Attempted {clicks} clicks but none successful")
            else:
                print("     ℹ️  No clicks attempted")
        else:
            print("     ℹ️  No Continue buttons found")

        if cycle < demo_cycles:
            print(f"     ⏱️  Waiting {config.get('automation.cycle_delay')} seconds...")
            await asyncio.sleep(config.get("automation.cycle_delay"))

    # Step 6: Summary
    print("\n" + "=" * 50)
    print("📊 DEMO RESULTS")

    final_stats = engine.stats
    print(f"Cycles completed: {final_stats.get('cycles_completed', 0)}")
    print(f"Windows processed: {final_stats.get('windows_processed', 0)}")
    print(f"Buttons found: {final_stats.get('buttons_found', 0)}")
    print(f"Clicks attempted: {final_stats.get('clicks_attempted', 0)}")
    print(f"Clicks successful: {final_stats.get('clicks_successful', 0)}")

    success = final_stats.get("clicks_successful", 0) > 0

    if success:
        print("\n🎉 DEMO SUCCESSFUL!")
        print("✅ The automation successfully:")
        print("   • Detected Continue button in unfocused VS Code window")
        print("   • Brought the window into focus automatically")
        print("   • Clicked the Continue button")
        print("   • Worked while other applications were active")
        print("\n💡 This proves the automation can work in the background!")
    else:
        print("\n⚠️  Demo didn't show successful clicking.")
        print("   This might be because:")
        print("   • No actual Continue buttons were present")
        print("   • Button detection needs tuning")
        print("   • Focus management needs adjustment")

    return success


def main():
    """Run the live demo."""
    print("This will demonstrate unfocused window automation live.")
    print("It will open a test page and show automation clicking Continue")
    print("buttons while VS Code is in the background.")
    print()

    try:
        success = asyncio.run(run_live_demo())

        print("\n🎯 Demo completed!")
        if success:
            print("✅ Unfocused window automation is working correctly!")
        else:
            print("ℹ️  Check the automation configuration if needed.")

    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n💥 Demo failed: {e}")


if __name__ == "__main__":
    main()
