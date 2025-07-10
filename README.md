# VS Code Chat Continue Button Automation

Automatically click the "Continue" button in VS Code Copilot Chat across all open VS Code windows.

## 🚀 Features

- **Auto-detection**: Finds all VS Code windows automatically
- **Smart Recognition**: Identifies Continue buttons using multiple detection methods
- **Multi-window Support**: Handles multiple VS Code instances simultaneously
- **Safety Controls**: Emergency stop and user activity detection
- **Configurable**: Customizable intervals and filtering options

## 📋 Requirements

- Linux (X11 or Wayland)
- Python 3.8+
- VS Code with Copilot Chat extension
- Screen capture permissions

## 🛠️ Installation

### Quick Install
```bash
git clone https://github.com/yourusername/vscode-chat-continue.git
cd vscode-chat-continue
chmod +x scripts/install.sh
./scripts/install.sh
```

### Manual Install
```bash
pip install -r requirements.txt
python setup.py install
```

## 🎯 Usage

### Basic Usage
```bash
# Run once to click all Continue buttons
python src/main.py

# Run in watch mode (checks every 30 seconds)
python src/main.py --watch --interval 30

# Dry run to see what would be clicked
python src/main.py --dry-run
```

### Command Line Options
```bash
python src/main.py [OPTIONS]

Options:
  --watch              Run continuously
  --interval SECONDS   Check interval in seconds (default: 30)
  --dry-run           Show actions without executing
  --config FILE       Custom configuration file
  --verbose           Enable verbose logging
  --help              Show this message and exit
```

### Configuration

Create a config file at `~/.config/vscode-continue/config.json`:

```json
{
  "detection": {
    "method": "ocr",
    "confidence_threshold": 0.8,
    "button_text": ["Continue", "继续", "Continuar"]
  },
  "automation": {
    "click_delay": 0.1,
    "retry_attempts": 3,
    "safety_pause": 2.0
  },
  "filtering": {
    "include_workspaces": [],
    "exclude_workspaces": ["test", "tmp"],
    "min_window_age": 5
  },
  "hotkeys": {
    "emergency_stop": "ctrl+alt+shift+q",
    "manual_trigger": "ctrl+alt+shift+c",
    "toggle_pause": "ctrl+alt+shift+p"
  }
}
```

## 🔧 How It Works

1. **Window Detection**: Scans for VS Code processes and windows
2. **Screen Capture**: Takes screenshots of relevant window areas
3. **Button Recognition**: Uses OCR and image matching to find Continue buttons
4. **Click Simulation**: Simulates mouse clicks on detected buttons
5. **Safety Checks**: Monitors for user activity and provides emergency stops

## 🛡️ Safety Features

- **Emergency Stop**: Press `Ctrl+Alt+Shift+Q` to immediately halt automation
- **Activity Detection**: Pauses when user is actively typing or clicking
- **Focus Preservation**: Maintains your current active window
- **Dry Run Mode**: Preview actions before execution

## 🐛 Troubleshooting

### Common Issues

**No Continue buttons detected**
- Ensure VS Code Copilot Chat is active and visible
- Check that button text matches your language settings
- Try adjusting confidence threshold in config

**Clicks not registering**
- Verify screen scaling settings
- Check window permissions
- Ensure VS Code windows are not minimized

**High CPU usage**
- Increase interval between checks
- Reduce image processing quality
- Limit number of concurrent windows

See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for detailed solutions.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for detailed guidelines.

## ⚠️ Disclaimer

This tool automates UI interactions with VS Code. Use responsibly and ensure compliance with your organization's automation policies. The authors are not responsible for any unintended actions or consequences.

## 📊 Status

![Build Status](https://github.com/yourusername/vscode-chat-continue/workflows/CI/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)

---

**Made with ❤️ for VS Code developers who want to streamline their AI chat workflow**
