#!/bin/bash
# Development helper script for VS Code Chat Continue Automation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Function to display help
show_help() {
    echo "VS Code Chat Continue Automation - Development Helper"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  test         Run all tests"
    echo "  test-unit    Run unit tests only"
    echo "  test-int     Run integration tests only"
    echo "  lint         Run code linting"
    echo "  format       Format code with black"
    echo "  type         Run type checking"
    echo "  coverage     Generate coverage report"
    echo "  docs         Generate documentation"
    echo "  clean        Clean build artifacts"
    echo "  build        Build package"
    echo "  install-dev  Install in development mode"
    echo "  help         Show this help"
    echo ""
}

# Ensure virtual environment is activated
activate_venv() {
    if [ ! -d "venv" ]; then
        echo "❌ Virtual environment not found. Run scripts/install.sh --dev first."
        exit 1
    fi
    
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        source venv/bin/activate
    fi
}

# Run tests
run_tests() {
    echo "🧪 Running tests..."
    activate_venv
    pytest tests/ -v
}

# Run unit tests
run_unit_tests() {
    echo "🔬 Running unit tests..."
    activate_venv
    pytest tests/unit/ -v
}

# Run integration tests
run_integration_tests() {
    echo "🔗 Running integration tests..."
    activate_venv
    pytest tests/integration/ -v
}

# Run linting
run_lint() {
    echo "🔍 Running linting..."
    activate_venv
    echo "Flake8..."
    flake8 src tests
    echo "Pylint..."
    pylint src
}

# Format code
format_code() {
    echo "🎨 Formatting code..."
    activate_venv
    black src tests
    isort src tests
}

# Type checking
run_type_check() {
    echo "🔬 Running type checking..."
    activate_venv
    mypy src/
}

# Generate coverage report
generate_coverage() {
    echo "📊 Generating coverage report..."
    activate_venv
    pytest tests/ --cov=src --cov-report=html --cov-report=term
    echo "Coverage report generated in htmlcov/"
}

# Generate documentation
generate_docs() {
    echo "📚 Generating documentation..."
    activate_venv
    sphinx-build -b html docs docs/_build
    echo "Documentation generated in docs/_build/"
}

# Clean build artifacts
clean_build() {
    echo "🧹 Cleaning build artifacts..."
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info/
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    rm -rf .pytest_cache/
    rm -rf htmlcov/
    rm -rf .coverage
}

# Build package
build_package() {
    echo "🏗️  Building package..."
    activate_venv
    python -m build
}

# Install in development mode
install_dev() {
    echo "🔧 Installing in development mode..."
    activate_venv
    pip install -e .
}

# Main command handling
case "$1" in
    "test")
        run_tests
        ;;
    "test-unit")
        run_unit_tests
        ;;
    "test-int")
        run_integration_tests
        ;;
    "lint")
        run_lint
        ;;
    "format")
        format_code
        ;;
    "type")
        run_type_check
        ;;
    "coverage")
        generate_coverage
        ;;
    "docs")
        generate_docs
        ;;
    "clean")
        clean_build
        ;;
    "build")
        build_package
        ;;
    "install-dev")
        install_dev
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    "")
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
