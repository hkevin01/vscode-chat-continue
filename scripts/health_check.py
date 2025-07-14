#!/usr/bin/env python3
"""
Health check script for VS Code Chat Continue automation.
Validates system requirements, dependencies, and configuration.
"""

import importlib.util
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict


class HealthChecker:
    """Comprehensive health check for the automation system."""
    
    def __init__(self):
        self.results = []
        self.errors = []
        self.warnings = []
        
    def check_all(self) -> Dict[str, Any]:
        """Run all health checks and return results."""
        print("🔍 Running VS Code Chat Continue Health Check...")
        print("=" * 60)
        
        checks = [
            ("Python Version", self.check_python_version),
            ("Required Dependencies", self.check_dependencies),
            ("Optional Dependencies", self.check_optional_dependencies),
            ("System Tools", self.check_system_tools),
            ("Configuration", self.check_configuration),
            ("Permissions", self.check_permissions),
            ("Screen Capture", self.check_screen_capture),
            ("Window Detection", self.check_window_detection),
            ("Project Structure", self.check_project_structure),
            ("Log Directories", self.check_log_directories),
        ]
        
        for name, check_func in checks:
            print(f"\n📋 Checking {name}...")
            try:
                result = check_func()
                if result['status'] == 'pass':
                    print(f"✅ {name}: {result['message']}")
                elif result['status'] == 'warning':
                    print(f"⚠️  {name}: {result['message']}")
                    self.warnings.append(f"{name}: {result['message']}")
                else:
                    print(f"❌ {name}: {result['message']}")
                    self.errors.append(f"{name}: {result['message']}")
                    
                self.results.append({
                    'check': name,
                    'status': result['status'],
                    'message': result['message'],
                    'details': result.get('details', {})
                })
                
            except Exception as e:
                error_msg = f"Check failed with exception: {str(e)}"
                print(f"❌ {name}: {error_msg}")
                self.errors.append(f"{name}: {error_msg}")
                self.results.append({
                    'check': name,
                    'status': 'error',
                    'message': error_msg,
                    'details': {}
                })
        
        return self.generate_summary()
    
    def check_python_version(self) -> Dict[str, Any]:
        """Check Python version compatibility."""
        version = sys.version_info
        
        if version < (3, 8):
            return {
                'status': 'error',
                'message': f"Python {version.major}.{version.minor} is too old. Requires Python 3.8+",
                'details': {'version': f"{version.major}.{version.minor}.{version.micro}"}
            }
        elif version < (3, 9):
            return {
                'status': 'warning',
                'message': f"Python {version.major}.{version.minor} works but 3.9+ recommended",
                'details': {'version': f"{version.major}.{version.minor}.{version.micro}"}
            }
        else:
            return {
                'status': 'pass',
                'message': f"Python {version.major}.{version.minor}.{version.micro} is compatible",
                'details': {'version': f"{version.major}.{version.minor}.{version.micro}"}
            }
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Check required Python dependencies."""
        required_deps = [
            ('PIL', 'Pillow'),
            ('cv2', 'opencv-python'),
            ('numpy', 'numpy'),
            ('pytesseract', 'pytesseract'),
            ('pynput', 'pynput'),
            ('pyautogui', 'pyautogui'),
            ('PyQt6', 'PyQt6'),
        ]
        
        missing = []
        working = []
        
        for import_name, package_name in required_deps:
            try:
                spec = importlib.util.find_spec(import_name)
                if spec is None:
                    missing.append(package_name)
                else:
                    # Try to actually import to catch installation issues
                    module = importlib.import_module(import_name)
                    working.append(package_name)
            except ImportError:
                missing.append(package_name)
            except Exception as e:
                missing.append(f"{package_name} (error: {str(e)})")
        
        if missing:
            return {
                'status': 'error',
                'message': f"Missing dependencies: {', '.join(missing)}",
                'details': {
                    'missing': missing,
                    'working': working,
                    'install_command': f"pip install {' '.join(missing)}"
                }
            }
        else:
            return {
                'status': 'pass',
                'message': f"All {len(working)} required dependencies available",
                'details': {'working': working}
            }
    
    def check_optional_dependencies(self) -> Dict[str, Any]:
        """Check optional dependencies that enhance functionality."""
        optional_deps = [
            ('psutil', 'psutil'),
            ('requests', 'requests'),
            ('watchdog', 'watchdog'),
            ('colorama', 'colorama'),
        ]
        
        missing = []
        working = []
        
        for import_name, package_name in optional_deps:
            try:
                importlib.import_module(import_name)
                working.append(package_name)
            except ImportError:
                missing.append(package_name)
        
        if missing:
            return {
                'status': 'warning',
                'message': f"Optional dependencies missing: {', '.join(missing)}",
                'details': {
                    'missing': missing,
                    'working': working,
                    'install_command': f"pip install {' '.join(missing)}"
                }
            }
        else:
            return {
                'status': 'pass',
                'message': f"All {len(working)} optional dependencies available",
                'details': {'working': working}
            }
    
    def check_system_tools(self) -> Dict[str, Any]:
        """Check system tools availability."""
        system = platform.system()
        tools = []
        missing = []
        
        # Common tools
        common_tools = ['tesseract']
        
        # Platform-specific tools
        if system == 'Linux':
            tools.extend(['wmctrl', 'xwininfo', 'xdotool'])
        elif system == 'Windows':
            tools.extend(['powershell'])
        elif system == 'Darwin':  # macOS
            tools.extend(['screencapture'])
        
        tools.extend(common_tools)
        
        for tool in tools:
            try:
                result = subprocess.run(
                    ['which', tool] if system != 'Windows' else ['where', tool],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    missing.append(tool)
            except FileNotFoundError:
                missing.append(tool)
        
        if missing:
            install_hints = {
                'tesseract': {
                    'Linux': 'sudo apt-get install tesseract-ocr',
                    'Darwin': 'brew install tesseract',
                    'Windows': 'Download from GitHub releases'
                },
                'wmctrl': {'Linux': 'sudo apt-get install wmctrl'},
                'xwininfo': {'Linux': 'sudo apt-get install x11-utils'},
                'xdotool': {'Linux': 'sudo apt-get install xdotool'},
            }
            
            hints = []
            for tool in missing:
                if tool in install_hints and system in install_hints[tool]:
                    hints.append(f"{tool}: {install_hints[tool][system]}")
            
            return {
                'status': 'warning',
                'message': f"Missing system tools: {', '.join(missing)}",
                'details': {
                    'missing': missing,
                    'install_hints': hints,
                    'system': system
                }
            }
        else:
            working = [t for t in tools if t not in missing]
            return {
                'status': 'pass',
                'message': f"System tools available: {', '.join(working)}",
                'details': {'working': working}
            }
    
    def check_configuration(self) -> Dict[str, Any]:
        """Check configuration file validity."""
        config_path = Path('config/default.json')
        
        if not config_path.exists():
            return {
                'status': 'error',
                'message': f"Configuration file not found: {config_path}",
                'details': {'path': str(config_path)}
            }
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Basic validation
            required_sections = ['detection', 'automation', 'logging']
            missing_sections = [s for s in required_sections if s not in config]
            
            if missing_sections:
                return {
                    'status': 'error',
                    'message': f"Missing config sections: {', '.join(missing_sections)}",
                    'details': {'missing_sections': missing_sections}
                }
            
            # Check for user coordinates
            has_coordinates = (
                'continue_button_coordinates' in config.get('automation', {}) or
                'chat_field_coordinates' in config.get('automation', {})
            )
            
            if has_coordinates:
                return {
                    'status': 'pass',
                    'message': "Configuration valid with user coordinates",
                    'details': {'has_user_coordinates': True}
                }
            else:
                return {
                    'status': 'warning',
                    'message': "Configuration valid but no user coordinates set",
                    'details': {'has_user_coordinates': False}
                }
                
        except json.JSONDecodeError as e:
            return {
                'status': 'error',
                'message': f"Invalid JSON in configuration: {str(e)}",
                'details': {'json_error': str(e)}
            }
    
    def check_permissions(self) -> Dict[str, Any]:
        """Check file and system permissions."""
        issues = []
        
        # Check write permissions for logs
        log_dir = Path('logs')
        if log_dir.exists():
            test_file = log_dir / 'test_write.tmp'
            try:
                test_file.write_text('test')
                test_file.unlink()
            except PermissionError:
                issues.append("Cannot write to logs directory")
        
        # Check cache directory
        cache_dir = Path('cache')
        if cache_dir.exists():
            try:
                (cache_dir / 'test.tmp').touch()
                (cache_dir / 'test.tmp').unlink()
            except PermissionError:
                issues.append("Cannot write to cache directory")
        
        # Platform-specific permission checks
        system = platform.system()
        if system == 'Linux':
            # Check X11 permissions
            display = os.environ.get('DISPLAY')
            if not display:
                issues.append("DISPLAY environment variable not set")
        
        if issues:
            return {
                'status': 'error',
                'message': f"Permission issues: {', '.join(issues)}",
                'details': {'issues': issues}
            }
        else:
            return {
                'status': 'pass',
                'message': "File and system permissions OK",
                'details': {}
            }
    
    def check_screen_capture(self) -> Dict[str, Any]:
        """Test screen capture functionality."""
        try:
            import pyautogui

            # Test screenshot
            screenshot = pyautogui.screenshot()
            if screenshot.size[0] > 0 and screenshot.size[1] > 0:
                return {
                    'status': 'pass',
                    'message': f"Screen capture working ({screenshot.size[0]}x{screenshot.size[1]})",
                    'details': {'resolution': screenshot.size}
                }
            else:
                return {
                    'status': 'error',
                    'message': "Screen capture returned empty image",
                    'details': {}
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Screen capture failed: {str(e)}",
                'details': {'error': str(e)}
            }
    
    def check_window_detection(self) -> Dict[str, Any]:
        """Test window detection capabilities."""
        system = platform.system()
        
        if system == 'Linux':
            try:
                # Test wmctrl
                result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True)
                if result.returncode == 0:
                    windows = result.stdout.strip().split('\n')
                    return {
                        'status': 'pass',
                        'message': f"Window detection working ({len(windows)} windows found)",
                        'details': {'window_count': len(windows)}
                    }
                else:
                    return {
                        'status': 'error',
                        'message': "wmctrl failed to list windows",
                        'details': {'error': result.stderr}
                    }
            except FileNotFoundError:
                return {
                    'status': 'warning',
                    'message': "wmctrl not available for window detection",
                    'details': {}
                }
        
        # For other platforms or as fallback
        return {
            'status': 'warning',
            'message': f"Window detection not tested on {system}",
            'details': {'platform': system}
        }
    
    def check_project_structure(self) -> Dict[str, Any]:
        """Verify project directory structure."""
        required_dirs = ['src', 'config', 'logs', 'docs']
        required_files = ['pyproject.toml', 'README.md']
        
        missing_dirs = [d for d in required_dirs if not Path(d).exists()]
        missing_files = [f for f in required_files if not Path(f).exists()]
        
        if missing_dirs or missing_files:
            missing = missing_dirs + missing_files
            return {
                'status': 'error',
                'message': f"Missing project structure: {', '.join(missing)}",
                'details': {
                    'missing_dirs': missing_dirs,
                    'missing_files': missing_files
                }
            }
        else:
            return {
                'status': 'pass',
                'message': "Project structure complete",
                'details': {}
            }
    
    def check_log_directories(self) -> Dict[str, Any]:
        """Check log directory setup and permissions."""
        log_dir = Path('logs')
        
        if not log_dir.exists():
            try:
                log_dir.mkdir(parents=True)
                return {
                    'status': 'pass',
                    'message': "Created logs directory",
                    'details': {}
                }
            except Exception as e:
                return {
                    'status': 'error',
                    'message': f"Cannot create logs directory: {str(e)}",
                    'details': {'error': str(e)}
                }
        
        # Check if we can write to logs
        test_log = log_dir / 'health_check.log'
        try:
            test_log.write_text('Health check test')
            test_log.unlink()
            return {
                'status': 'pass',
                'message': "Log directory writable",
                'details': {}
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Cannot write to logs directory: {str(e)}",
                'details': {'error': str(e)}
            }
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate summary of all health checks."""
        total_checks = len(self.results)
        passed = len([r for r in self.results if r['status'] == 'pass'])
        warnings = len([r for r in self.results if r['status'] == 'warning'])
        errors = len([r for r in self.results if r['status'] == 'error'])
        
        print("\n" + "=" * 60)
        print("📊 HEALTH CHECK SUMMARY")
        print("=" * 60)
        print(f"Total checks: {total_checks}")
        print(f"✅ Passed: {passed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"❌ Errors: {errors}")
        
        if errors == 0 and warnings == 0:
            overall_status = "excellent"
            print("\n🎉 System is in excellent condition!")
        elif errors == 0:
            overall_status = "good"
            print("\n👍 System is in good condition with minor warnings.")
        elif errors <= 2:
            overall_status = "fair"
            print("\n⚠️  System has issues that should be addressed.")
        else:
            overall_status = "poor"
            print("\n🚨 System has significant issues that must be fixed.")
        
        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")
        
        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  ❌ {error}")
        
        # Provide recommendations
        print("\n💡 RECOMMENDATIONS:")
        if errors > 0:
            print("  1. Fix critical errors before running automation")
            print("  2. Install missing dependencies")
            print("  3. Check system permissions")
        
        if warnings > 0:
            print("  1. Address warnings for optimal performance")
            print("  2. Install optional dependencies")
        
        print("  3. Run 'python src/main.py --test' to verify fixes")
        print("  4. Check docs/guides/TROUBLESHOOTING.md for help")
        
        return {
            'overall_status': overall_status,
            'total_checks': total_checks,
            'passed': passed,
            'warnings': warnings,
            'errors': errors,
            'results': self.results,
            'warning_messages': self.warnings,
            'error_messages': self.errors
        }

def main():
    """Run health check from command line."""
    checker = HealthChecker()
    
    try:
        summary = checker.check_all()
        
        # Save results to file
        report_file = Path('logs/health_check_report.json')
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        # Exit with appropriate code
        if summary['errors'] > 0:
            sys.exit(1)
        elif summary['warnings'] > 0:
            sys.exit(2)
        else:
            sys.exit(0)
            
    except Exception as e:
        print(f"\n💥 Health check failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(3)

if __name__ == '__main__':
    main()
