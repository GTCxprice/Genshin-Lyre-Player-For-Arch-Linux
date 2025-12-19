"""
Auto Key Smash Tab for Genshin Lyre MIDI Player.
Provides automated key spamming functionality.
"""

import random
import threading
import time

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib


class KeySmashTab(Gtk.Box):
    """Auto Key Smash tab with key selection and speed controls."""
    
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.app = app
        self.set_margin_top(16)
        self.set_margin_bottom(16)
        self.set_margin_start(16)
        self.set_margin_end(16)
        
        self._running = False
        self._thread = None
        self._selected_keys = set(range(21))  # All keys by default
        
        self._build_ui()
        self._load_settings()
    
    def _build_ui(self):
        """Build the key smash UI."""
        # Title
        title = Gtk.Label(label="Auto Key Smash")
        title.add_css_class('title-1')
        self.append(title)
        
        description = Gtk.Label(label="Automatically press lyre keys at high speed")
        description.add_css_class('dim-label')
        self.append(description)
        
        # Key Selection Grid
        key_frame = Gtk.Frame()
        key_frame.set_label("Select Keys to Smash")
        
        key_grid_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        key_grid_box.set_margin_top(12)
        key_grid_box.set_margin_bottom(12)
        key_grid_box.set_margin_start(12)
        key_grid_box.set_margin_end(12)
        
        # Key toggle buttons arranged in 3 rows like the lyre
        self.key_buttons = []
        
        # Row labels and keys
        rows = [
            ("Upper (C5-B5)", ['Q', 'W', 'E', 'R', 'T', 'Y', 'U'], range(14, 21)),
            ("Middle (C4-B4)", ['A', 'S', 'D', 'F', 'G', 'H', 'J'], range(7, 14)),
            ("Lower (C3-B3)", ['Z', 'X', 'C', 'V', 'B', 'N', 'M'], range(0, 7)),
        ]
        
        for row_name, key_labels, indices in rows:
            row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            
            row_label = Gtk.Label(label=row_name)
            row_label.set_size_request(100, -1)
            row_label.set_xalign(0)
            row_box.append(row_label)
            
            for i, (label, idx) in enumerate(zip(key_labels, indices)):
                btn = Gtk.ToggleButton(label=label)
                btn.set_active(True)
                btn.set_size_request(45, 45)
                btn.connect('toggled', self._on_key_toggled, idx)
                btn.add_css_class('circular')
                row_box.append(btn)
                self.key_buttons.append((idx, btn))
            
            key_grid_box.append(row_box)
        
        # Quick select buttons
        quick_select_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        quick_select_box.set_halign(Gtk.Align.CENTER)
        quick_select_box.set_margin_top(8)
        
        all_btn = Gtk.Button(label="All")
        all_btn.connect('clicked', self._on_select_all)
        quick_select_box.append(all_btn)
        
        none_btn = Gtk.Button(label="None")
        none_btn.connect('clicked', self._on_select_none)
        quick_select_box.append(none_btn)
        
        upper_btn = Gtk.Button(label="Upper Row")
        upper_btn.connect('clicked', lambda b: self._select_row(range(14, 21)))
        quick_select_box.append(upper_btn)
        
        middle_btn = Gtk.Button(label="Middle Row")
        middle_btn.connect('clicked', lambda b: self._select_row(range(7, 14)))
        quick_select_box.append(middle_btn)
        
        lower_btn = Gtk.Button(label="Lower Row")
        lower_btn.connect('clicked', lambda b: self._select_row(range(0, 7)))
        quick_select_box.append(lower_btn)
        
        key_grid_box.append(quick_select_box)
        key_frame.set_child(key_grid_box)
        self.append(key_frame)
        
        # Speed Control
        speed_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        speed_box.set_halign(Gtk.Align.CENTER)
        
        speed_label = Gtk.Label(label="Speed (keys/second):")
        speed_box.append(speed_label)
        
        self.speed_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, 50, 1)
        self.speed_scale.set_value(10)
        self.speed_scale.set_size_request(200, -1)
        self.speed_scale.set_draw_value(True)
        self.speed_scale.connect('value-changed', self._on_speed_changed)
        speed_box.append(self.speed_scale)
        
        self.append(speed_box)
        
        # Mode Selection
        mode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        mode_box.set_halign(Gtk.Align.CENTER)
        
        mode_label = Gtk.Label(label="Mode:")
        mode_box.append(mode_label)
        
        self.mode_dropdown = Gtk.DropDown.new_from_strings([
            "Sequential",
            "Random",
            "Chord (all at once)"
        ])
        self.mode_dropdown.set_selected(1)  # Random by default
        self.mode_dropdown.connect('notify::selected', self._on_mode_changed)
        mode_box.append(self.mode_dropdown)
        
        self.append(mode_box)
        
        # Start/Stop Button
        button_box = Gtk.Box()
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.set_margin_top(16)
        
        self.start_button = Gtk.Button(label="Start Smashing")
        self.start_button.set_size_request(200, 60)
        self.start_button.add_css_class('suggested-action')
        self.start_button.add_css_class('pill')
        self.start_button.connect('clicked', self._on_start_clicked)
        button_box.append(self.start_button)
        
        self.append(button_box)
        
        # Status label
        self.status_label = Gtk.Label(label="Ready")
        self.status_label.add_css_class('dim-label')
        self.append(self.status_label)
        
        # Spacer
        spacer = Gtk.Box()
        spacer.set_vexpand(True)
        self.append(spacer)
        
        # Warning
        warning = Gtk.Label(label="⚠️ Make sure Genshin Impact is focused before starting!")
        warning.add_css_class('warning')
        self.append(warning)
    
    def _load_settings(self):
        """Load settings from storage."""
        settings = self.app.settings
        
        # Speed
        speed = settings.get('keysmash_speed', 10)
        self.speed_scale.set_value(speed)
        
        # Mode
        modes = ['sequential', 'random', 'chord']
        mode = settings.get('keysmash_mode', 'random')
        try:
            mode_idx = modes.index(mode)
            self.mode_dropdown.set_selected(mode_idx)
        except ValueError:
            self.mode_dropdown.set_selected(1)
        
        # Selected keys
        selected = settings.get('keysmash_keys', list(range(21)))
        self._selected_keys = set(selected)
        for idx, btn in self.key_buttons:
            btn.set_active(idx in self._selected_keys)
    
    def _save_selected_keys(self):
        """Save selected keys to settings."""
        self.app.settings.set('keysmash_keys', list(self._selected_keys))
    
    def _on_key_toggled(self, button, key_index):
        """Handle key toggle."""
        if button.get_active():
            self._selected_keys.add(key_index)
        else:
            self._selected_keys.discard(key_index)
        self._save_selected_keys()
    
    def _on_select_all(self, button):
        """Select all keys."""
        self._selected_keys = set(range(21))
        for idx, btn in self.key_buttons:
            btn.set_active(True)
        self._save_selected_keys()
    
    def _on_select_none(self, button):
        """Deselect all keys."""
        self._selected_keys = set()
        for idx, btn in self.key_buttons:
            btn.set_active(False)
        self._save_selected_keys()
    
    def _select_row(self, indices):
        """Select only keys in a specific row."""
        self._selected_keys = set(indices)
        for idx, btn in self.key_buttons:
            btn.set_active(idx in indices)
        self._save_selected_keys()
    
    def _on_speed_changed(self, scale):
        """Handle speed change."""
        speed = int(scale.get_value())
        self.app.settings.set('keysmash_speed', speed)
    
    def _on_mode_changed(self, dropdown, param):
        """Handle mode change."""
        modes = ['sequential', 'random', 'chord']
        selected = dropdown.get_selected()
        if 0 <= selected < len(modes):
            self.app.settings.set('keysmash_mode', modes[selected])
    
    def _on_start_clicked(self, button):
        """Handle start/stop button click."""
        if self._running:
            self._stop()
        else:
            self._start()
    
    def _start(self):
        """Start key smashing."""
        if not self._selected_keys:
            self.status_label.set_label("No keys selected!")
            return
        
        self._running = True
        self.start_button.set_label("Stop Smashing")
        self.start_button.remove_css_class('suggested-action')
        self.start_button.add_css_class('destructive-action')
        self.status_label.set_label("Smashing keys...")
        
        self._thread = threading.Thread(target=self._smash_loop)
        self._thread.daemon = True
        self._thread.start()
    
    def _stop(self):
        """Stop key smashing."""
        self._running = False
        
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        
        GLib.idle_add(self._update_ui_stopped)
    
    def _update_ui_stopped(self):
        """Update UI when stopped."""
        self.start_button.set_label("Start Smashing")
        self.start_button.remove_css_class('destructive-action')
        self.start_button.add_css_class('suggested-action')
        self.status_label.set_label("Ready")
    
    def _smash_loop(self):
        """Main key smashing loop."""
        key_mapper = self.app.key_mapper
        key_sender = self.app.key_sender
        
        keys = [key_mapper.get_key_for_index(i) for i in sorted(self._selected_keys)]
        keys = [k for k in keys if k]  # Filter out empty keys
        
        if not keys:
            GLib.idle_add(self._stop)
            return
        
        speed = int(self.speed_scale.get_value())
        delay = 1.0 / speed if speed > 0 else 0.1
        
        modes = ['sequential', 'random', 'chord']
        mode = modes[self.mode_dropdown.get_selected()]
        
        key_index = 0
        
        while self._running:
            if mode == 'sequential':
                key = keys[key_index]
                key_sender.send_key(key)
                key_index = (key_index + 1) % len(keys)
            
            elif mode == 'random':
                key = random.choice(keys)
                key_sender.send_key(key)
            
            elif mode == 'chord':
                # Send all keys at once
                for key in keys:
                    key_sender.send_key(key)
            
            time.sleep(delay)
        
        GLib.idle_add(self._update_ui_stopped)
