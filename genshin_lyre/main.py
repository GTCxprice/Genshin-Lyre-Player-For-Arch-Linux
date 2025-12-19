#!/usr/bin/env python3
"""
Entry point for Genshin Lyre MIDI Player.
"""

import sys
from .application import LyreApplication


def main():
    """Main entry point."""
    app = LyreApplication()
    return app.run(sys.argv)


if __name__ == '__main__':
    sys.exit(main())
