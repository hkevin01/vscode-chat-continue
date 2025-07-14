# Enhanced Button Detection Modules for VS Code Chat Continue

## 1. Computer Vision & ML Enhancements

### Deep Learning Object Detection
```python
# Install: pip install ultralytics torch torchvision
import torch
from ultralytics import YOLO

class YOLOButtonDetector:
    """YOLO-based button detection for high accuracy."""
    
    def __init__(self):
        # Use pre-trained model or custom trained on VS Code buttons
        self.model = YOLO('yolov8n.pt')  # or custom model
        
    def detect_buttons(self, image):
        """Detect buttons using YOLO object detection."""
        results = self.model(image)
        buttons = []
        
        for result in results:
            for box in result.boxes:
                if box.conf > 0.8:  # High confidence
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    buttons.append({
                        'bbox': (x1, y1, x2-x1, y2-y1),
                        'confidence': float(box.conf),
                        'class': result.names[int(box.cls)]
                    })
        return buttons
```

### Advanced Image Processing
```python
# Install: pip install scikit-image
from skimage import feature, filters, morphology
from skimage.measure import label, regionprops

class AdvancedImageProcessor:
    """Enhanced image processing for button detection."""
    
    def detect_buttons_morphology(self, image):
        """Use morphological operations to find button-like shapes."""
        gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
        
        # Apply Gaussian blur
        blurred = filters.gaussian(gray, sigma=1)
        
        # Edge detection
        edges = feature.canny(blurred, sigma=1, low_threshold=0.1, high_threshold=0.2)
        
        # Morphological operations to close button shapes
        closed = morphology.closing(edges, morphology.rectangle(3, 10))
        
        # Find connected components
        labeled = label(closed)
        regions = regionprops(labeled)
        
        buttons = []
        for region in regions:
            # Filter by aspect ratio and size for button-like shapes
            if self._is_button_like_region(region):
                buttons.append(region)
                
        return buttons
```

## 2. Enhanced OCR & Text Detection

### EasyOCR (Better than Tesseract for some cases)
```python
# Install: pip install easyocr
import easyocr

class EnhancedOCRDetector:
    """Advanced OCR with multiple engines."""
    
    def __init__(self):
        self.easy_reader = easyocr.Reader(['en'])
        
    def detect_text_easyocr(self, image):
        """Use EasyOCR for text detection."""
        results = self.easy_reader.readtext(np.array(image))
        
        continue_buttons = []
        for (bbox, text, confidence) in results:
            if 'continue' in text.lower() and confidence > 0.7:
                x1, y1 = bbox[0]
                x2, y2 = bbox[2]
                continue_buttons.append({
                    'bbox': (x1, y1, x2-x1, y2-y1),
                    'text': text,
                    'confidence': confidence
                })
        return continue_buttons
```

### PaddleOCR (Multilingual support)
```python
# Install: pip install paddlepaddle paddleocr
from paddleocr import PaddleOCR

class MultilingualOCR:
    """Support for multiple languages."""
    
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en')
        
    def detect_multilingual_text(self, image):
        """Detect text in multiple languages."""
        result = self.ocr.ocr(np.array(image))
        
        continue_patterns = ['continue', '继续', 'continuar', 'fortsett']
        buttons = []
        
        for line in result:
            for item in line:
                text = item[1][0].lower()
                confidence = item[1][1]
                
                if any(pattern in text for pattern in continue_patterns):
                    bbox = item[0]
                    buttons.append({
                        'bbox': self._normalize_bbox(bbox),
                        'text': text,
                        'confidence': confidence
                    })
        return buttons
```

## 3. Machine Learning Approaches

### Custom Button Classifier
```python
# Install: pip install tensorflow scikit-learn
import tensorflow as tf
from sklearn.ensemble import RandomForestClassifier

class ButtonClassifier:
    """ML-based button classification."""
    
    def __init__(self):
        self.model = self._load_or_train_model()
        
    def extract_features(self, image_region):
        """Extract features from image region."""
        # Color histogram
        hist = cv2.calcHist([image_region], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        
        # Texture features (LBP)
        gray = cv2.cvtColor(image_region, cv2.COLOR_RGB2GRAY)
        lbp = feature.local_binary_pattern(gray, 8, 1, method='uniform')
        lbp_hist, _ = np.histogram(lbp, bins=10, range=(0, 9))
        
        # Shape features
        height, width = image_region.shape[:2]
        aspect_ratio = width / height
        area = height * width
        
        return np.concatenate([hist.flatten(), lbp_hist, [aspect_ratio, area]])
        
    def classify_region(self, image_region):
        """Classify if region contains a Continue button."""
        features = self.extract_features(image_region)
        probability = self.model.predict_proba([features])[0][1]  # Probability of being a button
        return probability > 0.8
```

## 4. Advanced Color & Pattern Detection

### HSV Color Space Analysis
```python
class AdvancedColorDetector:
    """Enhanced color-based button detection."""
    
    def detect_vs_code_buttons(self, image):
        """Detect VS Code specific button colors."""
        hsv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2HSV)
        
        # VS Code button color ranges
        color_ranges = {
            'primary_blue': ([100, 50, 50], [130, 255, 255]),
            'accent_blue': ([200, 100, 100], [220, 255, 255]),
            'hover_blue': ([110, 60, 60], [140, 255, 255]),
        }
        
        all_buttons = []
        for color_name, (lower, upper) in color_ranges.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                if self._is_button_contour(contour):
                    x, y, w, h = cv2.boundingRect(contour)
                    all_buttons.append({
                        'bbox': (x, y, w, h),
                        'color_type': color_name,
                        'confidence': self._calculate_color_confidence(mask, contour)
                    })
                    
        return all_buttons
```

## 5. Accessibility & UI Automation

### pyautogui Enhancements
```python
# Install: pip install pyautogui pillow-simd (faster PIL)
import pyautogui
from pyautogui import ImageNotFoundException

class SmartClicker:
    """Enhanced clicking with visual feedback."""
    
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
    def locate_and_click_continue(self, screenshot_path=None):
        """Locate and click Continue button with multiple strategies."""
        strategies = [
            self._locate_by_template,
            self._locate_by_text_template,
            self._locate_by_color_template
        ]
        
        for strategy in strategies:
            try:
                location = strategy()
                if location:
                    # Add visual feedback
                    self._highlight_before_click(location)
                    pyautogui.click(location)
                    return True
            except ImageNotFoundException:
                continue
                
        return False
        
    def _highlight_before_click(self, location):
        """Visually highlight the area before clicking."""
        # Draw a temporary highlight box
        import tkinter as tk
        
        highlight = tk.Toplevel()
        highlight.attributes('-topmost', True)
        highlight.attributes('-alpha', 0.3)
        highlight.configure(bg='red')
        highlight.geometry(f"100x40+{location.left}+{location.top}")
        highlight.after(500, highlight.destroy)
```

### Accessibility API Integration
```python
# Install: pip install pygetwindow psutil accessibility
import pygetwindow as gw
from accessibility import get_accessibility_tree

class AccessibilityDetector:
    """Use accessibility APIs for button detection."""
    
    def find_continue_buttons_a11y(self):
        """Find Continue buttons using accessibility tree."""
        vscode_windows = gw.getWindowsWithTitle('Visual Studio Code')
        
        buttons = []
        for window in vscode_windows:
            try:
                # Get accessibility tree for the window
                tree = get_accessibility_tree(window._hWnd)
                
                # Search for buttons with "Continue" text
                continue_buttons = self._search_accessibility_tree(tree, 'Continue')
                buttons.extend(continue_buttons)
                
            except Exception as e:
                self.logger.warning(f"Accessibility detection failed: {e}")
                
        return buttons
```

## 6. Real-time Performance Monitoring

### Memory-efficient Processing
```python
# Install: pip install psutil memory-profiler
import psutil
from memory_profiler import profile

class PerformanceOptimizer:
    """Optimize detection performance and memory usage."""
    
    def __init__(self):
        self.cache = {}
        self.max_cache_size = 100
        
    @profile
    def optimized_detection(self, image, window_info):
        """Memory-efficient button detection."""
        # Calculate image hash for caching
        image_hash = self._calculate_image_hash(image)
        
        if image_hash in self.cache:
            self.logger.debug("Using cached detection result")
            return self.cache[image_hash]
            
        # Crop to likely button areas first
        button_regions = self._get_likely_button_regions(image, window_info)
        
        buttons = []
        for region in button_regions:
            # Process smaller regions for better performance
            region_buttons = self._detect_in_region(region)
            buttons.extend(region_buttons)
            
        # Cache result
        if len(self.cache) >= self.max_cache_size:
            self.cache.pop(next(iter(self.cache)))  # Remove oldest
        self.cache[image_hash] = buttons
        
        return buttons
```

## 7. Multi-threading & Async Improvements

### Async Detection Pipeline
```python
# Install: pip install asyncio aiofiles
import asyncio
import concurrent.futures

class AsyncButtonDetector:
    """Asynchronous button detection for better performance."""
    
    def __init__(self):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        
    async def detect_buttons_async(self, images):
        """Detect buttons in multiple images concurrently."""
        tasks = []
        
        for image in images:
            task = asyncio.create_task(
                self._detect_single_image_async(image)
            )
            tasks.append(task)
            
        results = await asyncio.gather(*tasks)
        return [button for result in results for button in result]
        
    async def _detect_single_image_async(self, image):
        """Detect buttons in a single image asynchronously."""
        loop = asyncio.get_event_loop()
        
        # Run CPU-intensive detection in thread pool
        buttons = await loop.run_in_executor(
            self.executor,
            self._cpu_intensive_detection,
            image
        )
        
        return buttons
```

## 8. Integration Suggestions

### Enhanced Configuration
```python
ENHANCED_CONFIG = {
    "detection": {
        "methods": ["yolo", "easyocr", "color_enhanced", "accessibility"],
        "confidence_thresholds": {
            "yolo": 0.8,
            "easyocr": 0.7,
            "color": 0.6,
            "accessibility": 0.9
        },
        "preprocessing": {
            "gaussian_blur": True,
            "contrast_enhancement": True,
            "noise_reduction": True
        }
    },
    "performance": {
        "use_gpu": True,
        "cache_enabled": True,
        "async_processing": True,
        "max_threads": 4
    },
    "fallback": {
        "coordinates": {"x": 1713, "y": 1723},
        "chat_typing": True,
        "visual_feedback": True
    }
}
```
