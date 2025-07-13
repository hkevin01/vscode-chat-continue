"""Button detection module for finding Continue buttons in VS Code."""

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import cv2
    import numpy as np
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False


@dataclass
class ButtonLocation:
    """Represents a detected button location."""
    x: int
    y: int
    width: int
    height: int
    confidence: float
    method: str
    text: Optional[str] = None
    
    @property
    def center_x(self) -> int:
        """Get the center X coordinate."""
        return self.x + self.width // 2
    
    @property
    def center_y(self) -> int:
        """Get the center Y coordinate."""
        return self.y + self.height // 2
    
    @property
    def center(self) -> Tuple[int, int]:
        """Get the center coordinates as a tuple."""
        return (self.center_x, self.center_y)


class ButtonFinder:
    """Finds Continue buttons in VS Code screenshots using multiple methods."""
    
    def __init__(self, template_dir: Optional[Path] = None):
        """Initialize the button finder.
        
        Args:
            template_dir: Directory containing button template images
        """
        self.logger = logging.getLogger(__name__)
        self.template_dir = template_dir or Path(__file__).parent.parent / "templates"
        
        # Button detection configuration
        self.continue_patterns = [
            r'\bcontinue\b',
            r'\bcontinue\s*\.\.\.',
            r'\bcontinue\s*response\b',
            r'\bkeep\s*going\b',
            r'\bmore\b',
        ]
        
        # OCR configuration with more permissive settings for better detection
        self.tesseract_config = r'--oem 3 --psm 8'  # Single word mode
        self.tesseract_config_backup = r'--oem 3 --psm 6'  # Block of text mode
        
        self._check_dependencies()
    
    def _check_dependencies(self) -> None:
        """Check which detection methods are available."""
        methods = []
        
        if HAS_OPENCV:
            methods.append("template_matching")
        if HAS_TESSERACT:
            methods.append("ocr")
        if HAS_PIL:
            methods.append("color_detection")
        
        if not methods:
            self.logger.warning("No button detection methods available!")
        else:
            self.logger.debug(f"Available detection methods: {', '.join(methods)}")
    
    def find_continue_buttons(self, image: Image.Image, 
                            window_x: int = 0, window_y: int = 0) -> List[ButtonLocation]:
        """Find all Continue buttons in an image.
        
        Args:
            image: PIL Image to search in
            window_x: X offset of the window (for absolute coordinates)
            window_y: Y offset of the window (for absolute coordinates)
            
        Returns:
            List of ButtonLocation objects
        """
        buttons = []
        
        try:
            # Check if this is a mock/fallback image (small black image from Wayland)
            if (image.width <= 100 and image.height <= 100 and 
                self._is_mock_image(image)):
                self.logger.info("🚨 Detected mock screenshot - using coordinate-based fallback")
                return self._get_coordinate_based_buttons(window_x, window_y)
            
            # Method 1: Specific Continue button detection (HIGHEST PRIORITY)
            specific_buttons = self._detect_specific_continue_button(image, window_x, window_y)
            buttons.extend(specific_buttons)
            self.logger.debug(f"Specific Continue detection found {len(specific_buttons)} buttons")
            
            # If we found high-confidence specific buttons, prioritize them heavily
            if specific_buttons:
                high_conf_specific = [b for b in specific_buttons if b.confidence > 0.9]
                if high_conf_specific:
                    self.logger.info(f"🎯 Found {len(high_conf_specific)} high-confidence Continue buttons!")
                    # Return immediately if we have very confident detections
                    return self._deduplicate_buttons(high_conf_specific)
            
            # Method 2: OCR-based text detection
            if HAS_TESSERACT:
                ocr_buttons = self._find_buttons_ocr(image, window_x, window_y)
                buttons.extend(ocr_buttons)
                self.logger.debug(f"OCR found {len(ocr_buttons)} buttons")
            
            # Method 3: Template matching
            if HAS_OPENCV:
                template_buttons = self._find_buttons_template(image, window_x, window_y)
                buttons.extend(template_buttons)
                self.logger.debug(f"Template matching found {len(template_buttons)} buttons")
            
            # Method 4: Blue button detection (high priority for VS Code)
            blue_buttons = self._find_blue_buttons(image, window_x, window_y)
            buttons.extend(blue_buttons)
            self.logger.debug(f"Blue button detection found {len(blue_buttons)} buttons")
            
            # Method 4: Color-based detection
            color_buttons = self._find_buttons_color(image, window_x, window_y)
            buttons.extend(color_buttons)
            self.logger.debug(f"Color detection found {len(color_buttons)} buttons")
            
            # Method 5: Blue rectangle fallback (when OCR unavailable)
            if not HAS_TESSERACT:
                self.logger.info("OCR not available, using blue rectangle fallback")
                fallback_buttons = self._find_blue_rectangles(image, window_x, window_y)
                buttons.extend(fallback_buttons)
                self.logger.debug(f"Blue rectangle detection found {len(fallback_buttons)} buttons")
            
            # Remove duplicates and sort by confidence
            buttons = self._filter_non_continue_buttons(buttons, 
                                                       image.width, 
                                                       image.height)
            buttons = self._deduplicate_buttons(buttons)
            buttons.sort(key=lambda b: b.confidence, reverse=True)
            
            self.logger.debug(f"Total found {len(buttons)} continue buttons after deduplication")
            
        except Exception as e:
            self.logger.error(f"Error finding buttons: {e}")
        
        return buttons
    
    def _find_buttons_ocr(self, image: Image.Image, 
                         window_x: int, window_y: int) -> List[ButtonLocation]:
        """Find buttons using OCR text detection with preprocessing.
        
        Args:
            image: PIL Image to search in
            window_x: X offset of the window
            window_y: Y offset of the window
            
        Returns:
            List of ButtonLocation objects
        """
        buttons = []
        
        if not HAS_TESSERACT:
            return buttons
        
        try:
            # Get preprocessed versions of the image
            processed_images = self._preprocess_for_ocr(image)
            self.logger.debug(f"Testing OCR on {len(processed_images)} processed versions")
            
            # Try different OCR configurations
            ocr_configs = [
                ('PSM 6 Block', '--oem 3 --psm 6'),
                ('PSM 8 Word', '--oem 3 --psm 8'),
                ('PSM 11 Sparse', '--oem 3 --psm 11'),
            ]
            
            # Test each combination of preprocessing and OCR config
            for proc_idx, proc_image in enumerate(processed_images):
                for config_name, config in ocr_configs:
                    try:
                        result = pytesseract.image_to_data(proc_image, config=config,
                                                         output_type=pytesseract.Output.DICT)
                        
                        # Count words to see if this preprocessing/config combo works
                        word_count = sum(1 for i, text in enumerate(result['text'])
                                       if len(text.strip()) > 1 and result['conf'][i] > 10)
                        
                        if word_count > 0:
                            self.logger.debug(f"Preprocessing {proc_idx} + {config_name}: {word_count} words")
                            
                            # Process the OCR results
                            found_buttons = self._process_ocr_results(result, window_x, window_y, 
                                                                    f"{config_name}_proc{proc_idx}")
                            buttons.extend(found_buttons)
                            
                    except Exception as e:
                        self.logger.debug(f"OCR error with {config_name} on preprocessing {proc_idx}: {e}")
                        continue
        except Exception as e:
            self.logger.debug(f"OCR detection error: {e}")
        
        return buttons
    
    def _find_buttons_template(self, image: Image.Image, 
                             window_x: int, window_y: int) -> List[ButtonLocation]:
        """Find buttons using template matching.
        
        Args:
            image: PIL Image to search in
            window_x: X offset of the window
            window_y: Y offset of the window
            
        Returns:
            List of ButtonLocation objects
        """
        buttons = []
        
        if not HAS_OPENCV:
            return buttons
        
        try:
            # Convert PIL image to OpenCV format
            cv_image = self._pil_to_opencv(image)
            if cv_image is None:
                return buttons
            
            # Load template images
            templates = self._load_templates()
            
            for template_name, template in templates.items():
                matches = self._match_template(cv_image, template)
                
                for match in matches:
                    x, y, w, h, confidence = match
                    
                    button = ButtonLocation(
                        x=x + window_x,
                        y=y + window_y,
                        width=w,
                        height=h,
                        confidence=confidence,
                        method=f"template_{template_name}",
                        text=template_name
                    )
                    
                    buttons.append(button)
                    
        except Exception as e:
            self.logger.debug(f"Template matching error: {e}")
        
        return buttons
    
    def _find_buttons_color(self, image: Image.Image, 
                          window_x: int, window_y: int) -> List[ButtonLocation]:
        """Find buttons using color-based detection.
        
        Args:
            image: PIL Image to search in
            window_x: X offset of the window
            window_y: Y offset of the window
            
        Returns:
            List of ButtonLocation objects
        """
        buttons = []
        
        try:
            # This is a simplified color detection approach
            # Look for common button colors (blue, gray backgrounds)
            if HAS_OPENCV:
                cv_image = self._pil_to_opencv(image)
                if cv_image is not None:
                    # Convert to HSV for better color detection
                    hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
                    
                    # Define color ranges for typical VS Code buttons
                    button_ranges = [
                        # Blue buttons (primary action) - VS Code blue #007ACC
                        ((100, 100, 100), (130, 255, 255)),
                        # Darker blue buttons
                        ((90, 80, 80), (140, 255, 200)),
                        # Gray buttons (secondary action)
                        ((0, 0, 100), (180, 30, 200)),
                    ]
                    
                    for i, (lower, upper) in enumerate(button_ranges):
                        mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
                        
                        # Find contours
                        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, 
                                                     cv2.CHAIN_APPROX_SIMPLE)
                        
                        for contour in contours:
                            area = cv2.contourArea(contour)
                            
                            # Filter by area (typical button size)
                            if 500 < area < 10000:
                                x, y, w, h = cv2.boundingRect(contour)
                                
                                # Check aspect ratio (buttons are usually wider than tall)
                                if 0.3 < h / w < 3.0:
                                    button = ButtonLocation(
                                        x=x + window_x,
                                        y=y + window_y,
                                        width=w,
                                        height=h,
                                        confidence=0.3,  # Lower confidence for color detection
                                        method=f"color_{i}",
                                        text=None
                                    )
                                    
                                    buttons.append(button)
                                    
        except Exception as e:
            self.logger.debug(f"Color detection error: {e}")
        
        return buttons
    
    def _matches_continue_pattern(self, text: str) -> bool:
        """Check if text matches continue button patterns.
        
        Args:
            text: Text to check
            
        Returns:
            True if text matches a continue pattern
        """
        for pattern in self.continue_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _pil_to_opencv(self, image: Image.Image) -> Optional[np.ndarray]:
        """Convert PIL Image to OpenCV format.
        
        Args:
            image: PIL Image
            
        Returns:
            OpenCV image array or None
        """
        try:
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            numpy_image = np.array(image)
            opencv_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)
            return opencv_image
            
        except Exception as e:
            self.logger.debug(f"Image conversion error: {e}")
            return None
    
    def _load_templates(self) -> Dict[str, np.ndarray]:
        """Load button template images.
        
        Returns:
            Dictionary of template name to OpenCV image
        """
        templates = {}
        
        try:
            if not self.template_dir.exists():
                self.logger.debug(f"Template directory {self.template_dir} does not exist")
                return templates
            
            for template_file in self.template_dir.glob("*.png"):
                try:
                    template = cv2.imread(str(template_file))
                    if template is not None:
                        templates[template_file.stem] = template
                except Exception as e:
                    self.logger.debug(f"Error loading template {template_file}: {e}")
                    
        except Exception as e:
            self.logger.debug(f"Error loading templates: {e}")
        
        return templates
    
    def _match_template(self, image: np.ndarray, 
                       template: np.ndarray, 
                       threshold: float = 0.7) -> List[Tuple[int, int, int, int, float]]:
        """Match a template in an image.
        
        Args:
            image: Source image
            template: Template to match
            threshold: Matching threshold (0-1)
            
        Returns:
            List of (x, y, width, height, confidence) tuples
        """
        matches = []
        
        try:
            result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= threshold)
            
            template_h, template_w = template.shape[:2]
            
            for pt in zip(*locations[::-1]):
                confidence = result[pt[1], pt[0]]
                matches.append((pt[0], pt[1], template_w, template_h, confidence))
                
        except Exception as e:
            self.logger.debug(f"Template matching error: {e}")
        
        return matches
    
    def _deduplicate_buttons(self, buttons: List[ButtonLocation], 
                           overlap_threshold: float = 0.5) -> List[ButtonLocation]:
        """Remove duplicate/overlapping button detections.
        
        Args:
            buttons: List of button locations
            overlap_threshold: Minimum overlap ratio to consider duplicate
            
        Returns:
            Deduplicated list of buttons
        """
        if not buttons:
            return buttons
        
        # Sort by confidence (highest first)
        sorted_buttons = sorted(buttons, key=lambda b: b.confidence, reverse=True)
        
        filtered_buttons = []
        
        for button in sorted_buttons:
            # Check if this button overlaps significantly with any existing button
            is_duplicate = False
            
            for existing in filtered_buttons:
                overlap = self._calculate_overlap(button, existing)
                if overlap > overlap_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered_buttons.append(button)
        
        return filtered_buttons
    
    def _calculate_overlap(self, button1: ButtonLocation, 
                          button2: ButtonLocation) -> float:
        """Calculate overlap ratio between two buttons.
        
        Args:
            button1: First button
            button2: Second button
            
        Returns:
            Overlap ratio (0-1)
        """
        # Calculate intersection
        x1 = max(button1.x, button2.x)
        y1 = max(button1.y, button2.y)
        x2 = min(button1.x + button1.width, button2.x + button2.width)
        y2 = min(button1.y + button1.height, button2.y + button2.height)
        
        if x2 <= x1 or y2 <= y1:
            return 0.0
        
        intersection = (x2 - x1) * (y2 - y1)
        
        # Calculate areas
        area1 = button1.width * button1.height
        area2 = button2.width * button2.height
        
        # Use the smaller area for overlap calculation
        smaller_area = min(area1, area2)
        
        return intersection / smaller_area if smaller_area > 0 else 0.0
    
    def _find_blue_rectangles(self, image: Image.Image, 
                            window_x: int, window_y: int) -> List[ButtonLocation]:
        """Find blue rectangular areas that could be Continue buttons.
        
        This is a fallback method when OCR is not available.
        
        Args:
            image: PIL Image to search in
            window_x: X offset of the window
            window_y: Y offset of the window
            
        Returns:
            List of ButtonLocation objects
        """
        buttons = []
        
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            width, height = image.size
            
            # Define VS Code blue color (#007ACC) with some tolerance
            target_blue = (0, 122, 204)  # VS Code blue
            tolerance = 50
            
            # Scan image for blue rectangular regions
            for y in range(0, height - 20, 10):  # Skip small increments
                for x in range(0, width - 50, 10):  # Skip small increments
                    pixel = image.getpixel((x, y))
                    
                    # Check if pixel is close to VS Code blue
                    if (abs(pixel[0] - target_blue[0]) < tolerance and
                        abs(pixel[1] - target_blue[1]) < tolerance and 
                        abs(pixel[2] - target_blue[2]) < tolerance):
                        
                        # Found blue pixel, try to find the button bounds
                        button_bounds = self._trace_blue_rectangle(image, x, y, target_blue, tolerance)
                        
                        if button_bounds:
                            bx, by, bw, bh = button_bounds
                            
                            # Check if it's button-sized
                            if (40 <= bw <= 200 and 20 <= bh <= 60 and 
                                1.5 <= bw/bh <= 6.0):  # Reasonable button proportions
                                
                                button = ButtonLocation(
                                    x=bx + window_x,
                                    y=by + window_y,
                                    width=bw,
                                    height=bh,
                                    confidence=0.4,  # Medium confidence for color match
                                    method="blue_rectangle",
                                    text="potential_continue"
                                )
                                
                                buttons.append(button)
                                self.logger.debug(f"Found blue rectangle at ({bx}, {by}) size {bw}x{bh}")
        
        except Exception as e:
            self.logger.debug(f"Blue rectangle detection error: {e}")
        
        return buttons
    
    def _trace_blue_rectangle(self, image: Image.Image, start_x: int, start_y: int,
                            target_color: tuple, tolerance: int) -> Optional[tuple]:
        """Trace the bounds of a blue rectangular region.
        
        Args:
            image: PIL Image
            start_x: Starting X coordinate
            start_y: Starting Y coordinate  
            target_color: Target RGB color
            tolerance: Color tolerance
            
        Returns:
            (x, y, width, height) or None
        """
        try:
            width, height = image.size
            
            # Find left and right bounds
            left = start_x
            right = start_x
            
            # Expand right
            while (right < width - 1 and 
                   self._color_matches(image.getpixel((right + 1, start_y)), 
                                     target_color, tolerance)):
                right += 1
            
            # Expand left  
            while (left > 0 and
                   self._color_matches(image.getpixel((left - 1, start_y)),
                                     target_color, tolerance)):
                left -= 1
            
            # Find top and bottom bounds
            top = start_y
            bottom = start_y
            
            # Expand down
            while (bottom < height - 1 and
                   self._color_matches(image.getpixel((start_x, bottom + 1)),
                                     target_color, tolerance)):
                bottom += 1
            
            # Expand up
            while (top > 0 and
                   self._color_matches(image.getpixel((start_x, top - 1)),
                                     target_color, tolerance)):
                top -= 1
            
            return (left, top, right - left + 1, bottom - top + 1)
            
        except Exception:
            return None
    
    def _color_matches(self, pixel: tuple, target: tuple, tolerance: int) -> bool:
        """Check if a pixel color matches target within tolerance.
        
        Args:
            pixel: RGB pixel tuple
            target: Target RGB color tuple
            tolerance: Color tolerance
            
        Returns:
            True if colors match within tolerance
        """
        return (abs(pixel[0] - target[0]) < tolerance and
                abs(pixel[1] - target[1]) < tolerance and
                abs(pixel[2] - target[2]) < tolerance)
    
    def _preprocess_for_ocr(self, image: Image.Image) -> List[Image.Image]:
        """Preprocess image to improve OCR detection.
        
        Args:
            image: Original PIL Image
            
        Returns:
            List of preprocessed images to try OCR on
        """
        processed_images = [image]  # Always include original
        
        if not HAS_OPENCV:
            return processed_images
            
        try:
            # Convert PIL to OpenCV
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            opencv_image = np.array(image)
            opencv_image = cv2.cvtColor(opencv_image, cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            
            # 1. High contrast binary threshold
            _, high_thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
            processed_images.append(Image.fromarray(high_thresh))
            
            # 2. Inverted binary (white text on dark background)
            _, inv_thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
            processed_images.append(Image.fromarray(inv_thresh))
            
            # 3. Adaptive threshold for varying lighting
            adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv2.THRESH_BINARY, 11, 2)
            processed_images.append(Image.fromarray(adaptive))
            
            # 4. Enhance contrast and then threshold
            enhanced = cv2.convertScaleAbs(gray, alpha=2.0, beta=50)
            _, enh_thresh = cv2.threshold(enhanced, 150, 255, cv2.THRESH_BINARY)
            processed_images.append(Image.fromarray(enh_thresh))
            
            # 5. Edge detection with dilation (for button outlines)
            edges = cv2.Canny(gray, 50, 150)
            kernel = np.ones((2, 2), np.uint8)
            dilated = cv2.dilate(edges, kernel, iterations=1)
            processed_images.append(Image.fromarray(dilated))
            
        except Exception as e:
            self.logger.debug(f"Image preprocessing error: {e}")
        
        return processed_images

    def _try_multiple_ocr_configs(self, image: Image.Image) -> Dict[str, Any]:
        """Try multiple OCR configurations and return the best result.
        
        Args:
            image: PIL Image to process
            
        Returns:
            Best OCR result dictionary
        """
        configs = [
            ('PSM 6 Block', '--oem 3 --psm 6'),
            ('PSM 8 Word', '--oem 3 --psm 8'), 
            ('PSM 3 Auto', '--oem 3 --psm 3'),
            ('PSM 11 Sparse', '--oem 3 --psm 11'),
            ('PSM 7 Line', '--oem 3 --psm 7'),
        ]
        
        best_result = None
        best_word_count = 0
        
        for name, config in configs:
            try:
                result = pytesseract.image_to_data(image, config=config,
                                                 output_type=pytesseract.Output.DICT)
                
                # Count meaningful words (length > 1, confidence > 10)
                word_count = sum(1 for i, text in enumerate(result['text']) 
                               if len(text.strip()) > 1 and result['conf'][i] > 10)
                
                self.logger.debug(f"OCR {name}: {word_count} meaningful words")
                
                if word_count > best_word_count:
                    best_word_count = word_count
                    best_result = result
                    self.logger.debug(f"New best OCR result: {name}")
                    
            except Exception as e:
                self.logger.debug(f"OCR config {name} failed: {e}")
                
        return best_result or {'text': [], 'conf': [], 'left': [], 'top': [], 'width': [], 'height': []}
    
    def _find_blue_buttons(self, image: Image.Image, window_x: int, window_y: int) -> List[ButtonLocation]:
        """Find blue buttons with white text (like VS Code Continue buttons).
        
        Args:
            image: PIL Image to search
            window_x: Window x offset
            window_y: Window y offset
            
        Returns:
            List of potential blue button locations
        """
        if not HAS_OPENCV:
            return []
            
        buttons = []
        
        try:
            # Convert PIL to OpenCV
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
            
            # Define blue color range for VS Code buttons
            # VS Code blue is typically around hue 210-220
            lower_blue = np.array([100, 100, 100])  # Lower HSV threshold
            upper_blue = np.array([130, 255, 255])  # Upper HSV threshold
            
            # Create mask for blue areas
            blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
            
            # Find contours of blue areas
            contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter for button-like dimensions
                aspect_ratio = w / h if h > 0 else 0
                area = cv2.contourArea(contour)
                
                # Typical Continue button: width 60-120px, height 25-40px
                if (50 < w < 150 and 20 < h < 50 and 
                    1.5 < aspect_ratio < 5 and area > 800):
                    
                    # Extract the button region for OCR
                    button_region = cv_image[y:y+h, x:x+w]
                    
                    # Convert to grayscale for better OCR
                    gray_button = cv2.cvtColor(button_region, cv2.COLOR_BGR2GRAY)
                    
                    # Invert colors (white text on blue background -> black text on white)
                    inverted = 255 - gray_button
                    
                    # Enhance contrast
                    enhanced = cv2.convertScaleAbs(inverted, alpha=2.0, beta=50)
                    
                    # Try OCR on the enhanced button region
                    if HAS_TESSERACT:
                        try:
                            # Use single word mode for button text
                            text = pytesseract.image_to_string(
                                enhanced, 
                                config='--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
                            ).strip().lower()
                            
                            if text and any(pattern in text for pattern in ['continue', 'cont', 'contin']):
                                confidence = 0.9  # High confidence for blue button with Continue text
                                
                                button = ButtonLocation(
                                    x=x,
                                    y=y,
                                    width=w,
                                    height=h,
                                    center_x=x + w // 2,
                                    center_y=y + h // 2,
                                    confidence=confidence,
                                    text=text,
                                    method="blue_button_detection"
                                )
                                buttons.append(button)
                                self.logger.debug(f"Found blue Continue button: '{text}' at ({x}, {y})")
                                
                        except Exception as ocr_error:
                            self.logger.debug(f"OCR failed for blue button at ({x}, {y}): {ocr_error}")
                    
                    else:
                        # If no OCR, still consider it a candidate based on color and shape
                        button = ButtonLocation(
                            x=x,
                            y=y,
                            width=w,
                            height=h,
                            center_x=x + w // 2,
                            center_y=y + h // 2,
                            confidence=0.6,  # Lower confidence without text verification
                            text="blue_button",
                            method="blue_color_detection"
                        )
                        buttons.append(button)
                        self.logger.debug(f"Found blue button candidate at ({x}, {y})")
                        
        except Exception as e:
            self.logger.debug(f"Blue button detection failed: {e}")
        
        return buttons

    def _process_ocr_results(self, result, window_x: int, window_y: int, method: str) -> List[ButtonLocation]:
        """Process OCR results to find Continue buttons.
        
        Args:
            result: Tesseract OCR result dictionary
            window_x: Window X offset
            window_y: Window Y offset
            method: Detection method name
            
        Returns:
            List of ButtonLocation objects
        """
        buttons = []
        
        try:
            # Look for text containing "continue" or similar patterns
            for i, text in enumerate(result['text']):
                if not text.strip():
                    continue
                
                # Check if this text matches continue patterns
                if self._matches_continue_pattern(text):
                    confidence = result['conf'][i] / 100.0 if result['conf'][i] > 0 else 0.1
                    
                    # Only consider high-confidence detections
                    if confidence > 0.3:
                        x = result['left'][i]
                        y = result['top'][i]
                        w = result['width'][i]
                        h = result['height'][i]
                        
                        # Filter out very small or very large detections
                        if 20 < w < 200 and 15 < h < 60:
                            button = ButtonLocation(
                                x=x + window_x,
                                y=y + window_y,
                                width=w,
                                height=h,
                                confidence=confidence,
                                method=method,
                                text=text.strip()
                            )
                            buttons.append(button)
                            self.logger.debug(f"Found '{text}' button at ({x}, {y}) confidence: {confidence:.2f}")
        
        except Exception as e:
            self.logger.debug(f"Error processing OCR results: {e}")
        
        return buttons

    def _is_search_field_or_top_element(self, button: ButtonLocation, 
                                        image_width: int, 
                                        image_height: int) -> bool:
        """Check if a button is likely a search field or top toolbar element.
        
        Args:
            button: Button location to check
            image_width: Width of the captured image
            image_height: Height of the captured image
            
        Returns:
            True if this appears to be a search field or top element
        """
        # Check if button is in the top area (search bar, toolbar, etc.)
        top_area_height = min(100, image_height * 0.15)  # Top 15% or 100px
        if button.y < top_area_height:
            self.logger.debug(f"Button at ({button.x}, {button.y}) is in top area "
                            f"(< {top_area_height}px), likely search/toolbar")
            return True
        
        # Check if button looks like a search field (wide and shallow)
        aspect_ratio = button.width / button.height if button.height > 0 else 0
        if aspect_ratio > 8:  # Very wide buttons are likely search fields
            self.logger.debug(f"Button at ({button.x}, {button.y}) has wide "
                            f"aspect ratio {aspect_ratio:.1f}, likely search field")
            return True
        
        # Check if button is in the left sidebar area (Explorer, etc.)
        left_sidebar_width = min(300, image_width * 0.2)  # Left 20% or 300px
        if button.x < left_sidebar_width and button.y < image_height * 0.8:
            self.logger.debug(f"Button at ({button.x}, {button.y}) is in left "
                            f"sidebar area, likely navigation")
            return True
        
        # Check if button text contains search-related terms
        if button.text:
            text_lower = button.text.lower().strip()
            search_terms = [
                'search', 'find', 'filter', 'query', 'lookup', 'locate',
                'explorer', 'files', 'folders', 'workspace', 'project',
                'extensions', 'marketplace', 'settings', 'preferences'
            ]
            
            for term in search_terms:
                if term in text_lower:
                    self.logger.debug(f"Button text '{button.text}' contains "
                                    f"search term '{term}'")
                    return True
        
        return False

    def _is_in_chat_panel_area(self, x: int, y: int, 
                              image_width: int, 
                              image_height: int) -> bool:
        """Check if coordinates are likely in the chat panel area.
        
        Args:
            x: X coordinate
            y: Y coordinate  
            image_width: Width of the captured image
            image_height: Height of the captured image
            
        Returns:
            True if coordinates are likely in chat panel
        """
        # Chat panel is typically in the right half and bottom 2/3 of screen
        right_half_start = image_width * 0.4  # Allow some margin
        bottom_two_thirds_start = image_height * 0.3
        
        in_right_area = x > right_half_start
        in_lower_area = y > bottom_two_thirds_start
        
        # Also avoid the very bottom (status bar)
        status_bar_height = 30
        not_in_status_bar = y < (image_height - status_bar_height)
        
        is_chat_area = in_right_area and in_lower_area and not_in_status_bar
        
        if is_chat_area:
            self.logger.debug(f"Position ({x}, {y}) is in chat panel area")
        else:
            self.logger.debug(f"Position ({x}, {y}) is NOT in chat panel area "
                            f"(right: {in_right_area}, lower: {in_lower_area}, "
                            f"not_status: {not_in_status_bar})")
        
        return is_chat_area

    def _detect_specific_continue_button(self, image: Image.Image, window_x: int, window_y: int) -> List[ButtonLocation]:
        """Detect the specific blue Continue button with white text.
        
        This method is optimized for the exact Continue button appearance shown in VS Code Copilot.
        
        Args:
            image: PIL Image to search
            window_x: Window x offset
            window_y: Window y offset
            
        Returns:
            List of detected Continue button locations
        """
        if not HAS_OPENCV:
            return []
            
        buttons = []
        
        try:
            # Convert PIL to OpenCV
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Convert to HSV for better blue detection
            hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
            
            # Define blue color range for the specific Continue button
            # The button appears to be a medium blue (#007ACC-like color)
            lower_blue = np.array([95, 80, 80])   # Lower HSV threshold for VS Code blue
            upper_blue = np.array([125, 255, 255]) # Upper HSV threshold for VS Code blue
            
            # Create mask for blue regions
            blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
            
            # Find contours of blue regions
            contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter by size - Continue button is typically 60-80px wide, 25-35px tall
                aspect_ratio = w / h if h > 0 else 0
                area = cv2.contourArea(contour)
                
                if (50 < w < 100 and 20 < h < 45 and 
                    1.5 < aspect_ratio < 4 and area > 800):
                    
                    # Extract the button region for OCR verification
                    button_region = cv_image[y:y+h, x:x+w]
                    
                    # Convert to grayscale for OCR
                    gray_button = cv2.cvtColor(button_region, cv2.COLOR_BGR2GRAY)
                    
                    # Invert colors to make white text black for better OCR
                    inverted = 255 - gray_button
                    
                    # Enhance contrast
                    enhanced = cv2.convertScaleAbs(inverted, alpha=2.5, beta=30)
                    
                    # Try OCR on the enhanced button region
                    if HAS_TESSERACT:
                        try:
                            # Use single word mode optimized for button text
                            config = '--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
                            text = pytesseract.image_to_string(enhanced, config=config).strip().lower()
                            
                            # Check for Continue text with some flexibility
                            if (text and any(pattern in text for pattern in 
                                           ['continue', 'contin', 'cont', 'tinue'])):
                                
                                confidence = 0.95  # Very high confidence for specific detection
                                
                                button = ButtonLocation(
                                    x=x + window_x,
                                    y=y + window_y,
                                    width=w,
                                    height=h,
                                    confidence=confidence,
                                    text=text,
                                    method="specific_continue_button"
                                )
                                buttons.append(button)
                                self.logger.info(f"🎯 Found specific Continue button: '{text}' at ({x}, {y})")
                                
                        except Exception as ocr_error:
                            self.logger.debug(f"OCR failed for specific blue button at ({x}, {y}): {ocr_error}")
                    
                    else:
                        # If no OCR, still consider it a strong candidate based on color and shape
                        if self._is_in_chat_panel_area(x, y, image.width, image.height):
                            button = ButtonLocation(
                                x=x + window_x,
                                y=y + window_y,
                                width=w,
                                height=h,
                                confidence=0.8,  # High confidence for color/shape match in chat area
                                text="blue_continue_candidate",
                                method="specific_blue_detection"
                            )
                            buttons.append(button)
                            self.logger.info(f"🔵 Found blue Continue button candidate at ({x}, {y})")
                        
        except Exception as e:
            self.logger.debug(f"Specific Continue button detection failed: {e}")
        
        return buttons

    def _filter_non_continue_buttons(self, buttons: List[ButtonLocation],
                                     image_width: int = 0,
                                     image_height: int = 0) -> List[ButtonLocation]:
        """Filter out buttons that are clearly not Continue buttons.
        
        Args:
            buttons: List of button locations to filter
            image_width: Width of captured image for position filtering
            image_height: Height of captured image for position filtering
            
        Returns:
            Filtered list of buttons
        """
        filtered = []
        
        # Words/phrases that indicate this is NOT a Continue button
        exclude_patterns = [
            r'\bsearch\b',      # Search buttons
            r'\bfind\b',        # Find buttons  
            r'\bopen\b',        # Open buttons
            r'\bfile\b',        # File buttons
            r'\bedit\b',        # Edit buttons
            r'\bview\b',        # View buttons
            r'\bhelp\b',        # Help buttons
            r'\bsettings\b',    # Settings buttons
            r'\boptions\b',     # Options buttons
            r'\bpreferences\b', # Preferences buttons
            r'\bterminal\b',    # Terminal buttons
            r'\bconsole\b',     # Console buttons
            r'\bdebug\b',       # Debug buttons
            r'\brun\b',         # Run buttons
            r'\bbuild\b',       # Build buttons
            r'\btest\b',        # Test buttons
            r'\bgit\b',         # Git buttons
            r'\bcommit\b',      # Commit buttons
            r'\bpush\b',        # Push buttons
            r'\bpull\b',        # Pull buttons
            r'\bmerge\b',       # Merge buttons
            r'\bbranch\b',      # Branch buttons
            r'\bsync\b',        # Sync buttons
            r'\brefresh\b',     # Refresh buttons
            r'\breload\b',      # Reload buttons
            r'\bclose\b',       # Close buttons
            r'\bcancel\b',      # Cancel buttons
            r'\babort\b',       # Abort buttons
            r'\bstop\b',        # Stop buttons
            r'\bpause\b',       # Pause buttons
            r'\breset\b',       # Reset buttons
            r'\bclear\b',       # Clear buttons
            r'\bdelete\b',      # Delete buttons
            r'\bremove\b',      # Remove buttons
            r'\bundo\b',        # Undo buttons
            r'\bredo\b',        # Redo buttons
            r'\bcopy\b',        # Copy buttons
            r'\bpaste\b',       # Paste buttons
            r'\bcut\b',         # Cut buttons
            r'\bselect\b',      # Select buttons
            r'\bmenu\b',        # Menu buttons
            r'\bdropdown\b',    # Dropdown buttons
            r'\bfilter\b',      # Filter buttons
            r'\bsort\b',        # Sort buttons
            r'\bexport\b',      # Export buttons
            r'\bimport\b',      # Import buttons
            r'\bsave\b',        # Save buttons (except "Save and Continue")
            r'\bload\b',        # Load buttons
            r'\bnew\b',         # New buttons
            r'\bcreate\b',      # Create buttons
            r'\badd\b',         # Add buttons
            r'\binsert\b',      # Insert buttons
            r'\bextension\b',   # Extension buttons
            r'\bplugin\b',      # Plugin buttons
            r'\bworkspace\b',   # Workspace buttons
            r'\bfolder\b',      # Folder buttons
            r'\bdirectory\b',   # Directory buttons
            r'\bpath\b',        # Path buttons
            r'\burl\b',         # URL buttons
            r'\blink\b',        # Link buttons
            r'\bgo\s+to\b',     # Go to buttons
            r'\bnavigate\b',    # Navigate buttons
            r'\bback\b',        # Back buttons
            r'\bforward\b',     # Forward buttons
            r'\bhome\b',        # Home buttons
            r'\bup\b',          # Up buttons
            r'\bdown\b',        # Down buttons
            r'\bleft\b',        # Left buttons
            r'\bright\b',       # Right buttons
            r'\bnext\b',        # Next buttons (unless "Next/Continue")
            r'\bprev\b',        # Previous buttons
            r'\bprevious\b',    # Previous buttons
            r'\bfirst\b',       # First buttons
            r'\blast\b',        # Last buttons
            r'\bbegin\b',       # Begin buttons
            r'\bend\b',         # End buttons
            r'\bstart\b',       # Start buttons (unless "Start Continue")
            r'\bfinish\b',      # Finish buttons
            r'\bcomplete\b',    # Complete buttons
            r'\bdone\b',        # Done buttons
            r'\bok\b',          # OK buttons
            r'\byes\b',         # Yes buttons
            r'\bno\b',          # No buttons
            r'\baccept\b',      # Accept buttons
            r'\bdecline\b',     # Decline buttons
            r'\bapprove\b',     # Approve buttons
            r'\breject\b',      # Reject buttons
            r'\bconfirm\b',     # Confirm buttons
            r'\bsubmit\b',      # Submit buttons
            r'\bsend\b',        # Send buttons
            r'\breceive\b',     # Receive buttons
            r'\bdownload\b',    # Download buttons
            r'\bupload\b',      # Upload buttons
            r'\binstall\b',     # Install buttons
            r'\buninstall\b',   # Uninstall buttons
            r'\bupdate\b',      # Update buttons
            r'\bupgrade\b',     # Upgrade buttons
            r'\bconfig\b',      # Config buttons
            r'\bconfigure\b',   # Configure buttons
            r'\bsetup\b',       # Setup buttons
            r'\binitialize\b',  # Initialize buttons
            r'\binit\b',        # Init buttons
            r'\benable\b',      # Enable buttons
            r'\bdisable\b',     # Disable buttons
            r'\bactivate\b',    # Activate buttons
            r'\bdeactivate\b',  # Deactivate buttons
            r'\btoggle\b',      # Toggle buttons
            r'\bswitch\b',      # Switch buttons
            r'\bchange\b',      # Change buttons
            r'\bmodify\b',      # Modify buttons
            r'\bedit\b',        # Edit buttons
            r'\bupdate\b',      # Update buttons
            r'\brenew\b',       # Renew buttons
            r'\brefresh\b',     # Refresh buttons
            r'\brestore\b',     # Restore buttons
            r'\brevert\b',      # Revert buttons
            r'\breset\b',       # Reset buttons
            r'\brestart\b',     # Restart buttons
            r'\breboot\b',      # Reboot buttons
            r'\bshutdown\b',    # Shutdown buttons
            r'\blogout\b',      # Logout buttons
            r'\bsignout\b',     # Sign out buttons
            r'\blogin\b',       # Login buttons
            r'\bsignin\b',      # Sign in buttons
            r'\bregister\b',    # Register buttons
            r'\bsignup\b',      # Sign up buttons
            r'\bsubscribe\b',   # Subscribe buttons
            r'\bunsubscribe\b', # Unsubscribe buttons
        ]
        
        for button in buttons:
            # First check if this is a search field or top element
            if (image_width > 0 and image_height > 0 and 
                self._is_search_field_or_top_element(button, image_width, 
                                                   image_height)):
                self.logger.debug(f"Excluding button at ({button.x}, "
                                f"{button.y}) - appears to be search field "
                                "or top element")
                continue
            
            # For Continue buttons, prefer those in the chat panel area
            if (image_width > 0 and image_height > 0):
                in_chat_area = self._is_in_chat_panel_area(
                    button.x, button.y, image_width, image_height)
                if not in_chat_area:
                    # If it's not in chat area and has low confidence, skip it
                    if button.confidence < 0.7:
                        self.logger.debug(f"Excluding low-confidence button "
                                        f"outside chat area: ({button.x}, "
                                        f"{button.y}) conf={button.confidence}")
                        continue
            
            if not button.text:
                # No text - could be a valid Continue button, keep it
                # But only if it's in a reasonable location
                if (image_width > 0 and image_height > 0 and 
                    not self._is_in_chat_panel_area(button.x, button.y, 
                                                   image_width, image_height)):
                    self.logger.debug(f"Excluding no-text button outside "
                                    f"chat area: ({button.x}, {button.y})")
                    continue
                filtered.append(button)
                continue
                
            text_lower = button.text.lower().strip()
            
            # Skip buttons with excluded patterns
            is_excluded = False
            for pattern in exclude_patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    self.logger.debug(f"Excluding button '{button.text}' - "
                                    f"matches pattern '{pattern}'")
                    is_excluded = True
                    break
            
            if not is_excluded:
                # Check if it has continue-like text or is a good candidate
                if (self._matches_continue_pattern(text_lower) or 
                    not text_lower or  # No text detected
                    text_lower in ['', ' ', 'button', 'btn']):
                    filtered.append(button)
                else:
                    self.logger.debug(f"Excluding button '{button.text}' - "
                                    "doesn't match continue patterns")
        
        self.logger.debug(f"Filtered {len(buttons)} buttons down to "
                        f"{len(filtered)} Continue candidates")
        return filtered

    def _is_mock_image(self, image: Image.Image) -> bool:
        """Check if the image is a mock image (e.g., all black or all white).
        
        Args:
            image: PIL Image to check
            
        Returns:
            True if the image is a mock image
        """
        try:
            # Convert to grayscale and calculate mean brightness
            gray_image = image.convert('L')
            histogram = gray_image.histogram()
            
            # Calculate brightness as the average of the histogram
            brightness = sum(i * hist for i, hist in enumerate(histogram)) / sum(histogram)
            
            # Heuristic thresholds for mock image detection
            return brightness < 10 or brightness > 245  # Very dark or very bright images
        except Exception as e:
            self.logger.debug(f"Error checking mock image: {e}")
            return False
    
    def _get_coordinate_based_buttons(self, window_x: int, window_y: int) -> List[ButtonLocation]:
        """Fallback to coordinate-based button detection with user-specific coordinates.
        
        Args:
            window_x: X offset of the window
            window_y: Y offset of the window
            
        Returns:
            List of ButtonLocation objects with predefined coordinates
        """
        self.logger.info("📍 Using coordinate-based Continue button detection")
        self.logger.info(f"   Window position: ({window_x}, {window_y})")
        
        buttons = []
        
        # Position 1: USER-SPECIFIC COORDINATES - Continue button location
        # X: 1713, Y: 1723 (most common Continue button location)
        user_btn_x = 1713
        user_btn_y = 1723
        buttons.append(ButtonLocation(
            x=user_btn_x, y=user_btn_y, width=120, height=32,
            confidence=0.98, method="user_coordinates",
            text="Continue (user-specific location)"
        ))
        
        # Position 2: VS Code Copilot Chat Continue buttons (fallback positions)
        # Bottom-right area of the chat panel (most common)
        btn1_x = window_x + 1920 - 180  # 180px from right edge
        btn1_y = window_y + 992 - 100   # 100px from bottom
        buttons.append(ButtonLocation(
            x=btn1_x, y=btn1_y, width=120, height=32,
            confidence=0.95, method="coordinate_fallback",
            text="Continue (bottom-right)"
        ))
        
        # Position 3: Center-right area (alternative chat location)
        btn2_x = window_x + 1920 - 180
        btn2_y = window_y + 992 - 200   # Higher up in chat
        buttons.append(ButtonLocation(
            x=btn2_x, y=btn2_y, width=120, height=32,
            confidence=0.90, method="coordinate_fallback",
            text="Continue (center-right)"
        ))
        
        # Position 4: Chat input area (where responses appear)
        btn3_x = window_x + 1920 - 180
        btn3_y = window_y + 992 - 300   # Chat response area
        buttons.append(ButtonLocation(
            x=btn3_x, y=btn3_y, width=120, height=32,
            confidence=0.85, method="coordinate_fallback",
            text="Continue (input area)"
        ))
        
        # Position 5: Left side of chat (some layouts)
        btn4_x = window_x + 1920 - 900  # More center-left
        btn4_y = window_y + 992 - 100
        buttons.append(ButtonLocation(
            x=btn4_x, y=btn4_y, width=120, height=32,
            confidence=0.80, method="coordinate_fallback",
            text="Continue (center-left)"
        ))
        
        # Log the calculated positions for debugging
        for i, btn in enumerate(buttons, 1):
            self.logger.info(f"   Button {i}: ({btn.x}, {btn.y}) - {btn.text}")
        
        return buttons
