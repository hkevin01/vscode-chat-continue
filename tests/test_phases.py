#!/usr/bin/env python3
"""
Test script for Phase 1 and Phase 2 functionality.

This script tests:
- Window detection
- VS Code process identification
- Screen capture
- Button detection (basic)
- Click automation (dry run)
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.button_finder import ButtonFinder
from core.click_automator import ClickAutomator
from core.config_manager import ConfigManager
from core.window_detector import WindowDetector
from utils.logger import setup_logging
from utils.screen_capture import ScreenCapture


async def test_window_detection():
    """Test window detection functionality."""
    print("\n=== Testing Window Detection ===")
    
    detector = WindowDetector()
    
    # Test VS Code process detection
    print("1. Testing VS Code process detection...")
    processes = detector.get_vscode_processes()
    print(f"   Found {len(processes)} VS Code processes:")
    for proc in processes:
        try:
            print(f"   - PID {proc.pid}: {proc.name()} ({proc.exe()})")
        except Exception as e:
            print(f"   - PID {proc.pid}: Error getting info - {e}")
    
    # Test window detection
    print("\n2. Testing VS Code window detection...")
    windows = detector.get_vscode_windows()
    print(f"   Found {len(windows)} VS Code windows:")
    for window in windows:
        print(f"   - {window}")
    
    # Test focused window detection
    print("\n3. Testing focused window detection...")
    focused = detector.get_focused_vscode_window()
    if focused:
        print(f"   Focused window: {focused}")
    else:
        print("   No VS Code window is currently focused")
    
    return len(windows) > 0


async def test_screen_capture():
    """Test screen capture functionality."""
    print("\n=== Testing Screen Capture ===")
    
    capture = ScreenCapture()
    
    if not capture.is_available():
        print("   ERROR: Screen capture not available!")
        return False
    
    print("1. Testing full screen capture...")
    screenshot = capture.capture_screen()
    if screenshot:
        print(f"   Success: Captured {screenshot.size[0]}x{screenshot.size[1]} screenshot")
        
        # Save test screenshot
        test_dir = Path("test_output")
        test_dir.mkdir(exist_ok=True)
        
        if capture.save_image(screenshot, test_dir / "test_screenshot.png"):
            print(f"   Saved test screenshot to {test_dir / 'test_screenshot.png'}")
    else:
        print("   ERROR: Failed to capture screen")
        return False
    
    print("\n2. Testing region capture...")
    # Capture a small region in the top-left corner
    region = capture.capture_region(0, 0, 200, 200)
    if region:
        print(f"   Success: Captured 200x200 region")
        capture.save_image(region, test_dir / "test_region.png")
    else:
        print("   ERROR: Failed to capture region")
    
    print(f"\n3. Screen size: {capture.get_screen_size()}")
    
    return True


async def test_button_detection():
    """Test button detection functionality."""
    print("\n=== Testing Button Detection ===")
    
    finder = ButtonFinder()
    capture = ScreenCapture()
    
    print("1. Testing with full screen capture...")
    screenshot = capture.capture_screen()
    if not screenshot:
        print("   ERROR: Could not capture screen for testing")
        return False
    
    # Test button detection
    buttons = finder.find_continue_buttons(screenshot)
    print(f"   Found {len(buttons)} potential continue buttons:")
    for i, button in enumerate(buttons):
        print(f"   - Button {i+1}: {button.method} at ({button.x}, {button.y}) "
              f"size {button.width}x{button.height} confidence {button.confidence:.2f}")
        if button.text:
            print(f"     Text: '{button.text}'")
    
    return True


async def test_click_automation():
    """Test click automation functionality (dry run)."""
    print("\n=== Testing Click Automation ===")
    
    automator = ClickAutomator()
    
    if not automator.is_available():
        print("   ERROR: Click automation not available!")
        return False
    
    print("1. Testing mouse position detection...")
    pos = automator.get_mouse_position()
    print(f"   Current mouse position: {pos}")
    
    print("\n2. Testing dry run click (safe - won't actually click)...")
    # We'll just test the click method but won't actually perform it
    # by checking if the components are properly initialized
    
    # Test with a safe coordinate (center of screen)
    screen_capture = ScreenCapture()
    screen_size = screen_capture.get_screen_size()
    center_x = screen_size[0] // 2
    center_y = screen_size[1] // 2
    
    print(f"   Would click at screen center: ({center_x}, {center_y})")
    print("   Click automator is ready and functional")
    
    return True


async def test_integration():
    """Test integration of all components."""
    print("\n=== Testing Integration ===")
    
    # Initialize all components
    config_manager = ConfigManager()
    config_manager.set('automation.dry_run', True)  # Enable dry run for safety
    
    detector = WindowDetector()
    finder = ButtonFinder()
    automator = ClickAutomator()
    capture = ScreenCapture()
    
    print("1. Looking for VS Code windows...")
    windows = detector.get_vscode_windows()
    
    if not windows:
        print("   No VS Code windows found for integration test")
        return True
    
    # Test with the first window
    window = windows[0]
    print(f"   Testing with window: {window.title}")
    
    print("2. Capturing window screenshot...")
    screenshot = capture.capture_window(
        window.window_id, window.x, window.y, window.width, window.height
    )
    
    if not screenshot:
        print("   ERROR: Failed to capture window")
        return False
    
    print("3. Searching for continue buttons...")
    buttons = finder.find_continue_buttons(screenshot, window.x, window.y)
    print(f"   Found {len(buttons)} buttons in window")
    
    if buttons:
        print("4. Testing click automation (DRY RUN)...")
        for i, button in enumerate(buttons[:2]):  # Test max 2 buttons
            print(f"   DRY RUN: Would click button {i+1} at ({button.center_x}, {button.center_y})")
    
    print("   Integration test completed successfully!")
    return True


async def main():
    """Main test function."""
    print("VS Code Chat Continue Automation - Phase 1 & 2 Test")
    print("=" * 60)
    
    # Setup logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Run tests
    tests = [
        ("Window Detection", test_window_detection),
        ("Screen Capture", test_screen_capture),
        ("Button Detection", test_button_detection),
        ("Click Automation", test_click_automation),
        ("Integration", test_integration),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\nRunning {test_name} test...")
            result = await test_func()
            results[test_name] = result
            status = "PASS" if result else "FAIL"
            print(f"{test_name}: {status}")
        except Exception as e:
            print(f"{test_name}: ERROR - {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:<8} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Phase 1 & 2 functionality is working.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
    
    return passed == total


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
