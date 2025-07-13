#!/usr/bin/env python3
"""
Performance optimization for VS Code Continue Button Automation.
Reduces memory usage and system slowdown when GUI is running.
"""

import gc
import os
import sys
import time
from pathlib import Path

import psutil

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def optimize_system_performance():
    """Apply system-level performance optimizations."""
    print("🚀 Applying Performance Optimizations...")
    
    # 1. Force garbage collection
    print("  • Forcing garbage collection...")
    gc.collect()
    
    # 2. Set process priority to lower (nice)
    try:
        current_process = psutil.Process()
        current_process.nice(5)  # Lower priority
        print("  • Set process priority to lower (nice +5)")
    except Exception:
        print("  • Could not adjust process priority")
    
    # 3. Optimize memory allocation
    try:
        import resource

        # Limit memory usage to 1GB
        resource.setrlimit(resource.RLIMIT_AS, (1024*1024*1024, 1024*1024*1024))
        print("  • Set memory limit to 1GB")
    except Exception:
        print("  • Could not set memory limits")
    
    # 4. Optimize Python garbage collection
    gc.set_threshold(700, 10, 10)  # More aggressive GC
    print("  • Set aggressive garbage collection thresholds")
    
    print("✅ Performance optimizations applied!")


def monitor_performance():
    """Monitor system performance while automation runs."""
    print("\n📊 Performance Monitor")
    print("=" * 40)
    
    try:
        process = psutil.Process()
        
        # Memory usage
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        # CPU usage
        cpu_percent = process.cpu_percent()
        
        # System memory
        system_memory = psutil.virtual_memory()
        system_memory_percent = system_memory.percent
        
        print(f"Process Memory: {memory_mb:.1f} MB")
        print(f"Process CPU: {cpu_percent:.1f}%")
        print(f"System Memory: {system_memory_percent:.1f}% used")
        
        # Check if performance is concerning
        if memory_mb > 500:
            print("⚠️  High memory usage detected!")
            print("   Consider restarting the application")
            
        if cpu_percent > 50:
            print("⚠️  High CPU usage detected!")
            print("   Consider increasing detection intervals")
            
        if system_memory_percent > 80:
            print("⚠️  System memory is low!")
            print("   Consider closing other applications")
            
    except Exception as e:
        print(f"Error monitoring performance: {e}")


def optimize_automation_config():
    """Create optimized configuration for better performance."""
    from core.config_manager import ConfigManager
    
    print("\n⚙️  Creating optimized configuration...")
    
    config = ConfigManager()
    
    # Performance-optimized settings
    optimizations = {
        'automation.interval_seconds': 8.0,  # Longer intervals
        'automation.max_windows': 2,  # Limit processed windows
        'automation.click_delay': 0.5,  # Faster clicks
        'automation.auto_focus_windows': True,  # Keep focus feature
        
        'detection.max_buttons_per_window': 3,  # Limit button detection
        'detection.cache_screenshots': False,  # Disable caching to save memory
        'detection.ocr_confidence': 85,  # Higher confidence = fewer false positives
        
        'logging.level': 'WARNING',  # Reduce logging overhead
        'logging.max_log_size': 1024*1024,  # 1MB max log files
        
        'safety.pause_detection_threshold': 0.1,  # Less sensitive user detection
        'safety.memory_limit_mb': 512,  # Memory limit
    }
    
    for key, value in optimizations.items():
        config.set(key, value)
        print(f"  • {key}: {value}")
    
    print("✅ Optimized configuration created!")
    return config


def cleanup_resources():
    """Clean up resources to free memory."""
    print("\n🧹 Cleaning up resources...")
    
    # Force garbage collection multiple times
    for i in range(3):
        collected = gc.collect()
        if collected > 0:
            print(f"  • Garbage collection pass {i+1}: freed {collected} objects")
    
    # Clear Python caches
    try:
        sys.modules.clear()
        print("  • Cleared module cache")
    except Exception:
        pass
    
    print("✅ Resource cleanup complete!")


def main():
    """Main performance optimization function."""
    print("🎯 VS Code Continue Automation - Performance Optimizer")
    print("=" * 60)
    
    # Apply optimizations
    optimize_system_performance()
    
    # Create optimized config
    config = optimize_automation_config()
    
    # Monitor current performance
    monitor_performance()
    
    print("\n💡 Performance Tips:")
    print("  • Close unnecessary applications")
    print("  • Use 8+ second detection intervals") 
    print("  • Enable dry-run mode for testing")
    print("  • Monitor memory usage periodically")
    print("  • Restart application if memory > 500MB")
    
    print("\n🚀 To run optimized automation:")
    print("  python src/main.py --config config/optimized.json")
    
    # Save optimized config
    config_path = Path("config/optimized.json")
    config_path.parent.mkdir(exist_ok=True)
    config.save(config_path)
    print(f"\n✅ Optimized config saved to: {config_path}")


if __name__ == "__main__":
    main()
