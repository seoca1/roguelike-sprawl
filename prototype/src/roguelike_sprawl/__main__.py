"""Entry point for `python -m roguelike_sprawl`."""

from __future__ import annotations

import sys

from roguelike_sprawl.engine.app import main

if __name__ == "__main__":
    sys.exit(main())
