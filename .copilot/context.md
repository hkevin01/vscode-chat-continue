# Project Context for GitHub Copilot

## What This Project Does
This project automates clicking the "Continue" button in VS Code Copilot Chat windows across all open VS Code instances on Linux systems. It's designed to streamline AI-assisted coding workflows by eliminating the need to manually click continue buttons.

## Architecture Overview

### Core Components
1. **Window Management** (`src/core/window_detector.py`)
   - Detects VS Code processes and windows
   - Uses X11/Wayland APIs for window enumeration
   - Filters for windows with active Copilot Chat

2. **Button Detection** (`src/core/button_finder.py`)
   - OCR-based text recognition for "Continue" buttons
   - Image matching for visual button detection
   - Multi-language support and confidence scoring

3. **Click Automation** (`src/core/click_automator.py`)
   - Safe mouse click simulation
   - User activity detection and pausing
   - Focus preservation and error recovery

4. **Configuration** (`src/core/config_manager.py`)
   - JSON-based configuration system
   - User preferences and safety settings
   - Runtime parameter validation

### Key Libraries Used
- **pyautogui**: Mouse/keyboard automation
- **pytesseract**: OCR text recognition
- **opencv-python**: Image processing and matching
- **python-xlib**: X11 window management
- **psutil**: Process detection and management

## Common Patterns and Idioms

### Configuration Loading
```python
@dataclass
class Config:
    detection_method: str = "ocr"
    confidence_threshold: float = 0.8
    click_delay: float = 0.1
    
config = Config.from_file("config.json")
```

### Window Detection Pattern
```python
def find_vscode_windows() -> List[Window]:
    """Find all VS Code windows with active Copilot Chat."""
    processes = psutil.process_iter(['pid', 'name', 'cmdline'])
    vscode_processes = [p for p in processes if 'code' in p.info['name']]
    return [w for w in get_windows() if w.pid in vscode_pids]
```

### Safe Click Pattern
```python
def safe_click(x: int, y: int) -> bool:
    """Click with safety checks and error handling."""
    if self.is_user_active():
        logger.info("User active, skipping click")
        return False
    
    try:
        pyautogui.click(x, y)
        return True
    except Exception as e:
        logger.error(f"Click failed: {e}")
        return False
```

### Error Handling Pattern
```python
def with_retry(func, max_attempts: int = 3) -> Any:
    """Retry function with exponential backoff."""
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            time.sleep(2 ** attempt)
```

## File Organization

### Source Structure
- `src/main.py` - Entry point and CLI interface
- `src/core/` - Core automation logic
- `src/utils/` - Utility functions and helpers
- `src/gui/` - Optional GUI components (future)

### Configuration
- `config/default.json` - Default configuration template
- `~/.config/vscode-continue/` - User configuration directory

### Testing
- `tests/unit/` - Unit tests for individual components
- `tests/integration/` - End-to-end workflow tests
- `tests/fixtures/` - Test data and mock objects

## Development Workflow

### Local Development
1. Set up virtual environment with required dependencies
2. Use `pytest` for running tests with coverage
3. Format code with `black` and lint with `flake8`
4. Type check with `mypy` before committing

### Testing Strategy
- Mock external dependencies (screen capture, X11 APIs)
- Use `xvfb` for headless testing in CI
- Test with multiple VS Code configurations
- Validate safety features work correctly

## Key Design Principles

### Safety First
- Always check for user activity before automation
- Implement emergency stop mechanisms
- Preserve user context and window focus
- Provide dry-run mode for testing

### Performance
- Minimize screen capture frequency
- Cache detection results where possible
- Use efficient image processing algorithms
- Optimize for multiple window scenarios

### Reliability
- Robust error handling with informative messages
- Retry logic with exponential backoff
- Graceful degradation when features unavailable
- Comprehensive logging for debugging

### User Experience
- Clear configuration options with sensible defaults
- Comprehensive documentation and examples
- Troubleshooting guides for common issues
- Minimal setup and maintenance required

When contributing to this project, focus on maintaining these principles while ensuring the code is maintainable, testable, and well-documented.
