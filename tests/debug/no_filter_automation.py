#!/usr/bin/env python3
"""
Temporary fix: Run automation without chat panel filtering.
This will help identify if the filtering is too restrictive.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import and patch the button finder
from core.button_finder import ButtonFinder

# Temporarily disable chat panel filtering
original_filter = ButtonFinder._filter_chat_panel_buttons


def no_filter(self, buttons, width, height):
    print(f"⚠️  Filter bypassed - using all {len(buttons)} detected buttons")
    return buttons


ButtonFinder._filter_chat_panel_buttons = no_filter

# Now run the continuous automation
from scripts.continuous_automation import ContinuousAutomation

print("🚨 TESTING: Automation with NO CHAT PANEL FILTERING")
print("⚠️  This may click wrong buttons - use carefully!")
print("Press Ctrl+C to stop")
print()

try:
    automation = ContinuousAutomation()
    automation.run()
finally:
    # Restore original filter
    ButtonFinder._filter_chat_panel_filters = original_filter
