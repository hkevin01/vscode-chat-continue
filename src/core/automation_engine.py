"""Core automation engine for VS Code Chat Continue button clicking."""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

from core.button_finder import ButtonFinder, ButtonLocation
from core.click_automator import ClickAutomator
from core.config_manager import ConfigManager
from core.vscode_monitor import VSCodeMonitor
from core.window_detector import VSCodeWindow, WindowDetector
from core.window_focus_manager import WindowFocusManager
from utils.audio_suppressor import disable_audio_suppression, enable_audio_suppression
from utils.screen_capture import ScreenCapture

try:
    from pynput import keyboard, mouse

    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False


class AutomationEngine:
    """Main automation engine coordinates button detection and clicking."""

    def __init__(self, config_manager: ConfigManager):
        """Initialize the automation engine.

        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.running = False
        self._task: Optional[asyncio.Task] = None
        self._paused = False
        self._emergency_stop = False
        self._user_activity_detected = False
        self._last_user_activity = 0.0

        # Disable system bell to prevent beeping
        self._disable_system_bell()

        # Initialize components
        self.window_detector = WindowDetector()
        self.button_finder = ButtonFinder()
        self.click_automator = ClickAutomator(
            click_delay=config_manager.get("automation.click_delay", 0.1),
            move_duration=config_manager.get("automation.move_duration", 0.2),
        )
        self.screen_capture = ScreenCapture()
        self.focus_manager = WindowFocusManager()

        # VS Code window monitoring for freeze detection and recovery
        freeze_threshold = config_manager.get("monitoring.freeze_threshold", 600.0)  # 10 minutes
        recovery_cooldown = config_manager.get("monitoring.recovery_cooldown", 300.0)  # 5 minutes
        self.vscode_monitor = VSCodeMonitor(freeze_threshold, recovery_cooldown)
        self._monitor_task: Optional[asyncio.Task] = None

        # Performance monitoring
        self.performance_metrics = {
            "operation_times": [],
            "memory_usage": [],
            "cpu_usage": [],
            "cache_hits": 0,
            "cache_misses": 0,
        }

        # Statistics
        self.stats = {
            "windows_processed": 0,
            "buttons_found": 0,
            "clicks_attempted": 0,
            "clicks_successful": 0,
            "errors": 0,
            "start_time": None,
            "total_runtime": 0,
            "fallback_activations": 0,
            "performance_optimizations": 0,
        }

        # Safety features
        self._setup_safety_features()

        # Cache for performance optimization
        self._window_cache = {}
        cache_timeout_key = "performance.cache_timeout_seconds"
        self._cache_timeout = config_manager.get(cache_timeout_key, 30)

    def _disable_system_bell(self) -> None:
        """Disable system bell to prevent beeping during automation."""
        try:
            if self.config_manager.get("system.disable_bell", True):
                import os
                import subprocess

                # Disable terminal bell for current session
                os.system("setterm -blength 0 2>/dev/null || true")

                # Try to disable X11 bell
                subprocess.run(["xset", "b", "off"], capture_output=True, check=False)

                # Set environment variable to disable bell
                os.environ["TERM_BELL"] = "off"

                self.logger.debug("System bell disabled")
        except Exception as e:
            self.logger.debug(f"Could not disable system bell: {e}")

    def _setup_safety_features(self) -> None:
        """Set up safety features including emergency stop and monitoring."""
        if not PYNPUT_AVAILABLE:
            msg = "pynput not available - safety features disabled"
            self.logger.warning(msg)
            return

        safety_config = self.config_manager.get("safety", {})

        # Emergency stop key listener
        if safety_config.get("emergency_stop_key"):

            def on_key_press(key):
                try:
                    stop_key = safety_config["emergency_stop_key"]
                    if hasattr(key, "name") and key.name == stop_key:
                        self.emergency_stop()
                except AttributeError:
                    stop_key = safety_config["emergency_stop_key"]
                    if hasattr(key, "char") and key.char == stop_key:
                        self.emergency_stop()

            self._key_listener = keyboard.Listener(on_press=on_key_press)
            self._key_listener.start()

        # User activity monitoring
        if safety_config.get("pause_on_user_activity", True):

            def on_mouse_activity(*args):
                self._last_user_activity = time.time()
                self._user_activity_detected = True

            def on_key_activity(*args):
                self._last_user_activity = time.time()
                self._user_activity_detected = True

            self._mouse_listener = mouse.Listener(
                on_move=on_mouse_activity, on_click=on_mouse_activity, on_scroll=on_mouse_activity
            )
            self._activity_keyboard_listener = keyboard.Listener(on_press=on_key_activity)

            self._mouse_listener.start()
            self._activity_keyboard_listener.start()

    def pause(self) -> None:
        """Pause automation execution."""
        self._paused = True
        self.logger.info("Automation paused")

    def resume(self) -> None:
        """Resume automation execution."""
        self._paused = False
        self.logger.info("Automation resumed")

    def emergency_stop(self) -> None:
        """Emergency stop - immediately halt all automation."""
        self._emergency_stop = True
        self._paused = True
        self.logger.warning("EMERGENCY STOP activated")

    def is_user_activity_blocking(self) -> bool:
        """Check if user activity should block automation."""
        if not self._user_activity_detected:
            return False

        safety_config = self.config_manager.get("safety", {})
        timeout_key = "user_activity_timeout_seconds"
        activity_timeout = safety_config.get(timeout_key, 5)

        if time.time() - self._last_user_activity > activity_timeout:
            self._user_activity_detected = False
            return False

        return True

    def _should_pause_automation(self) -> bool:
        """Check if automation should be paused for safety reasons."""
        if self._emergency_stop:
            return True

        if self._paused:
            return True

        if self.is_user_activity_blocking():
            return True

        return False

    def _optimize_performance(self) -> None:
        """Apply performance optimizations."""
        # Clean old cache entries
        current_time = time.time()
        expired_keys = [
            key
            for key, (data, timestamp) in self._window_cache.items()
            if current_time - timestamp > self._cache_timeout
        ]

        for key in expired_keys:
            del self._window_cache[key]

        # Record performance optimization
        if expired_keys:
            self.stats["performance_optimizations"] += 1

    def _get_cached_windows(self) -> Optional[List[VSCodeWindow]]:
        """Get cached window list if available and fresh."""
        cache_key = "vscode_windows"
        current_time = time.time()

        if cache_key in self._window_cache:
            data, timestamp = self._window_cache[cache_key]
            if current_time - timestamp < self._cache_timeout:
                self.performance_metrics["cache_hits"] += 1
                return data

        self.performance_metrics["cache_misses"] += 1
        return None

    def _cache_windows(self, windows: List[VSCodeWindow]) -> None:
        """Cache window list with timestamp."""
        cache_key = "vscode_windows"
        self._window_cache[cache_key] = (windows, time.time())

    def get_performance_report(self) -> Dict[str, Any]:
        """Get detailed performance and statistics report."""
        current_time = time.time()
        runtime = current_time - (self.stats["start_time"] or current_time)

        return {
            "runtime_seconds": runtime,
            "statistics": self.stats.copy(),
            "performance_metrics": self.performance_metrics.copy(),
            "cache_efficiency": {
                "hit_rate": (
                    self.performance_metrics["cache_hits"]
                    / max(
                        1,
                        (
                            self.performance_metrics["cache_hits"]
                            + self.performance_metrics["cache_misses"]
                        ),
                    )
                ),
                "total_requests": (
                    self.performance_metrics["cache_hits"]
                    + self.performance_metrics["cache_misses"]
                ),
            },
            "success_rate": (
                self.stats["clicks_successful"] / max(1, self.stats["clicks_attempted"])
            ),
            "average_windows_per_cycle": (
                self.stats["windows_processed"] / max(1, self.stats.get("cycles_completed", 1))
            ),
        }

    async def start(self) -> None:
        """Start the automation engine."""
        if self.running:
            self.logger.warning("Automation engine is already running")
            return

        self.logger.info("Starting automation engine...")

        # Enable audio suppression if configured
        audio_enabled = self.config_manager.get("audio.enabled", False)
        if not audio_enabled:
            enable_audio_suppression()
            self.logger.debug("Audio suppression enabled")

        self.running = True

        # Start VS Code monitoring
        if self.config_manager.get("monitoring.enabled", True):
            self._monitor_task = asyncio.create_task(self.vscode_monitor.start_monitoring())
            self.logger.info("🔍 VS Code freeze monitoring started")

        # Create main automation task
        self._task = asyncio.create_task(self._automation_loop())

        try:
            await self._task
        except asyncio.CancelledError:
            self.logger.info("Automation task cancelled")
        except Exception as e:
            self.logger.error(f"Automation error: {e}", exc_info=True)
            raise

    async def stop(self) -> None:
        """Stop the automation engine."""
        if not self.running:
            return

        self.logger.info("Stopping automation engine...")
        self.running = False

        # Stop VS Code monitoring
        if self._monitor_task and not self._monitor_task.done():
            await self.vscode_monitor.stop_monitoring()
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
            self.logger.info("🛑 VS Code monitoring stopped")

        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _automation_loop(self) -> None:
        """Main automation loop."""
        interval = self.config_manager.get("automation.interval_seconds", 2.0)

        self.logger.info(f"Starting automation loop with {interval}s interval")

        while self.running:
            try:
                if self._should_pause_automation():
                    self.logger.info("Automation paused or stopped due to safety features")
                    await asyncio.sleep(interval)
                    continue

                # TODO: Implement actual automation logic
                await self._process_vscode_windows()
                await asyncio.sleep(interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in automation loop: {e}", exc_info=True)
                await asyncio.sleep(interval)

    async def _process_vscode_windows(self) -> None:
        """Process all VS Code windows for continue buttons."""
        try:
            # Debug mode: check if window detection should be bypassed
            debug_mode = self.config_manager.get("debug.skip_window_detection", False)
            if debug_mode:
                self.logger.info("Debug mode: skipping window detection")
                return

            # Get all VS Code windows
            self.logger.debug("Starting window detection...")
            windows = self.window_detector.get_vscode_windows()
            self.logger.info(f"Found {len(windows)} VS Code windows to process")

            if not windows:
                self.logger.debug("No VS Code windows found, skipping processing")
                return

            # Log all windows being processed
            for i, window in enumerate(windows, 1):
                self.logger.info(
                    f"Window {i}: {window.title[:50]}... " f"({window.width}x{window.height})"
                )

            self.stats["windows_processed"] += len(windows)

            # Process each window
            for window in windows:
                await self._process_window(window)

        except Exception as e:
            self.logger.error(f"Error processing VS Code windows: {e}", exc_info=True)
            self.stats["errors"] += 1

    async def _process_window(self, window: VSCodeWindow) -> None:
        """Process a single VS Code window for continue buttons.

        Args:
            window: VS Code window to process
        """
        try:
            self.logger.debug(f"Processing window: {window}")

            # Check if we should process this window
            if not self._should_process_window(window):
                self.logger.debug(f"Skipping window: {window.title}")
                return

            # Capture the window with silent error handling to prevent beeps
            screenshot = None
            try:
                screenshot = self.screen_capture.capture_window(
                    window.window_id, window.x, window.y, window.width, window.height
                )
            except Exception as capture_error:
                self.logger.debug(f"Window capture failed silently: {capture_error}")

            if not screenshot:
                # Fallback: try capturing full screen and search entire screen
                self.logger.debug(
                    f"Window capture failed for {window.title}, " f"trying full screen capture"
                )
                try:
                    screenshot = self.screen_capture.capture_screen()
                    if screenshot:
                        # Search the entire screen instead of window region
                        window_x, window_y = 0, 0
                    else:
                        self.logger.debug(f"Full screen capture also failed for: {window}")
                        return
                except Exception as screen_error:
                    self.logger.debug(f"Screen capture failed silently: {screen_error}")
                    return
            else:
                window_x, window_y = window.x, window.y

            # Find continue buttons
            self.logger.info(f"🔍 Screenshot info: {screenshot.width}x{screenshot.height}")
            if screenshot.width <= 100 and screenshot.height <= 100:
                self.logger.info("📸 Small screenshot detected - likely mock image")

            buttons = self.button_finder.find_continue_buttons(screenshot, window_x, window_y)

            self.logger.info(
                f"🎯 Found {len(buttons)} continue buttons in window: {window.title[:30]}"
            )
            if buttons:
                for i, btn in enumerate(buttons, 1):
                    self.logger.info(
                        f"   Button {i}: {btn.method} at ({btn.center_x}, {btn.center_y})"
                    )

            self.stats["buttons_found"] += len(buttons)

            # Click buttons if not in dry run mode
            if buttons:
                await self._click_buttons(buttons, window)
            else:
                # No buttons found - try chat typing fallback
                await self._try_chat_typing_fallback(window)

        except Exception as e:
            self.logger.error(f"Error processing window {window}: {e}", exc_info=True)
            self.stats["errors"] += 1

    def _should_process_window(self, window: VSCodeWindow) -> bool:
        """Check if a window should be processed.

        Args:
            window: VS Code window to check

        Returns:
            True if window should be processed
        """
        # Check minimum size requirements
        min_width = self.config_manager.get("filtering.min_window_width", 400)
        min_height = self.config_manager.get("filtering.min_window_height", 300)

        if window.width < min_width or window.height < min_height:
            return False

        # Check title filters
        title_filters = self.config_manager.get("filtering.title_exclude_patterns", [])
        title_lower = window.title.lower()

        for pattern in title_filters:
            if pattern.lower() in title_lower:
                return False

        # Check if window has chat-related content (by title)
        chat_indicators = ["chat", "copilot", "assistant"]
        has_chat_indicator = any(indicator in title_lower for indicator in chat_indicators)

        # If require chat indicator is enabled, only process windows with chat content
        if self.config_manager.get("filtering.require_chat_indicator", False):
            return has_chat_indicator

        return True

    async def _click_buttons(self, buttons: List[ButtonLocation], window: VSCodeWindow) -> None:
        """Click detected continue buttons.

        Args:
            buttons: List of button locations to click
            window: The window containing the buttons
        """
        max_clicks = self.config_manager.get("automation.max_clicks_per_window", 3)
        click_interval = self.config_manager.get("automation.click_interval", 0.5)
        auto_focus = self.config_manager.get("automation.auto_focus_windows", True)

        # Focus the window before clicking if auto_focus is enabled
        if auto_focus and not self.config_manager.is_dry_run():
            self.logger.info(f"Bringing window '{window.title}' into focus " "before clicking...")
            focus_result = self.focus_manager.focus_window(window)

            if focus_result.success:
                self.logger.info(f"Successfully focused window using " f"{focus_result.method}")
                # Give the window a moment to gain focus
                await asyncio.sleep(0.3)
            else:
                self.logger.warning(f"Failed to focus window: " f"{focus_result.error}")
                self.logger.info(
                    "Proceeding with clicks anyway - they may " "fail if window lacks focus"
                )

        # Limit number of clicks per window
        buttons_to_click = buttons[:max_clicks]

        for i, button in enumerate(buttons_to_click):
            try:
                if self.config_manager.is_dry_run():
                    self.logger.info(
                        f"DRY RUN: Would click button at "
                        f"({button.center_x}, {button.center_y}) in window "
                        f"'{window.title}' using method {button.method}"
                    )
                    continue

                self.logger.info(
                    f"Clicking continue button at "
                    f"({button.center_x}, {button.center_y}) in window "
                    f"'{window.title}'"
                )

                # Perform the click
                result = self.click_automator.click(
                    button.center_x, button.center_y, restore_position=True
                )

                self.stats["clicks_attempted"] += 1

                if result.success:
                    self.stats["clicks_successful"] += 1
                    self.logger.info(f"Successfully clicked button using " f"{result.method}")
                else:
                    self.logger.warning(f"Failed to click button: " f"{result.error}")

                # Wait between clicks
                if i < len(buttons_to_click) - 1:
                    await asyncio.sleep(click_interval)

            except Exception as e:
                self.logger.error(f"Error clicking button {button}: {e}")
                self.stats["errors"] += 1

    def get_statistics(self) -> dict:
        """Get automation statistics.

        Returns:
            Dictionary with statistics
        """
        return self.stats.copy()

    def reset_statistics(self) -> None:
        """Reset automation statistics."""
        self.stats = {
            "windows_processed": 0,
            "buttons_found": 0,
            "clicks_attempted": 0,
            "clicks_successful": 0,
            "errors": 0,
        }

    async def _try_chat_typing_fallback(self, window: VSCodeWindow) -> None:
        """Try typing 'continue' in chat field when no buttons found.

        Args:
            window: The VS Code window to try chat typing in
        """
        if self.config_manager.is_dry_run():
            self.logger.info("DRY RUN: Would try chat typing fallback")
            return

        # Check if chat typing fallback is enabled
        if not self.config_manager.get("automation.enable_chat_fallback", True):
            self.logger.debug("Chat typing fallback is disabled")
            return

        try:
            self.logger.info("🔤 No Continue buttons found - trying chat typing fallback")

            # User-specific chat field coordinates
            # X: 1725, Y: 1993 (chat typing field location)
            chat_x = 1725
            chat_y = 1993

            # Focus the window first
            auto_focus = self.config_manager.get("automation.auto_focus_windows", True)
            if auto_focus:
                self.logger.info(f"Focusing window '{window.title}' for chat typing...")
                focus_result = self.focus_manager.focus_window(window)

                if focus_result.success:
                    self.logger.info(f"Successfully focused window using {focus_result.method}")
                    await asyncio.sleep(0.3)  # Give window time to gain focus
                else:
                    self.logger.warning(f"Failed to focus window: {focus_result.error}")

            # Attempt to click chat field and type 'continue'
            self.logger.info(f"Clicking chat field at ({chat_x}, {chat_y}) and typing 'continue'")
            success = self.click_automator.click_and_type_continue(chat_x, chat_y)

            if success:
                self.logger.info("✅ Successfully typed 'continue' in chat field")
                self.stats["clicks_attempted"] += 1
                self.stats["clicks_successful"] += 1
                self.stats["fallback_activations"] += 1
            else:
                self.logger.warning("❌ Chat typing fallback failed")
                self.stats["clicks_attempted"] += 1
                self.stats["errors"] += 1

        except Exception as e:
            self.logger.error(f"Error in chat typing fallback: {e}")
            self.stats["errors"] += 1

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current VS Code monitoring status."""
        if not hasattr(self, "vscode_monitor"):
            return {"monitoring": False, "error": "Monitor not initialized"}

        return self.vscode_monitor.get_monitoring_status()

    async def trigger_manual_recovery(self, window_id: str) -> bool:
        """Manually trigger recovery for a specific window."""
        if not hasattr(self, "vscode_monitor"):
            return False

        # Find the window state
        if window_id in self.vscode_monitor.window_states:
            state = self.vscode_monitor.window_states[window_id]
            current_time = time.time()
            return await self.vscode_monitor._attempt_recovery(window_id, state, current_time)

        return False
