# GitHub Copilot Instructions

## Project Context
This is an automation tool for VS Code that automatically clicks "Continue" buttons in Copilot Chat windows. The tool is designed for Linux systems and uses Python for implementation.

## Code Style and Conventions

### Python Code Style
- Follow PEP 8 guidelines
- Use type hints for all functions and methods
- Include comprehensive docstrings using Google style
- Prefer composition over inheritance
- Use dataclasses for configuration and data structures
- Error handling should be explicit and informative

### Project Structure
- `src/core/` - Core automation logic
- `src/utils/` - Utility functions and helpers
- `src/gui/` - Optional GUI components
- `tests/` - Unit and integration tests
- `docs/` - Documentation files
- `config/` - Configuration templates

### Naming Conventions
- Classes: PascalCase (e.g., `WindowDetector`)
- Functions/Methods: snake_case (e.g., `find_continue_buttons`)
- Constants: UPPER_SNAKE_CASE (e.g., `DEFAULT_CONFIDENCE_THRESHOLD`)
- Files: snake_case (e.g., `button_finder.py`)

## Key Technologies and Libraries

### Core Dependencies
- `pyautogui` - Mouse and keyboard automation
- `pytesseract` - OCR for text recognition
- `opencv-python` - Image processing
- `pillow` - Image manipulation
- `psutil` - Process management
- `python-xlib` - X11 window management
- `pynput` - Input monitoring and control

### Development Dependencies
- `pytest` - Testing framework
- `black` - Code formatting
- `flake8` - Linting
- `mypy` - Type checking
- `coverage` - Test coverage

## Implementation Guidelines

### Window Detection
- Use X11 APIs to enumerate VS Code windows
- Filter windows by process name and window title
- Handle multiple display configurations
- Support both X11 and Wayland (where possible)

### Button Recognition
- Implement multiple detection methods (OCR, image matching)
- Support internationalization (multiple languages)
- Use confidence thresholds for reliable detection
- Cache button locations for performance

### Safety Features
- Always check for user activity before clicking
- Implement emergency stop functionality
- Preserve window focus and user context
- Provide dry-run mode for testing

### Error Handling
- Log all errors with appropriate detail levels
- Implement retry logic with exponential backoff
- Graceful degradation when features aren't available
- Clear error messages for end users

## Testing Strategy

### Unit Tests
- Test each component in isolation
- Mock external dependencies (screen capture, window APIs)
- Test edge cases and error conditions
- Aim for >90% code coverage

### Integration Tests
- Test complete workflows end-to-end
- Use virtual displays for CI/CD
- Test with multiple VS Code configurations
- Validate safety features work correctly

### Manual Testing
- Test on different Linux distributions
- Verify with various VS Code themes and layouts
- Test with multiple monitor setups
- Validate accessibility compliance

## Performance Considerations
- Minimize screen capture frequency
- Use efficient image processing algorithms
- Cache detection results where appropriate
- Optimize for multiple window scenarios

## Security Considerations
- Never log sensitive information
- Validate all user inputs
- Use secure defaults in configuration
- Document automation permissions required

## Documentation Requirements
- Include comprehensive README with examples
- Document all configuration options
- Provide troubleshooting guides
- Include API documentation for extensibility

When writing code for this project, prioritize reliability, safety, and user experience. The tool should work seamlessly in the background without interfering with the user's workflow.
