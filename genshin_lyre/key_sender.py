"""
Key sender module for Genshin Impact Lyre.
Sends keyboard input using xdotool.
"""

import subprocess
import threading
from typing import Optional


class KeySender:
    """Sends keyboard input using xdotool."""
    
    def __init__(self):
        """Initialize the key sender."""
        self._enabled = True
        self._lock = threading.Lock()
    
    def send_key(self, key: str) -> bool:
        """
        Send a key press using xdotool.
        
        Args:
            key: Key to send (e.g., 'a', 'q', 'z')
            
        Returns:
            True if key was sent successfully
        """
        if not self._enabled or not key:
            return False
        
        try:
            subprocess.Popen(
                ['xdotool', 'key', '--clearmodifiers', key],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except FileNotFoundError:
            print("Error: xdotool not found. Please install it: sudo apt install xdotool")
            return False
        except Exception as e:
            print(f"Error sending key: {e}")
            return False
    
    def send_keys(self, keys: list) -> bool:
        """
        Send multiple keys simultaneously (chord).
        
        Args:
            keys: List of keys to send together
            
        Returns:
            True if keys were sent successfully
        """
        if not self._enabled or not keys:
            return False
        
        # For chords, send all keys at once
        key_str = '+'.join(keys)
        return self.send_key(key_str)
    
    def enable(self) -> None:
        """Enable key sending."""
        self._enabled = True
    
    def disable(self) -> None:
        """Disable key sending."""
        self._enabled = False
    
    @property
    def enabled(self) -> bool:
        """Check if key sending is enabled."""
        return self._enabled
    
    @staticmethod
    def check_xdotool() -> bool:
        """Check if xdotool is available on the system."""
        try:
            result = subprocess.run(
                ['which', 'xdotool'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def get_active_window() -> Optional[str]:
        """Get the name of the currently active window."""
        try:
            result = subprocess.run(
                ['xdotool', 'getactivewindow', 'getwindowname'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None
    
    @staticmethod
    def is_genshin_focused() -> bool:
        """Check if Genshin Impact is the active window."""
        window_name = KeySender.get_active_window()
        if window_name:
            # Common window titles for Genshin Impact
            genshin_titles = ['genshin impact', 'genshin', '原神']
            return any(title in window_name.lower() for title in genshin_titles)
        return False
