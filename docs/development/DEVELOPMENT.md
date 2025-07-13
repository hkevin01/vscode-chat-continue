# Development Guide

## 🛠️ Development Setup

### Prerequisites
- Python 3.8+
- Git
- VS Code (recommended)

### Environment Setup

1. **Clone and setup development environment:**
```bash
git clone https://github.com/yourusername/vscode-chat-continue.git
cd vscode-chat-continue

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements-dev.txt
pip install -e .
```

2. **Install pre-commit hooks:**
```bash
pre-commit install
```

3. **Verify installation:**
```bash
python -m pytest tests/ -v
python src/gui/main_window.py
```

## 🏗️ Project Architecture

### Core Components

```
src/
├── core/                    # Core automation logic
│   ├── automation_engine.py # Main orchestration
│   ├── button_finder.py     # Detection algorithms
│   ├── click_automator.py   # Mouse/keyboard control
│   ├── window_detector.py   # Window management
│   └── config_manager.py    # Configuration handling
├── gui/                     # User interface
│   └── main_window.py       # PyQt6 GUI application
└── utils/                   # Utilities
    ├── screen_capture.py    # Screenshot functionality
    ├── logger.py            # Logging system
    └── audio_suppressor.py  # Audio management
```

### Key Design Patterns

- **Strategy Pattern**: Multiple detection methods (OCR, Template, Coordinate)
- **Observer Pattern**: GUI updates and event handling
- **Factory Pattern**: Configuration loading and validation
- **Dependency Injection**: Component initialization and testing

## 🧪 Testing Strategy

### Test Categories

1. **Unit Tests** (`tests/unit/`)
   - Individual component testing
   - Mock external dependencies
   - Fast execution (<1s per test)

2. **Integration Tests** (`tests/integration/`)
   - End-to-end workflows
   - Real component interactions
   - May require display/GUI

3. **Performance Tests** (`tests/performance/`)
   - Benchmarking critical paths
   - Memory usage validation
   - Performance regression detection

4. **Debug Scripts** (`tests/debug/`)
   - Development debugging tools
   - Manual testing utilities
   - Diagnostic scripts

### Running Tests

```bash
# All tests
python -m pytest tests/ -v

# Specific categories
python -m pytest tests/unit/ -v           # Unit tests only
python -m pytest tests/integration/ -v    # Integration tests
python -m pytest tests/performance/ -v    # Performance tests

# With coverage
python -m pytest tests/ --cov=src --cov-report=html

# Specific test file
python -m pytest tests/unit/test_button_finder.py -v
```

### Test Markers

Use pytest markers to categorize tests:

```python
import pytest

@pytest.mark.unit
def test_button_detection():
    """Unit test for button detection."""
    pass

@pytest.mark.integration  
@pytest.mark.slow
def test_full_automation():
    """Integration test for complete workflow."""
    pass

@pytest.mark.performance
def test_detection_speed():
    """Performance test for detection speed."""
    pass
```

Run specific markers:
```bash
pytest -m unit          # Unit tests only
pytest -m "not slow"    # Skip slow tests
pytest -m integration   # Integration tests only
```

## 🔄 Development Workflow

### 1. Feature Development

```bash
# Create feature branch
git checkout -b feature/button-detection-improvement

# Make changes
# ... code, code, code ...

# Run tests
python -m pytest tests/ -v

# Format code
black src/ tests/
isort src/ tests/

# Lint code  
flake8 src/ tests/
pylint src/

# Type check
mypy src/
```

### 2. Pre-commit Checks

Pre-commit hooks automatically run:
- Code formatting (Black)
- Import sorting (isort)  
- Linting (flake8)
- Type checking (mypy)
- Tests (pytest)

### 3. Pull Request Process

1. **Create PR** with descriptive title
2. **Fill out PR template** completely
3. **Ensure CI passes** (all checks green)
4. **Request review** from maintainers
5. **Address feedback** if needed
6. **Merge** when approved

### 4. Code Review Guidelines

**What to Look For:**
- Code follows project standards
- Tests cover new functionality
- Documentation is updated
- No performance regressions
- Security considerations addressed

**Review Checklist:**
- [ ] Code is readable and well-commented
- [ ] Tests are comprehensive and meaningful
- [ ] Performance impact is acceptable
- [ ] Breaking changes are documented
- [ ] Security implications considered

## 🚀 Release Process

### Version Management

We use **Semantic Versioning** (semver):
- `MAJOR.MINOR.PATCH`
- `MAJOR`: Breaking changes
- `MINOR`: New features (backward compatible)
- `PATCH`: Bug fixes (backward compatible)

### Release Steps

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with release notes
3. **Create release tag**:
   ```bash
   git tag -a v1.2.0 -m "Release v1.2.0"
   git push origin v1.2.0
   ```
4. **GitHub Actions** automatically builds and publishes

### Hotfix Process

For critical bugs in production:

1. **Create hotfix branch** from main:
   ```bash
   git checkout -b hotfix/critical-bug-fix main
   ```
2. **Fix the issue** with minimal changes
3. **Test thoroughly**
4. **Create PR** to main
5. **Emergency review** and merge
6. **Tag and release** immediately

## 🔧 Debugging Tips

### Common Issues

1. **Screenshot Failures**
   ```python
   # Enable debug logging
   import logging
   logging.getLogger('screen_capture').setLevel(logging.DEBUG)
   
   # Test screenshot manually
   from src.utils.screen_capture import ScreenCapture
   capture = ScreenCapture()
   img = capture.capture_window(window)
   ```

2. **Button Detection Problems**
   ```python
   # Debug button detection
   from src.core.button_finder import ButtonFinder
   finder = ButtonFinder()
   buttons = finder.find_continue_buttons(image)
   print(f"Found {len(buttons)} buttons")
   ```

3. **Window Detection Issues**
   ```python
   # Debug window detection
   from src.core.window_detector import WindowDetector
   detector = WindowDetector()
   windows = detector.get_vscode_windows()
   for window in windows:
       print(f"Window: {window.title} at ({window.x}, {window.y})")
   ```

### Debug Mode

Enable debug logging in config:
```json
{
  "logging": {
    "level": "DEBUG",
    "console": true,
    "file": "logs/debug.log"
  }
}
```

### Performance Profiling

```python
import cProfile
import pstats

# Profile a function
cProfile.run('your_function()', 'profile_stats')
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative').print_stats(10)
```

## 📝 Documentation Standards

### Code Documentation

- **Docstrings**: Google-style for all public functions/classes
- **Type hints**: Use for all function parameters and returns
- **Comments**: Explain complex logic, not obvious code

```python
def detect_continue_button(
    image: np.ndarray,
    confidence_threshold: float = 0.8
) -> List[ButtonLocation]:
    """Detect Continue buttons in an image using OCR.
    
    Args:
        image: Screenshot image to analyze
        confidence_threshold: Minimum confidence for detection
        
    Returns:
        List of detected button locations
        
    Raises:
        DetectionError: When detection fails critically
    """
    # Complex algorithm explanation here
    pass
```

### API Documentation

Generate API docs with Sphinx:
```bash
sphinx-apidoc -o docs/api src/
sphinx-build -b html docs/ docs/_build/html
```

## 🛡️ Security Considerations

### Input Validation
- Validate all configuration inputs
- Sanitize file paths and URLs
- Check image data before processing

### Screen Capture Security
- Minimize screenshot retention time
- Avoid capturing sensitive information
- Secure temporary file handling

### Dependency Security
```bash
# Check for vulnerabilities
safety check

# Audit dependencies
pip-audit
```

## 🤝 Contributing Guidelines

1. **Fork** the repository
2. **Create** a feature branch
3. **Follow** coding standards
4. **Write** comprehensive tests
5. **Document** your changes
6. **Submit** a pull request

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain a professional environment

## 📊 Performance Guidelines

### Optimization Targets
- Screenshot capture: <100ms
- Button detection: <500ms
- GUI responsiveness: <50ms
- Memory usage: <100MB

### Profiling Tools
- `cProfile` for function-level profiling
- `memory_profiler` for memory usage
- `pytest-benchmark` for performance tests

## 🔍 Troubleshooting

### Environment Issues
1. **Python version**: Ensure 3.8+
2. **Dependencies**: Run `pip install -r requirements-dev.txt`
3. **System packages**: Install tesseract, Qt dependencies
4. **Permissions**: Ensure screen capture access

### Common Errors
- **Import errors**: Check PYTHONPATH and virtual environment
- **GUI errors**: Verify Qt installation and display access
- **Detection failures**: Check Tesseract installation

### Getting Help
- Check existing [Issues](https://github.com/yourusername/vscode-chat-continue/issues)
- Read the [FAQ](docs/FAQ.md)
- Join our [Discussions](https://github.com/yourusername/vscode-chat-continue/discussions)
