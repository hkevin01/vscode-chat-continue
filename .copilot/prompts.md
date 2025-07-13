# GitHub Copilot Custom Prompts

## Project Context
This is the VS Code Chat Continue automation project - a sophisticated tool that automates the "Continue" button clicking in VS Code chat interfaces.

## Code Style Guidelines

### Python Style
- Use type hints for all functions
- Follow PEP 8 with black formatting
- Use descriptive variable names
- Include docstrings for all public methods

```python
def detect_continue_button(
    screenshot: np.ndarray,
    method: DetectionMethod = DetectionMethod.HYBRID
) -> Optional[ButtonLocation]:
    """
    Detect the Continue button using specified method.
    
    Args:
        screenshot: The screenshot to analyze
        method: Detection method to use
        
    Returns:
        Button location if found, None otherwise
    """
```

### Testing Patterns
- Use pytest with fixtures
- Follow AAA pattern (Arrange, Act, Assert)
- Use descriptive test names
- Mock external dependencies

```python
@pytest.mark.integration
async def test_complete_automation_workflow(
    config_manager: ConfigManager,
    mock_vscode_window: MockWindow
) -> None:
    """Test the complete automation workflow from detection to click."""
    # Arrange
    engine = AutomationEngine(config_manager)
    
    # Act
    result = await engine.process_window(mock_vscode_window)
    
    # Assert
    assert result.success
    assert result.clicks_performed > 0
```

## Architecture Guidelines

### Module Organization
- `src/core/`: Core automation logic
- `src/gui/`: PyQt6 interface components  
- `src/utils/`: Utility functions and helpers
- `tests/`: Organized by test type (unit/integration/performance)

### Design Patterns
- Use dependency injection for testability
- Implement strategy pattern for detection methods
- Use observer pattern for GUI updates
- Apply factory pattern for configuration loading

## Common Tasks

### Adding New Detection Method
1. Create method in `src/core/detection/`
2. Add enum value to `DetectionMethod`
3. Implement strategy in detection engine
4. Add comprehensive tests
5. Update documentation

### Adding New Configuration Option
1. Update `config/default.json` schema
2. Add validation in `ConfigManager`
3. Update GUI if user-facing
4. Add tests for new option
5. Document in README

### Performance Optimization
1. Profile with `cProfile` first
2. Add performance test in `tests/performance/`
3. Benchmark before/after changes
4. Consider caching for expensive operations
5. Update performance documentation

## Error Handling Patterns

### Graceful Degradation
```python
try:
    result = advanced_detection_method()
except DetectionError as e:
    logger.warning(f"Advanced detection failed: {e}")
    result = fallback_detection_method()
```

### User-Friendly Messages
```python
class AutomationError(Exception):
    """Base exception with user-friendly messaging."""
    
    def __init__(self, message: str, technical_details: str = None):
        super().__init__(message)
        self.message = message
        self.technical_details = technical_details
```

## Documentation Standards

### Code Comments
- Explain WHY, not what
- Use TODO comments with issue numbers
- Document complex algorithms
- Explain platform-specific workarounds

### API Documentation
- Use Google-style docstrings
- Include examples for complex functions
- Document exceptions that can be raised
- Specify parameter types and return values

## Platform Considerations

### Linux/Wayland Support
- Use coordinate-based fallback methods
- Handle window manager differences
- Test on multiple desktop environments
- Document known limitations

### Cross-Platform Testing
- Use GitHub Actions matrix testing
- Mock platform-specific dependencies
- Provide platform-specific configuration
- Document platform requirements

## Security Guidelines

### Screenshot Handling
- Minimize screenshot retention time
- Avoid logging sensitive screen content
- Use secure temporary file handling
- Document privacy implications

### Configuration Security
- Validate all configuration inputs
- Use secure defaults
- Sanitize file paths
- Implement input validation

## Performance Guidelines

### Screenshot Processing
- Process minimal required regions
- Cache detection results when appropriate
- Use efficient image comparison algorithms
- Monitor memory usage for large screenshots

### Threading Considerations
- Use asyncio for I/O operations
- Implement proper cleanup for threads
- Handle cancellation gracefully
- Avoid blocking the GUI thread

## Debugging Guidelines

### Logging Best Practices
```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Detailed debugging information")
logger.info("General information")
logger.warning("Something unexpected happened")
logger.error("Error occurred but app continues")
logger.critical("Serious error, app may not continue")
```

### Debug Mode Features
- Enhanced logging output
- Screenshot saving for analysis
- Performance timing information
- Detailed error tracebacks

## Release Guidelines

### Version Numbering
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Update CHANGELOG.md with each release
- Tag releases in git
- Update version in pyproject.toml

### Pre-Release Checklist
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Performance benchmarks run
- [ ] Security review completed
- [ ] Cross-platform testing done
