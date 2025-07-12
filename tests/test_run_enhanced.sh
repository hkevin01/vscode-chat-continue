#!/bin/bash
# Test the improved run.sh with better error handling

cd /home/kevin/Projects/vscode-chat-continue

echo "=== Testing Enhanced Run Script ==="
echo ""

# Test CLI mode first
echo "1. Testing CLI mode:"
echo "Running: ./scripts/run.sh --cli --dry-run"
echo ""
timeout 10s ./scripts/run.sh --cli --dry-run
echo ""
echo "CLI test completed"
echo ""

# Test GUI mode (will likely fail gracefully and fall back to CLI)
echo "2. Testing GUI mode (expecting fallback to CLI):"
echo "Running: ./scripts/run.sh --gui --dry-run"
echo ""
timeout 10s ./scripts/run.sh --gui --dry-run
echo ""
echo "GUI test completed"
echo ""

echo "=== Test Results Summary ==="
echo "✓ Both tests completed"
echo "✓ If you see meaningful error messages, the improvements work"
echo "✓ If GUI fails gracefully and falls back to CLI, that's expected"
echo ""
echo "For production use:"
echo "  • Use --cli for headless/SSH environments"
echo "  • Use --gui for desktop environments with display"
