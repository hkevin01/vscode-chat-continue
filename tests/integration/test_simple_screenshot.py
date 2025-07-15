#!/usr/bin/env python3
"""Simple screenshot test script for debugging Wayland issues."""

import os
import subprocess
import tempfile
from pathlib import Path


def test_imagemagick():
    """Test ImageMagick import method."""
    print("Testing ImageMagick import...")

    try:
        # Check if import is available
        result = subprocess.run(["which", "import"], capture_output=True, timeout=5)
        if result.returncode != 0:
            print("❌ ImageMagick import not available")
            return False

        print("✅ ImageMagick import found")

        # Create temp file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name

        print(f"Attempting screenshot to: {tmp_path}")

        # Try screenshot
        cmd = ["import", "-window", "root", tmp_path]
        result = subprocess.run(cmd, capture_output=True, timeout=20)

        print(f"Command exit code: {result.returncode}")
        if result.stderr:
            print(f"stderr: {result.stderr.decode()[:200]}")

        if result.returncode == 0 and Path(tmp_path).exists():
            size = Path(tmp_path).stat().st_size
            print(f"Screenshot file size: {size} bytes")

            if size > 1000:
                print("✅ ImageMagick screenshot successful!")
                Path(tmp_path).unlink()
                return True
            else:
                print("❌ Screenshot file too small")
        else:
            print("❌ Screenshot failed or file not created")

        # Cleanup
        Path(tmp_path).unlink(missing_ok=True)
        return False

    except Exception as e:
        print(f"❌ ImageMagick test failed: {e}")
        return False


def test_scrot():
    """Test scrot method."""
    print("\nTesting scrot...")

    try:
        # Check if scrot is available
        result = subprocess.run(["which", "scrot"], capture_output=True, timeout=5)
        if result.returncode != 0:
            print("❌ scrot not available")
            return False

        print("✅ scrot found")

        # Create temp file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name

        print(f"Attempting screenshot to: {tmp_path}")

        # Try screenshot
        cmd = ["scrot", "--silent", "--quiet", tmp_path]
        result = subprocess.run(cmd, capture_output=True, timeout=15)

        print(f"Command exit code: {result.returncode}")
        if result.stderr:
            print(f"stderr: {result.stderr.decode()[:200]}")

        if result.returncode == 0 and Path(tmp_path).exists():
            size = Path(tmp_path).stat().st_size
            print(f"Screenshot file size: {size} bytes")

            if size > 1000:
                print("✅ scrot screenshot successful!")
                Path(tmp_path).unlink()
                return True
            else:
                print("❌ Screenshot file too small")
        else:
            print("❌ Screenshot failed or file not created")

        # Cleanup
        Path(tmp_path).unlink(missing_ok=True)
        return False

    except Exception as e:
        print(f"❌ scrot test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🔍 Testing screenshot methods on Wayland...")
    print(f"Environment: WAYLAND_DISPLAY={os.environ.get('WAYLAND_DISPLAY', 'Not set')}")
    print(f"XDG_SESSION_TYPE={os.environ.get('XDG_SESSION_TYPE', 'Not set')}")

    methods = [
        ("ImageMagick", test_imagemagick),
        ("scrot", test_scrot),
    ]

    for name, test_func in methods:
        try:
            success = test_func()
            if success:
                print(f"\n🎉 {name} works! Using this method.")
                break
        except Exception as e:
            print(f"❌ {name} failed with exception: {e}")
    else:
        print("\n❌ No working screenshot methods found!")


if __name__ == "__main__":
    main()
