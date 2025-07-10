# Troubleshooting Guide

This guide helps you resolve common issues with the VS Code Chat Continue automation tool.

## Installation Issues

### Permission Denied Errors

**Problem**: Getting permission errors during installation
```bash
PermissionError: [Errno 13] Permission denied: '/usr/local/lib/python3.x/site-packages/'
```

**Solutions**:
1. Use virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Install for user only:
   ```bash
   pip install --user -r requirements.txt
   ```

3. Use sudo (not recommended):
   ```bash
   sudo pip install -r requirements.txt
   ```

### Missing System Dependencies

**Problem**: Import errors for system libraries
```bash
ImportError: No module named 'Xlib'
ModuleNotFoundError: No module named 'cv2'
```

**Solutions**:

For Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y \
    python3-dev \
    python3-tk \
    libx11-dev \
    libxtst6 \
    libxrandr2 \
    tesseract-ocr \
    tesseract-ocr-eng \
    libopencv-dev \
    python3-opencv
```

For Fedora/RHEL:
```bash
sudo dnf install -y \
    python3-devel \
    python3-tkinter \
    libX11-devel \
    libXtst \
    libXrandr \
    tesseract \
    tesseract-langpack-eng \
    opencv-python
```

For Arch Linux:
```bash
sudo pacman -S \
    python \
    tk \
    libx11 \
    libxtst \
    libxrandr \
    tesseract \
    tesseract-data-eng \
    opencv
```

## Detection Issues

### No Continue Buttons Found

**Problem**: Tool reports "No Continue buttons detected" despite visible buttons

**Diagnostic Steps**:
1. Check VS Code windows are visible:
   ```bash
   vscode-continue --dry-run --verbose
   ```

2. Verify button text language:
   ```json
   {
     "detection": {
       "button_text": ["Continue", "Continuar", "Continuer", "继续"]
     }
   }
   ```

3. Lower confidence threshold:
   ```json
   {
     "detection": {
       "confidence_threshold": 0.6
     }
   }
   ```

4. Test OCR manually:
   ```bash
   # Take screenshot and test OCR
   import pyautogui
   import pytesseract
   screenshot = pyautogui.screenshot()
   text = pytesseract.image_to_string(screenshot)
   print(text)
   ```

**Common Causes**:
- VS Code theme affects button visibility
- High display scaling interferes with OCR
- Non-English button text not configured
- Windows minimized or hidden behind other windows

### False Positive Detections

**Problem**: Tool clicks wrong buttons or non-Continue buttons

**Solutions**:
1. Increase confidence threshold:
   ```json
   {
     "detection": {
       "confidence_threshold": 0.9
     }
   }
   ```

2. Use more specific button text:
   ```json
   {
     "detection": {
       "button_text": ["Continue", "Continue →"]
     }
   }
   ```

3. Enable image preprocessing:
   ```json
   {
     "detection": {
       "preprocessing": {
         "grayscale": true,
         "contrast_enhancement": 1.5,
         "noise_reduction": true
       }
     }
   }
   ```

## Click Issues

### Clicks Not Registering

**Problem**: Tool detects buttons but clicks don't work

**Diagnostic Steps**:
1. Check click coordinates:
   ```bash
   vscode-continue --dry-run --verbose
   # Look for "Would click at coordinates (x, y)"
   ```

2. Test manual click at same coordinates:
   ```python
   import pyautogui
   pyautogui.click(x, y)  # Use coordinates from dry run
   ```

3. Check display scaling:
   ```bash
   xdpyinfo | grep resolution
   gsettings get org.gnome.desktop.interface scaling-factor
   ```

**Solutions**:
1. Adjust click offset:
   ```json
   {
     "automation": {
       "click_offset": {
         "x": 5,
         "y": 5
       }
     }
   }
   ```

2. Account for display scaling:
   ```json
   {
     "detection": {
       "scale_factor": 2.0
     }
   }
   ```

3. Increase click delay:
   ```json
   {
     "automation": {
       "click_delay": 0.5
     }
   }
   ```

### Window Focus Issues

**Problem**: Clicks happen in wrong window or lose focus

**Solutions**:
1. Enable focus preservation:
   ```json
   {
     "automation": {
       "preserve_focus": true
     }
   }
   ```

2. Add window activation delay:
   ```json
   {
     "automation": {
       "window_activation_delay": 0.2
     }
   }
   ```

## Performance Issues

### High CPU Usage

**Problem**: Tool consumes excessive CPU resources

**Solutions**:
1. Increase check interval:
   ```bash
   vscode-continue --watch --interval 60  # Check every minute
   ```

2. Limit processed windows:
   ```json
   {
     "filtering": {
       "max_windows": 5
     }
   }
   ```

3. Use template matching instead of OCR:
   ```json
   {
     "detection": {
       "method": "template"
     }
   }
   ```

4. Reduce image processing quality:
   ```json
   {
     "detection": {
       "image_scale": 0.5,
       "preprocessing": {
         "noise_reduction": false
       }
     }
   }
   ```

### Slow Detection

**Problem**: Button detection takes too long

**Solutions**:
1. Cache button locations:
   ```json
   {
     "detection": {
       "cache_duration": 30
     }
   }
   ```

2. Limit search area:
   ```json
   {
     "detection": {
       "search_region": {
         "x": 0,
         "y": 800,
         "width": 400,
         "height": 200
       }
     }
   }
   ```

## Display Server Issues

### X11 vs Wayland

**Problem**: Tool doesn't work on Wayland

**Current Limitations**:
- Window detection requires X11 APIs
- Screen capture may be restricted on Wayland

**Workarounds**:
1. Force X11 session:
   ```bash
   # At login, select "Ubuntu on Xorg" or similar
   ```

2. Use XWayland compatibility:
   ```bash
   export GDK_BACKEND=x11
   export QT_QPA_PLATFORM=xcb
   vscode-continue
   ```

3. Check session type:
   ```bash
   echo $XDG_SESSION_TYPE
   # Should output "x11" for compatibility
   ```

### Multiple Monitor Setup

**Problem**: Detection fails with multiple monitors

**Solutions**:
1. Specify primary monitor:
   ```json
   {
     "detection": {
       "monitor": 0
     }
   }
   ```

2. Handle different DPI settings:
   ```json
   {
     "detection": {
       "per_monitor_dpi": true
     }
   }
   ```

## VS Code Specific Issues

### Extension Compatibility

**Problem**: Tool doesn't work with certain VS Code extensions

**Known Issues**:
- Custom themes may change button appearance
- Some extensions modify chat UI layout
- Vim mode may interfere with automation

**Solutions**:
1. Test with minimal extensions:
   ```bash
   code --disable-extensions
   ```

2. Update button templates for custom themes:
   ```json
   {
     "detection": {
       "theme_specific": {
         "dark": ["continue_dark.png"],
         "light": ["continue_light.png"]
       }
     }
   }
   ```

### VS Code Updates

**Problem**: Tool stops working after VS Code update

**Solutions**:
1. Update tool to latest version:
   ```bash
   git pull origin main
   pip install -r requirements.txt
   ```

2. Clear cached templates:
   ```bash
   rm -rf ~/.cache/vscode-continue/
   ```

3. Reconfigure button detection:
   ```bash
   vscode-continue --reconfigure
   ```

## Security and Permissions

### Screen Capture Permissions

**Problem**: Permission denied for screen capture

**Solutions**:
1. Grant accessibility permissions:
   ```bash
   # Ubuntu: Settings > Privacy > Screen Sharing
   # Add your terminal or Python to allowed applications
   ```

2. Run with proper permissions:
   ```bash
   # May require running as user with desktop session
   DISPLAY=:0 vscode-continue
   ```

### Input Simulation Permissions

**Problem**: Cannot simulate mouse clicks

**Solutions**:
1. Add user to input group:
   ```bash
   sudo usermod -a -G input $USER
   # Logout and login again
   ```

2. Check udev rules:
   ```bash
   # Create rule for input access if needed
   sudo echo 'KERNEL=="event*", GROUP="input", MODE="0664"' > /etc/udev/rules.d/99-input.rules
   sudo udevadm control --reload-rules
   ```

## Debugging

### Enable Debug Logging

```json
{
  "logging": {
    "level": "DEBUG",
    "file": "~/.local/share/vscode-continue/debug.log"
  }
}
```

### Capture Screenshots for Analysis

```bash
# Run with screenshot capture
vscode-continue --debug-screenshots --output-dir /tmp/debug/
```

### Test Individual Components

```python
# Test window detection
from src.core.window_detector import WindowDetector
detector = WindowDetector()
windows = detector.find_vscode_windows()
print(f"Found {len(windows)} windows")

# Test button detection
from src.core.button_finder import ButtonFinder
finder = ButtonFinder()
buttons = finder.find_continue_buttons(screenshot)
print(f"Found {len(buttons)} buttons")
```

## Getting Additional Help

### Collect System Information

```bash
# Create diagnostic report
vscode-continue --system-info > system_info.txt
```

### Log Analysis

```bash
# View recent errors
tail -f ~/.local/share/vscode-continue/app.log | grep ERROR

# Search for specific issues
grep -n "confidence_threshold" ~/.local/share/vscode-continue/app.log
```

### Report Issues

When reporting issues, include:
1. System information (`uname -a`, desktop environment)
2. VS Code version and extensions
3. Tool version and configuration
4. Relevant log output
5. Screenshots of the issue

For more help, open an issue on GitHub with the "bug" label and include all diagnostic information.
