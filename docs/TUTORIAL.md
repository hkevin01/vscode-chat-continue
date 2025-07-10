# VS Code Chat Continue Automation - Tutorial

## Tutorial: Complete Setup and Usage

This tutorial walks you through setting up and using the VS Code Chat Continue automation tool from start to finish.

### Prerequisites Checklist

Before starting, ensure you have:
- [ ] VS Code installed and working
- [ ] GitHub Copilot Chat extension installed in VS Code
- [ ] Python 3.8+ installed
- [ ] Basic command line knowledge
- [ ] Administrator/sudo access for installation

### Step 1: Installation

#### 1.1 Download the Project
```bash
# Option A: Clone from repository (if available)
git clone <repository-url>
cd vscode-chat-continue

# Option B: Download and extract the project files
# (if you received the project as a zip file)
```

#### 1.2 Run the Installation Script
```bash
# Make the install script executable
chmod +x scripts/install.sh

# Run the installer (will prompt for sudo when needed)
./scripts/install.sh
```

The installer will:
- Check Python version
- Install system dependencies (OCR, GUI libraries)
- Create a virtual environment
- Install Python packages
- Set up configuration files
- Run basic tests

#### 1.3 Verify Installation
```bash
# Activate the virtual environment
source venv/bin/activate

# Test the installation
python tests/test_phases.py
```

### Step 2: Configuration

#### 2.1 Locate Configuration File
The configuration file is created at:
- Linux: `~/.config/vscode-chat-continue/config.json`
- macOS: `~/.config/vscode-chat-continue/config.json`
- Windows: `%APPDATA%\vscode-chat-continue\config.json`

#### 2.2 Basic Configuration
Edit the configuration file for your needs:

```json
{
  "automation": {
    "interval_seconds": 3.0,
    "dry_run": true,
    "max_retries": 3
  },
  "safety": {
    "emergency_stop_key": "escape",
    "pause_on_user_activity": true
  }
}
```

**Important Settings:**
- `dry_run: true` - Start with this enabled for safety
- `interval_seconds` - How often to check for buttons (start with 3-5 seconds)
- `emergency_stop_key` - Key to immediately stop automation

### Step 3: Prepare VS Code

#### 3.1 Open VS Code with Copilot Chat
1. Launch VS Code
2. Open a project or create a new file
3. Open Copilot Chat panel (View → Open Chat)
4. Start a conversation that will need "Continue" responses

Example conversation starters:
- "Write a comprehensive Python class for managing a shopping cart"
- "Explain the differences between React hooks in detail"
- "Create a complete REST API with error handling"

#### 3.2 Position Windows
- Keep VS Code visible (not minimized)
- Ensure Copilot Chat panel is open and visible
- If using multiple VS Code windows, arrange them so they're accessible

### Step 4: First Test Run (Dry Run)

#### 4.1 Start Dry Run Mode
```bash
# Activate virtual environment
source venv/bin/activate

# Run in dry-run mode (safe - no actual clicking)
python src/main.py --dry-run --verbose
```

#### 4.2 What to Expect
You should see output like:
```
[INFO] Starting automation engine in dry-run mode
[INFO] Found 1 VS Code window: VS Code - project
[INFO] Scanning window for Continue buttons...
[INFO] DRY RUN: Would click button at position (845, 623)
[INFO] Waiting 3.0 seconds before next check...
```

#### 4.3 Verify Detection
- Check that VS Code windows are detected
- Verify that Continue buttons are found when visible
- Ensure the automation pauses when you move the mouse

### Step 5: Live Testing

#### 5.1 Enable Live Mode
Once dry-run works correctly:

```bash
# Edit config to disable dry-run
nano ~/.config/vscode-chat-continue/config.json
# Change "dry_run": false

# Or use command line override
python src/main.py --live --interval 4.0
```

#### 5.2 Monitor First Live Run
1. Start a Copilot conversation that needs continuation
2. Run the tool and watch carefully
3. Use Emergency Stop (Escape key) if anything goes wrong
4. Verify clicks happen at the right time and place

#### 5.3 Troubleshooting Common Issues

**No Windows Detected:**
```bash
# Check VS Code is running
ps aux | grep code

# Verify X11 permissions (Linux)
xhost +local:
```

**Buttons Not Found:**
- Ensure Continue button is visible on screen
- Check button text matches configuration
- Try adjusting confidence threshold

**Clicks in Wrong Location:**
- Verify screen resolution settings
- Check if VS Code is in fullscreen mode
- Adjust detection regions in config

### Step 6: GUI Usage (Optional)

#### 6.1 Launch GUI
```bash
python src/gui/main_window.py
```

#### 6.2 GUI Features
- **Start/Stop**: Control automation with buttons
- **Real-time Stats**: Monitor performance and detection
- **Configuration**: Adjust settings through interface
- **Emergency Stop**: Large red button for immediate halt

#### 6.3 GUI Workflow
1. Load or adjust configuration
2. Click "Start Automation"
3. Monitor statistics and logs
4. Use "Pause" for temporary stops
5. "Emergency Stop" for immediate halt

### Step 7: Advanced Usage

#### 7.1 Multiple VS Code Windows
```bash
# Open multiple VS Code instances
code project1/
code project2/
code project3/

# Run automation (processes all windows)
python src/main.py --interval 2.5
```

#### 7.2 Scheduling Automation
```bash
# Example cron job (runs weekdays 9-5)
0 9-17 * * 1-5 /path/to/vscode-chat-continue/scripts/run.sh
```

#### 7.3 Custom Button Detection
Edit config for custom button text:
```json
{
  "detection": {
    "button_variants": [
      "Continue",
      "Generate more",
      "Keep going",
      "Your custom text"
    ]
  }
}
```

### Step 8: Performance Optimization

#### 8.1 Optimal Settings
- **Interval**: 2-5 seconds (balance between responsiveness and CPU usage)
- **Caching**: Enable for better performance with many windows
- **Window filtering**: Exclude non-relevant VS Code windows

#### 8.2 Monitor Performance
```bash
# Run with performance monitoring
python src/main.py --verbose

# Check logs
tail -f ~/.config/vscode-chat-continue/automation.log
```

#### 8.3 Resource Usage
- Monitor CPU usage: `htop` or `top`
- Check memory usage in GUI statistics
- Adjust interval if system becomes slow

### Step 9: Safety and Best Practices

#### 9.1 Safety Checklist
- [ ] Always test with dry-run first
- [ ] Set reasonable intervals (not too fast)
- [ ] Configure emergency stop key
- [ ] Enable user activity detection
- [ ] Monitor first few runs carefully

#### 9.2 Best Practices
- Start with longer intervals and decrease gradually
- Keep VS Code windows visible for best detection
- Use pause feature when doing manual work
- Regularly check logs for errors
- Update configuration as needed

#### 9.3 Emergency Procedures
**If Something Goes Wrong:**
1. Press Emergency Stop key (Escape by default)
2. Or use Ctrl+C in terminal
3. Or close the GUI application
4. Check what happened in logs
5. Adjust configuration before retrying

### Step 10: Maintenance and Updates

#### 10.1 Regular Maintenance
```bash
# Update Python packages
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Clean up logs (if they get large)
truncate -s 0 ~/.config/vscode-chat-continue/automation.log
```

#### 10.2 Configuration Backup
```bash
# Backup your configuration
cp ~/.config/vscode-chat-continue/config.json ~/vscode-continue-backup.json
```

#### 10.3 Performance Review
Regularly check:
- Success rate in statistics
- Error frequency in logs
- System resource usage
- Accuracy of button detection

## Troubleshooting Guide

### Common Problems and Solutions

#### Problem: "No VS Code processes found"
**Solution:**
1. Verify VS Code is running: `ps aux | grep code`
2. Check process name matches expected patterns
3. Try running VS Code from command line: `code .`

#### Problem: "Permission denied" errors
**Solution:**
1. Install X11 dependencies: `sudo apt install python3-xlib`
2. Grant screen capture permissions
3. Run with proper user permissions

#### Problem: Buttons detected but clicks miss
**Solution:**
1. Check screen scaling settings
2. Verify VS Code window is not in fullscreen
3. Adjust click offset in configuration
4. Test with different confidence thresholds

#### Problem: High CPU usage
**Solution:**
1. Increase automation interval
2. Enable window caching
3. Reduce detection methods
4. Close unnecessary VS Code windows

#### Problem: Automation stops unexpectedly
**Solution:**
1. Check logs for error messages
2. Verify VS Code windows are still open
3. Check if emergency stop was triggered
4. Review user activity detection settings

## Getting Help

### Documentation
- [Project Plan](PROJECT_PLAN.md) - Technical architecture
- [Troubleshooting](TROUBLESHOOTING.md) - Detailed problem solving
- [Contributing](CONTRIBUTING.md) - Development guide

### Self-Help Steps
1. **Check logs first**: Look in automation.log for error details
2. **Test in dry-run**: Always verify detection before live use
3. **Review configuration**: Ensure settings match your environment
4. **Verify dependencies**: Run the test suite to check installation

### Reporting Issues
When reporting problems, include:
- Operating system and version
- VS Code version
- Python version
- Configuration file (remove sensitive data)
- Relevant log entries
- Steps to reproduce the issue

## Conclusion

You should now have a fully functional VS Code Chat Continue automation tool! 

**Key takeaways:**
- Always start with dry-run mode
- Monitor the first few live runs carefully
- Adjust intervals and settings based on your needs
- Use safety features like emergency stop
- Regular maintenance keeps the tool running smoothly

**Happy automating!** 🚀
