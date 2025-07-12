#!/usr/bin/env python3
"""
Enhanced image analysis for Continue button detection.
Analyzes the captured debug images to improve OCR detection.
"""

import sys
from pathlib import Path

import cv2
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False

def analyze_image(image_path: str):
    """Analyze an image for Continue button detection."""
    print(f"\n=== Analyzing {image_path} ===")
    
    if not Path(image_path).exists():
        print(f"❌ Image not found: {image_path}")
        return
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Could not load image: {image_path}")
        return
    
    height, width = image.shape[:2]
    print(f"📏 Image size: {width}x{height}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Focus on the right side where the Continue button should be
    # Based on description: "right center"
    right_region = gray[:, width//2:]  # Right half
    center_region = right_region[height//4:3*height//4, :]  # Center vertically
    
    print(f"🔍 Analyzing right-center region: {center_region.shape[1]}x{center_region.shape[0]}")
    
    if not HAS_TESSERACT:
        print("⚠️ Tesseract not available, skipping OCR analysis")
        return
    
    # Try different preprocessing techniques
    preprocessing_methods = [
        ("Original", center_region),
        ("High Contrast", cv2.convertScaleAbs(center_region, alpha=2.0, beta=0)),
        ("Gaussian Blur", cv2.GaussianBlur(center_region, (3, 3), 0)),
        ("Threshold", cv2.threshold(center_region, 127, 255, cv2.THRESH_BINARY)[1]),
        ("Adaptive Threshold", cv2.adaptiveThreshold(center_region, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2))
    ]
    
    for method_name, processed_image in preprocessing_methods:
        print(f"\n--- {method_name} ---")
        try:
            # Extract text with different configs
            configs = [
                "--psm 6",  # Uniform block of text
                "--psm 7",  # Single text line
                "--psm 8",  # Single word
                "--psm 13", # Raw line (no character segmentation)
            ]
            
            for config in configs:
                text = pytesseract.image_to_string(processed_image, config=config).strip()
                if text:
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    if lines:
                        print(f"  PSM {config.split()[-1]}: {lines}")
                        
                        # Check for Continue-related text
                        for line in lines:
                            if any(word in line.lower() for word in ['continue', 'cancel', 'next', 'proceed']):
                                print(f"  🎯 FOUND RELEVANT TEXT: '{line}'")
        
        except Exception as e:
            print(f"  ❌ OCR failed for {method_name}: {e}")
    
    # Try to detect button-like shapes
    print(f"\n--- Button Detection ---")
    edges = cv2.Canny(center_region, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    button_candidates = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)
        
        # Filter for button-like rectangles
        aspect_ratio = w / h if h > 0 else 0
        if (50 < w < 200 and 20 < h < 60 and 
            1.5 < aspect_ratio < 6 and area > 500):
            button_candidates.append((x, y, w, h, area))
    
    print(f"🔲 Found {len(button_candidates)} button-like shapes:")
    for i, (x, y, w, h, area) in enumerate(sorted(button_candidates, key=lambda x: x[4], reverse=True)):
        print(f"  {i+1}. Position: ({x}, {y}), Size: {w}x{h}, Area: {area}")

def main():
    """Main analysis function."""
    print("🔍 Enhanced Continue Button Detection Analysis")
    print("=" * 50)
    
    if not HAS_TESSERACT:
        print("⚠️ Installing tesseract for better OCR analysis...")
        try:
            import subprocess
            result = subprocess.run(["sudo", "apt", "install", "-y", "tesseract-ocr"], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Tesseract installed successfully")
                global HAS_TESSERACT
                HAS_TESSERACT = True
                import pytesseract
            else:
                print(f"❌ Failed to install tesseract: {result.stderr}")
        except Exception as e:
            print(f"❌ Error installing tesseract: {e}")
    
    # Analyze the debug images
    debug_images = [
        "tmp/debug_attempt_1.png",
        "tmp/debug_attempt_2.png", 
        "tmp/debug_attempt_3.png"
    ]
    
    for image_path in debug_images:
        analyze_image(image_path)
    
    print("\n" + "="*50)
    print("💡 RECOMMENDATIONS:")
    print("1. Check if Continue button text is clearly visible")
    print("2. Try different VS Code themes (dark/light)")
    print("3. Ensure button contrast is high")
    print("4. Check if button text is exactly 'Continue'")
    print("5. Look for button styling (borders, background)")

if __name__ == "__main__":
    main()
