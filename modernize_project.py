#!/usr/bin/env python3
"""
Comprehensive Project Cleanup and Modernization Script
Organizes files, removes duplicates, and creates proper structure.
"""

import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Set


def create_organized_structure():
    """Create the modern project structure."""
    
    # Base directories
    directories = {
        # Core directories
        'src/': 'Source code',
        'tests/': 'Test files',
        'tests/unit/': 'Unit tests',
        'tests/integration/': 'Integration tests', 
        'tests/performance/': 'Performance tests',
        'tests/debug/': 'Debug scripts',
        'tests/fixtures/': 'Test fixtures and data',
        'docs/': 'Documentation',
        'docs/api/': 'API documentation',
        'docs/guides/': 'User guides',
        'docs/development/': 'Development documentation',
        'config/': 'Configuration files',
        'scripts/': 'Utility scripts',
        'tools/': 'Development tools',
        'assets/': 'Static assets',
        'logs/': 'Log files',
        'archive/': 'Archived/deprecated files',
        
        # Build and deployment
        'build/': 'Build artifacts',
        'dist/': 'Distribution files',
        '.github/workflows/': 'GitHub Actions',
        '.github/ISSUE_TEMPLATE/': 'Issue templates',
        '.github/PULL_REQUEST_TEMPLATE/': 'PR templates',
        
        # Temporary and cache
        'tmp/': 'Temporary files',
        '.pytest_cache/': 'Pytest cache',
        '__pycache__/': 'Python cache',
    }
    
    print("📁 Creating organized directory structure...")
    for directory, description in directories.items():
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ Created: {directory} - {description}")
        else:
            print(f"  ✓ Exists: {directory}")
    
    return directories

def organize_scattered_files():
    """Move scattered test and debug files to proper locations."""
    
    file_mappings = {
        # Root test files -> tests/integration/
        'test_actual_detection.py': 'tests/integration/',
        'test_button_detection.py': 'tests/integration/', 
        'test_beep_suppression.py': 'tests/integration/',
        'test_coordinate_clicking.py': 'tests/integration/',
        'test_coordinate_detection.py': 'tests/integration/',
        'test_enhanced_detection.py': 'tests/integration/',
        'test_full_automation.py': 'tests/integration/',
        'test_real_clicking.py': 'tests/integration/',
        'test_simple_screenshot.py': 'tests/integration/',
        
        # Debug files -> tests/debug/
        'debug_automation.py': 'tests/debug/',
        
        # Utility scripts -> scripts/
        'kill_automation.py': 'scripts/',
        'lightweight_automation.py': 'scripts/',
        'validate_modernization.py': 'scripts/',
        
        # Status and report files -> docs/reports/
        'AUTOMATION_STATUS.py': 'docs/reports/',
        'SUCCESS_REPORT.py': 'docs/reports/',
        'DEBUGGING_GUIDE.py': 'docs/development/',
        'DISCOVERY_SUMMARY.md': 'docs/reports/',
        'COORDINATE_ENHANCEMENT_SUMMARY.md': 'docs/reports/',
        'PROJECT_MODERNIZATION_SUMMARY.md': 'docs/reports/',
        
        # HTML test files -> tests/fixtures/
        'test_continue_button.html': 'tests/fixtures/',
    }
    
    print("\n📦 Organizing scattered files...")
    
    for filename, target_dir in file_mappings.items():
        source_path = Path(filename)
        if source_path.exists():
            target_path = Path(target_dir)
            target_path.mkdir(parents=True, exist_ok=True)
            
            destination = target_path / filename
            
            # Check if file already exists in destination
            if destination.exists():
                print(f"  ⚠️  {filename} already exists in {target_dir}, skipping")
                continue
                
            try:
                shutil.move(str(source_path), str(destination))
                print(f"  ✅ Moved: {filename} -> {target_dir}")
            except Exception as e:
                print(f"  ❌ Failed to move {filename}: {e}")
        else:
            print(f"  ℹ️  {filename} not found, skipping")

def remove_duplicate_files():
    """Identify and remove duplicate files."""
    
    print("\n🔍 Checking for duplicate files...")
    
    # Files that might have duplicates in tests/
    potential_duplicates = [
        ('tests/test_automation_quick.py', 'tests/integration/test_automation_quick.py'),
        ('tests/debug_button_detection_verbose.py', 'tests/debug/debug_button_detection_verbose.py'),
    ]
    
    for original, duplicate in potential_duplicates:
        orig_path = Path(original)
        dup_path = Path(duplicate)
        
        if orig_path.exists() and dup_path.exists():
            # Compare file sizes as a quick check
            if orig_path.stat().st_size == dup_path.stat().st_size:
                print(f"  🗑️  Removing duplicate: {duplicate}")
                dup_path.unlink()
            else:
                print(f"  ⚠️  Files differ in size, keeping both: {original} vs {duplicate}")

def create_missing_documentation():
    """Create missing essential documentation files."""
    
    print("\n📖 Creating/updating documentation...")
    
    # Create docs/reports directory
    Path('docs/reports').mkdir(parents=True, exist_ok=True)
    Path('docs/guides').mkdir(parents=True, exist_ok=True)
    Path('docs/development').mkdir(parents=True, exist_ok=True)
    Path('docs/api').mkdir(parents=True, exist_ok=True)
    
    # Create PROJECT_STRUCTURE.md
    structure_content = """# Project Structure

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
"""
    
    with open('docs/PROJECT_STRUCTURE.md', 'w') as f:
        f.write(structure_content)
    print("  ✅ Created: docs/PROJECT_STRUCTURE.md")
    
    # Create installation guide
    install_guide = """# Installation Guide

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (for development)

## 🚀 Quick Installation

### Option 1: Using pip (Recommended)
```bash
pip install vscode-chat-continue
```

### Option 2: From Source
```bash
git clone https://github.com/hkevin01/vscode-chat-continue.git
cd vscode-chat-continue
pip install -e .
```

## 🔧 Development Setup

```bash
# Clone repository
git clone https://github.com/hkevin01/vscode-chat-continue.git
cd vscode-chat-continue

# Install development dependencies
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/

# Start GUI
python src/gui/main_window.py
```

## 🐧 Linux-Specific Setup

### Install System Dependencies
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-dev python3-pyqt6 tesseract-ocr

# Fedora
sudo dnf install python3-devel python3-qt6 tesseract

# Arch Linux
sudo pacman -S python-pyqt6 tesseract
```

### Wayland Support
For Wayland desktop environments, coordinate-based fallback detection is automatically enabled.

## 🪟 Windows Setup

1. Install Python 3.8+ from python.org
2. Install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki
3. Add Tesseract to your PATH environment variable
4. Follow the pip installation steps above

## 🍎 macOS Setup

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python3 tesseract

# Follow the pip installation steps above
```

## ✅ Verification

Test your installation:
```bash
python -c "from src.core.automation_engine import AutomationEngine; print('✅ Installation successful!')"
```

## 🔧 Configuration

The application will create a config file at:
- Linux: `~/.config/vscode-chat-continue/config.json`
- Windows: `%APPDATA%\\vscode-chat-continue\\config.json`
- macOS: `~/Library/Application Support/vscode-chat-continue/config.json`
"""
    
    with open('docs/guides/INSTALLATION.md', 'w') as f:
        f.write(install_guide)
    print("  ✅ Created: docs/guides/INSTALLATION.md")

def clean_temporary_files():
    """Remove temporary and cache files."""
    
    print("\n🧹 Cleaning temporary files...")
    
    # Patterns to clean
    cleanup_patterns = [
        '__pycache__',
        '*.pyc',
        '*.pyo', 
        '.pytest_cache',
        '*.egg-info',
        'build/',
        'dist/',
        '.coverage',
        'htmlcov/',
        '*.log',
        'tmp/*',
    ]
    
    # Clean patterns
    import glob
    for pattern in cleanup_patterns:
        if '*' in pattern:
            for file_path in glob.glob(pattern, recursive=True):
                path = Path(file_path)
                if path.exists():
                    if path.is_file():
                        path.unlink()
                        print(f"  🗑️  Removed file: {file_path}")
                    elif path.is_dir():
                        shutil.rmtree(path)
                        print(f"  🗑️  Removed directory: {file_path}")

def update_gitignore():
    """Update .gitignore with comprehensive patterns."""
    
    gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/settings.json
.vscode/launch.json
.idea/
*.swp
*.swo
*~

# Project specific
logs/
tmp/
temp/
screenshots/
*.png
*.jpg
*.jpeg
*.gif
.DS_Store
Thumbs.db

# Configuration (keep templates)
config/user.json
*.local.json

# System files
.directory
desktop.ini

# Archive folder
archive/

# Build artifacts
build/
dist/
*.deb
*.rpm
*.dmg
*.exe
*.msi
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    print("  ✅ Updated: .gitignore")

def main():
    """Run the comprehensive cleanup and modernization."""
    
    print("🚀 VS Code Chat Continue - Comprehensive Project Modernization")
    print("=" * 70)
    
    # Step 1: Create organized structure
    create_organized_structure()
    
    # Step 2: Organize scattered files  
    organize_scattered_files()
    
    # Step 3: Remove duplicates
    remove_duplicate_files()
    
    # Step 4: Create documentation
    create_missing_documentation()
    
    # Step 5: Clean temporary files
    clean_temporary_files()
    
    # Step 6: Update .gitignore
    update_gitignore()
    
    print("\n" + "=" * 70)
    print("✅ Project modernization complete!")
    print("\n📊 Summary:")
    print("  • Organized file structure with logical directories")
    print("  • Moved scattered test and debug files to proper locations")
    print("  • Removed duplicate and temporary files")
    print("  • Created comprehensive documentation")
    print("  • Updated .gitignore with modern patterns")
    print("\n🎯 Next steps:")
    print("  • Review and commit changes")
    print("  • Run tests to ensure nothing broke")
    print("  • Update CI/CD workflows if needed")

if __name__ == "__main__":
    main()
