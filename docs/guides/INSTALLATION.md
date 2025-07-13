# Installation Guide

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
- Windows: `%APPDATA%\vscode-chat-continue\config.json`
- macOS: `~/Library/Application Support/vscode-chat-continue/config.json`
