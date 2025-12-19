"""
Key mapping module for Genshin Impact Lyre.
Maps MIDI notes to keyboard keys for different keyboard layouts.
"""

from typing import Optional, Dict

# Base MIDI note mappings for Genshin Lyre (3 octaves: C3-B5)
# Ported from Program.cs
BASE_NOTE_MAP = {
    # Row 1 (Lower octave: C3-B3) - zxcvbnm
    48: 0, 50: 1, 52: 2, 53: 3, 55: 4, 57: 5, 59: 6,
    # Row 2 (Middle octave: C4-B4) - asdfghj  
    60: 7, 62: 8, 64: 9, 65: 10, 67: 11, 69: 12, 71: 13,
    # Row 3 (Upper octave: C5-B5) - qwertyu
    72: 14, 74: 15, 76: 16, 77: 17, 79: 18, 81: 19, 83: 20,
}

# Keyboard layouts - index corresponds to BASE_NOTE_MAP values
KEYBOARD_LAYOUTS = {
    'QWERTY': [
        'z', 'x', 'c', 'v', 'b', 'n', 'm',  # Row 1
        'a', 's', 'd', 'f', 'g', 'h', 'j',  # Row 2
        'q', 'w', 'e', 'r', 't', 'y', 'u',  # Row 3
    ],
    'QWERTZ': [
        'y', 'x', 'c', 'v', 'b', 'n', 'm',  # Row 1
        'a', 's', 'd', 'f', 'g', 'h', 'j',  # Row 2
        'q', 'w', 'e', 'r', 't', 'z', 'u',  # Row 3
    ],
    'AZERTY': [
        'w', 'x', 'c', 'v', 'b', 'n', 'comma',  # Row 1
        'q', 's', 'd', 'f', 'g', 'h', 'j',      # Row 2
        'a', 'z', 'e', 'r', 't', 'y', 'u',      # Row 3
    ],
    'DVORAK': [
        'semicolon', 'q', 'j', 'k', 'x', 'b', 'm',  # Row 1
        'a', 'o', 'e', 'u', 'i', 'd', 'h',          # Row 2
        'apostrophe', 'comma', 'period', 'p', 'y', 'f', 'g',  # Row 3
    ],
}

# Note names for UI display
NOTE_NAMES = [
    'C3', 'D3', 'E3', 'F3', 'G3', 'A3', 'B3',  # Row 1
    'C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4',  # Row 2
    'C5', 'D5', 'E5', 'F5', 'G5', 'A5', 'B5',  # Row 3
]

# All valid MIDI notes for the lyre
VALID_MIDI_NOTES = set(BASE_NOTE_MAP.keys())
MIN_MIDI_NOTE = min(VALID_MIDI_NOTES)
MAX_MIDI_NOTE = max(VALID_MIDI_NOTES)


class KeyMapper:
    """Maps MIDI notes to keyboard keys with transposition and layout support."""
    
    def __init__(self, layout: str = 'QWERTY', transpose: int = 0):
        """
        Initialize the key mapper.
        
        Args:
            layout: Keyboard layout name (QWERTY, QWERTZ, AZERTY, DVORAK)
            transpose: Number of semitones to transpose (-12 to +12)
        """
        self.layout = layout if layout in KEYBOARD_LAYOUTS else 'QWERTY'
        self.transpose = max(-12, min(12, transpose))
        self._build_note_map()
    
    def _build_note_map(self) -> None:
        """Build the note-to-key mapping based on current settings."""
        keys = KEYBOARD_LAYOUTS[self.layout]
        self._note_map: Dict[int, str] = {}
        
        for midi_note, key_index in BASE_NOTE_MAP.items():
            # Apply transposition
            transposed_note = midi_note - self.transpose
            self._note_map[transposed_note] = keys[key_index]
    
    def set_layout(self, layout: str) -> None:
        """Change the keyboard layout."""
        if layout in KEYBOARD_LAYOUTS:
            self.layout = layout
            self._build_note_map()
    
    def set_transpose(self, transpose: int) -> None:
        """Change the transposition amount."""
        self.transpose = max(-12, min(12, transpose))
        self._build_note_map()
    
    def get_key(self, midi_note: int, clamp: bool = False) -> Optional[str]:
        """
        Get the keyboard key for a MIDI note.
        
        Args:
            midi_note: MIDI note number
            clamp: If True, clamp out-of-range notes to valid range
            
        Returns:
            Key string or None if note is out of range
        """
        if midi_note in self._note_map:
            return self._note_map[midi_note]
        
        if clamp:
            # Find the closest valid note
            while midi_note > MAX_MIDI_NOTE + self.transpose:
                midi_note -= 12
            while midi_note < MIN_MIDI_NOTE + self.transpose:
                midi_note += 12
            return self._note_map.get(midi_note)
        
        return None
    
    def get_all_keys(self) -> list:
        """Get all keys in the current layout."""
        return KEYBOARD_LAYOUTS[self.layout].copy()
    
    def get_key_for_index(self, index: int) -> str:
        """Get the key at a specific index (0-20)."""
        keys = KEYBOARD_LAYOUTS[self.layout]
        if 0 <= index < len(keys):
            return keys[index]
        return ''
    
    def get_note_name(self, index: int) -> str:
        """Get the note name for a key index."""
        if 0 <= index < len(NOTE_NAMES):
            return NOTE_NAMES[index]
        return ''
    
    @staticmethod
    def get_available_layouts() -> list:
        """Get list of available keyboard layouts."""
        return list(KEYBOARD_LAYOUTS.keys())
