# Project Structure

This document outlines the modernized structure of the VS Code Chat Continue automation project.

## 📁 Directory Structure

```
vscode-chat-continue/
├── 📁 .github/                    # GitHub-specific files
│   ├── workflows/                 # CI/CD workflows  
│   ├── ISSUE_TEMPLATE/           # Issue templates
│   ├── PULL_REQUEST_TEMPLATE.md  # PR template
│   └── CODEOWNERS                # Code ownership
│
├── 📁 .copilot/                   # GitHub Copilot configuration
│   └── copilot-instructions.md   # Copilot behavior guidelines
│
├── 📁 src/                        # Source code
│   ├── 📁 core/                   # Core automation logic
│   │   ├── automation_engine.py  # Main automation controller
│   │   ├── button_finder.py      # Button detection algorithms
│   │   ├── click_automator.py    # Click execution
│   │   ├── config_manager.py     # Configuration management
│   │   └── window_detector.py    # Window detection utilities
│   ├── 📁 gui/                    # User interface
│   │   └── main_window.py        # PyQt6 GUI application
│   ├── 📁 utils/                  # Utility modules
│   │   ├── screen_capture.py     # Screen capture utilities
│   │   ├── logger.py             # Logging configuration
│   │   └── audio_suppressor.py   # Audio management
│   ├── 📁 templates/              # Template files
│   └── main.py                   # Main entry point
│
├── 📁 tests/                      # Test suite
│   ├── 📁 unit/                   # Unit tests
│   ├── 📁 integration/           # Integration tests
│   │   ├── test_*.py             # Automated test files
│   │   ├── debug_*.py            # Debug utilities
│   │   └── performance_*.py      # Performance tests
│   └── 📁 performance/           # Performance benchmarks
│
├── 📁 docs/                       # Documentation
│   ├── api/                      # API documentation
│   ├── guides/                   # User guides
│   └── development/              # Development docs
│
├── 📁 config/                     # Configuration files
│   └── default.json              # Default configuration
│
├── 📁 scripts/                    # Utility scripts
│   ├── install.sh                # Installation script
│   ├── setup.py                  # Setup utilities
│   └── cleanup_*.sh              # Cleanup scripts
│
├── 📁 logs/                       # Log files
│
├── 📄 Core Files
├── pyproject.toml                # Modern Python packaging
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
├── README.md                     # Project overview
├── CHANGELOG.md                  # Version history
├── CONTRIBUTING.md               # Contribution guidelines
├── SECURITY.md                   # Security policy
├── WORKFLOW.md                   # Development workflow
├── PROJECT_GOALS.md              # Project objectives
├── .gitignore                    # Git ignore rules
├── .editorconfig                 # Editor configuration
├── .pylintrc                     # Python linting rules
└── run.sh                        # Quick start script
```

## 🏗️ Architecture Overview

### Core Components

1. **Automation Engine** (`src/core/automation_engine.py`)
   - Orchestrates the entire automation process
   - Manages window detection and button clicking cycles
   - Handles configuration and safety features

2. **Button Finder** (`src/core/button_finder.py`)
   - Advanced computer vision and OCR-based button detection
   - Multiple detection strategies with fallback support
   - Coordinate-based detection for Wayland compatibility

3. **GUI Interface** (`src/gui/main_window.py`)
   - Modern PyQt6 interface with dark theme
   - Real-time monitoring and statistics
   - Configuration management interface

4. **Window Detector** (`src/core/window_detector.py`)
   - Multi-platform window detection
   - VS Code instance identification
   - Window focus management

### Testing Strategy

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end automation testing  
- **Performance Tests**: Benchmarking and optimization
- **Manual Tests**: Interactive debugging and validation

### Configuration Management

- JSON-based configuration with validation
- Environment-specific settings
- Hot-reload support for development
- Secure credential handling

## 🔄 Development Workflow

1. **Feature Development**: Create feature branch from `main`
2. **Testing**: Run full test suite (`pytest tests/`)
3. **Code Quality**: Automated linting and formatting
4. **Review**: Pull request with automated CI checks
5. **Deployment**: Automated releases via GitHub Actions

## 📦 Deployment

- **Local Development**: `./run.sh` for quick start
- **Package Installation**: `pip install -e .` for development
- **Production**: Docker containers (planned)
- **Distribution**: PyPI package (planned)

## 🛠️ Technology Stack

- **Language**: Python 3.8+
- **GUI Framework**: PyQt6
- **Computer Vision**: OpenCV, PIL
- **OCR**: Tesseract
- **Build System**: setuptools with pyproject.toml
- **Testing**: pytest
- **CI/CD**: GitHub Actions
- **Documentation**: Markdown with automated generation
