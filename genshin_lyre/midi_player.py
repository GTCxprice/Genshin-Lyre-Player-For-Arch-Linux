"""
MIDI Player module for Genshin Impact Lyre.
Handles MIDI file parsing and playback with accurate timing.
"""

import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set

import mido

from .key_mapper import KeyMapper
from .key_sender import KeySender


@dataclass
class MidiNote:
    """Represents a single MIDI note event."""
    time_ms: float  # Time in milliseconds from start
    note: int       # MIDI note number
    velocity: int   # Note velocity
    duration_ms: float = 0  # Note duration
    track_index: int = 0  # Which track this note belongs to


@dataclass
class MidiTrack:
    """Represents a MIDI track."""
    index: int
    name: str
    notes: List[MidiNote] = field(default_factory=list)
    enabled: bool = True
    instrument: str = ""


class MidiPlayer:
    """Handles MIDI file loading and playback."""
    
    def __init__(self, key_mapper: KeyMapper, key_sender: KeySender):
        """
        Initialize the MIDI player.
        
        Args:
            key_mapper: KeyMapper instance for note-to-key conversion
            key_sender: KeySender instance for sending keypresses
        """
        self.key_mapper = key_mapper
        self.key_sender = key_sender
        
        # MIDI file data
        self.midi_file: Optional[mido.MidiFile] = None
        self.file_path: str = ""
        self.tracks: List[MidiTrack] = []
        self.all_notes: List[MidiNote] = []
        self.duration_ms: float = 0
        
        # Playback state
        self._playing = False
        self._paused = False
        self._stop_flag = False
        self._seek_requested = False  # Flag to signal the playback loop to update position
        self._current_position_ms: float = 0
        self._playback_thread: Optional[threading.Thread] = None
        self._speed: float = 1.0
        self._merge_threshold_ms: float = 50
        self._merge_enabled: bool = False
        
        # Callbacks
        self.on_position_changed: Optional[Callable[[float], None]] = None
        self.on_note_played: Optional[Callable[[MidiNote], None]] = None
        self.on_playback_finished: Optional[Callable[[], None]] = None
        self.on_playback_started: Optional[Callable[[], None]] = None
        self.on_playback_stopped: Optional[Callable[[], None]] = None
    
    def load_file(self, file_path: str) -> bool:
        """
        Load a MIDI file.
        
        Args:
            file_path: Path to the MIDI file
            
        Returns:
            True if file was loaded successfully
        """
        try:
            self.stop()
            self.midi_file = mido.MidiFile(file_path)
            self.file_path = file_path
            self._parse_tracks()
            self._current_position_ms = 0
            return True
        except Exception as e:
            print(f"Error loading MIDI file: {e}")
            return False
    
    def _parse_tracks(self) -> None:
        """Parse tracks and notes from the loaded MIDI file."""
        if not self.midi_file:
            return
        
        self.tracks = []
        self.all_notes = []
        
        ticks_per_beat = self.midi_file.ticks_per_beat
        tempo = 500000  # Default tempo (120 BPM)
        
        for track_idx, track in enumerate(self.midi_file.tracks):
            track_name = f"Track {track_idx + 1}"
            instrument = ""
            
            # Find track name and instrument
            for msg in track:
                if msg.type == 'track_name':
                    track_name = msg.name
                elif msg.type == 'program_change':
                    instrument = f"Program {msg.program}"
            
            midi_track = MidiTrack(
                index=track_idx,
                name=track_name,
                instrument=instrument
            )
            
            # Parse notes
            current_time_ticks = 0
            active_notes: Dict[int, tuple] = {}  # note -> (start_time_ms, velocity)
            
            for msg in track:
                current_time_ticks += msg.time
                
                # Update tempo if tempo change message
                if msg.type == 'set_tempo':
                    tempo = msg.tempo
                
                current_time_ms = mido.tick2second(
                    current_time_ticks, ticks_per_beat, tempo
                ) * 1000
                
                if msg.type == 'note_on' and msg.velocity > 0:
                    active_notes[msg.note] = (current_time_ms, msg.velocity)
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    if msg.note in active_notes:
                        start_time, velocity = active_notes.pop(msg.note)
                        note = MidiNote(
                            time_ms=start_time,
                            note=msg.note,
                            velocity=velocity,
                            duration_ms=current_time_ms - start_time,
                            track_index=track_idx
                        )
                        midi_track.notes.append(note)
            
            self.tracks.append(midi_track)
        
        # Calculate total duration
        self.duration_ms = self.midi_file.length * 1000
        
        # Build sorted list of all notes
        self._rebuild_all_notes()
    
    def _rebuild_all_notes(self) -> None:
        """Rebuild the all_notes list based on enabled tracks."""
        self.all_notes = []
        enabled_tracks: Set[int] = {t.index for t in self.tracks if t.enabled}
        
        for track in self.tracks:
            if track.enabled:
                self.all_notes.extend(track.notes)
        
        # Sort by time
        self.all_notes.sort(key=lambda n: n.time_ms)
        
        # Merge nearby notes if enabled
        if self._merge_enabled and self._merge_threshold_ms > 0:
            self._merge_nearby_notes()
    
    def _merge_nearby_notes(self) -> None:
        """Merge notes that are close together in time."""
        if not self.all_notes:
            return
        
        merged = []
        current_group: List[MidiNote] = [self.all_notes[0]]
        
        for note in self.all_notes[1:]:
            if note.time_ms - current_group[0].time_ms <= self._merge_threshold_ms:
                current_group.append(note)
            else:
                # Average the time of the group
                avg_time = sum(n.time_ms for n in current_group) / len(current_group)
                for n in current_group:
                    n.time_ms = avg_time
                merged.extend(current_group)
                current_group = [note]
        
        # Don't forget the last group
        if current_group:
            avg_time = sum(n.time_ms for n in current_group) / len(current_group)
            for n in current_group:
                n.time_ms = avg_time
            merged.extend(current_group)
        
        self.all_notes = merged
    
    def set_track_enabled(self, track_index: int, enabled: bool) -> None:
        """Enable or disable a track."""
        for track in self.tracks:
            if track.index == track_index:
                track.enabled = enabled
                self._rebuild_all_notes()
                break
    
    def set_speed(self, speed: float) -> None:
        """Set playback speed (0.25 to 2.0)."""
        self._speed = max(0.25, min(2.0, speed))
    
    def set_merge_enabled(self, enabled: bool, threshold_ms: float = 50) -> None:
        """Enable or disable merging of nearby notes."""
        self._merge_enabled = enabled
        self._merge_threshold_ms = threshold_ms
        self._rebuild_all_notes()
    
    def play(self) -> None:
        """Start or resume playback."""
        if self._playing:
            if self._paused:
                self._paused = False
            return
        
        if not self.all_notes:
            return
        
        self._playing = True
        self._paused = False
        self._stop_flag = False
        
        self._playback_thread = threading.Thread(target=self._playback_loop)
        self._playback_thread.daemon = True
        self._playback_thread.start()
        
        if self.on_playback_started:
            self.on_playback_started()
    
    def pause(self) -> None:
        """Pause playback."""
        if self._playing and not self._paused:
            self._paused = True
    
    def resume(self) -> None:
        """Resume playback."""
        if self._playing and self._paused:
            self._paused = False
    
    def stop(self) -> None:
        """Stop playback."""
        self._stop_flag = True
        self._playing = False
        self._paused = False
        
        if self._playback_thread and self._playback_thread.is_alive():
            self._playback_thread.join(timeout=1.0)
        
        self._current_position_ms = 0
        
        if self.on_playback_stopped:
            self.on_playback_stopped()
    
    def seek(self, position_ms: float) -> None:
        """Seek to a position in milliseconds."""
        self._current_position_ms = max(0, min(position_ms, self.duration_ms))
        self._seek_requested = True  # Signal the playback loop to update
    
    def _playback_loop(self) -> None:
        """Main playback loop running in a thread."""
        start_time = time.perf_counter()
        start_position = self._current_position_ms
        note_index = 0
        
        # Find the starting note index
        while note_index < len(self.all_notes) and \
              self.all_notes[note_index].time_ms < start_position:
            note_index += 1
        
        while not self._stop_flag and note_index < len(self.all_notes):
            if self._paused:
                # While paused, update start time to maintain position
                start_time = time.perf_counter()
                start_position = self._current_position_ms
                time.sleep(0.01)
                continue
            
            # Check if seek was requested
            if self._seek_requested:
                self._seek_requested = False
                start_time = time.perf_counter()
                start_position = self._current_position_ms
                # Re-find the note index for the new position
                note_index = 0
                while note_index < len(self.all_notes) and \
                      self.all_notes[note_index].time_ms < start_position:
                    note_index += 1
                continue
            
            # Calculate current position
            elapsed_ms = (time.perf_counter() - start_time) * 1000 * self._speed
            self._current_position_ms = start_position + elapsed_ms
            
            # Update position callback
            if self.on_position_changed:
                self.on_position_changed(self._current_position_ms)
            
            # Play all notes that should have played by now
            while note_index < len(self.all_notes) and \
                  self.all_notes[note_index].time_ms <= self._current_position_ms:
                note = self.all_notes[note_index]
                key = self.key_mapper.get_key(note.note, clamp=True)
                
                if key:
                    self.key_sender.send_key(key)
                    if self.on_note_played:
                        self.on_note_played(note)
                
                note_index += 1
            
            # Small sleep to prevent 100% CPU usage
            time.sleep(0.001)
        
        self._playing = False
        
        if not self._stop_flag and self.on_playback_finished:
            self.on_playback_finished()
    
    @property
    def is_playing(self) -> bool:
        return self._playing and not self._paused
    
    @property
    def is_paused(self) -> bool:
        return self._paused
    
    @property
    def current_position_ms(self) -> float:
        return self._current_position_ms
    
    @property
    def current_position_percent(self) -> float:
        if self.duration_ms > 0:
            return (self._current_position_ms / self.duration_ms) * 100
        return 0
    
    def get_file_name(self) -> str:
        """Get the name of the currently loaded file."""
        if self.file_path:
            return Path(self.file_path).name
        return ""
    
    @staticmethod
    def format_time(ms: float) -> str:
        """Format milliseconds as MM:SS."""
        total_seconds = int(ms / 1000)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
