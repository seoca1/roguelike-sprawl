"""Download the libtcod terminal font for the game."""

from __future__ import annotations

import urllib.request
from pathlib import Path

FONT_URL = (
    "https://raw.githubusercontent.com/libtcod/libtcod/master/data/fonts/terminal10x10_gs_tc.png"
)
DEST = Path(__file__).parent.parent / "data" / "fonts" / "terminal10x10_gs_tc.png"


def main() -> None:
    """Download the libtcod terminal font to the data/fonts directory."""
    DEST.parent.mkdir(parents=True, exist_ok=True)
    if DEST.exists():
        print(f"Font already exists at {DEST}")
        return
    print(f"Downloading font from {FONT_URL}...")
    urllib.request.urlretrieve(FONT_URL, DEST)  # noqa: S310
    print(f"Downloaded font to {DEST}")


if __name__ == "__main__":
    main()
