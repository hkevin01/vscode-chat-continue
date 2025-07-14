# 🛡️ System Freezing Prevention Guide

## ⚠️ URGENT: If System is Freezing

**IMMEDIATE ACTIONS:**

1. **Stop all automation processes:**
   ```bash
   ./stop.sh --force --cleanup
   ```

2. **Use SAFE MODE only:**
   ```bash
   ./run.sh --safe
   ```

## 🔧 What Was Fixed

### **Root Causes of System Freezing:**
- ❌ **Too frequent screenshot captures** (every 3-5 seconds)
- ❌ **Memory leaks** from image processing 
- ❌ **CPU-intensive OCR operations**
- ❌ **Multiple concurrent processes**
- ❌ **No system resource monitoring**

### **Solutions Implemented:**

#### **1. Safe Mode (`--safe` flag)**
- ✅ **10+ second intervals** (vs 3-5 seconds)
- ✅ **Coordinate-based clicking** (no image processing)
- ✅ **Automatic memory cleanup** every 5 cycles
- ✅ **System load monitoring** 
- ✅ **Limited to 1-2 windows** per cycle
- ✅ **Performance tracking** and auto-adjustment

#### **2. Resource Management**
- ✅ **Garbage collection** after each cycle
- ✅ **CPU load detection** - skips cycles if load > 3.0
- ✅ **Memory leak prevention**
- ✅ **Process limiting** - max 2 windows per cycle

#### **3. Optimized Scripts**
- ✅ **safe_automation.py** - Ultra-lightweight version
- ✅ **Enhanced termination** script
- ✅ **Automatic cleanup** of temp files

## 🚀 Usage Instructions

### **Always Use Safe Mode:**
```bash
# Primary recommendation - prevents freezing
./run.sh --safe

# Alternative direct call
./scripts/run_safe.sh
```

### **Stop All Processes:**
```bash
# Graceful stop
./stop.sh

# Force stop if needed
./stop.sh --force --cleanup
```

### **Check System Status:**
```bash
# Monitor system load
uptime

# Check running processes
./stop.sh --dry-run
```

## ⚙️ Configuration

The safe mode automatically uses these settings:

- **Minimum interval:** 10 seconds (vs 3-5 seconds)
- **Memory cleanup:** Every 5 cycles
- **Window limit:** 2 windows per cycle
- **Load threshold:** Skip if CPU load > 3.0
- **Fallback method:** Coordinate-based (no screenshots)

## 🔍 Monitoring

Safe mode includes built-in monitoring:

- **Performance tracking** - adjusts intervals if cycles take too long
- **System load detection** - skips cycles during high load
- **Memory management** - force garbage collection
- **Process counting** - limits resource usage

## 💡 Best Practices

1. **Always use `--safe` flag** when experiencing freezing
2. **Monitor system load** with `uptime` command
3. **Stop automation** if system becomes unresponsive
4. **Use coordinate fallback** instead of image processing
5. **Run only one automation instance** at a time

## 🚨 Emergency Recovery

If system becomes unresponsive:

1. **Switch to TTY:** `Ctrl+Alt+F2`
2. **Kill processes:** `pkill -f vscode-chat-continue`
3. **Force cleanup:** `killall python`
4. **Return to desktop:** `Ctrl+Alt+F7`

## ✅ Verification

Test that safe mode works:

```bash
# Test dry run (safe)
./run.sh --safe --dry-run

# Check for processes
./stop.sh --dry-run

# Monitor resources
watch -n 1 'uptime && free -h'
```

**Safe mode should show:**
- ✅ 10+ second intervals
- ✅ No image processing
- ✅ Coordinate-based clicking
- ✅ System load monitoring
