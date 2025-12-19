"""
Settings module for Genshin Lyre MIDI Player.
Handles persistent settings storage using JSON.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List


class Settings:
    """Manages application settings with JSON persistence."""
    
    DEFAULT_SETTINGS = {
        'keyboard_layout': 'QWERTY',
        'transpose': 0,
        'merge_nearby_notes': False,
        'merge_threshold_ms': 50,
        'hold_notes': False,
        'theme': 'dark',
        'auto_focus_genshin': True,
        'playback_speed': 1.0,
        'volume': 1.0,
        'last_directory': '',
        'window_width': 900,
        'window_height': 600,
        'history': [],
        'playlist': [],
        'keysmash_keys': list(range(21)),  # All keys selected by default
        'keysmash_speed': 10,  # Keys per second
        'keysmash_mode': 'sequential',  # sequential, random, chord
    }
    
    def __init__(self, config_path: str = None):
        """
        Initialize settings.
        
        Args:
            config_path: Path to config file. Defaults to ~/.config/genshin-lyre/settings.json
        """
        if config_path is None:
            config_dir = Path.home() / '.config' / 'genshin-lyre'
            config_dir.mkdir(parents=True, exist_ok=True)
            self.config_path = config_dir / 'settings.json'
        else:
            self.config_path = Path(config_path)
        
        self._settings: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """Load settings from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults to handle new settings
                    self._settings = {**self.DEFAULT_SETTINGS, **loaded}
            else:
                self._settings = self.DEFAULT_SETTINGS.copy()
        except (json.JSONDecodeError, IOError):
            self._settings = self.DEFAULT_SETTINGS.copy()
    
    def save(self) -> None:
        """Save settings to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self._settings, f, indent=2)
        except IOError as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self._settings.get(key, default)
    
    def set(self, key: str, value: Any, auto_save: bool = True) -> None:
        """Set a setting value."""
        self._settings[key] = value
        if auto_save:
            self.save()
    
    def reset(self) -> None:
        """Reset all settings to defaults."""
        self._settings = self.DEFAULT_SETTINGS.copy()
        self.save()
    
    # Convenience properties for common settings
    @property
    def keyboard_layout(self) -> str:
        return self.get('keyboard_layout', 'QWERTY')
    
    @keyboard_layout.setter
    def keyboard_layout(self, value: str):
        self.set('keyboard_layout', value)
    
    @property
    def transpose(self) -> int:
        return self.get('transpose', 0)
    
    @transpose.setter
    def transpose(self, value: int):
        self.set('transpose', max(-12, min(12, value)))
    
    @property
    def merge_nearby_notes(self) -> bool:
        return self.get('merge_nearby_notes', False)
    
    @merge_nearby_notes.setter
    def merge_nearby_notes(self, value: bool):
        self.set('merge_nearby_notes', value)
    
    @property
    def theme(self) -> str:
        return self.get('theme', 'dark')
    
    @theme.setter
    def theme(self, value: str):
        self.set('theme', value)
    
    @property
    def playback_speed(self) -> float:
        return self.get('playback_speed', 1.0)
    
    @playback_speed.setter
    def playback_speed(self, value: float):
        self.set('playback_speed', max(0.25, min(2.0, value)))
    
    # History management
    def add_to_history(self, file_path: str) -> None:
        """Add a file to history."""
        history = self.get('history', [])
        # Remove if already exists (to move to front)
        if file_path in history:
            history.remove(file_path)
        # Add to front
        history.insert(0, file_path)
        # Keep only last 20 items
        self.set('history', history[:20])
    
    def get_history(self) -> List[str]:
        """Get file history."""
        return self.get('history', [])
    
    def clear_history(self) -> None:
        """Clear file history."""
        self.set('history', [])
    
    # Playlist management
    def set_playlist(self, files: List[str]) -> None:
        """Set the playlist."""
        self.set('playlist', files)
    
    def get_playlist(self) -> List[str]:
        """Get the playlist."""
        return self.get('playlist', [])
    
    def add_to_playlist(self, file_path: str) -> None:
        """Add a file to the playlist."""
        playlist = self.get_playlist()
        if file_path not in playlist:
            playlist.append(file_path)
            self.set('playlist', playlist)
    
    def remove_from_playlist(self, file_path: str) -> None:
        """Remove a file from the playlist."""
        playlist = self.get_playlist()
        if file_path in playlist:
            playlist.remove(file_path)
            self.set('playlist', playlist)
