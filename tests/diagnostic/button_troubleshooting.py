#!/usr/bin/env python3
"""
VS Code Continue Button Detection - Troubleshooting Guide

This script helps diagnose and fix continue button clicking issues.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_dependencies():
    """Test all required dependencies for button detection."""
    print("🔍 Testing Button Detection Dependencies")
    print("=" * 50)

    # Test OCR (most important for Continue button detection)
    try:
        import pytesseract

        print("✅ pytesseract available")

        # Test if tesseract is actually installed
        try:
            version = pytesseract.get_tesseract_version()
            print(f"   Tesseract version: {version}")
        except Exception as e:
            print(f"⚠️  Tesseract binary issue: {e}")
            print("   Install with: sudo apt install tesseract-ocr")

    except ImportError:
        print("❌ pytesseract not available")
        print("   Install with: pip install pytesseract")

    # Test image processing
    try:
        import cv2

        print(f"✅ OpenCV available (version {cv2.__version__})")
    except ImportError:
        print("❌ OpenCV not available")
        print("   Install with: pip install opencv-python")

    # Test PIL
    try:
        from PIL import Image

        print("✅ PIL/Pillow available")
    except ImportError:
        print("❌ PIL not available")
        print("   Install with: pip install Pillow")

    # Test pyautogui
    try:
        import pyautogui

        print("✅ pyautogui available")
    except ImportError:
        print("❌ pyautogui not available")
        print("   Install with: pip install pyautogui")


def create_test_button_image():
    """Create a test image with a Continue button for testing."""
    try:
        from PIL import Image, ImageDraw, ImageFont

        # Create a test image that looks like a VS Code Continue button
        img = Image.new("RGB", (200, 50), color=(30, 30, 30))  # Dark background
        draw = ImageDraw.Draw(img)

        # Draw button-like rectangle
        draw.rectangle([20, 10, 180, 40], fill=(0, 122, 204), outline=(0, 122, 204))  # VS Code blue

        # Add text
        try:
            # Try to use a decent font
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            font = ImageFont.load_default()

        draw.text((60, 18), "Continue", fill="white", font=font)

        # Save test image
        os.makedirs("tmp", exist_ok=True)
        test_path = "tmp/test_continue_button.png"
        img.save(test_path)
        print(f"✅ Test button image created: {test_path}")

        return test_path

    except Exception as e:
        print(f"❌ Failed to create test image: {e}")
        return None


def test_button_detection_on_image(image_path):
    """Test button detection on a specific image."""
    try:
        from PIL import Image

        from core.button_finder import ButtonFinder

        print(f"\n🎯 Testing button detection on: {image_path}")

        # Load image
        image = Image.open(image_path)
        print(f"Image size: {image.size}")

        # Test button detection
        finder = ButtonFinder()
        buttons = finder.find_continue_buttons(image, 0, 0)

        print(f"Found {len(buttons)} buttons:")
        for i, btn in enumerate(buttons, 1):
            print(f"  {i}. Position: ({btn.center_x}, {btn.center_y})")
            print(f"     Confidence: {btn.confidence:.2f}")
            print(f"     Method: {btn.method}")
            if btn.text:
                print(f"     Text: '{btn.text}'")

        return len(buttons) > 0

    except Exception as e:
        print(f"❌ Button detection test failed: {e}")
        return False


def provide_troubleshooting_steps():
    """Provide step-by-step troubleshooting guide."""
    print("\n🔧 Troubleshooting Guide for Continue Button Detection")
    print("=" * 60)

    print("\n1. **Verify VS Code Setup:**")
    print("   - Open VS Code")
    print("   - Install GitHub Copilot extension")
    print(
        "   - Open the Copilot chat panel (Ctrl+Shift+I or View > Command Palette > 'Copilot: Open Chat')"
    )
    print("   - Ask a question that requires a long response")
    print("   - Look for a blue 'Continue' button at the bottom of the response")

    print("\n2. **Check Dependencies:**")
    print("   - Ensure all required packages are installed:")
    print("     pip install pytesseract opencv-python Pillow pyautogui pynput")
    print("   - Install Tesseract OCR:")
    print("     sudo apt install tesseract-ocr  # Ubuntu/Debian")
    print("     brew install tesseract          # macOS")

    print("\n3. **Test Button Detection:**")
    print("   - Run: python tests/manual/realtime_button_test.py")
    print("   - Check the debug images in tmp/ folder")
    print("   - Verify the Continue button is visible in the captured image")

    print("\n4. **Common Issues:**")
    print("   - **No Continue button visible**: Ask longer questions in Copilot chat")
    print("   - **Button text changed**: Update patterns in button_finder.py")
    print("   - **Wrong window captured**: Ensure correct VS Code window is focused")
    print("   - **OCR not working**: Check tesseract installation")

    print("\n5. **Manual Test:**")
    print('   - Create a test with: PYTHONPATH=src python -c "')
    print("     from utils.screen_capture import ScreenCapture")
    print("     capture = ScreenCapture()")
    print("     img = capture.capture_screen()")
    print("     img.save('tmp/full_screen.png')\"")
    print("   - Check tmp/full_screen.png to see what's being captured")


def main():
    """Main troubleshooting function."""
    print("🚀 VS Code Continue Button - Troubleshooting Tool")
    print("=" * 55)

    # Test dependencies
    test_dependencies()

    # Create and test with a sample Continue button
    print("\n📝 Creating Test Button Image...")
    test_image = create_test_button_image()

    if test_image:
        success = test_button_detection_on_image(test_image)
        if success:
            print("✅ Button detection works on test image!")
        else:
            print("❌ Button detection failed on test image")

    # Provide troubleshooting guide
    provide_troubleshooting_steps()

    print("\n💡 Quick Fix Commands:")
    print("=" * 30)
    print("# Install missing dependencies:")
    print("pip install pytesseract opencv-python Pillow pyautogui pynput")
    print("sudo apt install tesseract-ocr")
    print()
    print("# Test real-time detection:")
    print("PYTHONPATH=src python tests/manual/realtime_button_test.py")
    print()
    print("# Run main automation:")
    print("./run.sh --gui")


if __name__ == "__main__":
    main()
