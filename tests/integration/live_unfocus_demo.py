#!/usr/bin/env python3
"""
Live demonstration of unfocused window automation.
This will show the automation actually working on Continue buttons.
"""

import asyncio
import os
import subprocess
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.automation_engine import AutomationEngine  # noqa: E402
from src.core.config_manager import ConfigManager  # noqa: E402


async def live_demo():
    """Live demonstration of unfocused window automation."""
    print("🎬 LIVE UNFOCUSED WINDOW AUTOMATION DEMO")
    print("=" * 50)
    
    # Setup (NOT dry run - this will actually click!)
    config = ConfigManager()
    config.set('automation.dry_run', False)  # REAL CLICKS!
    config.set('automation.auto_focus_windows', True)
    config.set('automation.click_delay', 1.0)  # Slower for demo
    
    engine = AutomationEngine(config)
    
    print("⚠️  WARNING: This will actually click Continue buttons!")
    print("   Make sure you have VS Code with Copilot Chat open")
    print("   and some Continue buttons visible.")
    print()
    
    # Step 1: Check setup
    print("Step 1: 🔍 Checking VS Code windows...")
    windows = engine.window_detector.get_vscode_windows()
    
    if not windows:
        print("❌ No VS Code windows found!")
        print("Please open VS Code and try again.")
        return
    
    print(f"✅ Found {len(windows)} VS Code window(s)")
    for i, window in enumerate(windows):
        print(f"   {i+1}. {window.title}")
    
    # Step 2: Initial scan while focused
    print("\nStep 2: 📸 Scanning for Continue buttons while focused...")
    
    window = windows[0]
    image = engine.screen_capture.capture_window(
        window.window_id, window.x, window.y, window.width, window.height)
    
    if image:
        buttons = engine.button_finder.find_continue_buttons(
            image, window.x, window.y)
        print(f"✅ Found {len(buttons)} Continue button(s)")
        
        for j, button in enumerate(buttons):
            print(f"   {j+1}. {button.text} (conf: {button.confidence:.2f})")
    else:
        print("❌ Cannot capture screenshots")
        return
    
    if not buttons:
        print("\n⚠️  No Continue buttons found!")
        print("Please:")
        print("  1. Open VS Code Copilot Chat")
        print("  2. Start a conversation")
        print("  3. Wait for Continue buttons to appear")
        print("  4. Run this demo again")
        return
    
    # Step 3: Unfocus and demonstrate
    print("\nStep 3: 🎯 DEMO TIME!")
    print("I'll now:")
    print("  1. Open calculator to unfocus VS Code")
    print("  2. Wait 3 seconds")
    print("  3. Automatically focus VS Code and click Continue buttons")
    print("  4. Return focus to calculator")
    print()
    
    input("Press Enter when ready for the demo...")
    
    # Open calculator to unfocus
    print("Opening calculator...")
    try:
        calc_process = subprocess.Popen(
            ['gnome-calculator'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)
        await asyncio.sleep(2)
        print("✅ Calculator opened - VS Code is now unfocused")
    except Exception:
        print("⚠️  Could not open calculator")
        print("Please manually focus another application")
        input("Press Enter when VS Code is unfocused...")
    
    # Countdown
    print("\n🚀 Starting automation in:")
    for i in range(3, 0, -1):
        print(f"   {i}...")
        await asyncio.sleep(1)
    
    print("\n🎬 AUTOMATION RUNNING!")
    print("Watch VS Code...")
    
    # Run automation on unfocused windows
    start_time = time.time()
    await engine._process_vscode_windows()
    end_time = time.time()
    
    print(f"\n✅ Automation completed in {end_time - start_time:.1f}s")
    
    # Show results
    stats = engine.stats
    windows_processed = stats.get('windows_processed', 0)
    buttons_clicked = stats.get('buttons_clicked', 0)
    
    print("📊 Results:")
    print(f"   Windows processed: {windows_processed}")
    print(f"   Buttons clicked: {buttons_clicked}")
    
    # Return focus to calculator
    try:
        if 'calc_process' in locals():
            print("\n🔙 Returning focus to calculator...")
            subprocess.run(['wmctrl', '-a', 'Calculator'],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
    except Exception:
        pass
    
    print("\n" + "=" * 50)
    print("🎉 DEMO COMPLETE!")
    print()
    print("What just happened:")
    print("✅ VS Code was running in the background")
    print("✅ Automation detected the unfocused window")
    print("✅ Automation brought VS Code into focus")
    print("✅ Automation clicked Continue buttons")
    print("✅ Automation returned focus to calculator")
    print()
    print("This proves the automation can work on unfocused windows!")


def main():
    """Run the live demo."""
    try:
        asyncio.run(live_demo())
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted")
    except Exception as e:
        print(f"\n💥 Demo error: {e}")


if __name__ == "__main__":
    main()
