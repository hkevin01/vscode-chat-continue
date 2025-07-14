#!/usr/bin/env python3
"""
Debug information collector for VS Code Chat Continue automation.
Collects system info, dependencies, and configuration for troubleshooting.
"""

import json
import os
import platform
import sys
from datetime import datetime
from pathlib import Path


def collect_system_info():
    """Collect basic system information."""
    return {
        'platform': platform.platform(),
        'system': platform.system(),
        'release': platform.release(),
        'python_version': sys.version,
        'python_executable': sys.executable,
        'display': os.environ.get('DISPLAY', 'Not set'),
        'timestamp': datetime.now().isoformat()
    }


def check_dependencies():
    """Check if required dependencies are available."""
    deps = {
        'PIL': False,
        'cv2': False,
        'numpy': False,
        'pytesseract': False,
        'pynput': False,
        'pyautogui': False,
        'PyQt6': False,
    }
    
    for dep in deps:
        try:
            __import__(dep)
            deps[dep] = True
        except ImportError:
            deps[dep] = False
    
    return deps


def check_config():
    """Check configuration file."""
    config_path = Path('config/default.json')
    if not config_path.exists():
        return {'exists': False, 'path': str(config_path)}
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return {
            'exists': True,
            'path': str(config_path),
            'valid_json': True,
            'has_automation': 'automation' in config,
            'has_detection': 'detection' in config,
            'has_coordinates': (
                'continue_button_coordinates' in config.get('automation', {})
            )
        }
    except json.JSONDecodeError:
        return {
            'exists': True,
            'path': str(config_path),
            'valid_json': False
        }


def check_project_structure():
    """Check if project directories exist."""
    dirs = ['src', 'config', 'logs', 'docs', 'tests']
    files = ['pyproject.toml', 'README.md']
    
    return {
        'directories': {d: Path(d).exists() for d in dirs},
        'files': {f: Path(f).exists() for f in files}
    }


def main():
    """Collect and display debug information."""
    print("🔍 Collecting debug information...")
    print("=" * 50)
    
    debug_info = {
        'system': collect_system_info(),
        'dependencies': check_dependencies(),
        'configuration': check_config(),
        'project_structure': check_project_structure()
    }
    
    # Print formatted output
    print("\n📱 SYSTEM INFORMATION:")
    sys_info = debug_info['system']
    print(f"  Platform: {sys_info['platform']}")
    print(f"  Python: {sys_info['python_version'].split()[0]}")
    print(f"  Display: {sys_info['display']}")
    
    print("\n📦 DEPENDENCIES:")
    deps = debug_info['dependencies']
    for dep, available in deps.items():
        status = "✅" if available else "❌"
        print(f"  {status} {dep}")
    
    print("\n⚙️  CONFIGURATION:")
    config = debug_info['configuration']
    if config['exists']:
        print(f"  ✅ Config file exists: {config['path']}")
        if config['valid_json']:
            print("  ✅ Valid JSON format")
            coord_status = "✅" if config['has_coordinates'] else "⚠️ "
            has_coords = config['has_coordinates']
            print(f"  {coord_status} User coordinates: {has_coords}")
        else:
            print("  ❌ Invalid JSON format")
    else:
        print(f"  ❌ Config file missing: {config['path']}")
    
    print("\n📁 PROJECT STRUCTURE:")
    structure = debug_info['project_structure']
    for item_type, items in structure.items():
        print(f"  {item_type.capitalize()}:")
        for name, exists in items.items():
            status = "✅" if exists else "❌"
            print(f"    {status} {name}")
    
    # Save to file
    output_file = Path('logs/debug_info.json')
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(debug_info, f, indent=2)
    
    print(f"\n📄 Debug info saved to: {output_file}")
    
    # Quick health assessment
    missing_deps = sum(1 for available in deps.values() if not available)
    if missing_deps == 0:
        print("\n🎉 All dependencies available!")
    else:
        print(f"\n⚠️  {missing_deps} dependencies missing")
        print("Run: pip install -r requirements.txt")


if __name__ == '__main__':
    main()
