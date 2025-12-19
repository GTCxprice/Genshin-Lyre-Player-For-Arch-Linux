"""
Application class for Genshin Lyre MIDI Player.
Manages the GTK application lifecycle and global state.
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GLib, Gdk

from .settings import Settings
from .key_mapper import KeyMapper
from .key_sender import KeySender
from .midi_player import MidiPlayer


class LyreApplication:
    """Main application class managing all components."""
    
    def __init__(self):
        self.gtk_app = Gtk.Application(
            application_id='com.genshin.lyreplayer',
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS
        )
        
        self.gtk_app.connect('activate', self._on_activate)
        self.gtk_app.connect('startup', self._on_startup)
        
        # Components (initialized in startup)
        self.settings = None
        self.key_mapper = None
        self.key_sender = None
        self.midi_player = None
        self.main_window = None
    
    def _on_startup(self, app):
        """Handle application startup."""
        # Initialize components
        self.settings = Settings()
        self.key_mapper = KeyMapper(
            layout=self.settings.keyboard_layout,
            transpose=self.settings.transpose
        )
        self.key_sender = KeySender()
        self.midi_player = MidiPlayer(self.key_mapper, self.key_sender)
        
        # Set up playback callbacks
        self.midi_player.on_playback_finished = self._on_playback_finished
        
        # Set up actions
        self._setup_actions()
        
        # Load CSS
        self._load_css()
        
        # Apply theme
        self.apply_theme(self.settings.theme)
    
    def _on_activate(self, app):
        """Handle application activation."""
        if self.main_window is None:
            from .ui.main_window import MainWindow
            self.main_window = MainWindow(self)
        
        self.main_window.present()
    
    def _setup_actions(self):
        """Set up application actions."""
        # About action
        about_action = Gio.SimpleAction.new('about', None)
        about_action.connect('activate', self._on_about)
        self.gtk_app.add_action(about_action)
        
        # Quit action
        quit_action = Gio.SimpleAction.new('quit', None)
        quit_action.connect('activate', self._on_quit)
        self.gtk_app.add_action(quit_action)
    
    def _load_css(self):
        """Load custom CSS styling."""
        css_provider = Gtk.CssProvider()
        
        css = """
        .title-1 {
            font-size: 24px;
            font-weight: bold;
        }
        
        .title-2 {
            font-size: 18px;
            font-weight: bold;
        }
        
        .title-3 {
            font-size: 14px;
            font-weight: bold;
        }
        
        .dim-label {
            opacity: 0.6;
        }
        
        .monospace {
            font-family: monospace;
        }
        
        .success {
            color: #4caf50;
        }
        
        .error {
            color: #f44336;
        }
        
        .warning {
            color: #ff9800;
        }
        
        .circular {
            border-radius: 9999px;
            min-width: 40px;
            min-height: 40px;
        }
        
        .pill {
            border-radius: 20px;
            padding: 8px 24px;
        }
        
        notebook tab {
            padding: 8px 16px;
        }
        """
        
        css_provider.load_from_data(css.encode())
        
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def apply_theme(self, theme):
        """Apply color theme."""
        settings = Gtk.Settings.get_default()
        if settings:
            settings.set_property('gtk-application-prefer-dark-theme', theme == 'dark')
    
    def _on_about(self, action, param):
        """Show about dialog."""
        about = Gtk.AboutDialog()
        about.set_transient_for(self.main_window)
        about.set_modal(True)
        about.set_program_name('Genshin Lyre MIDI Player')
        about.set_version('1.0.0')
        about.set_comments('Play MIDI files on the Genshin Impact Lyre')
        about.set_license_type(Gtk.License.MIT_X11)
        about.present()
    
    def _on_quit(self, action, param):
        """Handle quit action."""
        self.midi_player.stop()
        self.gtk_app.quit()
    
    def _on_playback_finished(self):
        """Handle playback finished callback."""
        if self.main_window:
            GLib.idle_add(self.main_window.player_tab.on_playback_finished)
    
    def run(self, args=None):
        """Run the application."""
        import sys
        return self.gtk_app.run(args or sys.argv)
