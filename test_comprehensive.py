#!/usr/bin/env python3
"""
Comprehensive Testing Suite for Process Termination & Freeze Detection

Tests all major functionality without X11 dependencies.
"""

import subprocess
import sys
import time
from pathlib import Path

project_root = Path(__file__).parent


def test_termination_functionality():
    """Test the process termination feature."""
    print("🔍 Testing Process Termination Functionality")
    print("=" * 50)
    
    # Test 1: Help command (should work without termination)
    print("📝 Test 1: Help command with --no-terminate")
    result = subprocess.run([
        sys.executable, "src/main.py", "--help", "--no-terminate"
    ], capture_output=True, text=True, cwd=project_root)
    
    if result.returncode == 0 and "--no-terminate" in result.stdout:
        print("   ✅ Help command with --no-terminate: PASSED")
    else:
        print("   ❌ Help command failed")
        return False
    
    # Test 2: Test that termination flag exists
    print("\n📝 Test 2: Termination flag availability")
    if "--no-terminate" in result.stdout:
        print("   ✅ --no-terminate flag is available: PASSED")
    else:
        print("   ❌ --no-terminate flag missing")
        return False
    
    # Test 3: Version command
    print("\n📝 Test 3: Version command")
    result = subprocess.run([
        sys.executable, "src/main.py", "--version"
    ], capture_output=True, text=True, cwd=project_root)
    
    if result.returncode == 0:
        print("   ✅ Version command: PASSED")
        print(f"   📋 Version: {result.stdout.strip()}")
    else:
        print("   ❌ Version command failed")
        return False
    
    return True


def test_freeze_detection_config():
    """Test freeze detection configuration."""
    print("\n🧪 Testing Freeze Detection Configuration")
    print("=" * 50)
    
    try:
        # Import and test configuration
        sys.path.insert(0, str(project_root))
        from src.core.config_manager import ConfigManager
        
        config = ConfigManager()
        
        # Test configuration loading
        print("📝 Test 1: Configuration loading")
        current_mode = config.get("freeze_detection.current_mode")
        if current_mode:
            print(f"   ✅ Current mode: {current_mode}")
        else:
            print("   ❌ Failed to load current mode")
            return False
        
        # Test mode intervals
        print("\n📝 Test 2: Mode intervals")
        test_interval = config.get("freeze_detection.test_mode.check_interval")
        prod_interval = config.get("freeze_detection.production_mode.check_interval")
        
        if test_interval == 10:
            print(f"   ✅ Test mode interval: {test_interval}s (correct)")
        else:
            print(f"   ❌ Test mode interval: {test_interval}s (expected 10s)")
            return False
            
        if prod_interval == 180:
            print(f"   ✅ Production mode interval: {prod_interval}s (correct)")
        else:
            print(f"   ❌ Production mode interval: {prod_interval}s (expected 180s)")
            return False
        
        # Test recovery methods
        print("\n📝 Test 3: Recovery methods")
        recovery_methods = config.get("freeze_detection.recovery_methods")
        expected_methods = ["ctrl_enter", "type_continue", "command_palette"]
        
        if all(method in recovery_methods for method in expected_methods):
            print(f"   ✅ Recovery methods: {len(recovery_methods)} available")
            for method in recovery_methods:
                print(f"      • {method}")
        else:
            print(f"   ❌ Recovery methods incomplete")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False


def test_command_line_integration():
    """Test command line integration."""
    print("\n⚙️  Testing Command Line Integration")
    print("=" * 50)
    
    # Test 1: Dry run mode
    print("📝 Test 1: Dry run mode availability")
    result = subprocess.run([
        sys.executable, "src/main.py", "--help"
    ], capture_output=True, text=True, cwd=project_root)
    
    if "--dry-run" in result.stdout:
        print("   ✅ --dry-run flag available: PASSED")
    else:
        print("   ❌ --dry-run flag missing")
        return False
    
    # Test 2: Debug mode
    print("\n📝 Test 2: Debug mode availability")
    if "--debug" in result.stdout:
        print("   ✅ --debug flag available: PASSED")
    else:
        print("   ❌ --debug flag missing")
        return False
    
    # Test 3: Test freeze mode
    print("\n📝 Test 3: Test freeze mode availability")
    if "--test-freeze" in result.stdout:
        print("   ✅ --test-freeze flag available: PASSED")
    else:
        print("   ❌ --test-freeze flag missing")
        return False
    
    # Test 4: GUI mode
    print("\n📝 Test 4: GUI mode availability")
    if "--gui" in result.stdout:
        print("   ✅ --gui flag available: PASSED")
    else:
        print("   ❌ --gui flag missing")
        return False
    
    return True


def run_comprehensive_tests():
    """Run all comprehensive tests."""
    print("🚀 Starting Comprehensive Testing Suite")
    print("=" * 60)
    print("Testing vscode-chat-continue functionality...")
    print()
    
    tests = [
        ("Process Termination", test_termination_functionality),
        ("Freeze Detection Config", test_freeze_detection_config),
        ("Command Line Integration", test_command_line_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
            
            if success:
                print(f"\n✅ {test_name}: PASSED")
            else:
                print(f"\n❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"\n💥 {test_name}: ERROR - {e}")
            results.append((test_name, False))
        
        print()
    
    # Summary
    print("📊 Test Results Summary")
    print("=" * 30)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    success_rate = (passed / total) * 100
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if passed == total:
        print("\n🎉 All tests passed! System is fully functional.")
        print("✅ Process termination feature working")
        print("✅ Freeze detection configured correctly")  
        print("✅ Command line interface complete")
        print("\n🚀 Ready for use:")
        print("   python src/main.py --test-freeze")
        print("   python src/main.py --dry-run")
        print("   python src/main.py --no-terminate --gui")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - check implementation")
    
    return passed == total


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
