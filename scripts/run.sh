#!/bin/bash
# VS Code Chat Continue Button Automation - Run Script

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run scripts/install.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if required dependencies are installed
if ! python -c "import pyautogui, cv2, pytesseract" 2>/dev/null; then
    echo "❌ Dependencies not installed. Please run scripts/install.sh first."
    exit 1
fi

# Check if VS Code is running
if ! pgrep -f "code" > /dev/null; then
    echo "⚠️  VS Code doesn't appear to be running."
    echo "Please start VS Code with Copilot Chat sessions before running this tool."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Display startup message
echo "🚀 Starting VS Code Chat Continue Automation..."
echo "📊 Press Ctrl+C to stop gracefully"
echo "🔧 Configuration: ~/.config/vscode-chat-continue/config.json"
echo ""

# Run the main application
python src/main.py "$@"

# Deactivate virtual environment
deactivate

echo "👋 VS Code Chat Continue Automation stopped."
