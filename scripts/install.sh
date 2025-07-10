#!/bin/bash
set -e

echo "🚀 Installing VS Code Chat Continue Automation Tool"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Utility functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    log_error "This tool currently only supports Linux. Detected OS: $OSTYPE"
    exit 1
fi

log_info "Detected Linux system: $(lsb_release -d 2>/dev/null | cut -f2 || echo "Unknown distribution")"

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))" 2>/dev/null || echo "0.0")
REQUIRED_VERSION="3.8"

if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    log_success "Python version $PYTHON_VERSION meets requirements (>= $REQUIRED_VERSION)"
else
    log_error "Python 3.8+ required. Found: $PYTHON_VERSION"
    log_info "Please install Python 3.8 or newer and try again."
    exit 1
fi

# Detect package manager and install system dependencies
install_system_deps() {
    log_info "Installing system dependencies..."
    
    if command -v apt-get >/dev/null 2>&1; then
        # Ubuntu/Debian
        log_info "Detected APT package manager (Ubuntu/Debian)"
        sudo apt-get update
        sudo apt-get install -y \
            python3-pip \
            python3-venv \
            python3-dev \
            python3-tk \
            libx11-dev \
            libxtst6 \
            libxrandr2 \
            tesseract-ocr \
            tesseract-ocr-eng \
            libopencv-dev \
            python3-opencv \
            git
            
    elif command -v dnf >/dev/null 2>&1; then
        # Fedora/RHEL
        log_info "Detected DNF package manager (Fedora/RHEL)"
        sudo dnf install -y \
            python3-pip \
            python3-devel \
            python3-tkinter \
            libX11-devel \
            libXtst \
            libXrandr \
            tesseract \
            tesseract-langpack-eng \
            opencv-python \
            git
            
    elif command -v pacman >/dev/null 2>&1; then
        # Arch Linux
        log_info "Detected Pacman package manager (Arch Linux)"
        sudo pacman -S --noconfirm \
            python \
            python-pip \
            tk \
            libx11 \
            libxtst \
            libxrandr \
            tesseract \
            tesseract-data-eng \
            opencv \
            git
            
    elif command -v zypper >/dev/null 2>&1; then
        # openSUSE
        log_info "Detected Zypper package manager (openSUSE)"
        sudo zypper install -y \
            python3-pip \
            python3-devel \
            python3-tk \
            libX11-devel \
            libXtst6 \
            libXrandr2 \
            tesseract-ocr \
            tesseract-ocr-traineddata-english \
            python3-opencv \
            git
    else
        log_warning "Could not detect package manager. Please install dependencies manually:"
        log_info "Required: python3-dev, python3-tk, libx11-dev, libxtst, tesseract-ocr"
    fi
}

# Check if VS Code is installed
check_vscode() {
    if command -v code >/dev/null 2>&1; then
        VSCODE_VERSION=$(code --version | head -n1)
        log_success "VS Code detected: $VSCODE_VERSION"
    else
        log_warning "VS Code not found in PATH"
        log_info "Please install VS Code and ensure it's accessible via 'code' command"
        log_info "Download from: https://code.visualstudio.com/"
    fi
}

# Create virtual environment and install Python dependencies
setup_python_env() {
    log_info "Setting up Python virtual environment..."
    
    # Create virtual environment
    if [[ ! -d "venv" ]]; then
        python3 -m venv venv
        log_success "Created virtual environment"
    else
        log_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    log_info "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Install package in development mode
    log_info "Installing vscode-continue package..."
    pip install -e .
    
    log_success "Python environment setup complete"
}

# Create configuration directory and files
setup_config() {
    log_info "Setting up configuration..."
    
    CONFIG_DIR="$HOME/.config/vscode-continue"
    mkdir -p "$CONFIG_DIR"
    
    # Copy default configuration if it doesn't exist
    if [[ ! -f "$CONFIG_DIR/config.json" ]]; then
        cp config/default.json "$CONFIG_DIR/config.json"
        log_success "Created default configuration at $CONFIG_DIR/config.json"
    else
        log_info "Configuration already exists at $CONFIG_DIR/config.json"
    fi
    
    # Create data and cache directories
    mkdir -p "$HOME/.local/share/vscode-continue"
    mkdir -p "$HOME/.cache/vscode-continue"
    
    log_success "Configuration setup complete"
}

# Create desktop entry
create_desktop_entry() {
    log_info "Creating desktop entry..."
    
    DESKTOP_FILE="$HOME/.local/share/applications/vscode-continue.desktop"
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=VS Code Continue Automator
Comment=Automate clicking Continue buttons in VS Code Copilot Chat
Exec=$SCRIPT_DIR/venv/bin/python -m vscode_continue.main --gui
Icon=applications-development
Terminal=false
Categories=Development;Utility;
Keywords=vscode;automation;copilot;chat;
EOF
    
    chmod +x "$DESKTOP_FILE"
    log_success "Desktop entry created"
}

# Run tests to verify installation
run_tests() {
    log_info "Running installation tests..."
    
    source venv/bin/activate
    
    # Test imports
    if python3 -c "import vscode_continue; print('Import test passed')" 2>/dev/null; then
        log_success "Import test passed"
    else
        log_error "Import test failed"
        return 1
    fi
    
    # Test CLI
    if python3 -m vscode_continue.main --help >/dev/null 2>&1; then
        log_success "CLI test passed"
    else
        log_error "CLI test failed"
        return 1
    fi
    
    # Test system dependencies
    if python3 -c "import pyautogui, pytesseract, cv2, Xlib; print('Dependencies test passed')" 2>/dev/null; then
        log_success "Dependencies test passed"
    else
        log_warning "Some dependencies may not be properly installed"
        log_info "Run 'python3 -c \"import pyautogui, pytesseract, cv2, Xlib\"' to check specific issues"
    fi
    
    log_success "Installation tests completed"
}

# Main installation flow
main() {
    log_info "Starting installation process..."
    
    # Check prerequisites
    log_info "Checking prerequisites..."
    
    # Install system dependencies
    install_system_deps
    
    # Check VS Code
    check_vscode
    
    # Setup Python environment
    setup_python_env
    
    # Setup configuration
    setup_config
    
    # Create desktop entry
    create_desktop_entry
    
    # Run tests
    run_tests
    
    log_success "Installation completed successfully!"
    echo
    log_info "Next steps:"
    echo "  1. Activate the virtual environment: source venv/bin/activate"
    echo "  2. Test the installation: vscode-continue --help"
    echo "  3. Run a dry test: vscode-continue --dry-run"
    echo "  4. Configure settings: nano ~/.config/vscode-continue/config.json"
    echo "  5. Start automation: vscode-continue --watch"
    echo
    log_info "Documentation available at: docs/USAGE.md"
    log_info "For issues, see: docs/TROUBLESHOOTING.md"
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
