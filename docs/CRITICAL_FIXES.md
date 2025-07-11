# 🔧 Two Critical Fixes Applied

## ✅ **Fix 1: Window Count Accumulation Issue**

### Problem
- GUI showed "Windows Found: 10" and kept incrementing by 2 each cycle
- Even though only 2 VS Code windows were open
- The counter was showing cumulative processed windows, not current windows

### Root Cause
```python
'windows_found': engine_stats.get('windows_processed', 0)  # WRONG: Cumulative
```

### Solution Applied
```python
# Get current window count (not cumulative)
current_windows = self.automation_engine.window_detector.get_vscode_windows()
current_window_count = len(current_windows)

'windows_found': current_window_count,  # CORRECT: Current count
```

### Expected Result
- GUI should now show "Windows Found: 2" (constant)
- No more accumulating counter

---

## ✅ **Fix 2: gnome-screenshot Snap Conflicts**

### Problem
```
gnome-screenshot: symbol lookup error: /snap/core20/current/lib/x86_64-linux-gnu/libpthread.so.0: undefined symbol: __libc_pthread_init, version GLIBC_PRIVATE
```

### Root Cause
- Even though `HAS_PYSCREENSHOT = False`, pyscreenshot code paths still existed
- These could still trigger gnome-screenshot under certain conditions
- System beeping due to repeated errors

### Solution Applied
- **Completely removed** all pyscreenshot code paths on Linux
- **Disabled** both fullscreen and region capture via pyscreenshot
- **Forces** scrot → PIL → pyautogui fallback chain only

### Expected Result
- No more gnome-screenshot errors
- No more system beeping
- Reliable screenshot capture via scrot/PIL

---

## 🚀 **Test the Fixes**

Run the GUI again:
```bash
./run.sh --gui --dry-run
```

Expected behavior:
- ✅ **Windows Found**: Shows 2 (constant, not incrementing)
- ✅ **No errors**: No gnome-screenshot errors or beeping
- ✅ **Detection Cycles**: Incrementing normally
- ✅ **Screenshots**: Working via scrot/PIL without conflicts

Both issues should now be resolved!
