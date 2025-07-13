# VS Code Chat Continue - Project Configuration

## Project Overview
An intelligent automation tool for VS Code chat interfaces that automatically detects and clicks "Continue" buttons to maintain conversation flow.

## Key Technologies
- **Language**: Python 3.8+
- **GUI Framework**: PyQt6
- **Computer Vision**: OpenCV, PIL
- **OCR Engine**: Tesseract
- **Testing**: pytest, coverage
- **Packaging**: Modern pyproject.toml

## Architecture
- **Modular Design**: Core automation engine with pluggable detection methods
- **Cross-Platform**: Linux (X11/Wayland), Windows, macOS support
- **Fallback Strategies**: Multiple detection methods for reliability
- **Configuration-Driven**: JSON-based configuration with hot reload

## Development Workflow
1. **Setup**: `./run.sh` for automated environment setup
2. **Testing**: `python -m pytest tests/ -v` for comprehensive test suite
3. **Quality**: Automated formatting (black), linting (flake8), type checking (mypy)
4. **CI/CD**: GitHub Actions for multi-Python version testing

## Code Standards
- Type hints required for all functions
- Comprehensive docstrings following Google style
- 80%+ test coverage requirement
- PEP 8 compliance with black formatting

## Common Patterns
- Dependency injection for testability
- Strategy pattern for detection methods
- Observer pattern for GUI updates
- Graceful degradation with fallback methods
