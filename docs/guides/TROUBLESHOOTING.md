# Troubleshooting Guide

## Quick Diagnostics

### Run the Health Check

```bash
# Run comprehensive diagnostic
python scripts/health_check.py

# Quick system check
python -c "
import sys
print(f'Python: {sys.version}')
try:
    import cv2, PIL, pyautogui, pynput
    print('✅ All dependencies available')
except ImportError as e:
    print(f'❌ Missing: {e}')
"
```

### Common Issues & Solutions

## Button Detection Issues

### Problem: No Continue buttons found

**Symptoms:**
- Automation runs but doesn't click anything
- Log shows "No Continue buttons detected"
- GUI shows empty detection results

**Diagnosis:**
```bash
# Test screenshot capture
python tests/debug/test_screenshot.py

# Test button detection
python tests/debug/test_button_detection.py

# Check OCR setup
python -c "
import pytesseract
from PIL import Image
img = Image.new('RGB', (100, 50), 'white')
try:
    result = pytesseract.image_to_string(img)
    print('✅ Tesseract working')
except Exception as e:
    print(f'❌ Tesseract error: {e}')
"
```

**Solutions:**

1. **Verify Tesseract Installation:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr tesseract-ocr-eng
   
   # macOS
   brew install tesseract
   
   # Windows
   # Download from: https://github.com/UB-Mannheim/tesseract/wiki
   ```

2. **Check Text Detection:**
   ```bash
   # Test with verbose output
   python tests/debug/debug_button_detection_verbose.py
   ```

3. **Adjust Configuration:**
   ```json
   {
     "detection": {
       "confidence_threshold": 0.6,
       "button_text": ["Continue", "继续", "Continuar", "Next"],
       "method": "hybrid"
     }
   }
   ```

4. **Use Coordinate Fallback:**
   ```json
   {
     "automation": {
       "enable_chat_fallback": true,
       "continue_button_coordinates": {
         "x": 1713,
         "y": 1723
       }
     }
   }
   ```

### Problem: False positive detections

**Symptoms:**
- Clicking on wrong elements
- Multiple detections of same button
- Clicking outside VS Code windows

**Solutions:**

1. **Increase Confidence Threshold:**
   ```json
   {
     "detection": {
       "confidence_threshold": 0.9
     }
   }
   ```

2. **Restrict Detection Area:**
   ```python
   # In automation_engine.py
   def detect_in_region(self, window):
       # Crop to likely button area (bottom portion)
       crop_area = (0, window.height * 0.7, window.width, window.height)
       cropped_image = image.crop(crop_area)
   ```

3. **Enable Window Filtering:**
   ```json
   {
     "detection": {
       "filter_by_window_title": true,
       "valid_window_patterns": ["VS Code", "Visual Studio Code"]
     }
   }
   ```

## Click Issues

### Problem: Clicks not registering

**Symptoms:**
- Successful click detection but no UI response
- Cursor moves but no click occurs
- Permission denied errors

**Diagnosis:**
```bash
# Test click functionality
python tests/debug/test_real_clicking.py

# Check permissions (Linux)
xhost +local:
```

**Solutions:**

1. **Linux Permission Fix:**
   ```bash
   # Add to display permissions
   xhost +local:$(whoami)
   
   # For Wayland
   export XDG_SESSION_TYPE=x11
   ```

2. **Adjust Click Method:**
   ```json
   {
     "automation": {
       "click_method": "pynput",
       "click_delay": 0.2,
       "restore_cursor": true
     }
   }
   ```

3. **Test Different Click Libraries:**
   ```python
   # Test in debug_automation.py
   click_methods = ['pynput', 'pyautogui', 'xlib']
   for method in click_methods:
       try:
           # Test each method
           pass
       except Exception as e:
           print(f"{method} failed: {e}")
   ```

### Problem: Clicks at wrong coordinates

**Symptoms:**
- Clicking outside target area
- Offset clicks
- Multi-monitor coordinate issues

**Solutions:**

1. **Verify Coordinate System:**
   ```python
   import pyautogui
   
   # Check screen resolution
   width, height = pyautogui.size()
   print(f"Screen: {width}x{height}")
   
   # Check mouse position
   x, y = pyautogui.position()
   print(f"Mouse: ({x}, {y})")
   ```

2. **Handle Multi-Monitor Setup:**
   ```json
   {
     "automation": {
       "multi_monitor": true,
       "primary_monitor_only": false
     }
   }
   ```

3. **Use Manual Coordinate Calibration:**
   ```bash
   # Run coordinate finder
   python tools/coordinate_finder.py
   ```

## Window Detection Issues

### Problem: VS Code windows not found

**Symptoms:**
- "No VS Code windows detected"
- Empty window list
- Only partial window information

**Diagnosis:**
```bash
# Test window detection
python tests/debug/test_window_detection.py

# List all windows (Linux)
wmctrl -l

# Check process list
ps aux | grep code
```

**Solutions:**

1. **Linux Window Detection:**
   ```bash
   # Install required tools
   sudo apt-get install wmctrl xwininfo
   
   # Test window detection
   wmctrl -l | grep -i code
   ```

2. **Adjust Window Patterns:**
   ```json
   {
     "window_detection": {
       "title_patterns": [
         "Visual Studio Code",
         "VS Code",
         "Code - ",
         "code-oss"
       ]
     }
   }
   ```

3. **Manual Window Specification:**
   ```json
   {
     "windows": {
       "manual_windows": [
         {
           "title": "My VS Code",
           "x": 100,
           "y": 100,
           "width": 1200,
           "height": 800
         }
       ]
     }
   }
   ```

## Performance Issues

### Problem: High CPU usage

**Symptoms:**
- System slowdown during automation
- High CPU in task manager
- Thermal throttling

**Solutions:**

1. **Reduce Detection Frequency:**
   ```json
   {
     "automation": {
       "detection_interval": 5.0,
       "sleep_when_idle": true
     }
   }
   ```

2. **Enable Caching:**
   ```json
   {
     "detection": {
       "cache_duration": 30,
       "cache_screenshots": true
     }
   }
   ```

3. **Optimize Detection Area:**
   ```json
   {
     "detection": {
       "crop_to_region": true,
       "detection_region": {
         "x_percent": 50,
         "y_percent": 70,
         "width_percent": 50,
         "height_percent": 30
       }
     }
   }
   ```

### Problem: Memory leaks

**Symptoms:**
- Increasing RAM usage over time
- System becoming unresponsive
- Out of memory errors

**Solutions:**

1. **Enable Memory Management:**
   ```python
   # In automation loop
   import gc
   
   def cleanup_iteration(self):
       gc.collect()
       # Clear image caches
       self.image_cache.clear()
   ```

2. **Limit Cache Size:**
   ```json
   {
     "performance": {
       "max_cache_size": 100,
       "cache_cleanup_interval": 60
     }
   }
   ```

## Platform-Specific Issues

### Linux (X11/Wayland)

**Common Issues:**
- Permission denied for screen capture
- Window detection failures
- Clipboard access issues

**Solutions:**

1. **X11 Setup:**
   ```bash
   # Fix display permissions
   xhost +local:
   
   # Set DISPLAY variable
   export DISPLAY=:0
   ```

2. **Wayland Workarounds:**
   ```bash
   # Use X11 session instead
   export XDG_SESSION_TYPE=x11
   
   # Install additional tools
   sudo apt-get install grim slurp wl-clipboard
   ```

3. **Screen Capture Fix:**
   ```bash
   # Install screen capture tools
   sudo apt-get install scrot imagemagick
   
   # Test screenshot
   scrot test.png
   ```

### Windows

**Common Issues:**
- UAC permission dialogs
- DPI scaling issues
- Windows Defender blocking

**Solutions:**

1. **Run as Administrator:**
   ```cmd
   # Run PowerShell as admin
   Start-Process powershell -Verb runAs
   ```

2. **Fix DPI Scaling:**
   ```python
   import ctypes
   
   # Set DPI awareness
   ctypes.windll.shcore.SetProcessDpiAwareness(1)
   ```

3. **Windows Defender Exclusion:**
   ```powershell
   # Add exclusion for project folder
   Add-MpPreference -ExclusionPath "C:\path\to\vscode-chat-continue"
   ```

### macOS

**Common Issues:**
- Screen recording permissions
- Accessibility permissions
- Notarization warnings

**Solutions:**

1. **Grant Permissions:**
   ```bash
   # System Preferences → Security & Privacy → Privacy
   # Add Python to Screen Recording and Accessibility
   ```

2. **Test Permissions:**
   ```python
   import pyautogui
   
   try:
       screenshot = pyautogui.screenshot()
       print("✅ Screen capture working")
   except Exception as e:
       print(f"❌ Permission issue: {e}")
   ```

## Configuration Issues

### Problem: Configuration not loading

**Symptoms:**
- Using default values only
- Configuration changes ignored
- File not found errors

**Solutions:**

1. **Check File Location:**
   ```bash
   # Verify config file exists
   ls -la config/default.json
   
   # Check JSON syntax
   python -m json.tool config/default.json
   ```

2. **Configuration Path Debug:**
   ```python
   from src.core.config_manager import ConfigManager
   
   config = ConfigManager()
   print(f"Config file: {config.config_path}")
   print(f"Loaded: {config.config}")
   ```

3. **Environment Override:**
   ```bash
   # Set custom config path
   export VSCODE_CHAT_CONFIG="/path/to/custom/config.json"
   ```

### Problem: Invalid configuration values

**Symptoms:**
- Application crashes on startup
- Validation errors
- Unexpected behavior

**Solutions:**

1. **Validate Configuration:**
   ```bash
   # Run config validation
   python -c "
   from src.core.config_manager import ConfigManager
   try:
       config = ConfigManager()
       config.validate()
       print('✅ Configuration valid')
   except Exception as e:
       print(f'❌ Configuration error: {e}')
   "
   ```

2. **Reset to Defaults:**
   ```bash
   # Backup current config
   cp config/default.json config/backup.json
   
   # Reset to defaults
   git checkout config/default.json
   ```

## Debug Tools

### Enable Debug Logging

```bash
# Set debug level
export LOG_LEVEL=DEBUG

# Run with verbose output
python src/main.py --debug --verbose
```

### Screenshot Debug Mode

```python
# Enable screenshot saving
config = {
    "debug": {
        "save_screenshots": true,
        "screenshot_path": "debug/screenshots/",
        "annotate_detections": true
    }
}
```

### Performance Profiling

```bash
# Profile performance
python -m cProfile -o profile.stats src/main.py

# Analyze profile
python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(20)
"
```

### Memory Analysis

```bash
# Install memory profiler
pip install memory-profiler psutil

# Profile memory usage
python -m memory_profiler src/main.py
```

## Emergency Procedures

### Stop Automation Immediately

1. **Emergency Stop Key:** Press `F12` (default)
2. **Kill Process:** 
   ```bash
   # Find process
   ps aux | grep python
   
   # Kill by PID
   kill -9 <PID>
   
   # Kill all Python processes (DANGEROUS)
   pkill -9 python
   ```

3. **Use Kill Script:**
   ```bash
   python kill_automation.py
   ```

### Recovery Steps

1. **Clear Locks:**
   ```bash
   # Remove lock files
   rm -f /tmp/vscode-chat-continue.lock
   ```

2. **Reset Configuration:**
   ```bash
   # Reset to safe defaults
   cp config/safe-defaults.json config/default.json
   ```

3. **Clear Cache:**
   ```bash
   # Clear all caches
   rm -rf cache/
   rm -rf tmp/
   ```

## Getting Help

### Collect Debug Information

```bash
# Run comprehensive diagnostic
python scripts/collect_debug_info.py > debug_report.txt
```

### Create Issue Report

Include the following information:

1. **System Information:**
   - OS and version
   - Python version
   - Display setup (single/multi-monitor)
   - Desktop environment (GNOME, KDE, etc.)

2. **Error Details:**
   - Full error message
   - Log files (logs/automation.log)
   - Screenshots of the issue

3. **Configuration:**
   - Current config/default.json
   - Any custom settings

4. **Steps to Reproduce:**
   - Exact steps that trigger the issue
   - Expected vs actual behavior

### Community Resources

- **GitHub Issues:** [Project Issues](https://github.com/user/vscode-chat-continue/issues)
- **Documentation:** docs/ folder
- **Examples:** examples/ folder

This troubleshooting guide covers the most common issues and their solutions. For persistent problems, collect debug information and create a detailed issue report.
