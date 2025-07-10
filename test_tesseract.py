#!/usr/bin/env python3
"""
Simple manual test to check tesseract OCR
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_basic_ocr():
    """Test if tesseract can read simple text"""
    try:
        import pytesseract
        from PIL import Image, ImageDraw, ImageFont
        
        print("Creating test image with 'Continue' text...")
        
        # Create a simple test image
        img = Image.new('RGB', (200, 60), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw a blue button with white text (like VS Code)
        draw.rectangle([20, 15, 180, 45], fill='#007ACC', outline='black')
        draw.text((70, 22), "Continue", fill='white')
        
        # Save test image
        img.save('/tmp/test_continue_button.png')
        print("Test image saved: /tmp/test_continue_button.png")
        
        # Test OCR
        print("Testing OCR...")
        text = pytesseract.image_to_string(img).strip()
        print(f"OCR result: '{text}'")
        
        if 'continue' in text.lower():
            print("✅ OCR successfully detected 'Continue' text!")
            return True
        else:
            print("❌ OCR failed to detect 'Continue' text")
            
            # Try with detailed data
            print("Trying detailed OCR...")
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            for i in range(len(data['text'])):
                text_item = data['text'][i].strip()
                conf = data['conf'][i]
                if text_item and conf > 0:
                    print(f"  Detected: '{text_item}' (confidence: {conf})")
            return False
            
    except Exception as e:
        print(f"❌ OCR test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_tesseract_installation():
    """Check if tesseract is properly installed"""
    import subprocess
    
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Tesseract system command works:")
            print(f"   {result.stdout.split(chr(10))[0]}")
            return True
        else:
            print("❌ Tesseract command failed")
            print(f"   Error: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Tesseract command not found in PATH")
        return False
    except Exception as e:
        print(f"❌ Error checking tesseract: {e}")
        return False

def main():
    print("=== Tesseract OCR Diagnostic ===")
    
    # Check system installation
    print("\n1. Checking tesseract system installation...")
    system_ok = check_tesseract_installation()
    
    # Check Python integration
    print("\n2. Testing Python-tesseract integration...")
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✅ Python tesseract version: {version}")
        python_ok = True
    except Exception as e:
        print(f"❌ Python tesseract failed: {e}")
        python_ok = False
    
    # Test OCR functionality
    print("\n3. Testing OCR on simple 'Continue' button...")
    if python_ok:
        ocr_ok = test_basic_ocr()
    else:
        print("Skipping OCR test due to Python integration failure")
        ocr_ok = False
    
    # Summary
    print("\n=== SUMMARY ===")
    print(f"System tesseract: {'✅' if system_ok else '❌'}")
    print(f"Python integration: {'✅' if python_ok else '❌'}")
    print(f"OCR functionality: {'✅' if ocr_ok else '❌'}")
    
    if not system_ok:
        print("\n🔧 Install tesseract:")
        print("   sudo apt-get install tesseract-ocr tesseract-ocr-eng")
    elif not python_ok:
        print("\n🔧 Install Python tesseract:")
        print("   pip install pytesseract")
    elif not ocr_ok:
        print("\n🔧 OCR is installed but not working correctly")
        print("   This may be a configuration issue")

if __name__ == "__main__":
    main()
