"""Core automation engine for VS Code Chat Continue button clicking."""

import asyncio
import logging
from typing import List, Optional

from core.button_finder import ButtonFinder, ButtonLocation
from core.click_automator import ClickAutomator, ClickResult
from core.config_manager import ConfigManager
from core.window_detector import VSCodeWindow, WindowDetector
from utils.screen_capture import ScreenCapture


class AutomationEngine:
    """Main automation engine that coordinates button detection and clicking."""
    
    def __init__(self, config_manager: ConfigManager):
        """Initialize the automation engine.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.running = False
        self._task: Optional[asyncio.Task] = None
        
        # Initialize components
        self.window_detector = WindowDetector()
        self.button_finder = ButtonFinder()
        self.click_automator = ClickAutomator(
            click_delay=config_manager.get('automation.click_delay', 0.1),
            move_duration=config_manager.get('automation.move_duration', 0.2)
        )
        self.screen_capture = ScreenCapture()
        
        # Statistics
        self.stats = {
            'windows_processed': 0,
            'buttons_found': 0,
            'clicks_attempted': 0,
            'clicks_successful': 0,
            'errors': 0
        }
    
    async def start(self) -> None:
        """Start the automation engine."""
        if self.running:
            self.logger.warning("Automation engine is already running")
            return
        
        self.logger.info("Starting automation engine...")
        self.running = True
        
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
        
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _automation_loop(self) -> None:
        """Main automation loop."""
        interval = self.config_manager.get('automation.interval_seconds', 2.0)
        
        self.logger.info(f"Starting automation loop with {interval}s interval")
        
        while self.running:
            try:
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
            # Get all VS Code windows
            windows = self.window_detector.get_vscode_windows()
            self.logger.debug(f"Found {len(windows)} VS Code windows")
            
            if not windows:
                return
            
            self.stats['windows_processed'] += len(windows)
            
            # Process each window
            for window in windows:
                await self._process_window(window)
                
        except Exception as e:
            self.logger.error(f"Error processing VS Code windows: {e}", exc_info=True)
            self.stats['errors'] += 1
    
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
            
            # Capture the window
            screenshot = self.screen_capture.capture_window(
                window.window_id, window.x, window.y, window.width, window.height
            )
            
            if not screenshot:
                self.logger.warning(f"Failed to capture window: {window}")
                return
            
            # Find continue buttons
            buttons = self.button_finder.find_continue_buttons(
                screenshot, window.x, window.y
            )
            
            self.logger.debug(f"Found {len(buttons)} continue buttons in window")
            self.stats['buttons_found'] += len(buttons)
            
            # Click buttons if not in dry run mode
            if buttons:
                await self._click_buttons(buttons, window)
                
        except Exception as e:
            self.logger.error(f"Error processing window {window}: {e}", exc_info=True)
            self.stats['errors'] += 1
    
    def _should_process_window(self, window: VSCodeWindow) -> bool:
        """Check if a window should be processed.
        
        Args:
            window: VS Code window to check
            
        Returns:
            True if window should be processed
        """
        # Check minimum size requirements
        min_width = self.config_manager.get('filtering.min_window_width', 400)
        min_height = self.config_manager.get('filtering.min_window_height', 300)
        
        if window.width < min_width or window.height < min_height:
            return False
        
        # Check title filters
        title_filters = self.config_manager.get('filtering.title_exclude_patterns', [])
        title_lower = window.title.lower()
        
        for pattern in title_filters:
            if pattern.lower() in title_lower:
                return False
        
        # Check if window has chat-related content (by title)
        chat_indicators = ['chat', 'copilot', 'assistant']
        has_chat_indicator = any(indicator in title_lower for indicator in chat_indicators)
        
        # If require chat indicator is enabled, only process windows with chat content
        if self.config_manager.get('filtering.require_chat_indicator', False):
            return has_chat_indicator
        
        return True
    
    async def _click_buttons(self, buttons: List[ButtonLocation], window: VSCodeWindow) -> None:
        """Click detected continue buttons.
        
        Args:
            buttons: List of button locations to click
            window: The window containing the buttons
        """
        max_clicks = self.config_manager.get('automation.max_clicks_per_window', 3)
        click_interval = self.config_manager.get('automation.click_interval', 0.5)
        
        # Limit number of clicks per window
        buttons_to_click = buttons[:max_clicks]
        
        for i, button in enumerate(buttons_to_click):
            try:
                if self.config_manager.is_dry_run():
                    self.logger.info(f"DRY RUN: Would click button at ({button.center_x}, {button.center_y}) "
                                   f"in window '{window.title}' using method {button.method}")
                    continue
                
                self.logger.info(f"Clicking continue button at ({button.center_x}, {button.center_y}) "
                               f"in window '{window.title}'")
                
                # Perform the click
                result = self.click_automator.click(
                    button.center_x, 
                    button.center_y,
                    restore_position=True
                )
                
                self.stats['clicks_attempted'] += 1
                
                if result.success:
                    self.stats['clicks_successful'] += 1
                    self.logger.info(f"Successfully clicked button using {result.method}")
                else:
                    self.logger.warning(f"Failed to click button: {result.error}")
                
                # Wait between clicks
                if i < len(buttons_to_click) - 1:
                    await asyncio.sleep(click_interval)
                    
            except Exception as e:
                self.logger.error(f"Error clicking button {button}: {e}")
                self.stats['errors'] += 1
    
    def get_statistics(self) -> dict:
        """Get automation statistics.
        
        Returns:
            Dictionary with statistics
        """
        return self.stats.copy()
    
    def reset_statistics(self) -> None:
        """Reset automation statistics."""
        self.stats = {
            'windows_processed': 0,
            'buttons_found': 0,
            'clicks_attempted': 0,
            'clicks_successful': 0,
            'errors': 0
        }
