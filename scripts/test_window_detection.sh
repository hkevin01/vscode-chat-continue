#!/bin/bash
"""
Comprehensive automation test script to verify VS Code window detection works.
"""

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🔍 VS Code Chat Continue Automation - Window Detection Test"
echo "================================================================"
echo "📁 Project root: $PROJECT_ROOT"
echo "🖥️  Testing environment setup..."

# Set up environment for GUI access
export DISPLAY=:0
echo "   ✓ DISPLAY set to: $DISPLAY"

# Check for required tools
echo ""
echo "🛠️  Checking required tools..."

if command -v xwininfo &> /dev/null; then
    echo "   ✓ xwininfo available"
else
    echo "   ⚠️  xwininfo not found (not critical)"
fi

if command -v scrot &> /dev/null; then
    echo "   ✓ scrot available for screenshots"
else
    echo "   ⚠️  scrot not found - installing..."
    sudo apt update && sudo apt install -y scrot
fi

# Check VS Code processes
echo ""
echo "📋 Checking VS Code processes..."
CODE_PROCESSES=$(ps aux | grep -v grep | grep -c "code.*--no-sandbox" || echo "0")
echo "   Found $CODE_PROCESSES main VS Code processes"

if [ "$CODE_PROCESSES" -eq 0 ]; then
    echo "   ❌ No VS Code processes found - please open VS Code first"
    exit 1
fi

# Check VS Code windows via X11
echo ""
echo "🪟 Checking VS Code windows via X11..."
VSCODE_WINDOWS=$(xwininfo -root -tree 2>/dev/null | grep -i "visual studio code" | wc -l || echo "0")
echo "   Found $VSCODE_WINDOWS VS Code windows in X11"

# Test Python window detection
echo ""
echo "🐍 Testing Python window detection..."
echo "   Running WindowDetector test..."

python3 -c "
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path('$PROJECT_ROOT')))

try:
    from src.core.window_detector import WindowDetector
    from src.core.config_manager import ConfigManager
    from src.utils.logger import setup_logging
    
    # Setup logging
    setup_logging('INFO')
    
    # Test window detection
    detector = WindowDetector()
    windows = detector.get_vscode_windows()
    
    print(f'   ✓ WindowDetector created successfully')
    print(f'   ✓ Found {len(windows)} VS Code windows')
    
    for i, window in enumerate(windows, 1):
        title = window.title[:60] + '...' if len(window.title) > 60 else window.title
        print(f'      {i}. \"{title}\"')
        print(f'         PID: {window.pid}, Position: ({window.x}, {window.y}), Size: {window.width}x{window.height}')
    
    if len(windows) == 0:
        print('   ❌ No windows detected by Python - check DISPLAY and X11 access')
        sys.exit(1)
    else:
        print(f'   ✅ Window detection working! Found {len(windows)} windows')

except Exception as e:
    print(f'   ❌ Error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

# Test the automation engine in dry-run mode
echo ""
echo "🤖 Testing automation engine (dry-run mode)..."
echo "   Running automation for 10 seconds..."

timeout 10s python3 -c "
import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path('$PROJECT_ROOT')))

async def test_automation():
    try:
        from src.core.automation_engine import AutomationEngine
        from src.core.config_manager import ConfigManager
        from src.utils.logger import setup_logging
        
        # Setup
        config = ConfigManager()
        setup_logging('INFO')
        
        # Configure for dry-run
        config.set('automation.dry_run', True)
        config.set('automation.interval_seconds', 2.0)
        config.set('logging.level', 'INFO')
        
        # Create and test engine
        engine = AutomationEngine(config)
        print('   ✓ AutomationEngine created successfully')
        
        # Run for a few cycles
        print('   ✓ Starting automation loop...')
        
        # Start the engine
        start_task = asyncio.create_task(engine.start())
        
        # Let it run for a few seconds
        await asyncio.sleep(8)
        
        # Stop the engine
        await engine.stop()
        print('   ✓ Automation stopped cleanly')
        
        # Wait for the start task to complete
        await start_task
        
    except Exception as e:
        print(f'   ❌ Automation error: {e}')
        import traceback
        traceback.print_exc()

# Run the test
asyncio.run(test_automation())
" 2>&1 | head -50

echo ""
echo "🎯 Test Results Summary:"
echo "========================"

if [ "$CODE_PROCESSES" -gt 0 ]; then
    echo "   ✅ VS Code processes: $CODE_PROCESSES found"
else
    echo "   ❌ VS Code processes: None found"
fi

if [ "$VSCODE_WINDOWS" -gt 0 ]; then
    echo "   ✅ X11 windows: $VSCODE_WINDOWS found"
else
    echo "   ❌ X11 windows: None found"
fi

echo ""
echo "🚀 Next Steps:"
echo "   • To run automation: DISPLAY=:0 python src/main.py --dry-run"
echo "   • To run GUI:        DISPLAY=:0 python src/gui/main_window.py"
echo "   • To run tests:      python tests/pyunit_suite.py"
echo ""
echo "✅ Window detection test completed!"
