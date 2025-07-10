#!/usr/bin/env python3
"""
Simple test to check if OCR is working
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont


# Create a test image with "Continue" text
def create_test_image():
    # Create a simple image with Continue button text
    img = Image.new('RGB', (200, 50), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    # Draw Continue text
    draw.rectangle([10, 10, 190, 40], fill='#007ACC', outline='black')
    draw.text((60, 20), "Continue", fill='white', font=font)
    
    img.save('/tmp/test_continue_button.png')
    return img

def test_ocr():
    result_file = "/tmp/ocr_test_result.txt"
    
    try:
        with open(result_file, "w") as f:
            f.write("OCR Test Results\n")
            f.write("================\n\n")
            
            # Test imports
            try:
                import pytesseract
                f.write("✅ pytesseract imported successfully\n")
                
                # Test tesseract version
                version = pytesseract.get_tesseract_version()
                f.write(f"Tesseract version: {version}\n")
                
            except Exception as e:
                f.write(f"❌ pytesseract import error: {e}\n")
                return
            
            # Create test image
            f.write("\nCreating test image...\n")
            test_img = create_test_image()
            f.write("Test image saved to: /tmp/test_continue_button.png\n")
            
            # Test OCR
            f.write("\nRunning OCR on test image...\n")
            text = pytesseract.image_to_string(test_img)
            f.write(f"OCR result: '{text.strip()}'\n")
            
            # Test detailed OCR
            f.write("\nRunning detailed OCR...\n")
            data = pytesseract.image_to_data(test_img, output_type=pytesseract.Output.DICT)
            
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                conf = data['conf'][i]
                if text and conf > 0:
                    f.write(f"Text: '{text}' | Confidence: {conf}\n")
            
            f.write("\nOCR test completed successfully!\n")
            
    except Exception as e:
        with open(result_file, "w") as f:
            f.write(f"OCR test failed: {e}\n")
            import traceback
            f.write(f"Traceback: {traceback.format_exc()}\n")
    
    print(f"OCR test completed. Check results: {result_file}")

if __name__ == "__main__":
    test_ocr()
