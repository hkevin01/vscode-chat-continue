#!/bin/bash
# VS Code Chat Continue Automation - SAFE MODE
# Optimized to prevent system freezing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_color() { echo -e "${1}$2${NC}"; }
print_error() { print_color "$RED" "❌ $*"; }
print_success() { print_color "$GREEN" "✅ $*"; }
print_warning() { print_color "$YELLOW" "⚠️  $*"; }
print_info() { print_color "$BLUE" "ℹ️  $*"; }

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🛡️  VS Code Chat Continue Automation - SAFE MODE"
echo "=================================================="
echo ""
print_warning "This version is optimized to prevent system freezing:"
echo "   • 🐌 Conservative resource usage (10+ second intervals)"
echo "   • 🧠 Minimal memory footprint" 
echo "   • 📊 Automatic performance monitoring"
echo "   • 🔄 System load detection"
echo "   • 🛑 Coordinate-based fallback (no image processing)"
echo ""

# Check if we should force stop existing processes first
if [ "$1" = "--stop-first" ]; then
    print_info "Stopping any existing automation processes first..."
    "$SCRIPT_DIR/stop.sh" --force --cleanup || true
    echo ""
fi

# Change to project root
cd "$SCRIPT_DIR"

# Check if virtual environment exists and activate it
if [ -d "../venv" ]; then
    print_info "Activating virtual environment..."
    source ../venv/bin/activate
fi

# Check system load before starting
if [ -f "/proc/loadavg" ]; then
    LOAD=$(cat /proc/loadavg | cut -d' ' -f1)
    if (( $(echo "$LOAD > 2.0" | bc -l) )); then
        print_warning "High system load detected: $LOAD"
        print_warning "Consider waiting for system load to decrease"
        echo ""
    fi
fi

# Install wmctrl if needed (for lightweight window detection)
if ! command -v wmctrl &> /dev/null; then
    print_warning "wmctrl not found - automation will use fallback method"
    print_info "To install: sudo apt-get install wmctrl"
    echo ""
fi

print_info "Starting SAFE automation (system-friendly mode)..."
print_info "Press Ctrl+C to stop gracefully"
echo ""

# Run the safe automation
python safe_automation.py

# Deactivate virtual environment if it was activated
if [ -d "../venv" ]; then
    deactivate
fi

print_success "Safe automation stopped"
