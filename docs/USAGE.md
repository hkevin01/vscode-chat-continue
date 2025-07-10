# Usage Guide

## Installation

### Prerequisites
- Linux operating system (X11 or Wayland)
- Python 3.8 or higher
- VS Code with Copilot Chat extension
- Screen capture permissions

### Quick Installation
```bash
git clone https://github.com/yourusername/vscode-chat-continue.git
cd vscode-chat-continue
chmod +x scripts/install.sh
./scripts/install.sh
```

### Manual Installation
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3-pip python3-venv tesseract-ocr tesseract-ocr-eng \
                     libx11-dev libxtst6 libxrandr2 python3-tk

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Basic Usage

### Command Line Interface

```bash
# Run once to click all Continue buttons
vscode-continue

# Run in watch mode (checks every 30 seconds)
vscode-continue --watch --interval 30

# Dry run to see what would be clicked without actually clicking
vscode-continue --dry-run

# Use custom configuration file
vscode-continue --config /path/to/config.json

# Enable verbose logging
vscode-continue --verbose
```

### Python API

```python
from vscode_continue import ContinueAutomator

# Basic usage
automator = ContinueAutomator()
result = automator.run_once()
print(f"Clicked {result.buttons_clicked} buttons in {result.windows_processed} windows")

# Advanced usage with custom config
config = {
    "detection": {
        "confidence_threshold": 0.9,
        "button_text": ["Continue", "继续"]
    },
    "automation": {
        "click_delay": 0.2,
        "safety_pause": 3.0
    }
}

automator = ContinueAutomator(config=config)
automator.start_watch_mode(interval=60)
```

## Configuration

### Configuration File Location
The tool looks for configuration files in the following order:
1. File specified with `--config` option
2. `~/.config/vscode-continue/config.json`
3. `./config/default.json` (fallback)

### Configuration Options

```json
{
  "detection": {
    "method": "ocr",
    "confidence_threshold": 0.8,
    "button_text": ["Continue", "继续", "Continuar", "Continuer"],
    "image_templates": ["continue_button.png"],
    "ocr_language": "eng",
    "preprocessing": {
      "grayscale": true,
      "contrast_enhancement": 1.2,
      "noise_reduction": true
    }
  },
  "automation": {
    "click_delay": 0.1,
    "retry_attempts": 3,
    "retry_delay": 1.0,
    "safety_pause": 2.0,
    "preserve_focus": true,
    "click_offset": {
      "x": 0,
      "y": 0
    }
  },
  "filtering": {
    "include_workspaces": [],
    "exclude_workspaces": ["test", "tmp", ".vscode"],
    "min_window_age": 5,
    "require_visible": true,
    "max_windows": 10
  },
  "safety": {
    "user_activity_timeout": 5.0,
    "emergency_stop_key": "ctrl+alt+shift+q",
    "pause_on_typing": true,
    "pause_on_mouse_movement": false,
    "dry_run_mode": false
  },
  "hotkeys": {
    "manual_trigger": "ctrl+alt+shift+c",
    "toggle_pause": "ctrl+alt+shift+p",
    "emergency_stop": "ctrl+alt+shift+q"
  },
  "logging": {
    "level": "INFO",
    "file": "~/.local/share/vscode-continue/app.log",
    "max_size": "10MB",
    "backup_count": 5,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  }
}
```

### Configuration Sections Explained

#### Detection Settings
- `method`: Detection method ("ocr", "template", "hybrid")
- `confidence_threshold`: Minimum confidence for OCR detection (0.0-1.0)
- `button_text`: List of text strings to look for
- `ocr_language`: Tesseract language code

#### Automation Settings
- `click_delay`: Delay between clicks in seconds
- `retry_attempts`: Number of retry attempts for failed operations
- `safety_pause`: Pause duration after detecting user activity
- `preserve_focus`: Whether to restore original window focus

#### Filtering Settings
- `include_workspaces`: Only process windows with these workspace names
- `exclude_workspaces`: Skip windows with these workspace names
- `min_window_age`: Minimum window age in seconds before processing
- `require_visible`: Only process visible windows

#### Safety Settings
- `user_activity_timeout`: How long to pause after detecting user activity
- `pause_on_typing`: Pause automation when user is typing
- `emergency_stop_key`: Hotkey to immediately stop automation

## Hotkeys

The following hotkeys are available when the tool is running:

- **Ctrl+Alt+Shift+C**: Manually trigger a scan and click cycle
- **Ctrl+Alt+Shift+P**: Toggle pause/resume automation
- **Ctrl+Alt+Shift+Q**: Emergency stop (immediately halt all automation)

You can customize these hotkeys in the configuration file.

## Examples

### Example 1: Basic One-Time Run
```bash
# Click all Continue buttons once
vscode-continue
```

### Example 2: Continuous Monitoring
```bash
# Check every 45 seconds for new Continue buttons
vscode-continue --watch --interval 45
```

### Example 3: Workspace-Specific Automation
```json
{
  "filtering": {
    "include_workspaces": ["my-project", "important-work"],
    "exclude_workspaces": ["test", "experimental"]
  }
}
```

### Example 4: Multiple Language Support
```json
{
  "detection": {
    "button_text": [
      "Continue", "继续", "Continuar", "Continuer", 
      "Weiter", "続行", "계속", "Продолжить"
    ],
    "ocr_language": "eng+chi_sim+spa+fra+deu+jpn+kor+rus"
  }
}
```

### Example 5: High Precision Mode
```json
{
  "detection": {
    "confidence_threshold": 0.95,
    "method": "hybrid"
  },
  "automation": {
    "retry_attempts": 5,
    "safety_pause": 5.0
  }
}
```

## Troubleshooting

### Common Issues

**No Continue buttons detected**
- Ensure VS Code windows are visible and not minimized
- Check that Copilot Chat is active with Continue buttons present
- Verify button text matches your language settings
- Try lowering the confidence threshold

**Clicks not registering**
- Check screen scaling settings in your display configuration
- Verify the tool has necessary permissions
- Try adjusting click offset in configuration
- Ensure VS Code windows are not in fullscreen mode

**High CPU usage**
- Increase the interval between checks
- Reduce image processing quality
- Limit the number of windows processed simultaneously
- Use template matching instead of OCR if possible

**Tool stops working after VS Code update**
- Update to the latest version of this tool
- Clear cached button templates
- Reset configuration to defaults
- Check for changes in VS Code UI layout

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more detailed solutions.
