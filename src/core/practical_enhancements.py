#!/usr/bin/env python3
"""
Practical enhancements for button detection that can be integrated immediately.
Focuses on proven techniques that improve accuracy without complex dependencies.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

try:
    import cv2
    from PIL import Image, ImageEnhance, ImageFilter

    HAS_CORE_DEPS = True
except ImportError:
    HAS_CORE_DEPS = False

try:
    import easyocr

    HAS_EASYOCR = True
except ImportError:
    HAS_EASYOCR = False


class PracticalEnhancements:
    """Practical enhancements that can be added to existing button_finder.py"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize EasyOCR if available
        if HAS_EASYOCR and config.get("use_easyocr", True):
            try:
                gpu_enabled = config.get("use_gpu", False)
                self.easyocr_reader = easyocr.Reader(["en"], gpu=gpu_enabled)
                self.logger.info("✅ EasyOCR initialized")
            except Exception as e:
                self.logger.warning(f"EasyOCR setup failed: {e}")
                self.easyocr_reader = None
        else:
            self.easyocr_reader = None

    def enhance_image_preprocessing(self, image: Image.Image) -> Image.Image:
        """Enhanced image preprocessing for better detection."""
        if not HAS_CORE_DEPS:
            return image

        try:
            # Convert to RGB if needed
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Enhance contrast (helps with low-contrast buttons)
            contrast_enhancer = ImageEnhance.Contrast(image)
            image = contrast_enhancer.enhance(1.2)

            # Enhance sharpness (helps with text detection)
            sharpness_enhancer = ImageEnhance.Sharpness(image)
            image = sharpness_enhancer.enhance(1.1)

            # Optional: Reduce noise with slight blur
            if self.config.get("reduce_noise", False):
                image = image.filter(ImageFilter.GaussianBlur(radius=0.5))

            return image

        except Exception as e:
            self.logger.warning(f"Image preprocessing error: {e}")
            return image

    def detect_with_easyocr(
        self, image: Image.Image, window_x: int = 0, window_y: int = 0
    ) -> List[Dict]:
        """EasyOCR detection - often more accurate than Tesseract."""
        if not self.easyocr_reader:
            return []

        try:
            # Convert to numpy array
            img_array = np.array(image)

            # Detect text
            results = self.easyocr_reader.readtext(img_array)

            buttons = []
            # Expanded continue patterns for better coverage
            continue_patterns = [
                "continue",
                "next",
                "proceed",
                "go",
                "submit",
                "继续",
                "continuar",
                "suivant",
                "weiter",
                "продолжить",
                "続ける",
            ]

            for bbox, text, confidence in results:
                text_clean = text.lower().strip()

                # More flexible text matching
                if any(pattern in text_clean for pattern in continue_patterns):
                    min_confidence = self.config.get("easyocr_confidence", 0.6)
                    if confidence >= min_confidence:
                        # Extract coordinates
                        x_coords = [point[0] for point in bbox]
                        y_coords = [point[1] for point in bbox]

                        x = int(min(x_coords)) + window_x
                        y = int(min(y_coords)) + window_y
                        width = int(max(x_coords) - min(x_coords))
                        height = int(max(y_coords) - min(y_coords))

                        # Add padding for easier clicking
                        padding = 8
                        x = max(0, x - padding)
                        y = max(0, y - padding)
                        width += 2 * padding
                        height += 2 * padding

                        buttons.append(
                            {
                                "x": x,
                                "y": y,
                                "width": width,
                                "height": height,
                                "confidence": confidence,
                                "method": "easyocr",
                                "text": text,
                                "center_x": x + width // 2,
                                "center_y": y + height // 2,
                            }
                        )

            return buttons

        except Exception as e:
            self.logger.error(f"EasyOCR detection error: {e}")
            return []

    def enhanced_color_detection(
        self, image: Image.Image, window_x: int = 0, window_y: int = 0
    ) -> List[Dict]:
        """Enhanced color detection with better VS Code theme support."""
        if not HAS_CORE_DEPS:
            return []

        try:
            # Convert to OpenCV format
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)

            buttons = []

            # Enhanced VS Code color ranges
            color_ranges = {
                "primary_blue": ([100, 50, 50], [130, 255, 255]),
                "github_blue": ([205, 50, 50], [215, 255, 255]),
                "hover_blue": ([110, 60, 60], [140, 255, 255]),
                "accent_blue": ([200, 100, 100], [220, 255, 255]),
                # Dark theme buttons
                "dark_blue": ([95, 40, 40], [125, 255, 200]),
                # Light theme buttons
                "light_blue": ([105, 80, 80], [135, 255, 255]),
            }

            for color_name, (lower, upper) in color_ranges.items():
                mask = cv2.inRange(hsv, np.array(lower), np.array(upper))

                # Clean up the mask
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

                # Find contours
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for contour in contours:
                    area = cv2.contourArea(contour)

                    # Filter by reasonable button size
                    if 300 <= area <= 8000:
                        x, y, w, h = cv2.boundingRect(contour)
                        aspect_ratio = w / h

                        # Button-like aspect ratio
                        if 1.5 <= aspect_ratio <= 4.5:
                            # Calculate confidence based on size and shape
                            size_score = min(1.0, area / 3000)
                            shape_score = min(1.0, aspect_ratio / 3.0)
                            confidence = 0.4 + size_score * 0.3 + shape_score * 0.2

                            buttons.append(
                                {
                                    "x": x + window_x,
                                    "y": y + window_y,
                                    "width": w,
                                    "height": h,
                                    "confidence": confidence,
                                    "method": f"enhanced_color_{color_name}",
                                    "center_x": x + w // 2 + window_x,
                                    "center_y": y + h // 2 + window_y,
                                    "color_type": color_name,
                                    "area": area,
                                }
                            )

            return buttons

        except Exception as e:
            self.logger.error(f"Enhanced color detection error: {e}")
            return []

    def smart_region_detection(
        self, image: Image.Image, window_x: int = 0, window_y: int = 0
    ) -> List[Dict]:
        """Focus detection on likely button areas."""
        if not HAS_CORE_DEPS:
            return []

        width, height = image.size
        buttons = []

        # Define regions where Continue buttons are likely to appear
        likely_regions = [
            # Bottom right (most common for Continue buttons)
            {
                "x": int(width * 0.6),
                "y": int(height * 0.7),
                "w": int(width * 0.4),
                "h": int(height * 0.3),
                "priority": 0.9,
            },
            # Bottom center
            {
                "x": int(width * 0.3),
                "y": int(height * 0.8),
                "w": int(width * 0.4),
                "h": int(height * 0.2),
                "priority": 0.7,
            },
            # Right side middle
            {
                "x": int(width * 0.7),
                "y": int(height * 0.4),
                "w": int(width * 0.3),
                "h": int(height * 0.3),
                "priority": 0.6,
            },
        ]

        for region in likely_regions:
            try:
                # Crop image to region
                crop_box = (
                    region["x"],
                    region["y"],
                    region["x"] + region["w"],
                    region["y"] + region["h"],
                )
                cropped = image.crop(crop_box)

                # Run enhanced detection on cropped region
                region_buttons = []

                # Try EasyOCR on this region
                if self.easyocr_reader:
                    ocr_buttons = self.detect_with_easyocr(
                        cropped, window_x + region["x"], window_y + region["y"]
                    )
                    region_buttons.extend(ocr_buttons)

                # Try enhanced color detection
                color_buttons = self.enhanced_color_detection(
                    cropped, window_x + region["x"], window_y + region["y"]
                )
                region_buttons.extend(color_buttons)

                # Boost confidence for buttons in high-priority regions
                for button in region_buttons:
                    button["confidence"] *= region["priority"]
                    button["region_priority"] = region["priority"]

                buttons.extend(region_buttons)

            except Exception as e:
                self.logger.warning(f"Region detection error: {e}")
                continue

        return buttons

    def adaptive_threshold_detection(
        self, image: Image.Image, window_x: int = 0, window_y: int = 0
    ) -> List[Dict]:
        """Use adaptive thresholding to find button-like shapes."""
        if not HAS_CORE_DEPS:
            return []

        try:
            # Convert to grayscale
            img_gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

            # Apply adaptive threshold
            thresh = cv2.adaptiveThreshold(
                img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )

            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            buttons = []
            for contour in contours:
                area = cv2.contourArea(contour)

                # Filter by area
                if 400 <= area <= 6000:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h

                    # Button-like aspect ratio and size
                    if 1.2 <= aspect_ratio <= 4.0 and 15 <= h <= 40:
                        # Calculate confidence
                        perimeter = cv2.arcLength(contour, True)
                        circularity = 4 * np.pi * area / (perimeter * perimeter)
                        confidence = min(0.7, 0.3 + circularity * 0.4)

                        buttons.append(
                            {
                                "x": x + window_x,
                                "y": y + window_y,
                                "width": w,
                                "height": h,
                                "confidence": confidence,
                                "method": "adaptive_threshold",
                                "center_x": x + w // 2 + window_x,
                                "center_y": y + h // 2 + window_y,
                                "circularity": circularity,
                            }
                        )

            return buttons

        except Exception as e:
            self.logger.error(f"Adaptive threshold detection error: {e}")
            return []

    def intelligent_deduplication(
        self, all_buttons: List[Dict], overlap_threshold: float = 0.5
    ) -> List[Dict]:
        """Smart deduplication that considers method confidence."""
        if not all_buttons:
            return []

        # Sort by confidence (highest first)
        sorted_buttons = sorted(all_buttons, key=lambda b: b["confidence"], reverse=True)

        final_buttons = []

        for button in sorted_buttons:
            is_duplicate = False

            for existing in final_buttons:
                overlap = self._calculate_overlap_ratio(button, existing)

                if overlap > overlap_threshold:
                    # If significant overlap, keep the higher confidence one
                    if button["confidence"] > existing["confidence"] * 1.1:
                        # Replace existing with higher confidence button
                        final_buttons.remove(existing)
                        final_buttons.append(button)
                    is_duplicate = True
                    break

            if not is_duplicate:
                final_buttons.append(button)

        return final_buttons

    def _calculate_overlap_ratio(self, btn1: Dict, btn2: Dict) -> float:
        """Calculate overlap ratio between two button rectangles."""
        # Get coordinates
        x1, y1, w1, h1 = btn1["x"], btn1["y"], btn1["width"], btn1["height"]
        x2, y2, w2, h2 = btn2["x"], btn2["y"], btn2["width"], btn2["height"]

        # Calculate intersection
        left = max(x1, x2)
        top = max(y1, y2)
        right = min(x1 + w1, x2 + w2)
        bottom = min(y1 + h1, y2 + h2)

        if right <= left or bottom <= top:
            return 0.0

        intersection = (right - left) * (bottom - top)
        area1 = w1 * h1
        area2 = w2 * h2
        union = area1 + area2 - intersection

        return intersection / union if union > 0 else 0.0


# Integration example for existing button_finder.py
def integrate_enhancements(existing_button_finder):
    """Example of how to integrate these enhancements."""

    # Configuration for enhancements
    enhancement_config = {
        "use_easyocr": True,
        "use_gpu": False,
        "easyocr_confidence": 0.6,
        "reduce_noise": False,
        "smart_regions": True,
        "adaptive_threshold": True,
    }

    # Initialize enhancements
    enhancer = PracticalEnhancements(enhancement_config)

    def enhanced_find_continue_buttons(self, image, window_x=0, window_y=0):
        """Enhanced version of find_continue_buttons method."""
        all_buttons = []

        # Preprocess image
        enhanced_image = enhancer.enhance_image_preprocessing(image)

        # Original detection methods
        original_buttons = self._original_find_continue_buttons(enhanced_image, window_x, window_y)
        all_buttons.extend(original_buttons)

        # New enhancement methods
        if enhancement_config.get("use_easyocr"):
            easyocr_buttons = enhancer.detect_with_easyocr(enhanced_image, window_x, window_y)
            all_buttons.extend(easyocr_buttons)

        if enhancement_config.get("smart_regions"):
            region_buttons = enhancer.smart_region_detection(enhanced_image, window_x, window_y)
            all_buttons.extend(region_buttons)

        if enhancement_config.get("adaptive_threshold"):
            threshold_buttons = enhancer.adaptive_threshold_detection(
                enhanced_image, window_x, window_y
            )
            all_buttons.extend(threshold_buttons)

        # Enhanced color detection
        color_buttons = enhancer.enhanced_color_detection(enhanced_image, window_x, window_y)
        all_buttons.extend(color_buttons)

        # Smart deduplication
        final_buttons = enhancer.intelligent_deduplication(all_buttons)

        return final_buttons

    return enhanced_find_continue_buttons


# Example usage and installation instructions
INSTALLATION_GUIDE = """
# Enhanced Button Detection - Installation Guide

## Quick Setup (Minimal Dependencies)
pip install easyocr

## Full Setup (All Features)
pip install easyocr opencv-python pillow
pip install scikit-image  # For advanced edge detection
pip install ultralytics   # For YOLO (optional, requires more setup)

## GPU Acceleration (Optional)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

## Integration Steps:
1. Copy practical_enhancements.py to your src/core/ directory
2. Import PracticalEnhancements in your button_finder.py
3. Add enhancement config to your default.json
4. Integrate enhanced methods into existing detection pipeline

## Recommended Config Addition:
{
  "enhancements": {
    "use_easyocr": true,
    "use_gpu": false,
    "easyocr_confidence": 0.6,
    "smart_regions": true,
    "adaptive_threshold": true,
    "image_preprocessing": true
  }
}
"""
