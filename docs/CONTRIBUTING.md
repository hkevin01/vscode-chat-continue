# Contributing to VS Code Chat Continue Automation

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Environment Setup

### Prerequisites
- Linux system (Ubuntu 20.04+ recommended)
- Python 3.8 or higher
- Git
- VS Code (for testing)

### Setup Steps

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/vscode-chat-continue.git
   cd vscode-chat-continue
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

5. **Verify Setup**
   ```bash
   pytest tests/
   black --check src/
   flake8 src/
   mypy src/
   ```

## Development Workflow

### Branch Strategy
- `main` - Stable releases
- `develop` - Integration branch for features
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Critical fixes for production

### Making Changes

1. **Create Feature Branch**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code following the style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Changes**
   ```bash
   # Run all tests
   pytest tests/ -v
   
   # Run with coverage
   pytest tests/ --cov=src --cov-report=html
   
   # Type checking
   mypy src/
   
   # Linting
   flake8 src/ tests/
   
   # Formatting
   black src/ tests/
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Style Guidelines

### Python Style
- Follow PEP 8 guidelines
- Use Black for code formatting (line length: 88)
- Use type hints for all functions and methods
- Write comprehensive docstrings using Google style

### Example Code Style
```python
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class WindowDetector:
    """Detects and manages VS Code windows for automation.
    
    This class provides functionality to find VS Code processes,
    enumerate their windows, and filter for those with active
    Copilot Chat sessions.
    
    Attributes:
        confidence_threshold: Minimum confidence for window detection.
        max_windows: Maximum number of windows to process.
    """
    
    def __init__(
        self, 
        confidence_threshold: float = 0.8,
        max_windows: int = 10
    ) -> None:
        """Initialize the window detector.
        
        Args:
            confidence_threshold: Minimum confidence for detection.
            max_windows: Maximum number of windows to process.
        """
        self.confidence_threshold = confidence_threshold
        self.max_windows = max_windows
    
    def find_vscode_windows(self) -> List[Dict[str, Any]]:
        """Find all VS Code windows with active Copilot Chat.
        
        Returns:
            List of window information dictionaries containing
            window ID, position, size, and other metadata.
            
        Raises:
            WindowDetectionError: If window detection fails.
        """
        try:
            windows = self._enumerate_windows()
            return self._filter_vscode_windows(windows)
        except Exception as e:
            logger.error(f"Window detection failed: {e}")
            raise WindowDetectionError(f"Failed to detect windows: {e}")
```

### Commit Message Format
Use conventional commits format:
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

Examples:
```
feat(detection): add support for Wayland display server
fix(automation): resolve click offset calculation bug
docs(readme): update installation instructions
test(core): add unit tests for button detection
```

## Testing Guidelines

### Test Structure
```
tests/
├── unit/
│   ├── test_window_detector.py
│   ├── test_button_finder.py
│   └── test_click_automator.py
├── integration/
│   ├── test_full_workflow.py
│   └── test_multi_window.py
└── fixtures/
    ├── sample_screenshots/
    └── mock_data/
```

### Writing Tests

1. **Unit Tests**
   ```python
   import pytest
   from unittest.mock import Mock, patch
   from src.core.window_detector import WindowDetector
   
   class TestWindowDetector:
       def setup_method(self):
           self.detector = WindowDetector()
       
       @patch('src.core.window_detector.psutil.process_iter')
       def test_find_vscode_processes(self, mock_process_iter):
           # Arrange
           mock_process = Mock()
           mock_process.info = {'name': 'code', 'pid': 1234}
           mock_process_iter.return_value = [mock_process]
           
           # Act
           processes = self.detector._find_vscode_processes()
           
           # Assert
           assert len(processes) == 1
           assert processes[0]['pid'] == 1234
   ```

2. **Integration Tests**
   ```python
   @pytest.mark.integration
   def test_full_automation_workflow():
       """Test complete automation workflow end-to-end."""
       with mock_vscode_environment():
           automator = ContinueAutomator()
           result = automator.run_once()
           assert result.success
           assert result.buttons_clicked > 0
   ```

3. **Test Fixtures**
   ```python
   @pytest.fixture
   def sample_screenshot():
       """Provide sample screenshot for testing."""
       return Image.open("tests/fixtures/sample_screenshots/continue_button.png")
   
   @pytest.fixture
   def mock_config():
       """Provide mock configuration for testing."""
       return {
           "detection": {"confidence_threshold": 0.8},
           "automation": {"click_delay": 0.1}
       }
   ```

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# With coverage
pytest --cov=src --cov-report=html

# Specific test file
pytest tests/unit/test_window_detector.py -v

# Specific test method
pytest tests/unit/test_window_detector.py::TestWindowDetector::test_find_vscode_processes -v
```

## Documentation Guidelines

### Code Documentation
- All public functions and classes must have docstrings
- Use Google-style docstrings
- Include type information in docstrings
- Provide usage examples for complex functions

### User Documentation
- Update README.md for significant changes
- Add new configuration options to USAGE.md
- Update troubleshooting guide for known issues
- Include examples for new features

### API Documentation
Generate API documentation with:
```bash
# Generate documentation
sphinx-build -b html docs/ docs/_build/

# Serve documentation locally
python -m http.server 8000 --directory docs/_build/
```

## Pull Request Process

1. **Before Submitting**
   - Ensure all tests pass
   - Update documentation
   - Add changelog entry
   - Verify code formatting

2. **PR Description Template**
   Use the provided PR template and include:
   - Clear description of changes
   - Testing information
   - Screenshots for UI changes
   - Breaking change notes

3. **Review Process**
   - All PRs require at least one review
   - Address review feedback promptly
   - Ensure CI checks pass
   - Squash commits before merge

4. **Merge Requirements**
   - ✅ All CI checks pass
   - ✅ Code review approved
   - ✅ Documentation updated
   - ✅ Tests added/updated
   - ✅ No merge conflicts

## Issue Reporting

### Bug Reports
- Use the bug report template
- Include system information
- Provide reproduction steps
- Attach relevant logs and screenshots

### Feature Requests
- Use the feature request template
- Explain the use case clearly
- Consider implementation complexity
- Discuss alternatives

## Release Process

### Version Numbering
Follow Semantic Versioning (SemVer):
- `MAJOR.MINOR.PATCH`
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

### Release Checklist
- [ ] Update version numbers
- [ ] Update CHANGELOG.md
- [ ] Tag release in Git
- [ ] Build and test packages
- [ ] Upload to PyPI
- [ ] Update documentation
- [ ] Announce release

## Getting Help

### Development Questions
- Open a discussion on GitHub
- Ask in development Discord/Slack
- Check existing issues and PRs

### Technical Issues
- Search existing issues first
- Provide detailed reproduction steps
- Include system and environment information

Thank you for contributing to make VS Code automation better for everyone!
