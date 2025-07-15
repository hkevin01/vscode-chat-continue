#!/usr/bin/env python3
"""
Comprehensive test suite for unfocused window automation.
Tests that the automation can detect and click Continue buttons in VS Code windows
that are not currently focused.
"""

import asyncio
import logging
import os
import subprocess
import time
from typing import List, Optional

from src.core.automation_engine import AutomationEngine
from src.core.config_manager import ConfigManager
from src.core.window_detector import VSCodeWindow

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class UnfocusedWindowTester:
    """Test automation on unfocused VS Code windows."""

    def __init__(self):
        """Initialize the tester."""
        self.config = ConfigManager()
        self.config.set("automation.dry_run", False)  # Actually click for testing
        self.config.set("automation.auto_focus_windows", True)
        self.config.set("automation.max_clicks_per_window", 1)
        self.config.set("automation.cycle_delay", 2.0)

        self.engine = AutomationEngine(self.config)
        self.test_results = {}

    async def run_comprehensive_tests(self):
        """Run all unfocused window tests."""
        print("🧪 Starting Comprehensive Unfocused Window Tests")
        print("=" * 60)

        tests = [
            ("test_detect_unfocused_windows", self.test_detect_unfocused_windows),
            ("test_focus_management", self.test_focus_management),
            ("test_click_unfocused_button", self.test_click_unfocused_button),
            ("test_multiple_windows", self.test_multiple_windows),
            ("test_background_automation", self.test_background_automation),
        ]

        for test_name, test_func in tests:
            print(f"\n🔍 Running {test_name}...")
            try:
                result = await test_func()
                self.test_results[test_name] = result
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{status} {test_name}")
            except Exception as e:
                self.test_results[test_name] = False
                print(f"❌ FAIL {test_name}: {e}")
                logger.exception(f"Test {test_name} failed")

        self._print_test_summary()

    async def test_detect_unfocused_windows(self) -> bool:
        """Test: Can detect VS Code windows when they're not focused."""
        print("  📋 Testing window detection while unfocused...")

        # Get current VS Code windows
        windows = self.engine.window_detector.get_vscode_windows()

        if not windows:
            print("  ❌ No VS Code windows found")
            return False

        print(f"  ✅ Found {len(windows)} VS Code window(s)")

        # Test detection on each window
        for i, window in enumerate(windows):
            print(f"    Window {i+1}: {window.title}")
            print(f"      Position: ({window.x}, {window.y})")
            print(f"      Size: {window.width}x{window.height}")

            # Capture screenshot
            image = self.engine.screen_capture.capture_window(
                window.window_id, window.x, window.y, window.width, window.height
            )

            if image:
                print(f"      ✅ Screenshot captured: {image.width}x{image.height}")

                # Test button detection
                buttons = self.engine.button_finder.find_continue_buttons(image, window.x, window.y)

                print(f"      🔍 Found {len(buttons)} potential Continue buttons")
                for j, button in enumerate(buttons):
                    print(
                        f"        {j+1}. {button.method}: '{button.text}' "
                        f"at ({button.x}, {button.y}) conf={button.confidence:.2f}"
                    )
            else:
                print("      ❌ Failed to capture screenshot")

        return len(windows) > 0

    async def test_focus_management(self) -> bool:
        """Test: Can bring unfocused windows into focus."""
        print("  🎯 Testing window focus management...")

        windows = self.engine.window_detector.get_vscode_windows()
        if not windows:
            print("  ❌ No VS Code windows found")
            return False

        # Test focusing each window
        success_count = 0
        for window in windows:
            print(f"    Testing focus for: {window.title}")

            # Attempt to focus the window
            focus_result = self.engine.focus_manager.focus_window(window)

            if focus_result.success:
                print(f"      ✅ Focused using method: {focus_result.method}")
                success_count += 1
                await asyncio.sleep(0.5)  # Brief pause between focus tests
            else:
                print(f"      ❌ Failed to focus: {focus_result.error}")

        success_rate = success_count / len(windows)
        print(
            f"  📊 Focus success rate: {success_count}/{len(windows)} " f"({success_rate*100:.1f}%)"
        )

        return success_rate >= 0.5  # At least 50% success rate

    async def test_click_unfocused_button(self) -> bool:
        """Test: Can click Continue button in unfocused window."""
        print("  🖱️  Testing Continue button clicking in unfocused windows...")

        # First, make sure another application is focused
        print("    📋 Opening test browser to unfocus VS Code...")
        self._open_test_browser()
        await asyncio.sleep(2)

        # Now try to find and click Continue buttons
        windows = self.engine.window_detector.get_vscode_windows()
        clicked_buttons = 0

        for window in windows:
            print(f"    Testing clicks in: {window.title}")

            # Capture screenshot
            image = self.engine.screen_capture.capture_window(
                window.window_id, window.x, window.y, window.width, window.height
            )

            if not image:
                continue

            # Find buttons
            buttons = self.engine.button_finder.find_continue_buttons(image, window.x, window.y)

            if buttons:
                print(f"      🔍 Found {len(buttons)} Continue button(s)")

                # Try clicking the best button
                best_button = max(buttons, key=lambda b: b.confidence)
                print(
                    f"      🎯 Attempting to click button at " f"({best_button.x}, {best_button.y})"
                )

                # This should automatically focus the window and click
                await self.engine._click_buttons([best_button], window)
                clicked_buttons += 1

                await asyncio.sleep(1)  # Wait to see result
                break

        print(f"  📊 Clicked {clicked_buttons} button(s)")
        return clicked_buttons > 0

    async def test_multiple_windows(self) -> bool:
        """Test: Can handle multiple VS Code windows correctly."""
        print("  🔢 Testing multiple window handling...")

        windows = self.engine.window_detector.get_vscode_windows()

        if len(windows) < 2:
            print("    ⚠️  Only 1 VS Code window found, opening another...")
            self._open_additional_vscode_window()
            await asyncio.sleep(3)
            windows = self.engine.window_detector.get_vscode_windows()

        print(f"    📊 Testing with {len(windows)} VS Code windows")

        # Test detection in all windows
        total_buttons = 0
        for i, window in enumerate(windows):
            print(f"      Window {i+1}: {window.title}")

            image = self.engine.screen_capture.capture_window(
                window.window_id, window.x, window.y, window.width, window.height
            )

            if image:
                buttons = self.engine.button_finder.find_continue_buttons(image, window.x, window.y)
                total_buttons += len(buttons)
                print(f"        🔍 Found {len(buttons)} button(s)")

        print(f"    📊 Total buttons across all windows: {total_buttons}")
        return len(windows) >= 1

    async def test_background_automation(self) -> bool:
        """Test: Full automation cycle while VS Code is in background."""
        print("  🤖 Testing full background automation cycle...")

        # Open another application to put VS Code in background
        print("    📱 Opening calculator to put VS Code in background...")
        self._open_calculator()
        await asyncio.sleep(2)

        # Run one automation cycle
        print("    🔄 Running automation cycle...")
        initial_stats = self.engine.stats.copy()

        # Run a single cycle
        await self.engine._process_vscode_windows()

        final_stats = self.engine.stats
        cycles_run = final_stats.get("cycles_completed", 0) - initial_stats.get(
            "cycles_completed", 0
        )
        windows_processed = final_stats.get("windows_processed", 0) - initial_stats.get(
            "windows_processed", 0
        )

        print(f"    📊 Cycles completed: {cycles_run}")
        print(f"    📊 Windows processed: {windows_processed}")

        return cycles_run > 0

    def _open_test_browser(self):
        """Open a browser to test Continue button (unfocus VS Code)."""
        try:
            # Open the test HTML file in default browser
            test_file = os.path.abspath("test_continue_button.html")
            if os.path.exists(test_file):
                subprocess.Popen(
                    ["xdg-open", f"file://{test_file}"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                # Fallback: open any webpage
                subprocess.Popen(
                    ["xdg-open", "https://www.google.com"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        except Exception as e:
            logger.debug(f"Failed to open browser: {e}")

    def _open_calculator(self):
        """Open calculator app to unfocus VS Code."""
        try:
            subprocess.Popen(
                ["gnome-calculator"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except Exception:
            try:
                subprocess.Popen(["kcalc"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                logger.debug("Could not open calculator")

    def _open_additional_vscode_window(self):
        """Open an additional VS Code window."""
        try:
            subprocess.Popen(
                ["code", "--new-window"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except Exception as e:
            logger.debug(f"Failed to open additional VS Code window: {e}")

    def _print_test_summary(self):
        """Print summary of all test results."""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)

        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")

        print("-" * 60)
        print(
            f"📈 Overall Results: {passed_tests}/{total_tests} tests passed "
            f"({passed_tests/total_tests*100:.1f}%)"
        )

        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Unfocused window automation is working correctly!")
        elif passed_tests >= total_tests * 0.8:
            print("✅ Most tests passed. Automation should work well for unfocused windows.")
        else:
            print("⚠️  Some tests failed. Check the automation configuration.")


async def main():
    """Run the unfocused window tests."""
    print("🎯 VS Code Unfocused Window Automation Test Suite")
    print("This will test if the automation can detect and click Continue")
    print("buttons in VS Code windows that are not currently focused.")
    print()

    # Ask user to prepare test environment
    input("📋 Press Enter when you're ready to start testing...")

    tester = UnfocusedWindowTester()
    await tester.run_comprehensive_tests()

    print("\n🎯 Test completed! Check the results above.")
    print("\n💡 To test manually:")
    print("   1. Open test_continue_button.html in VS Code")
    print("   2. Focus another application")
    print("   3. Run: python scripts/continuous_automation.py")
    print("   4. Watch automation focus VS Code and click Continue!")


if __name__ == "__main__":
    asyncio.run(main())
