#!/usr/bin/env python3
"""Clean up root directory by moving files to appropriate subdirectories."""

import os
import shutil
from pathlib import Path


def main():
    root_dir = Path("/home/kevin/Projects/vscode-chat-continue")
    os.chdir(root_dir)
    
    print("🧹 Starting root directory cleanup...")
    
    # Files to keep in root
    keep_in_root = {
        "run.sh", "README.md", "pyproject.toml", 
        "requirements.txt", "requirements-dev.txt", 
        ".gitignore", ".pylintrc"
    }
    
    moved_count = 0
    
    # Get all files in root (excluding directories and hidden files)
    for item in root_dir.iterdir():
        if item.is_file() and not item.name.startswith('.') and item.name not in keep_in_root:
            filename = item.name
            
            # Determine destination
            if filename.startswith('test_automation') or filename == 'quick_automation_test.py':
                dest = root_dir / "tests" / "automation"
            elif filename.startswith('test_') and filename.endswith('.py'):
                dest = root_dir / "tests" / "unit"
            elif filename.startswith('test_') and filename.endswith('.sh'):
                dest = root_dir / "tests" / "scripts"
            elif filename.startswith('debug_') or filename == 'diagnostic.py':
                dest = root_dir / "tests" / "debug"
            elif filename == 'manual_click_test.py':
                dest = root_dir / "tests" / "manual"
            elif filename == 'verify_import_fix.py':
                dest = root_dir / "tests" / "unit"
            elif filename.startswith('cleanup_') or filename.startswith('organize_') or filename == 'final_cleanup.sh':
                dest = root_dir / "scripts"
            elif filename.endswith('.md') and filename != 'README.md':
                dest = root_dir / "docs"
            else:
                continue  # Skip files we don't know how to categorize
            
            # Create destination directory if it doesn't exist
            dest.mkdir(parents=True, exist_ok=True)
            
            # Move the file
            try:
                shutil.move(str(item), str(dest / filename))
                print(f"  ✓ {filename} → {dest.relative_to(root_dir)}/")
                moved_count += 1
            except Exception as e:
                print(f"  ✗ Failed to move {filename}: {e}")
    
    print(f"\n✅ Cleanup complete! Moved {moved_count} files.")
    
    # Show what remains in root
    remaining_files = [f for f in root_dir.iterdir() 
                      if f.is_file() and not f.name.startswith('.')]
    
    print(f"\n📂 Files remaining in root directory ({len(remaining_files)}):")
    for file in sorted(remaining_files):
        print(f"  • {file.name}")

if __name__ == "__main__":
    main()
