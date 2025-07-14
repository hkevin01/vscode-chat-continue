#!/bin/bash
# VS Code Chat Continue Automation Terminator - Simple Wrapper
# Usage: ./stop.sh [options]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_color() {
    color=$1
    shift
    echo -e "${color}$*${NC}"
}

print_error() { print_color "$RED" "❌ $*"; }
print_success() { print_color "$GREEN" "✅ $*"; }
print_warning() { print_color "$YELLOW" "⚠️  $*"; }
print_info() { print_color "$BLUE" "ℹ️  $*"; }

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Check if termination script exists
TERMINATOR_SCRIPT="$PROJECT_ROOT/scripts/terminate_automation.py"
if [ ! -f "$TERMINATOR_SCRIPT" ]; then
    print_error "Termination script not found: $TERMINATOR_SCRIPT"
    exit 1
fi

# Show help if requested
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "🛑 VS Code Chat Continue Automation Terminator"
    echo "=============================================="
    echo ""
    echo "USAGE:"
    echo "    ./stop.sh [options]"
    echo ""
    echo "OPTIONS:"
    echo "    --force      Force kill processes (SIGKILL)"
    echo "    --verbose    Show detailed output"
    echo "    --cleanup    Also clean temporary files"
    echo "    --dry-run    Show what would be terminated"
    echo "    --help       Show this help"
    echo ""
    echo "EXAMPLES:"
    echo "    ./stop.sh              # Graceful termination"
    echo "    ./stop.sh --force      # Force kill"
    echo "    ./stop.sh --cleanup    # Terminate and clean up"
    echo "    ./stop.sh --dry-run    # Preview what would be stopped"
    echo ""
    exit 0
fi

# Change to project root
cd "$PROJECT_ROOT"

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    print_info "Activating virtual environment..."
    source venv/bin/activate
fi

# Run the termination script
print_info "Running automation terminator..."
python "$TERMINATOR_SCRIPT" "$@"

# Deactivate virtual environment if it was activated
if [ -d "venv" ]; then
    deactivate
fi

print_success "Termination complete"
