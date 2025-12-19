"""
Main Window for Genshin Lyre MIDI Player.
Contains the main application window with tab navigation.
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GLib, Gdk

from .player_tab import PlayerTab
from .settings_tab import SettingsTab
from .keysmash_tab import KeySmashTab


class MainWindow(Gtk.ApplicationWindow):
    """Main application window with tab navigation."""
    
    def __init__(self, app):
        super().__init__(application=app.gtk_app)
        self.app = app
        
        self.set_title("Genshin Lyre MIDI Player")
        self.set_default_size(
            app.settings.get('window_width', 900),
            app.settings.get('window_height', 600)
        )
        
        self._build_ui()
        self._connect_signals()
        self._setup_drag_drop()
    
    def _build_ui(self):
        """Build the main window UI."""
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(main_box)
        
        # Header bar
        header = Gtk.HeaderBar()
        self.set_titlebar(header)
        
        # Open file button
        open_button = Gtk.Button()
        open_button.set_icon_name('document-open-symbolic')
        open_button.set_tooltip_text('Open MIDI File')
        open_button.connect('clicked', self._on_open_clicked)
        header.pack_start(open_button)
        
        # Menu button
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name('open-menu-symbolic')
        
        # Create menu
        menu = Gio.Menu.new()
        menu.append('About', 'app.about')
        menu.append('Quit', 'app.quit')
        menu_button.set_menu_model(menu)
        header.pack_end(menu_button)
        
        # Tab view using Notebook
        self.notebook = Gtk.Notebook()
        self.notebook.set_vexpand(True)
        
        # Player tab
        self.player_tab = PlayerTab(self.app)
        player_label = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        player_icon = Gtk.Image.new_from_icon_name('media-playback-start-symbolic')
        player_text = Gtk.Label(label='Player')
        player_label.append(player_icon)
        player_label.append(player_text)
        self.notebook.append_page(self.player_tab, player_label)
        
        # Settings tab
        self.settings_tab = SettingsTab(self.app)
        settings_label = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        settings_icon = Gtk.Image.new_from_icon_name('preferences-system-symbolic')
        settings_text = Gtk.Label(label='Settings')
        settings_label.append(settings_icon)
        settings_label.append(settings_text)
        self.notebook.append_page(self.settings_tab, settings_label)
        
        # Key Smash tab
        self.keysmash_tab = KeySmashTab(self.app)
        keysmash_label = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        keysmash_icon = Gtk.Image.new_from_icon_name('input-keyboard-symbolic')
        keysmash_text = Gtk.Label(label='Auto Key Smash')
        keysmash_label.append(keysmash_icon)
        keysmash_label.append(keysmash_text)
        self.notebook.append_page(self.keysmash_tab, keysmash_label)
        
        main_box.append(self.notebook)
        
        # Status bar
        self.status_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.status_bar.set_margin_start(8)
        self.status_bar.set_margin_end(8)
        self.status_bar.set_margin_top(4)
        self.status_bar.set_margin_bottom(4)
        
        self.status_label = Gtk.Label(label='Ready')
        self.status_label.set_hexpand(True)
        self.status_label.set_xalign(0)
        self.status_bar.append(self.status_label)
        
        self.xdotool_status = Gtk.Label()
        self._update_xdotool_status()
        self.status_bar.append(self.xdotool_status)
        
        main_box.append(self.status_bar)
    
    def _connect_signals(self):
        """Connect window signals."""
        self.connect('close-request', self._on_close)
    
    def _setup_drag_drop(self):
        """Set up drag and drop for MIDI files."""
        # Create a drop target for files
        drop_target = Gtk.DropTarget.new(Gio.File, Gdk.DragAction.COPY)
        drop_target.connect('drop', self._on_drop)
        drop_target.connect('enter', self._on_drag_enter)
        drop_target.connect('leave', self._on_drag_leave)
        self.add_controller(drop_target)
    
    def _on_drag_enter(self, drop_target, x, y):
        """Handle drag enter event."""
        self.set_status('Drop MIDI file here...')
        return Gdk.DragAction.COPY
    
    def _on_drag_leave(self, drop_target):
        """Handle drag leave event."""
        self.set_status('Ready')
    
    def _on_drop(self, drop_target, value, x, y):
        """Handle file drop."""
        if isinstance(value, Gio.File):
            path = value.get_path()
            if path and (path.lower().endswith('.mid') or path.lower().endswith('.midi')):
                self._load_midi_file(path)
                return True
            else:
                self.set_status('Error: Please drop a MIDI file (.mid or .midi)')
        return False
    
    def _on_open_clicked(self, button):
        """Handle open file button click."""
        dialog = Gtk.FileDialog.new()
        dialog.set_title('Open MIDI File')
        
        # MIDI file filter
        filter_midi = Gtk.FileFilter()
        filter_midi.set_name('MIDI Files')
        filter_midi.add_pattern('*.mid')
        filter_midi.add_pattern('*.midi')
        
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(filter_midi)
        dialog.set_filters(filters)
        
        # Set initial folder
        last_dir = self.app.settings.get('last_directory')
        if last_dir:
            try:
                folder = Gio.File.new_for_path(last_dir)
                dialog.set_initial_folder(folder)
            except Exception:
                pass
        
        dialog.open(self, None, self._on_file_selected)
    
    def _on_file_selected(self, dialog, result):
        """Handle file selection result."""
        try:
            file = dialog.open_finish(result)
            if file:
                path = file.get_path()
                self._load_midi_file(path)
        except GLib.Error:
            # User cancelled
            pass
    
    def _load_midi_file(self, path):
        """Load a MIDI file."""
        import os
        
        if self.app.midi_player.load_file(path):
            # Update UI
            self.player_tab.update_tracks()
            self.player_tab.update_file_info()
            
            # Save to history
            self.app.settings.add_to_history(path)
            self.app.settings.set('last_directory', os.path.dirname(path))
            
            self.set_status(f'Loaded: {os.path.basename(path)}')
        else:
            self.set_status('Failed to load file')
    
    def set_status(self, message):
        """Set status bar message."""
        self.status_label.set_label(message)
    
    def _update_xdotool_status(self):
        """Update xdotool status indicator."""
        if self.app.key_sender.check_xdotool():
            self.xdotool_status.set_label('✓ xdotool')
            self.xdotool_status.add_css_class('success')
        else:
            self.xdotool_status.set_label('✗ xdotool not found')
            self.xdotool_status.add_css_class('error')
    
    def _on_close(self, window):
        """Handle window close."""
        # Save window size
        width = self.get_width()
        height = self.get_height()
        self.app.settings.set('window_width', width, auto_save=False)
        self.app.settings.set('window_height', height)
        
        # Stop any playback
        self.app.midi_player.stop()
        
        return False  # Allow close
