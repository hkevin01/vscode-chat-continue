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
            # Method 1: OCR-based text detection
            if HAS_TESSERACT:
                ocr_buttons = self._find_buttons_ocr(image, window_x, window_y)
                buttons.extend(ocr_buttons)
                self.logger.debug(f"OCR found {len(ocr_buttons)} buttons")
            
            # Method 2: Template matching
            if HAS_OPENCV:
                template_buttons = self._find_buttons_template(image, window_x, window_y)
                buttons.extend(template_buttons)
                self.logger.debug(f"Template matching found {len(template_buttons)} buttons")
            
            # Method 3: Color-based detection
            color_buttons = self._find_buttons_color(image, window_x, window_y)
            buttons.extend(color_buttons)
            self.logger.debug(f"Color detection found {len(color_buttons)} buttons")
            
            # Method 4: Blue rectangle fallback (when OCR unavailable)
            if not HAS_TESSERACT:
                self.logger.info("OCR not available, using blue rectangle fallback")
                blue_buttons = self._find_blue_rectangles(image, window_x, window_y)
                buttons.extend(blue_buttons)
                self.logger.debug(f"Blue rectangle detection found {len(blue_buttons)} buttons")
            
            # Remove duplicates and sort by confidence
            buttons = self._deduplicate_buttons(buttons)
            buttons.sort(key=lambda b: b.confidence, reverse=True)
            
            self.logger.debug(f"Total found {len(buttons)} continue buttons after deduplication")
            
        except Exception as e:
            self.logger.error(f"Error finding buttons: {e}")
        
        return buttons
    
    def _find_buttons_ocr(self, image: Image.Image, 
                         window_x: int, window_y: int) -> List[ButtonLocation]:
        """Find buttons using OCR text detection.
        
        Args:
            image: PIL Image to search in
            window_x: X offset of the window
            window_y: Y offset of the window
            
        Returns:
            List of ButtonLocation objects
        """
        buttons = []
        
        try:
            # Try primary OCR configuration (single word mode)
            try:
                ocr_data = pytesseract.image_to_data(image, config=self.tesseract_config, 
                                                   output_type=pytesseract.Output.DICT)
                self.logger.debug("Using PSM 8 (single word mode) for OCR")
            except Exception as e:
                self.logger.debug(f"PSM 8 failed: {e}, trying backup configuration")
                # Fallback to block text mode
                ocr_data = pytesseract.image_to_data(image, config=self.tesseract_config_backup, 
                                                   output_type=pytesseract.Output.DICT)
                self.logger.debug("Using PSM 6 (block text mode) for OCR")
            
            # Process each detected text element
            for i in range(len(ocr_data['text'])):
                text = ocr_data['text'][i].strip().lower()
                confidence = float(ocr_data['conf'][i])
                
                # Debug: log all detected text with lower threshold
                if text and confidence > 5:
                    self.logger.debug(f"OCR detected: '{text}' (confidence: {confidence})")
                
                # Skip low confidence or empty text (very low threshold for debugging)
                if confidence < 10 or not text:
                    continue
                
                # Check if text matches continue patterns
                if self._matches_continue_pattern(text):
                    self.logger.info(f"Found Continue button: '{text}' (confidence: {confidence})")
                    x = ocr_data['left'][i] + window_x
                    y = ocr_data['top'][i] + window_y
                    width = ocr_data['width'][i]
                    height = ocr_data['height'][i]
                    
                    # Expand the button area slightly for better clicking
                    padding = 15  # Increased padding for easier clicking
                    button = ButtonLocation(
                        x=max(0, x - padding),
                        y=max(0, y - padding),
                        width=width + 2 * padding,
                        height=height + 2 * padding,
                        confidence=confidence / 100.0,  # Normalize to 0-1
                        method="ocr",
                        text=text
                    )
                    
                    buttons.append(button)
                    
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
        """Preprocess image for better OCR detection.
        
        Args:
            image: Original PIL Image
            
        Returns:
            List of processed images to try for OCR
        """
        processed_images = [image]  # Always include original
        
        try:
            if HAS_PIL:
                # Convert to grayscale
                gray = image.convert('L')
                processed_images.append(gray)
                
                # High contrast (good for dark themes)
                from PIL import ImageEnhance
                enhancer = ImageEnhance.Contrast(gray)
                high_contrast = enhancer.enhance(2.0)
                processed_images.append(high_contrast)
                
                # Inverted (white text on black becomes black on white)
                from PIL import ImageOps
                inverted = ImageOps.invert(gray)
                processed_images.append(inverted)
                
                # Inverted high contrast
                inverted_contrast = ImageEnhance.Contrast(inverted).enhance(2.0)
                processed_images.append(inverted_contrast)
                
                # Threshold (binary black/white)
                import numpy as np
                arr = np.array(gray)
                threshold = np.mean(arr)
                binary = Image.fromarray((arr > threshold) * 255)
                processed_images.append(binary)
                
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
