# API Reference

## Core Components

### AutomationEngine

The main orchestration class that coordinates all automation activities.

```python
from src.core.automation_engine import AutomationEngine
from src.core.config_manager import ConfigManager

# Initialize with configuration
config = ConfigManager()
engine = AutomationEngine(config)

# Start automation
await engine.start()

# Get statistics
stats = engine.get_statistics()
print(f"Buttons clicked: {stats['clicks_successful']}")
```

#### Methods

**`async start()`**
- Starts the automation engine
- Returns: None
- Raises: `AutomationError` if initialization fails

**`async stop()`**
- Stops the automation engine gracefully
- Returns: None

**`get_statistics() -> Dict[str, Any]`**
- Returns current automation statistics
- Returns: Dictionary with performance metrics

**`get_performance_report() -> Dict[str, Any]`**
- Returns detailed performance analysis
- Returns: Comprehensive performance data

### ButtonFinder

Advanced button detection using multiple computer vision techniques.

```python
from src.core.button_finder import ButtonFinder
from PIL import Image

# Initialize button finder
finder = ButtonFinder()

# Find buttons in image
image = Image.open("screenshot.png")
buttons = finder.find_continue_buttons(image, window_x=0, window_y=0)

for button in buttons:
    print(f"Button at ({button.x}, {button.y}) - confidence: {button.confidence}")
```

#### Methods

**`find_continue_buttons(image: Image, window_x: int = 0, window_y: int = 0) -> List[ButtonLocation]`**
- Detects Continue buttons in an image using multiple methods
- Args:
  - `image`: PIL Image to analyze
  - `window_x`: X offset for absolute coordinates
  - `window_y`: Y offset for absolute coordinates
- Returns: List of `ButtonLocation` objects
- Raises: `DetectionError` for critical failures

### ClickAutomator

Handles mouse clicks and keyboard input with cross-platform support.

```python
from src.core.click_automator import ClickAutomator

# Initialize click automator
clicker = ClickAutomator()

# Click at coordinates
result = clicker.click(x=100, y=200)
if result.success:
    print(f"Clicked at ({result.x}, {result.y}) using {result.method}")

# Type text and press Enter
clicker.type_text("continue")
clicker.press_key(Key.enter)
```

#### Methods

**`click(x: int, y: int, button: str = "left", restore_position: bool = True) -> ClickResult`**
- Performs a mouse click at specified coordinates
- Args:
  - `x`, `y`: Target coordinates
  - `button`: Mouse button ("left", "right", "middle")
  - `restore_position`: Whether to restore original cursor position
- Returns: `ClickResult` with success status and details

**`type_text(text: str, delay: float = 0.05) -> bool`**
- Types text using keyboard controller
- Args:
  - `text`: Text to type
  - `delay`: Delay between keystrokes
- Returns: True if successful

**`press_key(key) -> bool`**
- Presses a specific key
- Args:
  - `key`: Key to press (from pynput.keyboard.Key)
- Returns: True if successful

**`click_and_type_continue(chat_x: int, chat_y: int) -> bool`**
- Clicks chat field and types 'continue' + Enter
- Args:
  - `chat_x`: X coordinate of chat input field
  - `chat_y`: Y coordinate of chat input field
- Returns: True if successful

### WindowDetector

Detects and manages VS Code windows across different platforms.

```python
from src.core.window_detector import WindowDetector

# Initialize detector
detector = WindowDetector()

# Get all VS Code windows
windows = detector.get_vscode_windows()

for window in windows:
    print(f"Window: {window.title}")
    print(f"Position: ({window.x}, {window.y})")
    print(f"Size: {window.width}x{window.height}")
```

#### Methods

**`get_vscode_windows() -> List[VSCodeWindow]`**
- Detects all open VS Code windows
- Returns: List of `VSCodeWindow` objects
- Platform-specific implementation

### ConfigManager

Manages application configuration with validation and hot-reload.

```python
from src.core.config_manager import ConfigManager

# Initialize with default config
config = ConfigManager()

# Get configuration value
interval = config.get('automation.detection_interval', 5.0)

# Set configuration value
config.set('automation.dry_run', True)

# Check if dry run mode
if config.is_dry_run():
    print("Running in dry-run mode")
```

#### Methods

**`get(key: str, default: Any = None) -> Any`**
- Gets a configuration value using dot notation
- Args:
  - `key`: Configuration key (e.g., 'automation.interval')
  - `default`: Default value if key not found
- Returns: Configuration value or default

**`set(key: str, value: Any) -> None`**
- Sets a configuration value using dot notation
- Args:
  - `key`: Configuration key
  - `value`: Value to set

**`is_dry_run() -> bool`**
- Checks if application is in dry-run mode
- Returns: True if dry-run mode is enabled

**`get_log_level() -> str`**
- Gets the current logging level
- Returns: Log level string ('DEBUG', 'INFO', etc.)

## Data Classes

### ButtonLocation

Represents a detected button with position and metadata.

```python
from src.core.button_finder import ButtonLocation

button = ButtonLocation(
    x=100, y=200, width=80, height=30,
    confidence=0.95, method="ocr",
    text="Continue"
)

print(f"Center: ({button.center_x}, {button.center_y})")
print(f"Area: {button.width * button.height}")
```

#### Properties

- `x: int` - Left edge X coordinate
- `y: int` - Top edge Y coordinate  
- `width: int` - Button width in pixels
- `height: int` - Button height in pixels
- `confidence: float` - Detection confidence (0.0-1.0)
- `method: str` - Detection method used
- `text: Optional[str]` - Detected text content
- `center_x: int` - Center X coordinate (computed)
- `center_y: int` - Center Y coordinate (computed)
- `center: Tuple[int, int]` - Center coordinates tuple (computed)

### VSCodeWindow

Represents a VS Code window with position and metadata.

```python
from src.core.window_detector import VSCodeWindow

window = VSCodeWindow(
    window_id=12345,
    title="VS Code - main.py",
    x=100, y=50, width=1200, height=800,
    pid=67890
)

print(f"Window area: {window.width * window.height}")
```

#### Properties

- `window_id: int` - System window identifier
- `title: str` - Window title text
- `x: int` - Window X position
- `y: int` - Window Y position
- `width: int` - Window width in pixels
- `height: int` - Window height in pixels
- `pid: int` - Process ID of the window

### ClickResult

Result of a click operation with status and metadata.

```python
from src.core.click_automator import ClickResult

result = ClickResult(
    success=True,
    x=100, y=200,
    method="pynput",
    error=None
)

if result.success:
    print(f"Click succeeded at ({result.x}, {result.y})")
else:
    print(f"Click failed: {result.error}")
```

#### Properties

- `success: bool` - Whether the click succeeded
- `x: int` - X coordinate that was clicked
- `y: int` - Y coordinate that was clicked  
- `method: str` - Click method used ("pynput", "xlib", etc.)
- `error: Optional[str]` - Error message if click failed

## Utility Functions

### Screen Capture

```python
from src.utils.screen_capture import ScreenCapture

# Initialize screen capture
capture = ScreenCapture()

# Capture entire screen
screenshot = capture.capture_screen()

# Capture specific window
window_image = capture.capture_window(window)

# Capture region
region_image = capture.capture_region(x=100, y=100, width=800, height=600)
```

### Logging

```python
from src.utils.logger import setup_logging
import logging

# Setup logging
setup_logging(level='DEBUG')

# Use logger
logger = logging.getLogger(__name__)
logger.info("Automation started")
logger.debug("Debug information")
logger.error("Error occurred")
```

## Configuration Schema

### Default Configuration Structure

```json
{
  "detection": {
    "method": "ocr",
    "confidence_threshold": 0.8,
    "button_text": ["Continue", "继续", "Continuar"],
    "ocr_language": "eng",
    "cache_duration": 30
  },
  "automation": {
    "click_delay": 0.1,
    "retry_attempts": 3,
    "retry_delay": 1.0,
    "auto_focus_windows": true,
    "enable_chat_fallback": true,
    "chat_field_coordinates": {
      "x": 1725,
      "y": 1993
    },
    "continue_button_coordinates": {
      "x": 1713,
      "y": 1723
    }
  },
  "logging": {
    "level": "INFO",
    "console": true,
    "file": "logs/automation.log"
  },
  "safety": {
    "pause_on_user_activity": true,
    "emergency_stop_key": "F12"
  }
}
```

## Error Handling

### Exception Hierarchy

```python
# Base exception
class AutomationError(Exception):
    """Base exception for automation errors."""
    pass

# Specific exceptions  
class DetectionError(AutomationError):
    """Button detection failed."""
    pass

class ClickError(AutomationError):
    """Click operation failed."""
    pass

class ConfigurationError(AutomationError):
    """Configuration is invalid."""
    pass

class WindowError(AutomationError):
    """Window operation failed."""
    pass
```

### Error Handling Example

```python
try:
    engine = AutomationEngine(config)
    await engine.start()
except ConfigurationError as e:
    logger.error(f"Configuration error: {e}")
except DetectionError as e:
    logger.warning(f"Detection failed: {e}")
except AutomationError as e:
    logger.error(f"Automation error: {e}")
except Exception as e:
    logger.critical(f"Unexpected error: {e}")
```

## Performance Monitoring

### Statistics Collection

```python
# Get current statistics
stats = engine.get_statistics()

print(f"""
Automation Statistics:
- Windows processed: {stats['windows_processed']}
- Buttons found: {stats['buttons_found']}
- Clicks attempted: {stats['clicks_attempted']}
- Clicks successful: {stats['clicks_successful']}
- Success rate: {stats['clicks_successful'] / max(1, stats['clicks_attempted']) * 100:.1f}%
- Errors: {stats['errors']}
- Runtime: {stats['total_runtime']} seconds
""")
```

### Performance Report

```python
# Get detailed performance report
report = engine.get_performance_report()

print(f"""
Performance Report:
- Average detection time: {report['avg_detection_time']:.2f}ms
- Cache hit rate: {report['cache_hit_rate']:.1f}%
- Memory usage: {report['memory_usage']:.1f}MB
- CPU usage: {report['cpu_usage']:.1f}%
""")
```

## Platform-Specific Notes

### Linux (X11)
- Requires `xlib` dependencies
- Window detection via X11 API
- Screenshot via `xwd` or `import`

### Linux (Wayland)
- Limited window detection capabilities
- Falls back to coordinate-based detection
- Screenshot via `gnome-screenshot` or similar

### Windows
- Uses Win32 API for window detection
- Screenshot via Windows API
- Requires appropriate permissions

### macOS
- Uses Quartz for window detection
- Screenshot via `screencapture`
- May require accessibility permissions

## Integration Examples

### Custom Detection Method

```python
from src.core.button_finder import ButtonFinder

class CustomButtonFinder(ButtonFinder):
    def find_continue_buttons(self, image, window_x=0, window_y=0):
        # Custom detection logic
        buttons = super().find_continue_buttons(image, window_x, window_y)
        
        # Add custom detection
        custom_buttons = self._custom_detection(image)
        buttons.extend(custom_buttons)
        
        return buttons
    
    def _custom_detection(self, image):
        # Implement custom detection logic
        return []
```

### Configuration Override

```python
from src.core.config_manager import ConfigManager

# Custom configuration
custom_config = {
    "automation": {
        "detection_interval": 3.0,
        "enable_chat_fallback": False
    }
}

# Override defaults
config = ConfigManager()
for key, value in custom_config.items():
    config.config[key].update(value)
```

This API reference provides comprehensive documentation for all major components and their usage patterns.
