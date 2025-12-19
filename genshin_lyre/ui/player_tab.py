"""
Player Tab for Genshin Lyre MIDI Player.
Contains MIDI file controls, track list, and media controls.
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Pango


class PlayerTab(Gtk.Box):
    """Player tab with MIDI controls and track selection."""
    
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.app = app
        self.set_margin_top(16)
        self.set_margin_bottom(16)
        self.set_margin_start(16)
        self.set_margin_end(16)
        
        self._build_ui()
        self._update_timer_id = None
    
    def _build_ui(self):
        """Build the player UI."""
        # Now Playing section
        now_playing_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        now_playing_box.set_halign(Gtk.Align.CENTER)
        
        self.now_playing_label = Gtk.Label(label="No file loaded")
        self.now_playing_label.add_css_class('title-2')
        now_playing_box.append(self.now_playing_label)
        self.append(now_playing_box)
        
        # Track list section
        track_frame = Gtk.Frame()
        track_frame.set_label("Tracks")
        track_frame.set_vexpand(True)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(150)
        
        self.track_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.track_list.set_margin_top(8)
        self.track_list.set_margin_bottom(8)
        self.track_list.set_margin_start(8)
        self.track_list.set_margin_end(8)
        
        self.no_tracks_label = Gtk.Label(label="Load a MIDI file to see tracks")
        self.no_tracks_label.add_css_class('dim-label')
        self.track_list.append(self.no_tracks_label)
        
        scrolled.set_child(self.track_list)
        track_frame.set_child(scrolled)
        self.append(track_frame)
        
        # Timeline section
        timeline_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        
        # Time labels
        time_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.current_time_label = Gtk.Label(label="00:00")
        self.current_time_label.add_css_class('monospace')
        self.total_time_label = Gtk.Label(label="00:00")
        self.total_time_label.add_css_class('monospace')
        
        time_box.append(self.current_time_label)
        time_box.append(Gtk.Label(label=" / "))
        time_box.append(self.total_time_label)
        time_box.set_halign(Gtk.Align.CENTER)
        timeline_box.append(time_box)
        
        # Timeline slider
        self.timeline_slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.timeline_slider.set_draw_value(False)
        self.timeline_slider.set_hexpand(True)
        self.timeline_slider.connect('value-changed', self._on_timeline_changed)
        self._programmatic_update = False  # Flag to prevent feedback loop during programmatic updates
        timeline_box.append(self.timeline_slider)
        
        self.append(timeline_box)
        
        # Speed control
        speed_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        speed_box.set_halign(Gtk.Align.CENTER)
        
        speed_label = Gtk.Label(label="Speed:")
        speed_box.append(speed_label)
        
        self.speed_slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0.25, 2.0, 0.05)
        self.speed_slider.set_value(1.0)
        self.speed_slider.set_size_request(200, -1)
        self.speed_slider.set_draw_value(True)
        self.speed_slider.set_value_pos(Gtk.PositionType.RIGHT)
        self.speed_slider.connect('value-changed', self._on_speed_changed)
        speed_box.append(self.speed_slider)
        
        self.speed_label = Gtk.Label(label="1.00x")
        self.speed_label.set_size_request(50, -1)
        speed_box.append(self.speed_label)
        
        self.append(speed_box)
        
        # Media controls
        controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        controls_box.set_halign(Gtk.Align.CENTER)
        controls_box.set_margin_top(8)
        
        # Previous button
        self.prev_button = Gtk.Button()
        self.prev_button.set_icon_name('media-skip-backward-symbolic')
        self.prev_button.add_css_class('circular')
        self.prev_button.set_tooltip_text('Previous')
        self.prev_button.connect('clicked', self._on_prev_clicked)
        controls_box.append(self.prev_button)
        
        # Stop button
        self.stop_button = Gtk.Button()
        self.stop_button.set_icon_name('media-playback-stop-symbolic')
        self.stop_button.add_css_class('circular')
        self.stop_button.set_tooltip_text('Stop')
        self.stop_button.connect('clicked', self._on_stop_clicked)
        controls_box.append(self.stop_button)
        
        # Play/Pause button
        self.play_button = Gtk.Button()
        self.play_button.set_icon_name('media-playback-start-symbolic')
        self.play_button.add_css_class('circular')
        self.play_button.add_css_class('suggested-action')
        self.play_button.set_tooltip_text('Play')
        self.play_button.connect('clicked', self._on_play_clicked)
        controls_box.append(self.play_button)
        
        # Next button
        self.next_button = Gtk.Button()
        self.next_button.set_icon_name('media-skip-forward-symbolic')
        self.next_button.add_css_class('circular')
        self.next_button.set_tooltip_text('Next')
        self.next_button.connect('clicked', self._on_next_clicked)
        controls_box.append(self.next_button)
        
        self.append(controls_box)
    
    def update_tracks(self):
        """Update the track list from the MIDI player."""
        # Clear existing tracks
        while True:
            child = self.track_list.get_first_child()
            if child:
                self.track_list.remove(child)
            else:
                break
        
        player = self.app.midi_player
        
        if not player.tracks:
            self.no_tracks_label = Gtk.Label(label="Load a MIDI file to see tracks")
            self.no_tracks_label.add_css_class('dim-label')
            self.track_list.append(self.no_tracks_label)
            return
        
        for track in player.tracks:
            track_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            
            check = Gtk.CheckButton()
            check.set_active(track.enabled)
            check.connect('toggled', self._on_track_toggled, track.index)
            track_row.append(check)
            
            name_label = Gtk.Label(label=track.name)
            name_label.set_hexpand(True)
            name_label.set_xalign(0)
            name_label.set_ellipsize(Pango.EllipsizeMode.END)
            track_row.append(name_label)
            
            note_count = len(track.notes)
            count_label = Gtk.Label(label=f"({note_count} notes)")
            count_label.add_css_class('dim-label')
            track_row.append(count_label)
            
            self.track_list.append(track_row)
    
    def update_file_info(self):
        """Update file information displays."""
        player = self.app.midi_player
        
        file_name = player.get_file_name() or "No file loaded"
        self.now_playing_label.set_label(file_name)
        
        self.total_time_label.set_label(player.format_time(player.duration_ms))
        self._update_position(0)
    
    def _update_position(self, position_ms):
        """Update position display."""
        player = self.app.midi_player
        self.current_time_label.set_label(player.format_time(position_ms))
        
        if player.duration_ms > 0:
            progress = (position_ms / player.duration_ms) * 100
            # Set flag to prevent feedback loop when we programmatically update the slider
            self._programmatic_update = True
            self.timeline_slider.set_value(progress)
            self._programmatic_update = False
    
    def _on_track_toggled(self, check, track_index):
        """Handle track toggle."""
        self.app.midi_player.set_track_enabled(track_index, check.get_active())
    
    def _on_timeline_changed(self, slider):
        """Handle timeline slider change."""
        # Ignore programmatic updates to prevent feedback loop
        if self._programmatic_update:
            return
        
        player = self.app.midi_player
        if player.duration_ms > 0:
            position_ms = (slider.get_value() / 100) * player.duration_ms
            player.seek(position_ms)
            self.current_time_label.set_label(player.format_time(position_ms))
    
    def _on_speed_changed(self, slider):
        """Handle speed slider change."""
        speed = slider.get_value()
        self.speed_label.set_label(f"{speed:.2f}x")
        self.app.midi_player.set_speed(speed)
        self.app.settings.playback_speed = speed
    
    def _on_play_clicked(self, button):
        """Handle play/pause button click."""
        player = self.app.midi_player
        
        if player.is_playing:
            player.pause()
            self.play_button.set_icon_name('media-playback-start-symbolic')
            self.play_button.set_tooltip_text('Play')
        elif player.is_paused:
            player.resume()
            self.play_button.set_icon_name('media-playback-pause-symbolic')
            self.play_button.set_tooltip_text('Pause')
        else:
            player.play()
            self.play_button.set_icon_name('media-playback-pause-symbolic')
            self.play_button.set_tooltip_text('Pause')
            self._start_update_timer()
    
    def _on_stop_clicked(self, button):
        """Handle stop button click."""
        self.app.midi_player.stop()
        self.play_button.set_icon_name('media-playback-start-symbolic')
        self.play_button.set_tooltip_text('Play')
        self._stop_update_timer()
        self._update_position(0)
    
    def _on_prev_clicked(self, button):
        """Handle previous button click."""
        # Seek to beginning or previous in playlist
        self.app.midi_player.seek(0)
        self._update_position(0)
    
    def _on_next_clicked(self, button):
        """Handle next button click."""
        # Go to next in playlist (if implemented)
        pass
    
    def _start_update_timer(self):
        """Start the position update timer."""
        if self._update_timer_id is None:
            self._update_timer_id = GLib.timeout_add(100, self._timer_callback)
    
    def _stop_update_timer(self):
        """Stop the position update timer."""
        if self._update_timer_id is not None:
            GLib.source_remove(self._update_timer_id)
            self._update_timer_id = None
    
    def _timer_callback(self):
        """Timer callback for updating UI."""
        player = self.app.midi_player
        
        if player.is_playing or player.is_paused:
            self._update_position(player.current_position_ms)
            return True
        else:
            self.play_button.set_icon_name('media-playback-start-symbolic')
            self.play_button.set_tooltip_text('Play')
            self._update_timer_id = None
            return False
    
    def on_playback_finished(self):
        """Called when playback finishes."""
        GLib.idle_add(self._on_playback_finished_ui)
    
    def _on_playback_finished_ui(self):
        """UI update when playback finishes."""
        self.play_button.set_icon_name('media-playback-start-symbolic')
        self.play_button.set_tooltip_text('Play')
        self._stop_update_timer()
        self._update_position(0)
