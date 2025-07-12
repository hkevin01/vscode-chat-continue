#!/usr/bin/env python3
"""Debug OCR functionality and tesseract configuration."""

import sys
from pathlib import Path

# Add project paths
project_root = Path("/home/kevin/Projects/vscode-chat-continue")
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

print("=== OCR Debug Test ===")

# Test 1: Import dependencies
print("\n1. Testing OCR imports...")
try:
    import pytesseract
    from PIL import Image
    print("   ✓ pytesseract imported")
    print("   ✓ PIL imported")
    
    # Check tesseract installation
    version = pytesseract.get_tesseract_version()
    print(f"   ✓ Tesseract version: {version}")
    
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Screenshot and basic OCR
print("\n2. Testing screenshot and basic OCR...")
try:
    from src.utils.screen_capture import ScreenCapture
    screen = ScreenCapture()
    screenshot = screen.capture_screen()
    
    if screenshot:
        w, h = screenshot.size
        print(f"   ✓ Screenshot: {w}x{h}")
        
        # Save screenshot for inspection
        screenshot.save("/tmp/debug_screenshot.png")
        print("   ✓ Screenshot saved to /tmp/debug_screenshot.png")
        
        # Test basic OCR with different configurations
        configs = [
            ('PSM 3 (Auto)', '--oem 3 --psm 3'),
            ('PSM 6 (Block)', '--oem 3 --psm 6'),
            ('PSM 8 (Word)', '--oem 3 --psm 8'),
            ('PSM 11 (Sparse)', '--oem 3 --psm 11'),
            ('PSM 12 (Sparse+OSD)', '--oem 3 --psm 12'),
            ('PSM 13 (Raw line)', '--oem 3 --psm 13'),
        ]
        
        for name, config in configs:
            try:
                text = pytesseract.image_to_string(screenshot, config=config)
                word_count = len(text.split())
                char_count = len(text.strip())
                print(f"   {name}: {char_count} chars, {word_count} words")
                if char_count > 0:
                    # Show first few words
                    sample = ' '.join(text.split()[:10])
                    print(f"      Sample: {repr(sample)}")
            except Exception as e:
                print(f"   {name}: ERROR - {e}")
        
    else:
        print("   ✗ No screenshot captured")
        
except Exception as e:
    print(f"   ✗ Screenshot/OCR test failed: {e}")

# Test 3: Test with a simple test image
print("\n3. Testing with simple text image...")
try:
    # Create a simple test image with "Continue" text
    from PIL import ImageDraw, ImageFont

    # Create a white image with black text
    img = Image.new('RGB', (200, 50), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        # Try to use a default font
        font = ImageFont.load_default()
    except Exception:
        font = None
    
    # Draw "Continue" text
    draw.text((10, 15), "Continue", fill='black', font=font)
    
    # Save test image
    img.save("/tmp/test_continue.png")
    print("   ✓ Test image created: /tmp/test_continue.png")
    
    # Test OCR on this simple image
    configs = [('PSM 8', '--oem 3 --psm 8'), ('PSM 6', '--oem 3 --psm 6')]
    for name, config in configs:
        try:
            text = pytesseract.image_to_string(img, config=config)
            print(f"   {name} result: {repr(text.strip())}")
        except Exception as e:
            print(f"   {name} failed: {e}")
            
except Exception as e:
    print(f"   ✗ Test image creation failed: {e}")

# Test 4: Check VS Code window content
print("\n4. Testing VS Code window detection...")
try:
    from src.core.window_detector import WindowDetector
    detector = WindowDetector()
    
    windows = detector.get_vscode_windows()
    print(f"   Found {len(windows)} VS Code windows")
    
    for i, window in enumerate(windows):
        print(f"   Window {i+1}: {window.x},{window.y} {window.width}x{window.height}")
        print(f"     Title: {repr(window.title)}")
        
        # Try to capture just this window
        try:
            window_img = screen.capture_region(window.x, window.y, window.width, window.height)
            if window_img:
                w, h = window_img.size
                print(f"     Window capture: {w}x{h}")
                
                # Save window capture
                window_img.save(f"/tmp/vscode_window_{i+1}.png")
                print(f"     Saved to /tmp/vscode_window_{i+1}.png")
                
                # Quick OCR test on window
                text = pytesseract.image_to_string(window_img, config='--oem 3 --psm 6')
                words = len(text.split())
                print(f"     OCR: {words} words detected")
                
                # Look for "continue" specifically
                if 'continue' in text.lower():
                    print("     ✓ Found 'continue' in window text!")
                else:
                    print("     No 'continue' found in window text")
                    
            else:
                print("     ✗ Failed to capture window")
                
        except Exception as e:
            print(f"     Window capture error: {e}")
    
except Exception as e:
    print(f"   ✗ Window detection failed: {e}")

print("\n=== OCR Debug Complete ===")
print("Check the saved images in /tmp/ for manual inspection")
