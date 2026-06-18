"""Translation manager (ADR-0010).

English is primary. Korean is supplementary translation.
Display mode: Off (English only, default) / Subtitle / Replace.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class Translator:
    """Manages translations for a specific language.

    Loads a JSON file (e.g. `en.json`) and provides dotted-key lookup
    with optional format arguments.
    """

    __slots__ = ("lang", "_data")

    def __init__(self, lang: str, data_dir: Path | None = None) -> None:
        self.lang = lang
        self._data: dict[str, Any] = {}
        if data_dir is not None:
            self._load(data_dir)

    def _load(self, data_dir: Path) -> None:
        path = data_dir / f"{self.lang}.json"
        if not path.exists():
            return
        with path.open(encoding="utf-8") as f:
            self._data = json.load(f)

    def t(self, key: str, **kwargs: Any) -> str:
        """Translate a dotted key with optional format arguments.

        Falls back to the key itself if not found.
        """
        value: Any = self._data
        for part in key.split("."):
            if not isinstance(value, dict) or part not in value:
                return key
            value = value[part]
        if not isinstance(value, str):
            return key
        if kwargs:
            try:
                return value.format(**kwargs)
            except (KeyError, IndexError, ValueError):
                return value
        return value

    def set_locale(self, lang: str, data_dir: Path | None = None) -> None:
        """Switch to a different language. Reloads from ``data_dir`` if given."""
        self.lang = lang
        self._data = {}
        if data_dir is not None:
            self._load(data_dir)

    def __call__(self, key: str, **kwargs: Any) -> str:
        """Shorthand for `t(key, **kwargs)`. Allows `translator("key")`."""
        return self.t(key, **kwargs)

    def has(self, key: str) -> bool:
        """Return True if the key exists in this language."""
        value: Any = self._data
        for part in key.split("."):
            if not isinstance(value, dict) or part not in value:
                return False
            value = value[part]
        return isinstance(value, str)

    def __repr__(self) -> str:
        return f"Translator(lang={self.lang!r}, keys={len(self._data)})"
