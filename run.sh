#!/bin/bash
# Run the Genshin Lyre MIDI Player

cd "$(dirname "$0")"

# Check for dependencies
if ! command -v xdotool &> /dev/null; then
    echo "Error: xdotool is not installed."
    echo "Arch Linux: sudo pacman -S xdotool"
    echo "Ubuntu/Debian: sudo apt install xdotool"
    exit 1
fi

# Use virtual environment if it exists, otherwise create it
VENV_DIR=".venv"
PYTHON="/usr/bin/python3"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment with system packages..."
    $PYTHON -m venv --system-site-packages "$VENV_DIR"
    "$VENV_DIR/bin/pip" install mido --quiet
fi

PYTHON="$VENV_DIR/bin/python"

# Check GTK4 Python bindings
if ! $PYTHON -c "import gi; gi.require_version('Gtk', '4.0'); from gi.repository import Gtk" 2>/dev/null; then
    echo "Error: GTK4 Python bindings not found."
    echo "Arch Linux: sudo pacman -S python-gobject gtk4"
    echo "Ubuntu/Debian: sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0"
    exit 1
fi

# Run the application
$PYTHON -m genshin_lyre.main "$@"
