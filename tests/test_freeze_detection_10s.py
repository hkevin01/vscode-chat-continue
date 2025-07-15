#!/usr/bin/env python3
"""
10-Second Freeze Detection Test for VS Code Windows.

Tests VS Code window monitoring every 10 seconds.
Production version uses 3-minute intervals.
"""

import asyncio
import hashlib
import logging
import os
import subprocess
import time
from typing import Any, Dict, List, Optional

# Configure logging for 10-second test mode
log_file = '/home/kevin/Projects/vscode-chat-continue/logs/' + \
           'freeze_detection_10s_test.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WindowSnapshot:
    """Simple window state snapshot."""
    
    def __init__(self, timestamp: float, screenshot_hash: str, 
                 window_geometry: str):
        self.timestamp = timestamp
        self.screenshot_hash = screenshot_hash
        self.window_geometry = window_geometry


class WindowState:
    """Window state tracking."""
    
    def __init__(self, window_id: str, title: str):
        self.window_id = window_id
        self.title = title
        self.snapshots: List[WindowSnapshot] = []
        self.last_change_time = time.time()
        self.same_state_duration = 0.0
        self.consecutive_same_states = 0
        self.last_continue_action = 0.0


class VSCodeFreezeDetector10s:
    """10-Second interval freeze detection system for VS Code windows."""
    
    def __init__(self):
        # 10 seconds for testing (vs 180 for production)
        self.check_interval = 10
        # Consider frozen after 10 seconds unchanged
        self.freeze_threshold = 10
        self.window_states: Dict[str, WindowState] = {}
        self.running = False
        self.stats = {
            'checks_performed': 0,
            'windows_monitored': 0,
            'freeze_events_detected': 0,
            'continue_actions_triggered': 0,
            'api_calls_made': 0,
            'recovery_attempts': 0
        }
        
    async def detect_vscode_windows(self) -> List[Dict[str, Any]]:
        """Detect all VS Code windows currently open."""
        try:
            # Use wmctrl to find VS Code windows
            result = subprocess.run(
                ['wmctrl', '-l'],
                capture_output=True,
                text=True,
                check=True
            )
            
            vscode_windows = []
            for line in result.stdout.strip().split('\n'):
                if line and ('Visual Studio Code' in line or 
                           'VSCode' in line or 'vscode' in line.lower()):
                    parts = line.split(None, 3)
                    if len(parts) >= 4:
                        window_id = parts[0]
                        title = parts[3]
                        vscode_windows.append({
                            'window_id': window_id,
                            'title': title,
                            'detected_at': time.time()
                        })
                        
            logger.info(f"Detected {len(vscode_windows)} VS Code windows")
            return vscode_windows
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to detect VS Code windows: {e}")
            return []
    
    async def capture_window_state(self, window_id: str) -> \
            Optional[WindowSnapshot]:
        """Capture the current state of a VS Code window."""
        try:
            # Capture window geometry
            geometry_result = subprocess.run(
                ['xwininfo', '-id', window_id],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Take screenshot of the window
            screenshot_result = subprocess.run(
                ['import', '-window', window_id, '-'],
                capture_output=True,
                check=True
            )
            
            # Create hash of screenshot for comparison
            screenshot_hash = hashlib.sha256(
                screenshot_result.stdout).hexdigest()
            
            return WindowSnapshot(
                timestamp=time.time(),
                screenshot_hash=screenshot_hash,
                window_geometry=geometry_result.stdout
            )
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to capture window state for "
                         f"{window_id}: {e}")
            return None
    
    async def check_for_freeze(self, window_state: WindowState) -> bool:
        """Check if a window has been frozen (unchanged) for too long."""
        if len(window_state.snapshots) < 2:
            return False
            
        latest_snapshot = window_state.snapshots[-1]
        previous_snapshot = window_state.snapshots[-2]
        
        # Compare screenshot hashes to detect if content changed
        if latest_snapshot.screenshot_hash == previous_snapshot.screenshot_hash:
            window_state.same_state_duration += self.check_interval
            window_state.consecutive_same_states += 1
            
            # Check if frozen longer than threshold
            if window_state.same_state_duration >= self.freeze_threshold:
                logger.warning(f"Window {window_state.window_id} frozen for "
                             f"{window_state.same_state_duration}s")
                return True
        else:
            # Window content changed, reset freeze tracking
            window_state.same_state_duration = 0
            window_state.consecutive_same_states = 0
            window_state.last_change_time = time.time()
            
        return False
    
    async def trigger_continue_action(self, window_id: str) -> bool:
        """Trigger GitHub Copilot continue action using VS Code API."""
        try:
            logger.info(f"Triggering continue action for window {window_id}")
            
            # Method 1: Focus window and use Ctrl+Enter
            subprocess.run(['wmctrl', '-i', '-a', window_id], check=True)
            await asyncio.sleep(0.5)  # Brief pause for window focus
            
            # Send Ctrl+Enter to trigger continue
            subprocess.run(['xdotool', 'key', 'ctrl+Return'], check=True)
            await asyncio.sleep(0.2)
            
            # Method 2: Alternative - type "continue" and press Enter
            # This mimics typing in the chat
            subprocess.run(['xdotool', 'type', 'continue'], check=True)
            await asyncio.sleep(0.2)
            subprocess.run(['xdotool', 'key', 'Return'], check=True)
            
            self.stats['continue_actions_triggered'] += 1
            self.stats['api_calls_made'] += 1
            
            logger.info(f"Continue action triggered successfully for "
                       f"window {window_id}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to trigger continue action for "
                        f"{window_id}: {e}")
            return False
    
    async def recover_frozen_window(self, window_state: WindowState) -> bool:
        """Attempt to recover a frozen VS Code window."""
        try:
            logger.info(f"Attempting recovery for frozen window "
                       f"{window_state.window_id}")
            self.stats['recovery_attempts'] += 1
            
            # Focus the window first
            subprocess.run(['wmctrl', '-i', '-a', window_state.window_id],
                         check=True)
            await asyncio.sleep(1.0)
            
            # Try Escape key to clear any modal dialogs
            subprocess.run(['xdotool', 'key', 'Escape'], check=True)
            await asyncio.sleep(0.5)
            
            # Try to open command palette and execute continue
            subprocess.run(['xdotool', 'key', 'ctrl+shift+p'], check=True)
            await asyncio.sleep(1.0)
            
            # Type continue command
            subprocess.run(['xdotool', 'type', 'GitHub Copilot: Continue'],
                         check=True)
            await asyncio.sleep(0.5)
            subprocess.run(['xdotool', 'key', 'Return'], check=True)
            
            # Update last action time
            window_state.last_continue_action = time.time()
            
            logger.info(f"Recovery attempt completed for window "
                       f"{window_state.window_id}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Recovery failed for window "
                        f"{window_state.window_id}: {e}")
            return False
    
    async def monitor_cycle(self):
        """Perform one monitoring cycle - check all VS Code windows."""
        try:
            logger.info("Starting monitoring cycle...")
            self.stats['checks_performed'] += 1
            
            # Detect current VS Code windows
            vscode_windows = await self.detect_vscode_windows()
            self.stats['windows_monitored'] = len(vscode_windows)
            
            for window_info in vscode_windows:
                window_id = window_info['window_id']
                
                # Initialize window state if new
                if window_id not in self.window_states:
                    self.window_states[window_id] = WindowState(
                        window_id=window_id,
                        title=window_info['title']
                    )
                    logger.info(f"Added new window to monitoring: "
                              f"{window_id}")
                
                window_state = self.window_states[window_id]
                
                # Capture current window state
                snapshot = await self.capture_window_state(window_id)
                if snapshot:
                    window_state.snapshots.append(snapshot)
                    
                    # Keep only last 2 snapshots for comparison
                    if len(window_state.snapshots) > 2:
                        window_state.snapshots = window_state.snapshots[-2:]
                    
                    # Check for freeze
                    is_frozen = await self.check_for_freeze(window_state)
                    
                    if is_frozen:
                        self.stats['freeze_events_detected'] += 1
                        logger.warning(f"Freeze detected in window "
                                     f"{window_id} - attempting recovery")
                        
                        # Attempt recovery
                        recovery_success = await self.recover_frozen_window(
                            window_state)
                        if recovery_success:
                            # Reset freeze tracking after successful recovery
                            window_state.same_state_duration = 0
                            window_state.consecutive_same_states = 0
                            window_state.last_change_time = time.time()
                
            # Clean up old window states for windows that no longer exist
            current_window_ids = {w['window_id'] for w in vscode_windows}
            old_windows = set(self.window_states.keys()) - current_window_ids
            for old_window_id in old_windows:
                del self.window_states[old_window_id]
                logger.info(f"Removed closed window from monitoring: "
                          f"{old_window_id}")
            
            logger.info(f"Monitoring cycle completed. Stats: {self.stats}")
            
        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}")
    
    async def run_test(self, duration_minutes: int = 5):
        """Run the 10-second freeze detection test for specified duration."""
        logger.info(f"Starting 10-second freeze detection test for "
                   f"{duration_minutes} minutes")
        logger.info(f"Check interval: {self.check_interval} seconds")
        logger.info(f"Freeze threshold: {self.freeze_threshold} seconds")
        
        self.running = True
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        try:
            while self.running and time.time() < end_time:
                await self.monitor_cycle()
                
                # Wait for next check interval
                await asyncio.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("Test interrupted by user")
        except Exception as e:
            logger.error(f"Test failed with error: {e}")
        finally:
            self.running = False
            
        # Print final statistics
        total_runtime = time.time() - start_time
        logger.info(f"\n=== 10-Second Freeze Detection Test Results ===")
        logger.info(f"Total runtime: {total_runtime:.1f} seconds")
        logger.info(f"Checks performed: {self.stats['checks_performed']}")
        logger.info(f"Windows monitored: {self.stats['windows_monitored']}")
        logger.info(f"Freeze events detected: "
                   f"{self.stats['freeze_events_detected']}")
        logger.info(f"Continue actions triggered: "
                   f"{self.stats['continue_actions_triggered']}")
        logger.info(f"Recovery attempts: {self.stats['recovery_attempts']}")
        logger.info(f"API calls made: {self.stats['api_calls_made']}")
        avg_interval = total_runtime / max(1, self.stats['checks_performed'])
        logger.info(f"Average check interval: {avg_interval:.1f}s")
    
    def stop_test(self):
        """Stop the monitoring test."""
        logger.info("Stopping freeze detection test...")
        self.running = False


async def main():
    """Main test function."""
    print("VS Code 10-Second Freeze Detection Test")
    print("======================================")
    print("This test monitors VS Code windows every 10 seconds")
    print("and detects when they're frozen (unchanged for 10+ seconds)")
    print("For production use, change intervals to 3 minutes (180 seconds)")
    print()
    
    detector = VSCodeFreezeDetector10s()
    
    try:
        # Run test for 5 minutes by default
        await detector.run_test(duration_minutes=5)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        detector.stop_test()


if __name__ == '__main__':
    # Check for required tools
    required_tools = ['wmctrl', 'xwininfo', 'import', 'xdotool']
    missing_tools = []
    
    for tool in required_tools:
        try:
            subprocess.run(['which', tool], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"ERROR: Missing required tools: {', '.join(missing_tools)}")
        print("Please install them with:")
        print("sudo apt-get install wmctrl x11-utils imagemagick xdotool")
        import sys
        sys.exit(1)
    
    # Run the test
    asyncio.run(main())
