#!/bin/bash
# Quick fix to install tesseract and test button detection

echo "Installing Tesseract OCR..."

# Install tesseract for different package managers
if command -v apt-get >/dev/null 2>&1; then
    echo "Using apt-get..."
    sudo apt-get update
    sudo apt-get install -y tesseract-ocr tesseract-ocr-eng
elif command -v dnf >/dev/null 2>&1; then
    echo "Using dnf..."
    sudo dnf install -y tesseract tesseract-langpack-eng
elif command -v pacman >/dev/null 2>&1; then
    echo "Using pacman..."
    sudo pacman -S tesseract tesseract-data-eng
else
    echo "Please install tesseract-ocr manually for your distribution"
    exit 1
fi

echo "Tesseract installed. Testing..."
tesseract --version

echo "Testing Python OCR integration..."
cd /home/kevin/Projects/vscode-chat-continue
/home/kevin/Projects/vscode-chat-continue/venv/bin/python -c "
import pytesseract
from PIL import Image, ImageDraw, ImageFont

# Create test image
img = Image.new('RGB', (150, 40), color='#007ACC')
draw = ImageDraw.Draw(img)
draw.text((40, 12), 'Continue', fill='white')
img.save('/tmp/test_button.png')
print('Test image created: /tmp/test_button.png')

# Test OCR
text = pytesseract.image_to_string(img).strip()
print(f'OCR result: \"{text}\"')

if 'continue' in text.lower():
    print('✅ OCR is working correctly!')
else:
    print('⚠️ OCR may need tuning')
"

echo "Now testing actual VS Code window detection..."
/home/kevin/Projects/vscode-chat-continue/venv/bin/python enhanced_button_test.py
