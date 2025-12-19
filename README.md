# Genshin Lyre MIDI Player for Linux

A GTK4-based application for playing MIDI files on the Genshin Impact Lyre, inspired by [GenshinLyreMidiPlayer](https://github.com/sabihoshi/GenshinLyreMidiPlayer).

![Player Tab Preview](https://user-images.githubusercontent.com/25006819/190002173-fa8e2b0d-8817-4980-81f1-fb491c584310.png)

## Features
Rework of this project for linux "https://github.com/sabihoshi/GenshinLyreMidiPlayer.git"
### 🎵 Player Tab
- Load and play MIDI files (`.mid`, `.midi`)
- Select which tracks to play
- Media controls: Play, Pause, Stop, Seek
- Adjustable playback speed (0.25x - 2.0x)
- Timeline slider with time display

### ⚙️ Settings Tab
- **Keyboard Layout**: QWERTY, QWERTZ, AZERTY, DVORAK
- **Key Transposition**: -12 to +12 semitones
- **Merge Nearby Notes**: Improve sound for some songs
- **Hold Notes**: Sustained note style
- **Dark/Light Theme**: Toggle as you prefer

### ⌨️ Auto Key Smash Tab
- Select which lyre keys to spam
- Adjustable speed (1-50 keys/second)
- Modes: Sequential, Random, Chord (all at once)
- Quick select: All, None, Upper/Middle/Lower row

### Other Features
- 💾 Settings persistence (saved between sessions)
- 📜 File history
- 🎨 Modern GTK4 dark theme

## Installation

### Prerequisites

#### Ubuntu / Debian

1. **xdotool** (for sending keypresses):
   ```bash
   sudo apt install xdotool
   ```

2. **GTK4 Python bindings**:
   ```bash
   sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0
   ```

3. **Python mido library**:
   ```bash
   pip install mido
   ```

#### Arch Linux

1. **xdotool** (for sending keypresses):
   ```bash
   sudo pacman -S xdotool
   ```

2. **GTK4 Python bindings**:
   ```bash
   sudo pacman -S python-gobject gtk4
   ```

3. **Python mido library**:
   ```bash
   pip install mido
   ```
   Or from AUR:
   ```bash
   yay -S python-mido
   ```

### Running the Application

Navigate to the project directory and run:

```bash
./run.sh
```

Or run directly with Python:
```bash
python3 -m genshin_lyre.main
```

## Usage

1. **Open a MIDI file**: Click the folder icon in the header bar
2. **Select tracks**: Check/uncheck tracks in the track list
3. **Adjust speed**: Use the speed slider if needed
4. **Press Play**: Focus Genshin Impact window, then the keys will be sent automatically
5. **Stop anytime**: Click Stop or close the player

### Auto Key Smash

1. Go to the "Auto Key Smash" tab
2. Select which keys to spam (toggle the key buttons)
3. Set the speed (keys per second)
4. Choose a mode (Sequential, Random, or Chord)
5. Focus Genshin Impact window
6. Click "Start Smashing"
7. Click "Stop Smashing" when done

## Keyboard Mapping

The lyre has 21 keys across 3 octaves:

| Octave | Notes | QWERTY Keys |
|--------|-------|-------------|
| Upper (C5-B5) | C D E F G A B | Q W E R T Y U |
| Middle (C4-B4) | C D E F G A B | A S D F G H J |
| Lower (C3-B3) | C D E F G A B | Z X C V B N M |

## File Structure

```
glp/
├── genshin_lyre/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── application.py       # GTK Application
│   ├── midi_player.py       # MIDI playback engine
│   ├── key_mapper.py        # Note-to-key mapping
│   ├── key_sender.py        # xdotool integration
│   ├── settings.py          # Settings persistence
│   └── ui/
│       ├── __init__.py
│       ├── main_window.py   # Main window
│       ├── player_tab.py    # Player controls
│       ├── settings_tab.py  # Settings UI
│       └── keysmash_tab.py  # Auto key smash UI
├── requirements.txt
├── run.sh
├── README.md
├── SH.mid                   # Sample MIDI file
└── Suzu.mid                 # Sample MIDI file
```

## Troubleshooting

### "xdotool not found"
Install xdotool:

**Ubuntu/Debian:**
```bash
sudo apt install xdotool
```

**Arch Linux:**
```bash
sudo pacman -S xdotool
```

### "GTK4 not available"
Install GTK4 Python bindings:

**Ubuntu/Debian:**
```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0
```

**Arch Linux:**
```bash
sudo pacman -S python-gobject gtk4
```

### Keys not being sent
- Make sure Genshin Impact is the focused window
- Check that xdotool is installed: `which xdotool`
- The status bar shows xdotool status (✓ or ✗)

## 💖 Appreciate My Work

If you find this application useful and would like to show your appreciation, consider supporting the development!

[![PayPal](https://img.shields.io/badge/PayPal-Appreciate%20My%20Work-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://www.paypal.com/paypalme/GTCxprice1)

Thank you for using Genshin Lyre MIDI Player! 🎶

## License

MIT License

##Contributors

- [GTCxprice1](https://github.com/GTCxprice1)
- [su1](https://github.com/su1)

