#!/usr/bin/env python3
"""
Simple visual test - just capture and show the current VS Code window.
This helps verify what the automation is actually seeing.
"""

import subprocess
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def main():
    """Capture VS Code window for manual inspection."""
    print("📸 VS Code Window Capture Test")
    print("=" * 40)

    # Get VS Code windows
    try:
        result = subprocess.run(["xwininfo", "-root", "-tree"], capture_output=True, text=True)

        vscode_windows = []
        for line in result.stdout.split("\n"):
            if "visual studio code" in line.lower():
                parts = line.strip().split()
                if len(parts) >= 3:
                    window_id = parts[0]

                    # Extract title
                    if '"' in line:
                        title_start = line.find('"') + 1
                        title_end = line.find('"', title_start)
                        title = line[title_start:title_end]
                    else:
                        title = "Unknown"

                    vscode_windows.append({"id": window_id, "title": title})

        if not vscode_windows:
            print("❌ No VS Code windows found")
            return 1

        print(f"Found {len(vscode_windows)} VS Code window(s):")
        for i, win in enumerate(vscode_windows):
            print(f"  {i+1}. {win['id']}: {win['title'][:60]}...")

        # Capture the first window
        window_id = vscode_windows[0]["id"]
        print(f"\n📸 Capturing window {window_id}...")

        # Create temp directory
        Path("tmp").mkdir(exist_ok=True)

        # Capture with XWD
        temp_path = f"tmp/visual_test_capture.png"
        result = subprocess.run(
            ["bash", "-c", f"xwd -id {window_id} | convert xwd:- {temp_path}"], capture_output=True
        )

        if result.returncode == 0 and Path(temp_path).exists():
            print(f"✅ Successfully captured to: {temp_path}")
            print(f"💾 File size: {Path(temp_path).stat().st_size} bytes")

            # Get image dimensions
            try:
                from PIL import Image

                img = Image.open(temp_path)
                print(f"🖼️  Image dimensions: {img.width}x{img.height}")

                # Calculate chat panel area for reference
                chat_left = int(img.width * 0.55)
                chat_bottom = int(img.height * 0.75)
                print(f"📍 Chat panel area would be: x > {chat_left}, y > {chat_bottom}")

            except ImportError:
                print("📝 PIL not available for dimension check")

            print("\n🔍 To manually inspect:")
            print(f"   Open the image file: {temp_path}")
            print("   Look for blue Continue buttons in the right side")
            print("   Check if they're in the bottom-right area")

        else:
            print("❌ Failed to capture window")
            print(f"   Return code: {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr.decode()}")

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
