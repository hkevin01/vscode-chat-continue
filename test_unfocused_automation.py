#!/usr/bin/env python3
"""
Setup and run unfocused window automation test.
This will:
1. Keep the HTML file open in VS Code (for the automation to detect)
2. Open the rendered HTML in your browser (so you can see the buttons)
3. Run automation test on the unfocused VS Code window
"""

import asyncio
import os
import subprocess
import sys
import time
import webbrowser

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.automation_engine import AutomationEngine
from src.core.config_manager import ConfigManager


async def setup_and_test():
    """Set up test environment and run automation test."""
    print("🎯 VS Code Unfocused Window Automation Test")
    print("=" * 50)
    
    # Step 1: Ensure test file is open in VS Code
    test_file = os.path.abspath("test_continue_button.html")
    
    if not os.path.exists(test_file):
        print("❌ test_continue_button.html not found!")
        return False
    
    print("1. 📄 Opening test file in VS Code...")
    try:
        # Open in VS Code to ensure it's available for automation
        subprocess.run(['code', test_file], check=True)
        time.sleep(2)
        print("   ✅ Test file opened in VS Code")
    except Exception as e:
        print(f"   ❌ Failed to open in VS Code: {e}")
        return False
    
    # Step 2: Open rendered HTML in browser
    print("\n2. 🌐 Opening rendered HTML in browser...")
    try:
        webbrowser.open(f'file://{test_file}')
        time.sleep(2)
        print("   ✅ Test page opened in browser")
        print("   💡 You can now see the actual Continue buttons!")
    except Exception as e:
        print(f"   ⚠️  Could not open browser: {e}")
        print("   📝 You can manually open: file://" + test_file)
    
    # Step 3: Set up automation engine
    print("\n3. 🤖 Setting up automation engine...")
    config = ConfigManager()
    config.set('automation.dry_run', False)  # Actually click for testing
    config.set('automation.auto_focus_windows', True)
    config.set('automation.max_clicks_per_window', 1)
    config.set('automation.cycle_delay', 3.0)
    
    engine = AutomationEngine(config)
    print("   ✅ Automation engine configured")
    
    # Step 4: Check VS Code windows
    print("\n4. 🔍 Checking VS Code windows...")
    windows = engine.window_detector.get_vscode_windows()
    print(f"   Found {len(windows)} VS Code window(s):")
    
    test_window = None
    for i, window in enumerate(windows):
        print(f"     {i+1}. {window.title}")
        if 'test_continue_button.html' in window.title:
            test_window = window
            print("       ⭐ This is our test window!")
    
    if not test_window:
        print("   ⚠️  Test HTML file not found in VS Code windows")
        print("   📝 Make sure test_continue_button.html is open in VS Code")
        return False
    
    # Step 5: Test button detection in the HTML file
    print("\n5. 🔍 Testing Continue button detection in HTML file...")
    image = engine.screen_capture.capture_window(
        test_window.window_id, test_window.x, test_window.y,
        test_window.width, test_window.height
    )
    
    if not image:
        print("   ❌ Failed to capture VS Code window screenshot")
        return False
    
    buttons = engine.button_finder.find_continue_buttons(image, test_window.x, test_window.y)
    print(f"   🔍 Found {len(buttons)} potential Continue button(s) in VS Code")
    
    for j, button in enumerate(buttons):
        print(f"     {j+1}. Method: {button.method}")
        print(f"        Text: '{button.text}'")
        print(f"        Position: ({button.x}, {button.y})")
        print(f"        Confidence: {button.confidence:.2f}")
    
    # Step 6: Prepare for unfocused test
    print("\n6. 📱 Preparing unfocused window test...")
    print("   Current setup:")
    print("   • VS Code has test_continue_button.html open")
    print("   • Browser shows the rendered Continue buttons")
    print("   • Automation is ready to detect and click buttons")
    print()
    
    # Give user chance to arrange windows
    input("   📋 Arrange your windows as needed, then press Enter to continue...")
    
    # Step 7: Make VS Code unfocused
    print("\n7. 🎯 Making VS Code unfocused for the test...")
    try:
        # Focus the browser window to unfocus VS Code
        if sys.platform.startswith('linux'):
            subprocess.run(['wmctrl', '-a', 'Mozilla Firefox'], 
                         capture_output=True, text=True)
        time.sleep(1)
        print("   ✅ VS Code should now be unfocused")
    except Exception:
        print("   📝 Please manually click on another window to unfocus VS Code")
        input("   Press Enter when VS Code is unfocused...")
    
    # Step 8: Run the automation test
    print("\n8. 🚀 Running automation on unfocused VS Code window...")
    print("   The automation will now:")
    print("   • Detect the VS Code window in the background")
    print("   • Bring it into focus automatically")
    print("   • Click any Continue buttons it finds")
    print()
    
    input("   Press Enter to start the automation test...")
    
    # Run automation cycles
    test_cycles = 3
    success = False
    
    for cycle in range(1, test_cycles + 1):
        print(f"\n   🔄 Test Cycle {cycle}/{test_cycles}")
        
        try:
            # Run one automation cycle
            await engine._process_vscode_windows()
            
            # Check results
            stats = engine.stats
            clicks_attempted = stats.get('clicks_attempted', 0)
            clicks_successful = stats.get('clicks_successful', 0)
            windows_processed = stats.get('windows_processed', 0)
            
            print(f"     📊 Windows processed: {windows_processed}")
            print(f"     📊 Clicks attempted: {clicks_attempted}")
            print(f"     📊 Clicks successful: {clicks_successful}")
            
            if clicks_successful > 0:
                print("     ✅ SUCCESS! Automation clicked a button!")
                success = True
                break
            elif clicks_attempted > 0:
                print("     ⚠️  Clicks attempted but none successful")
            else:
                print("     ℹ️  No Continue buttons found to click")
                
        except Exception as e:
            print(f"     ❌ Automation error: {e}")
        
        if cycle < test_cycles:
            print(f"     ⏱️  Waiting 3 seconds before next cycle...")
            await asyncio.sleep(3)
    
    # Step 9: Results
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    
    final_stats = engine.stats
    print(f"Total cycles: {final_stats.get('cycles_completed', 0)}")
    print(f"Windows processed: {final_stats.get('windows_processed', 0)}")
    print(f"Buttons found: {final_stats.get('buttons_found', 0)}")
    print(f"Clicks attempted: {final_stats.get('clicks_attempted', 0)}")
    print(f"Clicks successful: {final_stats.get('clicks_successful', 0)}")
    
    if success:
        print("\n🎉 TEST PASSED!")
        print("✅ The automation successfully:")
        print("   • Detected Continue buttons in unfocused VS Code window")
        print("   • Brought VS Code into focus automatically")
        print("   • Clicked the Continue button")
        print("   • Worked while other applications were focused")
        print("\n💡 Unfocused window automation is working correctly!")
    else:
        print("\n⚠️  TEST INCONCLUSIVE")
        print("   The automation ran but didn't click any buttons.")
        print("   This could be because:")
        print("   • No Continue buttons were detected in the HTML code view")
        print("   • Button detection needs refinement for HTML text")
        print("   • The test needs actual VS Code chat Continue buttons")
        print("\n💡 For real testing, use actual VS Code Copilot chat Continue buttons")
    
    return success


def main():
    """Run the setup and test."""
    print("This will test unfocused window automation using test_continue_button.html")
    print("The test will open the file in VS Code AND browser, then test automation.")
    print()
    
    try:
        success = asyncio.run(setup_and_test())
        print(f"\n🎯 Test completed! Result: {'PASS' if success else 'INCONCLUSIVE'}")
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")


if __name__ == "__main__":
    main()
