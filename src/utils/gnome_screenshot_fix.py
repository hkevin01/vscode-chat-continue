#!/usr/bin/env python3
"""
System-level gnome-screenshot disabler for VS Code Chat Continue automation.
This module prevents gnome-screenshot from being triggered by any component.
"""

import os
import sys


def disable_gnome_screenshot():
    """Aggressively disable gnome-screenshot system-wide."""
    # Set environment variables to prevent gnome-screenshot
    screenshot_env_vars = {
        "PYSCREENSHOT_BACKEND": "pil",
        "GNOME_SCREENSHOT_DISABLE": "1",
        "NO_GNOME_SCREENSHOT": "1",
        "SCROT_DISABLE_GNOME": "1",
        "QT_SCALE_FACTOR": "1",  # Prevent any scaling issues that might trigger screenshot services
        "GDK_SCALE": "1",  # Prevent GTK scaling issues
        "DISABLE_GNOME_EXTENSIONS": "1",  # Disable extensions that might use screenshot
    }

    for var, value in screenshot_env_vars.items():
        os.environ[var] = value

    # Remove any existing gnome-screenshot related environment variables
    gnome_vars_to_remove = [
        "GNOME_SCREENSHOT_DIR",
        "SCREENSHOT_TOOL",
        "GNOME_SCREENSHOT_DELAY",
        "GNOME_SCREENSHOT_BORDER",
    ]

    for var in gnome_vars_to_remove:
        if var in os.environ:
            del os.environ[var]

    # Try to redirect gnome-screenshot to /dev/null if it gets called anyway
    try:
        # Create a fake gnome-screenshot in temp directory that does nothing
        import stat
        import tempfile

        temp_dir = tempfile.mkdtemp()
        fake_gnome_screenshot = os.path.join(temp_dir, "gnome-screenshot")

        with open(fake_gnome_screenshot, "w") as f:
            f.write("#!/bin/bash\n# Fake gnome-screenshot to prevent snap conflicts\nexit 0\n")

        # Make it executable
        os.chmod(fake_gnome_screenshot, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)

        # Put it at the front of PATH (but don't break system functionality)
        current_path = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{temp_dir}:{current_path}"

    except Exception:
        # If we can't create fake gnome-screenshot, that's okay
        pass


def setup_screenshot_environment():
    """Set up the environment for safe screenshot capture."""
    disable_gnome_screenshot()

    # Additional safety measures
    if sys.platform.startswith("linux"):
        # Ensure we're using X11 display properly
        if "DISPLAY" not in os.environ:
            os.environ["DISPLAY"] = ":0"

        # Disable any potential Wayland screenshot services
        os.environ["XDG_SESSION_TYPE"] = "x11"  # Force X11 mode

        # Disable systemd screenshot services
        os.environ["SYSTEMD_SCREENSHOT_DISABLE"] = "1"


# Auto-setup when module is imported
if __name__ != "__main__":
    setup_screenshot_environment()


if __name__ == "__main__":
    setup_screenshot_environment()
    print("✅ Gnome-screenshot prevention setup complete")
    print("Environment variables set:")
    for key in os.environ:
        if "SCREENSHOT" in key or "GNOME" in key or "SCROT" in key:
            print(f"  {key}={os.environ[key]}")
