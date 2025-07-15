#!/usr/bin/env python3
"""
Enhanced VS Code Monitor with 10-second state checking and GitHub Copilot API integration.

This module provides active monitoring of VS Code windows, detecting when they're in the same state
for too long and automatically triggering GitHub Copilot continue actions using the extension's API.
"""

import asyncio
import hashlib
import json
import logging
import subprocess
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

import psutil


@dataclass
class WindowSnapshot:
    """Represents a window state snapshot."""
    
    timestamp: float
    screenshot_hash: str
    window_geometry: str
    process_info: Dict
    copilot_state: Optional[Dict] = None


@dataclass
class EnhancedWindowState:
    """Enhanced window state with detailed tracking."""
    
    window_id: str
    title: str
    process_id: int
    snapshots: List[WindowSnapshot] = field(default_factory=list)
    last_change_time: float = 0
    same_state_duration: float = 0
    consecutive_same_states: int = 0
    last_continue_action: float = 0
    last_stop_action: float = 0
    is_copilot_active: bool = False
    copilot_session_state: Optional[str] = None


class EnhancedVSCodeMonitor:
    """Enhanced VS Code monitor with 10-second checking and GitHub Copilot API integration."""
    
    def __init__(self, 
                 check_interval: float = 10.0,  # Check every 10 seconds
                 same_state_threshold: float = 30.0,  # Consider stuck after 30 seconds
                 continue_cooldown: float = 60.0):  # Wait 1 minute between continue actions
        """Initialize the enhanced monitor.
        
        Args:
            check_interval: Time between state checks (default: 10 seconds)
            same_state_threshold: Time to consider window stuck (default: 30 seconds)
            continue_cooldown: Time between continue actions (default: 60 seconds)
        """
        self.check_interval = check_interval
        self.same_state_threshold = same_state_threshold
        self.continue_cooldown = continue_cooldown
        self.logger = logging.getLogger(__name__)
        self.window_states: Dict[str, EnhancedWindowState] = {}
        self.monitoring = False
        self.stats = {
            'checks_performed': 0,
            'state_changes_detected': 0,
            'continue_actions_triggered': 0,
            'stop_actions_triggered': 0,
            'copilot_api_calls': 0
        }
        
    async def start_monitoring(self):
        """Start enhanced monitoring with 10-second checks."""
        self.monitoring = True
        self.logger.info("🔍 Starting enhanced VS Code monitoring (10-second checks)...")
        
        while self.monitoring:
            try:
                await self._perform_check_cycle()
                self.stats['checks_performed'] += 1
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Error in monitoring cycle: {e}")
                await asyncio.sleep(30)  # Wait shorter on error for quick recovery
                
    async def stop_monitoring(self):
        """Stop monitoring."""
        self.monitoring = False
        self.logger.info("🛑 Stopping enhanced VS Code monitoring")
        
    async def _perform_check_cycle(self):
        """Perform one check cycle - compare states and take action."""
        current_time = time.time()
        vscode_windows = await self._get_vscode_windows()
        
        self.logger.debug(f"🔍 Checking {len(vscode_windows)} VS Code windows...")
        
        # Track active windows
        active_window_ids = set()
        
        for window in vscode_windows:
            window_id = window['id']
            active_window_ids.add(window_id)
            
            # Create or update window state
            if window_id not in self.window_states:
                self.window_states[window_id] = EnhancedWindowState(
                    window_id=window_id,
                    title=window['title'],
                    process_id=window['pid'],
                    last_change_time=current_time
                )
                
            # Take snapshot
            snapshot = await self._take_window_snapshot(window_id, window)
            
            # Analyze state changes
            await self._analyze_window_state(window_id, snapshot, current_time)
            
        # Remove states for windows that no longer exist
        removed_windows = set(self.window_states.keys()) - active_window_ids
        for window_id in removed_windows:
            del self.window_states[window_id]
            
    async def _take_window_snapshot(self, window_id: str, window_info: Dict) -> WindowSnapshot:
        """Take a comprehensive snapshot of window state."""
        # Get screenshot hash
        screenshot_hash = await self._get_window_screenshot_hash(window_id)
        
        # Get window geometry
        geometry = await self._get_window_geometry(window_id)
        
        # Get process info
        try:
            process = psutil.Process(window_info['pid'])
            process_info = {
                'cpu_percent': process.cpu_percent(),
                'memory_percent': process.memory_percent(),
                'status': process.status(),
                'num_threads': process.num_threads()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            process_info = {}
            
        # Get GitHub Copilot state (if possible)
        copilot_state = await self._get_copilot_state(window_id)
        
        return WindowSnapshot(
            timestamp=time.time(),
            screenshot_hash=screenshot_hash,
            window_geometry=geometry,
            process_info=process_info,
            copilot_state=copilot_state
        )
        
    async def _analyze_window_state(self, window_id: str, snapshot: WindowSnapshot, current_time: float):
        """Analyze window state and determine if action is needed."""
        state = self.window_states[window_id]
        
        # Add snapshot to history (keep last 10)
        state.snapshots.append(snapshot)
        if len(state.snapshots) > 10:
            state.snapshots.pop(0)
            
        # Check if state has changed
        if len(state.snapshots) >= 2:
            prev_snapshot = state.snapshots[-2]
            current_snapshot = state.snapshots[-1]
            
            if self._snapshots_are_same(prev_snapshot, current_snapshot):
                state.consecutive_same_states += 1
                state.same_state_duration = current_time - state.last_change_time
                
                self.logger.debug(f"Window {window_id} same state for {state.same_state_duration:.1f}s "
                                f"(count: {state.consecutive_same_states})")
                
                # Check if we need to take action
                if state.same_state_duration >= self.same_state_threshold:
                    await self._handle_stuck_window(window_id, state, current_time)
                    
            else:
                # State changed
                state.consecutive_same_states = 0
                state.last_change_time = current_time
                state.same_state_duration = 0
                self.stats['state_changes_detected'] += 1
                
                self.logger.debug(f"✅ Window {window_id} state changed")
                
    def _snapshots_are_same(self, snap1: WindowSnapshot, snap2: WindowSnapshot) -> bool:
        """Compare two snapshots to determine if window state is the same."""
        # Primary comparison: screenshot hash
        if snap1.screenshot_hash != snap2.screenshot_hash:
            return False
            
        # Secondary comparison: window geometry
        if snap1.window_geometry != snap2.window_geometry:
            return False
            
        # Tertiary comparison: process activity (allow some variance)
        if abs(snap1.process_info.get('cpu_percent', 0) - 
               snap2.process_info.get('cpu_percent', 0)) > 5.0:
            return False
            
        return True
        
    async def _handle_stuck_window(self, window_id: str, state: EnhancedWindowState, current_time: float):
        """Handle a window that appears to be stuck."""
        # Check cooldown periods
        if (current_time - state.last_continue_action) < self.continue_cooldown:
            self.logger.debug(f"Skipping action for {window_id} - cooldown active")
            return
            
        self.logger.warning(f"🧊 Window {window_id} stuck for {state.same_state_duration:.1f}s - taking action")
        
        # Try continue action first
        if await self._trigger_continue_action(window_id, state):
            state.last_continue_action = current_time
            self.stats['continue_actions_triggered'] += 1
            self.logger.info(f"✅ Continue action triggered for {window_id}")
        else:
            # If continue fails, try stop action
            if await self._trigger_stop_action(window_id, state):
                state.last_stop_action = current_time
                self.stats['stop_actions_triggered'] += 1
                self.logger.info(f"⏹️ Stop action triggered for {window_id}")
                
    async def _trigger_continue_action(self, window_id: str, state: EnhancedWindowState) -> bool:
        """Trigger continue action using GitHub Copilot API and fallback methods."""
        self.logger.info(f"🔄 Triggering continue action for window {window_id}")
        
        try:
            # Method 1: Try GitHub Copilot extension API
            if await self._use_copilot_api_continue(window_id):
                return True
                
            # Method 2: Try VS Code command palette
            if await self._use_vscode_command_continue(window_id):
                return True
                
            # Method 3: Try keyboard shortcuts
            if await self._use_keyboard_continue(window_id):
                return True
                
            # Method 4: Type "continue" directly
            if await self._type_continue_direct(window_id):
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Error triggering continue action: {e}")
            return False
            
    async def _trigger_stop_action(self, window_id: str, state: EnhancedWindowState) -> bool:
        """Trigger stop action for GitHub Copilot."""
        self.logger.info(f"⏹️ Triggering stop action for window {window_id}")
        
        try:
            # Method 1: Try GitHub Copilot API stop
            if await self._use_copilot_api_stop(window_id):
                return True
                
            # Method 2: Try VS Code command palette
            if await self._use_vscode_command_stop(window_id):
                return True
                
            # Method 3: Try Escape key
            if await self._use_keyboard_stop(window_id):
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Error triggering stop action: {e}")
            return False
            
    async def _use_copilot_api_continue(self, window_id: str) -> bool:
        """Use GitHub Copilot extension API to continue."""
        try:
            # Focus window first
            await self._focus_window(window_id)
            
            # Try GitHub Copilot specific commands
            commands_to_try = [
                "github.copilot.chat.continue",
                "github.copilot.chat.accept",
                "github.copilot.chat.submit",
                "workbench.action.chat.continue",
                "workbench.action.chat.submit"
            ]
            
            for command in commands_to_try:
                if await self._execute_vscode_command(window_id, command):
                    self.stats['copilot_api_calls'] += 1
                    self.logger.info(f"✅ Copilot API command '{command}' executed")
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Copilot API continue failed: {e}")
            return False
            
    async def _use_copilot_api_stop(self, window_id: str) -> bool:
        """Use GitHub Copilot extension API to stop."""
        try:
            # Focus window first
            await self._focus_window(window_id)
            
            # Try GitHub Copilot specific stop commands
            commands_to_try = [
                "github.copilot.chat.stop",
                "github.copilot.chat.cancel",
                "workbench.action.chat.stop",
                "workbench.action.chat.cancel"
            ]
            
            for command in commands_to_try:
                if await self._execute_vscode_command(window_id, command):
                    self.stats['copilot_api_calls'] += 1
                    self.logger.info(f"✅ Copilot API stop command '{command}' executed")
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Copilot API stop failed: {e}")
            return False
            
    async def _execute_vscode_command(self, window_id: str, command: str) -> bool:
        """Execute a VS Code command via command palette."""
        try:
            # Open command palette
            result = await asyncio.create_subprocess_exec(
                'xdotool', 'key', '--window', window_id, 'ctrl+shift+p',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.communicate()
            
            if result.returncode != 0:
                return False
                
            await asyncio.sleep(0.5)
            
            # Type command
            result = await asyncio.create_subprocess_exec(
                'xdotool', 'type', '--window', window_id, command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.communicate()
            
            if result.returncode != 0:
                return False
                
            await asyncio.sleep(0.3)
            
            # Press Enter
            result = await asyncio.create_subprocess_exec(
                'xdotool', 'key', '--window', window_id, 'Return',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.communicate()
            
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            return False
            
    async def _use_vscode_command_continue(self, window_id: str) -> bool:
        """Use VS Code commands to continue."""
        try:
            await self._focus_window(window_id)
            
            # Try command palette with continue commands
            commands = [
                "Chat: Continue",
                "Chat: Accept",
                "Chat: Submit",
                "Inline Chat: Accept Changes"
            ]
            
            for command in commands:
                if await self._execute_vscode_command(window_id, command):
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"VS Code command continue failed: {e}")
            return False
            
    async def _use_vscode_command_stop(self, window_id: str) -> bool:
        """Use VS Code commands to stop."""
        try:
            await self._focus_window(window_id)
            
            # Try command palette with stop commands
            commands = [
                "Chat: Stop",
                "Chat: Cancel",
                "Inline Chat: Cancel",
                "Inline Chat: Discard"
            ]
            
            for command in commands:
                if await self._execute_vscode_command(window_id, command):
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"VS Code command stop failed: {e}")
            return False
            
    async def _use_keyboard_continue(self, window_id: str) -> bool:
        """Use keyboard shortcuts to continue."""
        try:
            await self._focus_window(window_id)
            
            # Try different keyboard shortcuts
            shortcuts = ['ctrl+Return', 'Return', 'alt+Return']
            
            for shortcut in shortcuts:
                result = await asyncio.create_subprocess_exec(
                    'xdotool', 'key', '--window', window_id, shortcut,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await result.communicate()
                
                if result.returncode == 0:
                    await asyncio.sleep(0.5)  # Give time for action
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Keyboard continue failed: {e}")
            return False
            
    async def _use_keyboard_stop(self, window_id: str) -> bool:
        """Use keyboard shortcuts to stop."""
        try:
            await self._focus_window(window_id)
            
            # Try escape and other stop shortcuts
            shortcuts = ['Escape', 'ctrl+c', 'ctrl+Break']
            
            for shortcut in shortcuts:
                result = await asyncio.create_subprocess_exec(
                    'xdotool', 'key', '--window', window_id, shortcut,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await result.communicate()
                
                if result.returncode == 0:
                    await asyncio.sleep(0.5)
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Keyboard stop failed: {e}")
            return False
            
    async def _type_continue_direct(self, window_id: str) -> bool:
        """Type 'continue' directly into the chat."""
        try:
            await self._focus_window(window_id)
            
            # Click in chat area (approximate position)
            await asyncio.create_subprocess_exec(
                'xdotool', 'mousemove', '--window', window_id, '400', '600',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await asyncio.create_subprocess_exec(
                'xdotool', 'click', '--window', window_id, '1',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await asyncio.sleep(0.3)
            
            # Clear existing text
            await asyncio.create_subprocess_exec(
                'xdotool', 'key', '--window', window_id, 'ctrl+a',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Type "continue"
            result = await asyncio.create_subprocess_exec(
                'xdotool', 'type', '--window', window_id, 'continue',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.communicate()
            
            if result.returncode != 0:
                return False
                
            await asyncio.sleep(0.3)
            
            # Press Enter
            result = await asyncio.create_subprocess_exec(
                'xdotool', 'key', '--window', window_id, 'Return',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.communicate()
            
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Direct typing failed: {e}")
            return False
            
    async def _focus_window(self, window_id: str) -> bool:
        """Focus a specific window."""
        try:
            result = await asyncio.create_subprocess_exec(
                'xdotool', 'windowactivate', window_id,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.communicate()
            
            if result.returncode == 0:
                await asyncio.sleep(0.3)  # Give time for focus
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Window focus failed: {e}")
            return False
            
    async def _get_vscode_windows(self) -> List[Dict]:
        """Get all VS Code windows."""
        try:
            result = await asyncio.create_subprocess_exec(
                'xdotool', 'search', '--name', 'Visual Studio Code',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                return []
                
            window_ids = stdout.decode().strip().split('\n')
            if not window_ids or window_ids == ['']:
                return []
                
            windows = []
            for window_id in window_ids:
                window_info = await self._get_window_info(window_id.strip())
                if window_info:
                    windows.append(window_info)
                    
            return windows
            
        except Exception as e:
            self.logger.error(f"Error getting VS Code windows: {e}")
            return []
            
    async def _get_window_info(self, window_id: str) -> Optional[Dict]:
        """Get window information."""
        try:
            # Get title
            title_result = await asyncio.create_subprocess_exec(
                'xdotool', 'getwindowname', window_id,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            title_stdout, _ = await title_result.communicate()
            
            if title_result.returncode != 0:
                return None
                
            # Get PID
            pid_result = await asyncio.create_subprocess_exec(
                'xdotool', 'getwindowpid', window_id,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            pid_stdout, _ = await pid_result.communicate()
            
            if pid_result.returncode != 0:
                return None
                
            return {
                'id': window_id,
                'title': title_stdout.decode().strip(),
                'pid': int(pid_stdout.decode().strip())
            }
            
        except Exception as e:
            self.logger.debug(f"Error getting window info: {e}")
            return None
            
    async def _get_window_screenshot_hash(self, window_id: str) -> str:
        """Get screenshot hash for window."""
        try:
            result = await asyncio.create_subprocess_exec(
                'import', '-window', window_id, '-resize', '200x200', 'png:-',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                return hashlib.md5(stdout).hexdigest()
            else:
                return await self._get_window_geometry(window_id)
                
        except Exception:
            return str(time.time())
            
    async def _get_window_geometry(self, window_id: str) -> str:
        """Get window geometry as fallback."""
        try:
            result = await asyncio.create_subprocess_exec(
                'xdotool', 'getwindowgeometry', window_id,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await result.communicate()
            
            if result.returncode == 0:
                return hashlib.md5(stdout).hexdigest()
            else:
                return str(time.time())
                
        except Exception:
            return str(time.time())
            
    async def _get_copilot_state(self, window_id: str) -> Optional[Dict]:
        """Try to get GitHub Copilot state (experimental)."""
        # This would require deeper integration with VS Code's extension API
        # For now, return None - could be enhanced with VS Code extension
        return None
        
    def get_monitoring_stats(self) -> Dict:
        """Get monitoring statistics."""
        return {
            'monitoring': self.monitoring,
            'check_interval': self.check_interval,
            'same_state_threshold': self.same_state_threshold,
            'continue_cooldown': self.continue_cooldown,
            'total_windows': len(self.window_states),
            'stats': self.stats.copy(),
            'window_states': {
                wid: {
                    'title': state.title,
                    'same_state_duration': state.same_state_duration,
                    'consecutive_same_states': state.consecutive_same_states,
                    'last_continue_action': state.last_continue_action,
                    'last_stop_action': state.last_stop_action,
                    'snapshots_count': len(state.snapshots)
                }
                for wid, state in self.window_states.items()
            }
        }


async def main():
    """Test the enhanced monitor."""
    logging.basicConfig(level=logging.INFO)
    
    monitor = EnhancedVSCodeMonitor(
        check_interval=10.0,  # Check every 10 seconds
        same_state_threshold=30.0,  # Consider stuck after 30 seconds
        continue_cooldown=60.0  # Wait 1 minute between actions
    )
    
    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        await monitor.stop_monitoring()
        print("Monitoring stopped")


if __name__ == "__main__":
    asyncio.run(main())
