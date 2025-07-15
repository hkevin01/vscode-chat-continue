#!/usr/bin/env python3
"""
Core detection test - verify basic functionality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from PIL import Image


def test_imports():
    """Test if all required imports work."""
    print("🔍 Testing imports...")

    try:
        import pytesseract

        print("✅ pytesseract available")

        # Test if tesseract is working
        test_result = pytesseract.image_to_string(Image.new("RGB", (100, 50), "white"))
        print("✅ tesseract executable working")
    except Exception as e:
        print(f"❌ pytesseract error: {e}")

    try:
        import cv2
        import numpy as np

        print("✅ OpenCV available")
    except Exception as e:
        print(f"❌ OpenCV error: {e}")

    try:
        from core.button_finder import ButtonFinder

        print("✅ ButtonFinder import successful")

        bf = ButtonFinder()
        print("✅ ButtonFinder creation successful")
    except Exception as e:
        print(f"❌ ButtonFinder error: {e}")


def test_simple_detection():
    """Test detection on a simple test image."""
    print("\n🧪 Testing simple detection...")

    try:
        # Create a simple test image with blue rectangle and white text
        import numpy as np
        from PIL import Image, ImageDraw, ImageFont

        from core.button_finder import ButtonFinder

        # Create a 400x300 test image
        img = Image.new("RGB", (400, 300), "white")
        draw = ImageDraw.Draw(img)

        # Draw a blue button with "Continue" text
        button_rect = [250, 200, 350, 230]  # x1, y1, x2, y2
        draw.rectangle(button_rect, fill=(70, 130, 180), outline=(50, 100, 150))

        # Add white text
        try:
            draw.text((265, 208), "Continue", fill="white")
        except:
            draw.text((265, 208), "Continue", fill="white")

        # Save test image
        Path("tmp").mkdir(exist_ok=True)
        test_path = "tmp/test_image.png"
        img.save(test_path)
        print(f"💾 Created test image: {test_path}")

        # Test detection
        bf = ButtonFinder()
        buttons = bf.find_continue_buttons(img, 0, 0)

        print(f"🎯 Detection result: {len(buttons)} buttons found")

        for i, button in enumerate(buttons):
            print(f"  {i+1}. ({button.x}, {button.y}) {button.width}x{button.height}")
            print(f"      Confidence: {button.confidence:.2f}")
            print(f"      Method: {button.method}")
            print(f"      Text: '{button.text}'")

        if buttons:
            print("✅ Basic detection working!")
        else:
            print("❌ Basic detection failed - no buttons found in test image")

    except Exception as e:
        print(f"❌ Simple detection test failed: {e}")
        import traceback

        traceback.print_exc()


def test_ocr_directly():
    """Test OCR functionality directly."""
    print("\n🔤 Testing OCR directly...")

    try:
        import pytesseract
        from PIL import Image, ImageDraw

        # Create simple text image
        img = Image.new("RGB", (200, 50), "white")
        draw = ImageDraw.Draw(img)
        draw.text((20, 15), "Continue", fill="black")

        Path("tmp").mkdir(exist_ok=True)
        ocr_test_path = "tmp/ocr_test.png"
        img.save(ocr_test_path)

        # Test OCR
        text = pytesseract.image_to_string(img).strip()
        print(f"📝 OCR result: '{text}'")

        if "continue" in text.lower():
            print("✅ OCR can detect 'Continue' text")
        else:
            print("❌ OCR failed to detect 'Continue' text")

    except Exception as e:
        print(f"❌ OCR test failed: {e}")


def main():
    """Run all diagnostic tests."""
    print("🔧 CORE DETECTION DIAGNOSTICS")
    print("=" * 50)

    test_imports()
    test_simple_detection()
    test_ocr_directly()

    print("\n📊 SUMMARY:")
    print("If basic detection failed, the core algorithms need fixing.")
    print("If basic detection worked but real detection doesn't,")
    print("the issue is likely with real VS Code button appearance.")


if __name__ == "__main__":
    main()
