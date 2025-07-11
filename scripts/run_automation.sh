#!/bin/bash
"""
Wrapper script to run VS Code Chat Continue automation with proper environment.
"""

set -e

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Set up environment for GUI access
export DISPLAY=${DISPLAY:-:0}

echo "🚀 VS Code Chat Continue Automation"
echo "===================================="
echo "📁 Project: $PROJECT_ROOT"
echo "🖥️  Display: $DISPLAY"

# Check if VS Code is running
CODE_PROCESSES=$(ps aux | grep -v grep | grep -c "code.*--no-sandbox" || echo "0")
if [ "$CODE_PROCESSES" -eq 0 ]; then
    echo "⚠️  Warning: No VS Code processes detected."
    echo "   Please open VS Code before running the automation."
    echo ""
fi

# Parse command line arguments
DRY_RUN=""
DEBUG=""
GUI_MODE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        --debug)
            DEBUG="--debug"
            shift
            ;;
        --gui)
            GUI_MODE="1"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --dry-run    Run in dry-run mode (no actual clicking)"
            echo "  --debug      Enable debug logging"
            echo "  --gui        Start GUI instead of CLI"
            echo "  --help       Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --dry-run --debug    # Test mode with debug output"
            echo "  $0 --gui               # Start GUI interface"
            echo "  $0                     # Start CLI automation"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run the appropriate mode
if [ "$GUI_MODE" = "1" ]; then
    echo "🖼️  Starting GUI interface..."
    python src/gui/main_window.py
else
    echo "⚙️  Starting CLI automation..."
    if [ -n "$DRY_RUN" ]; then
        echo "   🧪 Dry-run mode enabled (no actual clicking)"
    fi
    if [ -n "$DEBUG" ]; then
        echo "   🔍 Debug logging enabled"
    fi
    echo ""
    
    python src/main.py $DRY_RUN $DEBUG
fi
