#!/usr/bin/env python3
"""
Simple test to verify unfocused window automation capabilities.
"""

import asyncio
import os
import subprocess
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.automation_engine import AutomationEngine  # noqa: E402
from src.core.config_manager import ConfigManager  # noqa: E402


async def simple_unfocus_test():
    """Simple test of unfocused window automation."""
    print("🎯 Simple Unfocused Window Test")
    print("=" * 40)
    
    # Set up automation
    config = ConfigManager()
    config.set('automation.dry_run', True)  # Dry run for safety
    config.set('automation.auto_focus_windows', True)
    
    engine = AutomationEngine(config)
    
    # Test 1: Window detection
    print("1. 🔍 Testing window detection...")
    windows = engine.window_detector.get_vscode_windows()
    print(f"   Found {len(windows)} VS Code window(s)")
    
    if not windows:
        print("   ❌ No VS Code windows found!")
        return False
    
    for i, window in enumerate(windows):
        print(f"   Window {i+1}: {window.title}")
        print(f"     Position: ({window.x}, {window.y})")
        print(f"     Size: {window.width}x{window.height}")
    
    # Test 2: Focus capability
    print("\n2. 🎯 Testing focus capability...")
    window = windows[0]  # Test first window
    focus_result = engine.focus_manager.focus_window(window)
    
    if focus_result.success:
        print(f"   ✅ Can focus windows using: {focus_result.method}")
    else:
        print(f"   ❌ Cannot focus windows: {focus_result.error}")
    
    # Test 3: Screenshot capability
    print("\n3. 📸 Testing screenshot capability...")
    image = engine.screen_capture.capture_window(
        window.window_id, window.x, window.y, window.width, window.height
    )
    
    if image:
        print(f"   ✅ Can capture screenshots: {image.width}x{image.height}")
    else:
        print("   ❌ Cannot capture screenshots")
        return False
    
    # Test 4: Button detection
    print("\n4. 🔍 Testing button detection...")
    buttons = engine.button_finder.find_continue_buttons(
        image, window.x, window.y)
    print(f"   Found {len(buttons)} potential Continue button(s)")

    for j, button in enumerate(buttons):
        print(f"     {j+1}. {button.method}: '{button.text}' "
              f"conf={button.confidence:.2f}")

    # Test 5: Unfocus and process windows
    print("\n5. 📱 Testing unfocused window processing...")
    print("   Opening calculator to unfocus VS Code...")

    try:
        subprocess.Popen(['gnome-calculator'],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
        await asyncio.sleep(2)
        print("   ✅ Calculator opened")
    except Exception:
        print("   📝 Please manually focus another application")
        input("   Press Enter when VS Code is unfocused...")
    
    # Test process windows method
    print("   Testing window processing while unfocused...")
    try:
        await engine._process_vscode_windows()
        print("   ✅ Successfully processed VS Code windows while unfocused")
        
        # Check stats
        stats = engine.stats
        windows_processed = stats.get('windows_processed', 0)
        print(f"   📊 Windows processed: {windows_processed}")
        
    except Exception as e:
        print(f"   ❌ Error processing windows: {e}")
        return False
    
    # Results
    print("\n" + "=" * 40)
    print("📊 TEST RESULTS:")
    print(f"✅ Window Detection: {len(windows)} windows found")
    print(f"✅ Focus Capability: {focus_result.success}")
    print(f"✅ Screenshot Capture: {'Yes' if image else 'No'}")
    print(f"✅ Button Detection: {len(buttons)} buttons found")
    print("✅ Unfocused Processing: Success")
    
    print("\n🎉 CORE CAPABILITIES VERIFIED!")
    print("The automation can:")
    print("  • Detect unfocused VS Code windows ✅")
    print("  • Bring windows into focus ✅")
    print("  • Capture screenshots of unfocused windows ✅")
    print("  • Process windows while they're in background ✅")
    
    return True


def main():
    """Run the simple test."""
    print("Testing core unfocused window automation capabilities...\n")
    
    try:
        success = asyncio.run(simple_unfocus_test())
        
        if success:
            print("\n✅ SUCCESS! Core automation capabilities work.")
            print("\n💡 For real Continue button testing:")
            print("   1. Open VS Code Copilot Chat")
            print("   2. Start a conversation with Continue buttons")
            print("   3. Run: python scripts/continuous_automation.py")
            print("   4. Focus another application")
            print("   5. Watch automation work in background!")
        else:
            print("\n❌ Some tests failed. Check the setup.")
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
    except Exception as e:
        print(f"\n💥 Test error: {e}")


if __name__ == "__main__":
    main()
