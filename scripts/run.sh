#!/bin/bash
# VS Code Chat Continue Button Automation - Run Script
# Usage: ./scripts/run.sh [options]
# Options:
#   --gui         Launch GUI interface
#   --dry-run     Run in dry-run mode (no actual clicking)
#   --config FILE Use custom configuration file
#   --help        Show this help message

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_color() {
    color=$1
    shift
    echo -e "${color}$*${NC}"
}

print_error() { print_color "$RED" "❌ $*"; }
print_success() { print_color "$GREEN" "✅ $*"; }
print_warning() { print_color "$YELLOW" "⚠️  $*"; }
print_info() { print_color "$BLUE" "ℹ️  $*"; }

# Show help message
show_help() {
    cat << EOF
VS Code Chat Continue Button Automation - Run Script

USAGE:
    ./scripts/run.sh [OPTIONS]

OPTIONS:
    --lightweight   Use lightweight command-line interface (default)
    --gui           Launch GUI interface (resource intensive)
    --cli           Use command-line interface (same as --lightweight)
    --dry-run       Run in dry-run mode (no actual clicking)
    --config FILE   Use custom configuration file
    --validate      Validate installation and dependencies
    --help, -h      Show this help message

EXAMPLES:
    ./scripts/run.sh                    # Use lightweight interface (default)
    ./scripts/run.sh --lightweight      # Use lightweight interface (explicit)
    ./scripts/run.sh --gui              # Use GUI interface (resource intensive)
    ./scripts/run.sh --dry-run          # Test mode without clicking
    ./scripts/run.sh --lightweight --dry-run  # Lightweight test mode
    ./scripts/run.sh --validate         # Check if everything is working

SETUP:
    The script automatically installs dependencies and sets up the virtual 
    environment on first run. No manual installation required!

CONFIGURATION:
    Default config: ~/.config/vscode-chat-continue/config.json
    Custom config:  ./scripts/run.sh --config /path/to/config.json

DEFAULT BEHAVIOR:
    By default, the script uses the lightweight command-line interface for 
    optimal performance. Use --gui to launch the GUI if needed.

For more information, see docs/USAGE.md
EOF
}

# Parse command line arguments
GUI_MODE=false  # Default to lightweight mode for better performance
DRY_RUN=false
CONFIG_FILE=""
VALIDATE_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --gui)
            GUI_MODE=true
            shift
            ;;
        --lightweight|--cli)
            GUI_MODE=false
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --validate)
            VALIDATE_ONLY=true
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

print_info "Starting VS Code Chat Continue Automation..."
print_info "Project directory: $PROJECT_DIR"

# Check if virtual environment exists and set it up if needed
if [ ! -d "venv" ]; then
    print_warning "Virtual environment not found. Setting up automatically..."
    
    # Check if install script exists
    if [ ! -f "scripts/install.sh" ]; then
        print_error "Installation script not found at scripts/install.sh"
        exit 1
    fi
    
    # Make install script executable and run it
    chmod +x scripts/install.sh
    print_info "Running installation script..."
    
    if ./scripts/install.sh; then
        print_success "Installation completed successfully!"
    else
        print_error "Installation failed. Please check the error messages above."
        exit 1
    fi
else
    print_info "Virtual environment found."
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate

# Validate dependencies
print_info "Checking dependencies..."
missing_deps=()

# Check Python modules
python_modules=(
    "pyautogui:PyAutoGUI for automation"
    "cv2:OpenCV for image processing"
    "pytesseract:Tesseract OCR for text recognition"
    "psutil:Process utilities"
    "pynput:Input monitoring"
)

for module_info in "${python_modules[@]}"; do
    module_name="${module_info%%:*}"
    module_desc="${module_info##*:}"
    
    if ! python -c "import $module_name" 2>/dev/null; then
        missing_deps+=("$module_desc")
    fi
done

# Check GUI dependencies if needed
if $GUI_MODE; then
    if ! python -c "import PyQt6" 2>/dev/null; then
        missing_deps+=("PyQt6 for GUI interface")
    fi
fi

# Auto-install tesseract if missing
install_tesseract() {
    print_warning "Tesseract OCR not found. Installing automatically..."
    
    if command -v apt-get >/dev/null 2>&1; then
        print_info "Installing tesseract using apt-get..."
        sudo apt-get update && sudo apt-get install -y tesseract-ocr tesseract-ocr-eng
    elif command -v dnf >/dev/null 2>&1; then
        print_info "Installing tesseract using dnf..."
        sudo dnf install -y tesseract tesseract-langpack-eng
    elif command -v pacman >/dev/null 2>&1; then
        print_info "Installing tesseract using pacman..."
        sudo pacman -S --noconfirm tesseract tesseract-data-eng
    elif command -v zypper >/dev/null 2>&1; then
        print_info "Installing tesseract using zypper..."
        sudo zypper install -y tesseract-ocr tesseract-ocr-traineddata-english
    else
        print_error "Could not determine package manager."
        print_info "Please install tesseract-ocr manually:"
        print_info "  Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-eng"
        print_info "  Fedora/RHEL:   sudo dnf install tesseract tesseract-langpack-eng"
        print_info "  Arch Linux:    sudo pacman -S tesseract tesseract-data-eng"
        return 1
    fi
    
    # Verify installation
    if command -v tesseract &> /dev/null; then
        print_success "Tesseract OCR installed successfully!"
        tesseract --version | head -1
        return 0
    else
        print_error "Tesseract installation failed."
        return 1
    fi
}

# Check system dependencies
if ! command -v tesseract &> /dev/null; then
    print_warning "Tesseract OCR not found. Attempting auto-installation..."
    if install_tesseract; then
        print_success "Tesseract OCR installed successfully!"
    else
        missing_deps+=("tesseract-ocr system package")
        print_error "Auto-installation failed. Please install manually."
    fi
fi

if [ ${#missing_deps[@]} -gt 0 ]; then
    print_error "Missing dependencies:"
    for dep in "${missing_deps[@]}"; do
        echo "  - $dep"
    done
    print_info "Please run: ./scripts/install.sh"
    exit 1
fi

print_success "All dependencies are available"

# Run validation if requested
if $VALIDATE_ONLY; then
    print_info "Running project validation..."
    if python tests/validate_project.py; then
        print_success "Project validation passed!"
        exit 0
    else
        print_error "Project validation failed!"
        exit 1
    fi
fi

# Check display environment for GUI
if $GUI_MODE; then
    if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ]; then
        print_error "No display environment detected."
        print_info "GUI mode requires X11 (\$DISPLAY) or Wayland (\$WAYLAND_DISPLAY)"
        exit 1
    fi
    print_info "Display environment detected: ${DISPLAY:-$WAYLAND_DISPLAY}"
fi

# Check if VS Code is running
print_info "Checking for VS Code processes..."
if ! pgrep -f "code" > /dev/null; then
    print_warning "VS Code doesn't appear to be running."
    print_info "For best results, start VS Code with Copilot Chat sessions first."
    
    if ! $GUI_MODE; then
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Exiting. Start VS Code and try again."
            exit 1
        fi
    fi
else
    vscode_count=$(pgrep -f "code" | wc -l)
    print_success "Found $vscode_count VS Code process(es)"
fi

# Prepare command line arguments
PYTHON_ARGS=()

if $DRY_RUN; then
    PYTHON_ARGS+=("--dry-run")
fi

if [ -n "$CONFIG_FILE" ]; then
    if [ ! -f "$CONFIG_FILE" ]; then
        print_error "Configuration file not found: $CONFIG_FILE"
        exit 1
    fi
    PYTHON_ARGS+=("--config" "$CONFIG_FILE")
fi

# Display startup information
echo ""
print_success "🚀 Starting VS Code Chat Continue Automation"
print_info "Mode: $(if $GUI_MODE; then echo "GUI Interface"; else echo "Lightweight CLI"; fi)"
print_info "Dry Run: $(if $DRY_RUN; then echo "Enabled (no actual clicking)"; else echo "Disabled"; fi)"
print_info "Config: ${CONFIG_FILE:-"Default (~/.config/vscode-chat-continue/config.json)"}"
print_info "Project: $PROJECT_DIR"
echo ""
print_info "Press Ctrl+C to stop gracefully"
echo ""

# Set error handling for the main execution
trap 'print_warning "Stopping automation..."; exit 130' INT

# Run the appropriate application
if $GUI_MODE; then
    # Test PyQt6 availability first
    if ! python -c "import PyQt6" 2>/dev/null; then
        print_error "PyQt6 not available. Falling back to lightweight mode..."
        print_info "Install PyQt6 with: pip install PyQt6"
        GUI_MODE=false
    fi
fi

if $GUI_MODE; then
    
    # Test PyQt6 availability first
    if ! python -c "import PyQt6" 2>/dev/null; then
        print_error "PyQt6 not available. Falling back to CLI mode..."
        print_info "Install PyQt6 with: pip install PyQt6"
        GUI_MODE=false
    fi
fi

if $GUI_MODE; then
    # Try to launch GUI through main.py with --gui flag
    print_info "Starting GUI mode..."
    if ! python src/main.py --gui "${PYTHON_ARGS[@]}"; then
        print_error "GUI launch failed. Falling back to lightweight mode..."
        print_info "This might be due to:"
        print_info "  • No display environment (SSH without X11 forwarding)"
        print_info "  • Missing PyQt6 dependencies"
        print_info "  • Display permissions issues"
        print_info ""
        print_info "Starting lightweight automation..."
        python "$SCRIPT_DIR/lightweight_automation.py" "${PYTHON_ARGS[@]}"
    fi
else
    print_info "Starting lightweight automation..."
    python "$SCRIPT_DIR/lightweight_automation.py" "${PYTHON_ARGS[@]}"
fi

# Cleanup
deactivate
echo ""
print_success "👋 VS Code Chat Continue Automation stopped."
