#!/usr/bin/env python3
"""Enhanced button detection test with image preprocessing for better OCR."""

import sys
from pathlib import Path

# Add project paths
project_root = Path("/home/kevin/Projects/vscode-chat-continue")
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

print("=== Enhanced Button Detection Test ===")

def preprocess_for_ocr(image):
    """Preprocess image to improve OCR detection."""
    try:
        import cv2
        import numpy as np
        from PIL import Image

        # Convert PIL to OpenCV
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        opencv_image = np.array(image)
        opencv_image = cv2.cvtColor(opencv_image, cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        
        # Apply different preprocessing techniques
        processed_images = {}
        
        # 1. Original grayscale
        processed_images['grayscale'] = gray
        
        # 2. Threshold (binary)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        processed_images['threshold'] = thresh
        
        # 3. Adaptive threshold
        adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY, 11, 2)
        processed_images['adaptive'] = adaptive
        
        # 4. Gaussian blur + threshold
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, blur_thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed_images['blur_otsu'] = blur_thresh
        
        # 5. Morphological operations
        kernel = np.ones((2, 2), np.uint8)
        morphed = cv2.morphologyEx(adaptive, cv2.MORPH_CLOSE, kernel)
        processed_images['morphed'] = morphed
        
        # 6. Edge detection + dilation
        edges = cv2.Canny(gray, 50, 150)
        dilated = cv2.dilate(edges, kernel, iterations=1)
        processed_images['edges'] = dilated
        
        # Convert back to PIL Images
        pil_images = {}
        for name, img in processed_images.items():
            pil_img = Image.fromarray(img)
            pil_images[name] = pil_img
            # Save for inspection
            pil_img.save(f"/tmp/preprocessed_{name}.png")
            
        return pil_images
        
    except Exception as e:
        print(f"   Preprocessing error: {e}")
        return {}

# Test 1: Get screenshot and preprocess
print("\n1. Testing image preprocessing...")
try:
    import pytesseract

    from src.utils.screen_capture import ScreenCapture
    
    screen = ScreenCapture()
    screenshot = screen.capture_screen()
    
    if screenshot:
        print(f"   ✓ Screenshot: {screenshot.size[0]}x{screenshot.size[1]}")
        
        # Preprocess the image
        processed_images = preprocess_for_ocr(screenshot)
        print(f"   ✓ Created {len(processed_images)} preprocessed versions")
        
        # Test OCR on each preprocessed version
        ocr_configs = [
            ('PSM 6', '--oem 3 --psm 6'),
            ('PSM 8', '--oem 3 --psm 8'),
            ('PSM 11', '--oem 3 --psm 11'),
        ]
        
        best_results = []
        
        for proc_name, proc_img in processed_images.items():
            print(f"\n   Testing {proc_name} preprocessing:")
            
            for config_name, config in ocr_configs:
                try:
                    text = pytesseract.image_to_string(proc_img, config=config)
                    words = text.split()
                    word_count = len(words)
                    
                    # Look for continue-related words
                    continue_words = [w for w in words if 'continue' in w.lower()]
                    
                    print(f"     {config_name}: {word_count} words")
                    if continue_words:
                        print(f"       ✓ Found Continue: {continue_words}")
                        best_results.append((proc_name, config_name, continue_words, text))
                    
                    # Show sample of detected text
                    if word_count > 0:
                        sample = ' '.join(words[:5])
                        print(f"       Sample: {repr(sample)}")
                        
                except Exception as e:
                    print(f"     {config_name}: Error - {e}")
        
        if best_results:
            print(f"\n   🎉 Found {len(best_results)} promising results!")
            for proc_name, config_name, words, full_text in best_results:
                print(f"     {proc_name} + {config_name}: {words}")
        else:
            print("\n   ❌ No 'continue' text found in any preprocessing")
            
    else:
        print("   ✗ No screenshot captured")
        
except Exception as e:
    print(f"   ✗ Preprocessing test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Test VS Code window specific detection
print("\n2. Testing VS Code window specific detection...")
try:
    from src.core.window_detector import WindowDetector
    
    detector = WindowDetector()
    windows = detector.get_vscode_windows()
    
    print(f"   Found {len(windows)} VS Code windows")
    
    for i, window in enumerate(windows):
        print(f"\n   Window {i+1}: {window.x},{window.y} {window.width}x{window.height}")
        print(f"     Title: {repr(window.title)}")
        
        # Capture this specific window
        try:
            window_img = screen.capture_region(window.x, window.y, window.width, window.height)
            if window_img and window_img.size[0] > 100 and window_img.size[1] > 100:
                print(f"     ✓ Window captured: {window_img.size[0]}x{window_img.size[1]}")
                
                # Save window image
                window_img.save(f"/tmp/vscode_window_{i+1}.png")
                
                # Preprocess the window image
                window_processed = preprocess_for_ocr(window_img)
                print(f"     ✓ Preprocessed into {len(window_processed)} versions")
                
                # Test OCR on window
                window_best = []
                for proc_name, proc_img in window_processed.items():
                    for config_name, config in ocr_configs:
                        try:
                            text = pytesseract.image_to_string(proc_img, config=config)
                            if 'continue' in text.lower():
                                continue_matches = [w for w in text.split() if 'continue' in w.lower()]
                                window_best.append((proc_name, config_name, continue_matches))
                                print(f"     ✓ {proc_name}+{config_name}: {continue_matches}")
                        except:
                            pass
                
                if window_best:
                    print(f"     🎉 Window has Continue buttons!")
                else:
                    print(f"     ❌ No Continue found in window")
                    
            else:
                print(f"     ✗ Window capture failed or too small")
                
        except Exception as e:
            print(f"     Window capture error: {e}")
            
except Exception as e:
    print(f"   ✗ Window detection failed: {e}")

# Test 3: Test the enhanced button finder
print("\n3. Testing enhanced button finder...")
try:
    from src.core.button_finder import ButtonFinder
    
    finder = ButtonFinder()
    
    if screenshot:
        print("   Testing full screenshot...")
        buttons = finder.find_continue_buttons(screenshot)
        print(f"   Found {len(buttons)} buttons")
        
        for i, btn in enumerate(buttons):
            print(f"     Button {i+1}: ({btn.x},{btn.y}) {btn.width}x{btn.height}")
            print(f"       Method: {btn.method}, Confidence: {btn.confidence:.2f}")
            if btn.text:
                print(f"       Text: {repr(btn.text)}")
        
        # Also test on VS Code windows if found
        if windows:
            for i, window in enumerate(windows):
                try:
                    window_img = screen.capture_region(window.x, window.y, window.width, window.height)
                    if window_img and window_img.size[0] > 100:
                        window_buttons = finder.find_continue_buttons(window_img, window.x, window.y)
                        print(f"   Window {i+1} buttons: {len(window_buttons)}")
                        
                        for j, btn in enumerate(window_buttons):
                            print(f"     W{i+1}B{j+1}: ({btn.x},{btn.y}) method={btn.method} conf={btn.confidence:.2f}")
                except:
                    pass
    
except Exception as e:
    print(f"   ✗ Button finder test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Enhanced Test Complete ===")
print("Check /tmp/ for preprocessed images:")
print("  - debug_screenshot.png (original)")
print("  - preprocessed_*.png (processed versions)")
print("  - vscode_window_*.png (window captures)")
