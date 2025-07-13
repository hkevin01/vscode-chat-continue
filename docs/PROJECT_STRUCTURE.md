# Project Structure

## 📁 Directory Organization

```
vscode-chat-continue/
├── 📁 src/                          # Source code
│   ├── 📁 core/                     # Core automation logic
│   ├── 📁 gui/                      # PyQt6 GUI components
│   └── 📁 utils/                    # Utility modules
├── 📁 tests/                        # Test suite
│   ├── 📁 unit/                     # Unit tests
│   ├── 📁 integration/              # Integration tests
│   ├── 📁 performance/              # Performance tests
│   ├── 📁 debug/                    # Debug scripts
│   └── 📁 fixtures/                 # Test fixtures
├── 📁 docs/                         # Documentation
│   ├── 📁 api/                      # API documentation
│   ├── 📁 guides/                   # User guides
│   ├── 📁 development/              # Development docs
│   └── 📁 reports/                  # Status reports
├── 📁 config/                       # Configuration files
├── 📁 scripts/                      # Utility scripts
├── 📁 tools/                        # Development tools
├── 📁 .github/                      # GitHub workflows
└── 📁 archive/                      # Archived files
```

## 🧩 Core Components

### Source Code (`src/`)
- **core/**: Automation engine, button detection, window management
- **gui/**: PyQt6 interface with dark theme and tabbed layout
- **utils/**: Screenshot capture, logging, audio suppression

### Testing (`tests/`)
- **unit/**: Individual component tests
- **integration/**: End-to-end automation tests
- **performance/**: Benchmarks and optimization tests
- **debug/**: Debug utilities and diagnostic scripts

### Documentation (`docs/`)
- **api/**: Generated API documentation
- **guides/**: User installation and usage guides
- **development/**: Developer contribution guidelines
- **reports/**: Project status and enhancement reports

## 🔧 Configuration

- `pyproject.toml`: Modern Python packaging
- `config/default.json`: Application configuration
- `.github/workflows/`: CI/CD automation
- Requirements files for dependencies

## 🚀 Key Features

- Multi-method Continue button detection
- Cross-platform support (Linux/Windows/macOS)
- Professional GUI with real-time monitoring
- Comprehensive test suite with 80%+ coverage
- Modern Python packaging and development workflow
