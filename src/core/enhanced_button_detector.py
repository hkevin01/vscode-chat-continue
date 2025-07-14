#!/usr/bin/env python3
"""
Enhanced button detection using advanced computer vision techniques.
Integrates multiple detection methods for improved accuracy.
"""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Core dependencies
try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False

try:
    from PIL import Image, ImageEnhance, ImageFilter
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Enhanced OCR
try:
    import easyocr
    HAS_EASYOCR = True
except ImportError:
    HAS_EASYOCR = False

# Advanced image processing
try:
    from skimage import feature, filters, measure, morphology
    HAS_SKIMAGE = True
except ImportError:
    HAS_SKIMAGE = False

# Machine learning
try:
    from ultralytics import YOLO
    HAS_YOLO = True
except ImportError:
    HAS_YOLO = False


@dataclass
class EnhancedButtonLocation:
    """Enhanced button location with additional metadata."""
    x: int
    y: int
    width: int
    height: int
    confidence: float
    method: str
    text: Optional[str] = None
    color_info: Optional[Dict] = None
    features: Optional[Dict] = None
    
    @property
    def center(self) -> Tuple[int, int]:
        """Get center coordinates."""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    @property
    def area(self) -> int:
        """Get button area."""
        return self.width * self.height
    
    @property
    def aspect_ratio(self) -> float:
        """Get aspect ratio."""
        return self.width / self.height if self.height > 0 else 0


class EnhancedButtonDetector:
    """Advanced button detection with multiple CV techniques."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.cache = {}
        self.max_cache_size = config.get('cache_size', 50)
        
        # Initialize detection modules
        self._init_detection_modules()
        
    def _init_detection_modules(self):
        """Initialize available detection modules."""
        self.available_methods = []
        
        if HAS_EASYOCR and self.config.get('use_easyocr', True):
            try:
                self.easyocr_reader = easyocr.Reader(['en'], gpu=self.config.get('use_gpu', False))
                self.available_methods.append('easyocr')
                self.logger.info("✅ EasyOCR initialized")
            except Exception as e:
                self.logger.warning(f"EasyOCR initialization failed: {e}")
        
        if HAS_YOLO and self.config.get('use_yolo', False):
            try:
                self.yolo_model = YOLO('yolov8n.pt')
                self.available_methods.append('yolo')
                self.logger.info("✅ YOLO model loaded")
            except Exception as e:
                self.logger.warning(f"YOLO initialization failed: {e}")
        
        if HAS_OPENCV:
            self.available_methods.extend(['enhanced_color', 'morphology', 'contour'])
            self.logger.info("✅ OpenCV methods available")
        
        if HAS_SKIMAGE:
            self.available_methods.append('edge_detection')
            self.logger.info("✅ Scikit-image methods available")
    
    def detect_continue_buttons(self, image: Image.Image, 
                              window_x: int = 0, window_y: int = 0) -> List[EnhancedButtonLocation]:
        """Detect Continue buttons using multiple enhanced methods."""
        # Calculate image hash for caching
        image_hash = self._calculate_image_hash(image)
        
        if image_hash in self.cache:
            self.logger.debug("Using cached detection result")
            cached_buttons = self.cache[image_hash]
            # Adjust coordinates for window offset
            return [self._adjust_button_coordinates(btn, window_x, window_y) for btn in cached_buttons]
        
        # Preprocess image
        processed_image = self._preprocess_image(image)
        
        all_buttons = []
        detection_times = {}
        
        # Method 1: Enhanced EasyOCR detection
        if 'easyocr' in self.available_methods:
            start_time = time.time()
            easyocr_buttons = self._detect_with_easyocr(processed_image, window_x, window_y)
            detection_times['easyocr'] = time.time() - start_time
            all_buttons.extend(easyocr_buttons)
            self.logger.debug(f"EasyOCR found {len(easyocr_buttons)} buttons in {detection_times['easyocr']:.2f}s")
        
        # Method 2: Enhanced color detection
        if 'enhanced_color' in self.available_methods:
            start_time = time.time()
            color_buttons = self._detect_enhanced_color(processed_image, window_x, window_y)
            detection_times['enhanced_color'] = time.time() - start_time
            all_buttons.extend(color_buttons)
            self.logger.debug(f"Enhanced color found {len(color_buttons)} buttons in {detection_times['enhanced_color']:.2f}s")
        
        # Method 3: Morphological detection
        if 'morphology' in self.available_methods:
            start_time = time.time()
            morph_buttons = self._detect_morphological(processed_image, window_x, window_y)
            detection_times['morphology'] = time.time() - start_time
            all_buttons.extend(morph_buttons)
            self.logger.debug(f"Morphology found {len(morph_buttons)} buttons in {detection_times['morphology']:.2f}s")
        
        # Method 4: Edge detection (if skimage available)
        if 'edge_detection' in self.available_methods:
            start_time = time.time()
            edge_buttons = self._detect_edge_based(processed_image, window_x, window_y)
            detection_times['edge_detection'] = time.time() - start_time
            all_buttons.extend(edge_buttons)
            self.logger.debug(f"Edge detection found {len(edge_buttons)} buttons in {detection_times['edge_detection']:.2f}s")
        
        # Method 5: YOLO detection (if available)
        if 'yolo' in self.available_methods:
            start_time = time.time()
            yolo_buttons = self._detect_with_yolo(processed_image, window_x, window_y)
            detection_times['yolo'] = time.time() - start_time
            all_buttons.extend(yolo_buttons)
            self.logger.debug(f"YOLO found {len(yolo_buttons)} buttons in {detection_times['yolo']:.2f}s")
        
        # Deduplicate and rank buttons
        final_buttons = self._deduplicate_and_rank(all_buttons)
        
        # Cache results
        self._cache_results(image_hash, final_buttons, window_x, window_y)
        
        # Log performance summary
        total_time = sum(detection_times.values())
        self.logger.info(f"🎯 Enhanced detection: {len(final_buttons)} buttons found in {total_time:.2f}s using {len(detection_times)} methods")
        
        return final_buttons
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better detection."""
        if not self.config.get('preprocessing', {}).get('enabled', True):
            return image
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Enhance contrast
        if self.config.get('preprocessing', {}).get('enhance_contrast', True):
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)
        
        # Enhance sharpness
        if self.config.get('preprocessing', {}).get('enhance_sharpness', True):
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.1)
        
        # Gaussian blur for noise reduction
        if self.config.get('preprocessing', {}).get('gaussian_blur', False):
            image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        return image
    
    def _detect_with_easyocr(self, image: Image.Image, 
                           window_x: int, window_y: int) -> List[EnhancedButtonLocation]:
        """Detect buttons using EasyOCR."""
        if not hasattr(self, 'easyocr_reader'):
            return []
        
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Detect text
            results = self.easyocr_reader.readtext(img_array)
            
            buttons = []
            continue_patterns = ['continue', 'next', 'proceed', '继续', 'continuar']
            
            for (bbox, text, confidence) in results:
                text_lower = text.lower().strip()
                
                # Check if text matches continue patterns
                if any(pattern in text_lower for pattern in continue_patterns):
                    if confidence >= self.config.get('easyocr_confidence', 0.7):
                        # Extract coordinates
                        x_coords = [point[0] for point in bbox]
                        y_coords = [point[1] for point in bbox]
                        
                        x = int(min(x_coords)) + window_x
                        y = int(min(y_coords)) + window_y
                        width = int(max(x_coords) - min(x_coords))
                        height = int(max(y_coords) - min(y_coords))
                        
                        # Add padding for clickable area
                        padding = 5
                        x = max(0, x - padding)
                        y = max(0, y - padding)
                        width += 2 * padding
                        height += 2 * padding
                        
                        button = EnhancedButtonLocation(
                            x=x, y=y, width=width, height=height,
                            confidence=confidence,
                            method='easyocr',
                            text=text,
                            features={'ocr_bbox': bbox}
                        )
                        buttons.append(button)
            
            return buttons
            
        except Exception as e:
            self.logger.error(f"EasyOCR detection error: {e}")
            return []
    
    def _detect_enhanced_color(self, image: Image.Image, 
                             window_x: int, window_y: int) -> List[EnhancedButtonLocation]:
        """Enhanced color-based button detection."""
        if not HAS_OPENCV:
            return []
        
        try:
            # Convert to OpenCV format
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
            
            buttons = []
            
            # VS Code button color ranges (enhanced)
            color_ranges = {
                'primary_blue': {
                    'hsv_range': ([100, 50, 50], [130, 255, 255]),
                    'confidence_boost': 0.2
                },
                'accent_blue': {
                    'hsv_range': ([200, 100, 100], [220, 255, 255]),
                    'confidence_boost': 0.15
                },
                'hover_blue': {
                    'hsv_range': ([110, 60, 60], [140, 255, 255]),
                    'confidence_boost': 0.1
                },
                'github_blue': {
                    'hsv_range': ([205, 50, 50], [215, 255, 255]),
                    'confidence_boost': 0.25
                }
            }
            
            for color_name, color_info in color_ranges.items():
                lower, upper = color_info['hsv_range']
                mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
                
                # Morphological operations to clean up the mask
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                
                # Find contours
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    # Filter contours by area and aspect ratio
                    area = cv2.contourArea(contour)
                    if area < 200 or area > 10000:  # Reasonable button size
                        continue
                    
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    
                    # Button-like aspect ratio
                    if 0.5 <= aspect_ratio <= 5.0:
                        # Calculate confidence based on area and color match
                        confidence = min(0.9, 0.5 + color_info['confidence_boost'] + (area / 5000) * 0.2)
                        
                        button = EnhancedButtonLocation(
                            x=x + window_x, y=y + window_y, width=w, height=h,
                            confidence=confidence,
                            method=f'enhanced_color_{color_name}',
                            color_info={'color_type': color_name, 'area': area, 'aspect_ratio': aspect_ratio}
                        )
                        buttons.append(button)
            
            return buttons
            
        except Exception as e:
            self.logger.error(f"Enhanced color detection error: {e}")
            return []
    
    def _detect_morphological(self, image: Image.Image, 
                            window_x: int, window_y: int) -> List[EnhancedButtonLocation]:
        """Morphological button detection."""
        if not HAS_OPENCV:
            return []
        
        try:
            # Convert to grayscale
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(img_cv, (5, 5), 0)
            
            # Adaptive threshold
            thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY, 11, 2)
            
            # Morphological operations to find button-like shapes
            kernel_rect = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 3))
            morphed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel_rect)
            
            # Find contours
            contours, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            buttons = []
            for contour in contours:
                # Filter by area
                area = cv2.contourArea(contour)
                if area < 300 or area > 15000:
                    continue
                
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                
                # Button-like properties
                if 1.5 <= aspect_ratio <= 4.0 and h >= 15 and h <= 50:
                    # Calculate confidence based on shape properties
                    hull = cv2.convexHull(contour)
                    hull_area = cv2.contourArea(hull)
                    solidity = area / hull_area if hull_area > 0 else 0
                    
                    confidence = min(0.8, 0.3 + solidity * 0.4 + (aspect_ratio / 4.0) * 0.1)
                    
                    button = EnhancedButtonLocation(
                        x=x + window_x, y=y + window_y, width=w, height=h,
                        confidence=confidence,
                        method='morphological',
                        features={'solidity': solidity, 'hull_area': hull_area, 'area': area}
                    )
                    buttons.append(button)
            
            return buttons
            
        except Exception as e:
            self.logger.error(f"Morphological detection error: {e}")
            return []
    
    def _detect_edge_based(self, image: Image.Image, 
                         window_x: int, window_y: int) -> List[EnhancedButtonLocation]:
        """Edge-based button detection using scikit-image."""
        if not HAS_SKIMAGE:
            return []
        
        try:
            # Convert to grayscale numpy array
            img_gray = np.array(image.convert('L'))
            
            # Apply Gaussian filter
            img_smooth = filters.gaussian(img_gray, sigma=1)
            
            # Canny edge detection
            edges = feature.canny(img_smooth, sigma=1, low_threshold=0.1, high_threshold=0.2)
            
            # Close gaps in edges
            closed = morphology.closing(edges, morphology.rectangle(2, 8))
            
            # Fill holes
            filled = morphology.remove_small_holes(closed, area_threshold=100)
            
            # Label connected components
            labeled = measure.label(filled)
            regions = measure.regionprops(labeled)
            
            buttons = []
            for region in regions:
                # Filter by area and aspect ratio
                if region.area < 200 or region.area > 8000:
                    continue
                
                bbox = region.bbox  # (min_row, min_col, max_row, max_col)
                height = bbox[2] - bbox[0]
                width = bbox[3] - bbox[1]
                aspect_ratio = width / height
                
                # Button-like dimensions
                if 1.0 <= aspect_ratio <= 4.0 and 10 <= height <= 40:
                    # Calculate confidence based on region properties
                    extent = region.extent  # Ratio of region area to bounding box area
                    confidence = min(0.7, 0.3 + extent * 0.3 + (aspect_ratio / 4.0) * 0.1)
                    
                    button = EnhancedButtonLocation(
                        x=bbox[1] + window_x, y=bbox[0] + window_y, 
                        width=width, height=height,
                        confidence=confidence,
                        method='edge_detection',
                        features={'extent': extent, 'eccentricity': region.eccentricity}
                    )
                    buttons.append(button)
            
            return buttons
            
        except Exception as e:
            self.logger.error(f"Edge detection error: {e}")
            return []
    
    def _detect_with_yolo(self, image: Image.Image, 
                        window_x: int, window_y: int) -> List[EnhancedButtonLocation]:
        """YOLO-based object detection for buttons."""
        if not hasattr(self, 'yolo_model'):
            return []
        
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Run YOLO detection
            results = self.yolo_model(img_array)
            
            buttons = []
            for result in results:
                for box in result.boxes:
                    confidence = float(box.conf)
                    if confidence >= self.config.get('yolo_confidence', 0.8):
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        
                        button = EnhancedButtonLocation(
                            x=int(x1) + window_x, y=int(y1) + window_y,
                            width=int(x2 - x1), height=int(y2 - y1),
                            confidence=confidence,
                            method='yolo',
                            features={'class_id': int(box.cls), 'class_name': result.names[int(box.cls)]}
                        )
                        buttons.append(button)
            
            return buttons
            
        except Exception as e:
            self.logger.error(f"YOLO detection error: {e}")
            return []
    
    def _deduplicate_and_rank(self, buttons: List[EnhancedButtonLocation]) -> List[EnhancedButtonLocation]:
        """Deduplicate overlapping buttons and rank by confidence."""
        if not buttons:
            return []
        
        # Sort by confidence (highest first)
        sorted_buttons = sorted(buttons, key=lambda b: b.confidence, reverse=True)
        
        # Remove duplicates based on overlap
        final_buttons = []
        overlap_threshold = 0.5
        
        for button in sorted_buttons:
            is_duplicate = False
            
            for existing in final_buttons:
                overlap = self._calculate_overlap(button, existing)
                if overlap > overlap_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                final_buttons.append(button)
        
        return final_buttons
    
    def _calculate_overlap(self, btn1: EnhancedButtonLocation, btn2: EnhancedButtonLocation) -> float:
        """Calculate overlap ratio between two buttons."""
        # Calculate intersection
        x1 = max(btn1.x, btn2.x)
        y1 = max(btn1.y, btn2.y)
        x2 = min(btn1.x + btn1.width, btn2.x + btn2.width)
        y2 = min(btn1.y + btn1.height, btn2.y + btn2.height)
        
        if x2 <= x1 or y2 <= y1:
            return 0.0
        
        intersection = (x2 - x1) * (y2 - y1)
        area1 = btn1.area
        area2 = btn2.area
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_image_hash(self, image: Image.Image) -> str:
        """Calculate a simple hash for image caching."""
        # Use image size and a sample of pixels for quick hashing
        width, height = image.size
        sample_pixels = list(image.getdata())[::max(1, len(list(image.getdata())) // 100)]
        return f"{width}x{height}_{hash(tuple(sample_pixels))}"
    
    def _cache_results(self, image_hash: str, buttons: List[EnhancedButtonLocation], 
                      window_x: int, window_y: int):
        """Cache detection results."""
        # Adjust buttons to relative coordinates for caching
        relative_buttons = []
        for btn in buttons:
            relative_btn = EnhancedButtonLocation(
                x=btn.x - window_x, y=btn.y - window_y,
                width=btn.width, height=btn.height,
                confidence=btn.confidence, method=btn.method,
                text=btn.text, color_info=btn.color_info, features=btn.features
            )
            relative_buttons.append(relative_btn)
        
        # Manage cache size
        if len(self.cache) >= self.max_cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[image_hash] = relative_buttons
    
    def _adjust_button_coordinates(self, button: EnhancedButtonLocation, 
                                 window_x: int, window_y: int) -> EnhancedButtonLocation:
        """Adjust button coordinates with window offset."""
        return EnhancedButtonLocation(
            x=button.x + window_x, y=button.y + window_y,
            width=button.width, height=button.height,
            confidence=button.confidence, method=button.method,
            text=button.text, color_info=button.color_info, features=button.features
        )


# Example configuration for enhanced detection
ENHANCED_CONFIG = {
    'use_easyocr': True,
    'use_yolo': False,  # Set to True if you have YOLO model
    'use_gpu': False,   # Set to True for GPU acceleration
    'cache_size': 50,
    'easyocr_confidence': 0.7,
    'yolo_confidence': 0.8,
    'preprocessing': {
        'enabled': True,
        'enhance_contrast': True,
        'enhance_sharpness': True,
        'gaussian_blur': False
    }
}
