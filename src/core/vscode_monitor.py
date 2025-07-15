#!/usr/bin/env python3
"""
VS Code Window Monitor and Recovery System

Monitors VS Code windows for freezing/hanging and provides recovery using VS Code API.
"""

import asyncio
import hashlib
import json
import logging
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

import psutil


@dataclass
class WindowState:
    """Represents the state of a VS Code window."""

    window_id: str
    title: str
    screenshot_hash: str
    last_change_time: float
    process_id: int
    is_responsive: bool
    consecutive_freezes: int
    last_recovery_attempt: float


class VSCodeMonitor:
    """Monitor VS Code windows for freezing and perform automated recovery."""

    def __init__(self, freeze_threshold: float = 600.0, recovery_cooldown: float = 300.0):
        """Initialize the VS Code monitor.

        Args:
            freeze_threshold: Time in seconds to consider a window frozen (default: 10 minutes)
            recovery_cooldown: Time in seconds between recovery attempts (default: 5 minutes)
        """
        self.freeze_threshold = freeze_threshold
        self.recovery_cooldown = recovery_cooldown
        self.logger = logging.getLogger(__name__)
        self.window_states: Dict[str, WindowState] = {}
        self.monitoring = False

    async def start_monitoring(self):
        """Start monitoring VS Code windows."""
        self.monitoring = True
        self.logger.info("🔍 Starting VS Code window monitoring...")

        while self.monitoring:
            try:
                await self._monitor_cycle()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                self.logger.error(f"Error in monitoring cycle: {e}")
                await asyncio.sleep(60)  # Wait longer on error

    async def stop_monitoring(self):
        """Stop monitoring VS Code windows."""
        self.monitoring = False
        self.logger.info("🛑 Stopping VS Code window monitoring")

    async def _monitor_cycle(self):
        """Perform one monitoring cycle."""
        current_time = time.time()
        vscode_windows = await self._get_vscode_windows()

        # Update window states
        active_window_ids = set()
        for window in vscode_windows:
            window_id = window["id"]
            active_window_ids.add(window_id)

            # Take screenshot and calculate hash
            screenshot_hash = await self._get_window_screenshot_hash(window_id)

            if window_id in self.window_states:
                # Update existing window state
                await self._update_window_state(window_id, window, screenshot_hash, current_time)
            else:
                # Create new window state
                self.window_states[window_id] = WindowState(
                    window_id=window_id,
                    title=window["title"],
                    screenshot_hash=screenshot_hash,
                    last_change_time=current_time,
                    process_id=window["pid"],
                    is_responsive=True,
                    consecutive_freezes=0,
                    last_recovery_attempt=0,
                )

        # Remove states for windows that no longer exist
        removed_windows = set(self.window_states.keys()) - active_window_ids
        for window_id in removed_windows:
            del self.window_states[window_id]

        # Check for frozen windows and attempt recovery
        await self._check_and_recover_frozen_windows(current_time)

    async def _get_vscode_windows(self) -> List[Dict]:
        """Get all VS Code windows with their information."""
        try:
            # Get VS Code windows using xdotool
            result = await asyncio.create_subprocess_exec(
                "xdotool",
                "search",
                "--name",
                "Visual Studio Code",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()

            if result.returncode != 0:
                return []

            window_ids = stdout.decode().strip().split("\n")
            if not window_ids or window_ids == [""]:
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
        """Get detailed information about a window."""
        try:
            # Get window title
            title_result = await asyncio.create_subprocess_exec(
                "xdotool",
                "getwindowname",
                window_id,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            title_stdout, _ = await title_result.communicate()

            if title_result.returncode != 0:
                return None

            title = title_stdout.decode().strip()

            # Get window PID
            pid_result = await asyncio.create_subprocess_exec(
                "xdotool",
                "getwindowpid",
                window_id,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            pid_stdout, _ = await pid_result.communicate()

            if pid_result.returncode != 0:
                return None

            pid = int(pid_stdout.decode().strip())

            return {"id": window_id, "title": title, "pid": pid}

        except Exception as e:
            self.logger.debug(f"Error getting window info for {window_id}: {e}")
            return None

    async def _get_window_screenshot_hash(self, window_id: str) -> str:
        """Get a hash of the window screenshot for change detection."""
        try:
            # Take screenshot of specific window
            result = await asyncio.create_subprocess_exec(
                "import",
                "-window",
                window_id,
                "-resize",
                "200x200",
                "png:-",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()

            if result.returncode != 0:
                # Fallback: use window geometry as a simple hash
                return await self._get_window_geometry_hash(window_id)

            # Create hash of screenshot data
            return hashlib.md5(stdout).hexdigest()

        except Exception as e:
            self.logger.debug(f"Error taking screenshot of window {window_id}: {e}")
            return await self._get_window_geometry_hash(window_id)

    async def _get_window_geometry_hash(self, window_id: str) -> str:
        """Get window geometry as a fallback hash."""
        try:
            result = await asyncio.create_subprocess_exec(
                "xdotool",
                "getwindowgeometry",
                window_id,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await result.communicate()

            if result.returncode == 0:
                return hashlib.md5(stdout).hexdigest()
            else:
                return str(time.time())  # Fallback to timestamp

        except Exception:
            return str(time.time())

    async def _update_window_state(
        self, window_id: str, window_info: Dict, screenshot_hash: str, current_time: float
    ):
        """Update the state of a window."""
        state = self.window_states[window_id]

        # Check if window content has changed
        if state.screenshot_hash != screenshot_hash:
            state.screenshot_hash = screenshot_hash
            state.last_change_time = current_time
            state.is_responsive = True
            state.consecutive_freezes = 0

        # Update basic info
        state.title = window_info["title"]
        state.process_id = window_info["pid"]

    async def _check_and_recover_frozen_windows(self, current_time: float):
        """Check for frozen windows and attempt recovery."""
        for window_id, state in self.window_states.items():
            # Check if window is frozen
            time_since_change = current_time - state.last_change_time

            if time_since_change > self.freeze_threshold:
                # Window appears frozen
                if not state.is_responsive:
                    state.consecutive_freezes += 1
                else:
                    state.is_responsive = False
                    state.consecutive_freezes = 1

                self.logger.warning(
                    f"🧊 Window {window_id} appears frozen for {time_since_change:.1f}s "
                    f"(freeze #{state.consecutive_freezes})"
                )

                # Attempt recovery if cooldown period has passed
                if current_time - state.last_recovery_attempt > self.recovery_cooldown:
                    await self._attempt_recovery(window_id, state, current_time)

    async def _attempt_recovery(self, window_id: str, state: WindowState, current_time: float):
        """Attempt to recover a frozen VS Code window."""
        self.logger.info(f"🔧 Attempting recovery for frozen window {window_id}")
        state.last_recovery_attempt = current_time

        try:
            # Method 1: Try to check if process is responsive
            if await self._is_process_responsive(state.process_id):
                self.logger.info("Process is responsive, trying soft recovery...")
                success = await self._soft_recovery(window_id, state)
            else:
                self.logger.warning("Process appears unresponsive, trying hard recovery...")
                success = await self._hard_recovery(window_id, state)

            if success:
                self.logger.info(f"✅ Recovery successful for window {window_id}")
                state.is_responsive = True
                state.consecutive_freezes = 0
                state.last_change_time = current_time
            else:
                self.logger.error(f"❌ Recovery failed for window {window_id}")

        except Exception as e:
            self.logger.error(f"Error during recovery for window {window_id}: {e}")

    async def _is_process_responsive(self, pid: int) -> bool:
        """Check if a process is responsive."""
        try:
            process = psutil.Process(pid)

            # Check if process is running
            if not process.is_running():
                return False

            # Check CPU usage (very low CPU might indicate hanging)
            cpu_percent = process.cpu_percent(interval=1.0)

            # Check memory usage and other indicators
            memory_info = process.memory_info()

            # Simple heuristic: if CPU is 0% for extended time, might be hanging
            return cpu_percent > 0.1 or memory_info.rss > 0

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    async def _soft_recovery(self, window_id: str, state: WindowState) -> bool:
        """Attempt soft recovery using VS Code commands."""
        try:
            self.logger.info(f"🔄 Soft recovery: sending continue command to window {window_id}")

            # Focus the window
            await asyncio.create_subprocess_exec(
                "xdotool",
                "windowactivate",
                window_id,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await asyncio.sleep(0.5)

            # Method 1: Try Ctrl+Enter (accept/continue)
            result1 = await asyncio.create_subprocess_exec(
                "xdotool",
                "key",
                "--window",
                window_id,
                "ctrl+Return",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await asyncio.sleep(1.0)

            # Method 2: Try command palette approach
            await asyncio.create_subprocess_exec(
                "xdotool",
                "key",
                "--window",
                window_id,
                "ctrl+shift+p",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await asyncio.sleep(0.5)

            await asyncio.create_subprocess_exec(
                "xdotool",
                "type",
                "--window",
                window_id,
                "Chat: Continue",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await asyncio.sleep(0.3)

            await asyncio.create_subprocess_exec(
                "xdotool",
                "key",
                "--window",
                window_id,
                "Return",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await asyncio.sleep(1.0)

            # Method 3: Type "continue" directly
            # Click in chat area
            await asyncio.create_subprocess_exec(
                "xdotool",
                "mousemove",
                "--window",
                window_id,
                "400",
                "600",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await asyncio.create_subprocess_exec(
                "xdotool",
                "click",
                "--window",
                window_id,
                "1",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await asyncio.sleep(0.3)

            # Clear and type "continue"
            await asyncio.create_subprocess_exec(
                "xdotool",
                "key",
                "--window",
                window_id,
                "ctrl+a",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await asyncio.create_subprocess_exec(
                "xdotool",
                "type",
                "--window",
                window_id,
                "continue",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await asyncio.sleep(0.3)

            await asyncio.create_subprocess_exec(
                "xdotool",
                "key",
                "--window",
                window_id,
                "Return",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )

            return True

        except Exception as e:
            self.logger.error(f"Soft recovery failed: {e}")
            return False

    async def _hard_recovery(self, window_id: str, state: WindowState) -> bool:
        """Attempt hard recovery by restarting the process."""
        try:
            self.logger.warning(f"⚠️ Hard recovery: restarting process {state.process_id}")

            # Get process info before killing
            try:
                process = psutil.Process(state.process_id)
                cmdline = process.cmdline()
                cwd = process.cwd()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                self.logger.error("Cannot get process info for restart")
                return False

            # Kill the frozen process
            try:
                process.terminate()
                await asyncio.sleep(5)

                if process.is_running():
                    process.kill()
                    await asyncio.sleep(2)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass  # Process already dead

            # Restart VS Code
            try:
                # Extract VS Code executable and workspace from command line
                vscode_cmd = ["code"]

                # Try to preserve workspace/folder
                for i, arg in enumerate(cmdline):
                    if arg.endswith(".code-workspace") or (
                        not arg.startswith("-") and Path(arg).exists() and Path(arg).is_dir()
                    ):
                        vscode_cmd.append(arg)
                        break

                await asyncio.create_subprocess_exec(
                    *vscode_cmd,
                    cwd=cwd,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )

                # Wait for VS Code to start
                await asyncio.sleep(10)

                return True

            except Exception as e:
                self.logger.error(f"Failed to restart VS Code: {e}")
                return False

        except Exception as e:
            self.logger.error(f"Hard recovery failed: {e}")
            return False

    def get_monitoring_status(self) -> Dict:
        """Get current monitoring status."""
        current_time = time.time()

        status = {
            "monitoring": self.monitoring,
            "total_windows": len(self.window_states),
            "responsive_windows": sum(1 for s in self.window_states.values() if s.is_responsive),
            "frozen_windows": sum(1 for s in self.window_states.values() if not s.is_responsive),
            "windows": [],
        }

        for window_id, state in self.window_states.items():
            time_since_change = current_time - state.last_change_time
            status["windows"].append(
                {
                    "id": window_id,
                    "title": state.title,
                    "responsive": state.is_responsive,
                    "time_since_change": time_since_change,
                    "consecutive_freezes": state.consecutive_freezes,
                    "last_recovery": state.last_recovery_attempt,
                }
            )

        return status


async def main():
    """Test the VS Code monitor."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    monitor = VSCodeMonitor(
        freeze_threshold=60.0, recovery_cooldown=30.0
    )  # Shorter thresholds for testing

    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        await monitor.stop_monitoring()
        print("Monitoring stopped")


if __name__ == "__main__":
    asyncio.run(main())
