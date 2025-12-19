"""
Settings Tab for Genshin Lyre MIDI Player.
Contains configuration options for playback and display.
"""

import gi
import webbrowser
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Adw, Gio

from ..key_mapper import KeyMapper


class SettingsTab(Gtk.Box):
    """Settings tab with configuration options."""
    
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.app = app
        self.set_margin_top(16)
        self.set_margin_bottom(16)
        self.set_margin_start(16)
        self.set_margin_end(16)
        
        self._build_ui()
        self._load_settings()
    
    def _build_ui(self):
        """Build the settings UI."""
        # Keyboard Settings Group
        keyboard_group = self._create_group("Keyboard Settings")
        
        # Keyboard Layout
        layout_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        layout_label = Gtk.Label(label="Keyboard Layout")
        layout_label.set_hexpand(True)
        layout_label.set_xalign(0)
        layout_row.append(layout_label)
        
        self.layout_dropdown = Gtk.DropDown.new_from_strings(
            KeyMapper.get_available_layouts()
        )
        self.layout_dropdown.connect('notify::selected', self._on_layout_changed)
        layout_row.append(self.layout_dropdown)
        keyboard_group.append(layout_row)
        
        # Transpose
        transpose_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        transpose_label = Gtk.Label(label="Transpose (semitones)")
        transpose_label.set_hexpand(True)
        transpose_label.set_xalign(0)
        transpose_row.append(transpose_label)
        
        self.transpose_spin = Gtk.SpinButton.new_with_range(-12, 12, 1)
        self.transpose_spin.set_value(0)
        self.transpose_spin.connect('value-changed', self._on_transpose_changed)
        transpose_row.append(self.transpose_spin)
        keyboard_group.append(transpose_row)
        
        self.append(keyboard_group)
        
        # Playback Settings Group
        playback_group = self._create_group("Playback Settings")
        
        # Merge Nearby Notes
        merge_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        merge_label = Gtk.Label(label="Merge Nearby Notes")
        merge_label.set_hexpand(True)
        merge_label.set_xalign(0)
        merge_row.append(merge_label)
        
        self.merge_switch = Gtk.Switch()
        self.merge_switch.set_valign(Gtk.Align.CENTER)
        self.merge_switch.connect('notify::active', self._on_merge_changed)
        merge_row.append(self.merge_switch)
        playback_group.append(merge_row)
        
        # Merge Threshold
        threshold_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        threshold_label = Gtk.Label(label="Merge Threshold (ms)")
        threshold_label.set_hexpand(True)
        threshold_label.set_xalign(0)
        threshold_row.append(threshold_label)
        
        self.threshold_spin = Gtk.SpinButton.new_with_range(10, 200, 10)
        self.threshold_spin.set_value(50)
        self.threshold_spin.connect('value-changed', self._on_threshold_changed)
        threshold_row.append(self.threshold_spin)
        playback_group.append(threshold_row)
        
        # Hold Notes
        hold_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        hold_label = Gtk.Label(label="Hold Notes")
        hold_label.set_hexpand(True)
        hold_label.set_xalign(0)
        hold_row.append(hold_label)
        
        self.hold_switch = Gtk.Switch()
        self.hold_switch.set_valign(Gtk.Align.CENTER)
        self.hold_switch.connect('notify::active', self._on_hold_changed)
        hold_row.append(self.hold_switch)
        playback_group.append(hold_row)
        
        self.append(playback_group)
        
        # Window Settings Group
        window_group = self._create_group("Window Settings")
        
        # Auto Focus Genshin
        focus_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        focus_label = Gtk.Label(label="Auto Focus Genshin Window")
        focus_label.set_hexpand(True)
        focus_label.set_xalign(0)
        focus_row.append(focus_label)
        
        self.focus_switch = Gtk.Switch()
        self.focus_switch.set_valign(Gtk.Align.CENTER)
        self.focus_switch.connect('notify::active', self._on_focus_changed)
        focus_row.append(self.focus_switch)
        window_group.append(focus_row)
        
        # Theme
        theme_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        theme_label = Gtk.Label(label="Dark Theme")
        theme_label.set_hexpand(True)
        theme_label.set_xalign(0)
        theme_row.append(theme_label)
        
        self.theme_switch = Gtk.Switch()
        self.theme_switch.set_valign(Gtk.Align.CENTER)
        self.theme_switch.set_active(True)
        self.theme_switch.connect('notify::active', self._on_theme_changed)
        theme_row.append(self.theme_switch)
        window_group.append(theme_row)
        
        self.append(window_group)
        
        # Spacer
        spacer = Gtk.Box()
        spacer.set_vexpand(True)
        self.append(spacer)
        
        # Appreciate My Work button
        appreciate_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        appreciate_box.set_halign(Gtk.Align.CENTER)
        appreciate_box.set_margin_bottom(8)
        
        appreciate_button = Gtk.Button()
        appreciate_button.set_tooltip_text("Support the developer via PayPal")
        appreciate_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        # PayPal heart icon
        heart_label = Gtk.Label(label="💖")
        appreciate_button_box.append(heart_label)
        
        appreciate_label = Gtk.Label(label="Appreciate My Work")
        appreciate_button_box.append(appreciate_label)
        
        appreciate_button.set_child(appreciate_button_box)
        appreciate_button.add_css_class('suggested-action')
        appreciate_button.connect('clicked', self._on_appreciate_clicked)
        appreciate_box.append(appreciate_button)
        
        self.append(appreciate_box)
        
        # Reset button
        reset_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        reset_box.set_halign(Gtk.Align.CENTER)
        
        reset_button = Gtk.Button(label="Reset to Defaults")
        reset_button.add_css_class('destructive-action')
        reset_button.connect('clicked', self._on_reset_clicked)
        reset_box.append(reset_button)
        
        self.append(reset_box)
    
    def _create_group(self, title):
        """Create a settings group with title."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        label = Gtk.Label(label=title)
        label.add_css_class('title-3')
        label.set_xalign(0)
        box.append(label)
        
        separator = Gtk.Separator()
        box.append(separator)
        
        return box
    
    def _load_settings(self):
        """Load settings from storage."""
        settings = self.app.settings
        
        # Layout
        layouts = KeyMapper.get_available_layouts()
        try:
            layout_index = layouts.index(settings.keyboard_layout)
            self.layout_dropdown.set_selected(layout_index)
        except ValueError:
            self.layout_dropdown.set_selected(0)
        
        # Transpose
        self.transpose_spin.set_value(settings.transpose)
        
        # Merge
        self.merge_switch.set_active(settings.merge_nearby_notes)
        self.threshold_spin.set_value(settings.get('merge_threshold_ms', 50))
        
        # Hold notes
        self.hold_switch.set_active(settings.get('hold_notes', False))
        
        # Auto focus
        self.focus_switch.set_active(settings.get('auto_focus_genshin', True))
        
        # Theme
        self.theme_switch.set_active(settings.theme == 'dark')
    
    def _on_layout_changed(self, dropdown, param):
        """Handle layout change."""
        layouts = KeyMapper.get_available_layouts()
        selected = dropdown.get_selected()
        if 0 <= selected < len(layouts):
            layout = layouts[selected]
            self.app.settings.keyboard_layout = layout
            self.app.key_mapper.set_layout(layout)
    
    def _on_transpose_changed(self, spin):
        """Handle transpose change."""
        value = int(spin.get_value())
        self.app.settings.transpose = value
        self.app.key_mapper.set_transpose(value)
    
    def _on_merge_changed(self, switch, param):
        """Handle merge toggle."""
        active = switch.get_active()
        self.app.settings.merge_nearby_notes = active
        threshold = self.threshold_spin.get_value()
        self.app.midi_player.set_merge_enabled(active, threshold)
    
    def _on_threshold_changed(self, spin):
        """Handle merge threshold change."""
        value = spin.get_value()
        self.app.settings.set('merge_threshold_ms', value)
        if self.merge_switch.get_active():
            self.app.midi_player.set_merge_enabled(True, value)
    
    def _on_hold_changed(self, switch, param):
        """Handle hold notes toggle."""
        self.app.settings.set('hold_notes', switch.get_active())
    
    def _on_focus_changed(self, switch, param):
        """Handle auto focus toggle."""
        self.app.settings.set('auto_focus_genshin', switch.get_active())
    
    def _on_theme_changed(self, switch, param):
        """Handle theme toggle."""
        theme = 'dark' if switch.get_active() else 'light'
        self.app.settings.theme = theme
        self.app.apply_theme(theme)
    
    def _on_reset_clicked(self, button):
        """Handle reset button click."""
        self.app.settings.reset()
        self._load_settings()
    
    def _on_appreciate_clicked(self, button):
        """Handle appreciate button click - opens PayPal link."""
        webbrowser.open('https://www.paypal.com/paypalme/GTCxprice1')
