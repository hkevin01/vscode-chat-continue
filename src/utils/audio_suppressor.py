#!/usr/bin/env python3
"""
Audio and beep suppression utility for VS Code Chat Continue automation.
This module provides functionality to disable system beeps and audio feedback.
"""

import logging
import os
import subprocess
import sys
from typing import Optional


class AudioSuppressor:
    """Utility class to suppress audio and beeps during automation."""
    
    def __init__(self):
        """Initialize the audio suppressor."""
        self.logger = logging.getLogger(__name__)
        self.original_bell_setting: Optional[str] = None
        self.suppression_active = False
    
    def suppress_system_beeps(self) -> bool:
        """Suppress system beeps and audio notifications.
        
        Returns:
            True if suppression was successful, False otherwise
        """
        try:
            # Disable terminal bell
            self._disable_terminal_bell()
            
            # Set environment variables to suppress audio
            self._set_audio_env_vars()
            
            # Try to disable PCM speaker if on Linux
            if sys.platform.startswith('linux'):
                self._disable_pc_speaker()
            
            self.suppression_active = True
            self.logger.debug("System beep suppression activated")
            return True
            
        except Exception as e:
            self.logger.warning(f"Could not fully suppress system beeps: {e}")
            return False
    
    def restore_audio(self) -> bool:
        """Restore original audio settings.
        
        Returns:
            True if restoration was successful, False otherwise
        """
        try:
            if self.original_bell_setting is not None:
                subprocess.run(['setterm', '-bell', self.original_bell_setting], 
                             capture_output=True, check=False)
            
            # Remove suppression environment variables
            env_vars = [
                'PYGAME_HIDE_SUPPORT_PROMPT',
                'SDL_AUDIODRIVER',
                'ALSA_CARD',
                'PULSE_RUNTIME_PATH'
            ]
            
            for var in env_vars:
                if var in os.environ:
                    del os.environ[var]
            
            self.suppression_active = False
            self.logger.debug("Audio settings restored")
            return True
            
        except Exception as e:
            self.logger.warning(f"Could not restore audio settings: {e}")
            return False
    
    def _disable_terminal_bell(self) -> None:
        """Disable terminal bell/beep."""
        try:
            # Save current setting
            result = subprocess.run(['stty', '-a'], capture_output=True, text=True)
            if result.returncode == 0 and 'bel' in result.stdout:
                self.original_bell_setting = 'on'
            else:
                self.original_bell_setting = 'off'
            
            # Disable bell
            subprocess.run(['stty', '-echo', '-g'], capture_output=True, check=False)
            subprocess.run(['setterm', '-bell', 'off'], capture_output=True, check=False)
            
        except Exception as e:
            self.logger.debug(f"Could not disable terminal bell: {e}")
    
    def _set_audio_env_vars(self) -> None:
        """Set environment variables to suppress audio."""
        # Pygame audio suppression
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
        
        # SDL audio driver - set to dummy to disable audio
        os.environ['SDL_AUDIODRIVER'] = 'dummy'
        
        # ALSA suppression (Linux)
        if sys.platform.startswith('linux'):
            os.environ['ALSA_CARD'] = '/dev/null'
            # Disable PulseAudio for this process
            os.environ['PULSE_RUNTIME_PATH'] = '/dev/null'
    
    def _disable_pc_speaker(self) -> None:
        """Disable PC speaker on Linux systems."""
        try:
            # Try to blacklist pcspkr module (requires sudo, so may fail)
            pcspkr_blacklist = '/etc/modprobe.d/blacklist-pcspkr.conf'
            if not os.path.exists(pcspkr_blacklist):
                self.logger.debug("PC speaker module blacklist not found (normal for user-level operation)")
            
            # Try to unload the module if it's loaded (may require sudo)
            result = subprocess.run(['lsmod'], capture_output=True, text=True)
            if result.returncode == 0 and 'pcspkr' in result.stdout:
                # Module is loaded, try to remove (will likely fail without sudo)
                subprocess.run(['rmmod', 'pcspkr'], capture_output=True, check=False)
                
        except Exception as e:
            self.logger.debug(f"Could not disable PC speaker (normal for user operation): {e}")
    
    def __enter__(self):
        """Context manager entry."""
        self.suppress_system_beeps()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.restore_audio()


# Global instance for easy access
_global_suppressor: Optional[AudioSuppressor] = None


def enable_audio_suppression() -> bool:
    """Enable global audio suppression.
    
    Returns:
        True if suppression was successful, False otherwise
    """
    global _global_suppressor
    
    if _global_suppressor is None:
        _global_suppressor = AudioSuppressor()
    
    return _global_suppressor.suppress_system_beeps()


def disable_audio_suppression() -> bool:
    """Disable global audio suppression and restore settings.
    
    Returns:
        True if restoration was successful, False otherwise
    """
    global _global_suppressor
    
    if _global_suppressor is not None:
        result = _global_suppressor.restore_audio()
        _global_suppressor = None
        return result
    
    return True


def is_audio_suppressed() -> bool:
    """Check if audio suppression is currently active.
    
    Returns:
        True if audio is suppressed, False otherwise
    """
    global _global_suppressor
    return _global_suppressor is not None and _global_suppressor.suppression_active


# Context manager for temporary suppression
def suppress_audio():
    """Context manager for temporary audio suppression.
    
    Usage:
        with suppress_audio():
            # Audio is suppressed in this block
            automation_code()
    """
    return AudioSuppressor()
