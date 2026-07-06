"""Chapter screen — displays short-story excerpt with typing effect (ADR-0031).

Renders one of the three original-scenario chapters (Case/Marly/Kumiko).
Text is revealed character by character with a 30ms delay. After
``duration_ms`` elapses, the screen auto-advances to the next screen
(default HUB).

Module structure:
    - ChapterData: dataclass wrapping a single chapter JSON
    - load_chapter: read JSON file from data/story/chapters/
    - render_chapter: render typing-effect text + portrait + progress bar
    - tick_chapter: advance state.elapsed_ms and return new typed_chars
    - chapter_for_character: return ChapterData for the chosen character
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import tcod.console

if TYPE_CHECKING:
    from ..i18n import Translator


@dataclass(frozen=True, slots=True)
class ChapterData:
    """Loaded chapter data for a single character.

    Attributes:
        character: "novice" | "veteran" | "heretic"
        id: unique chapter id (e.g. "chapter_novice")
        title_en: English chapter title
        title_ko: Korean chapter title
        subtitle_en: English subtitle (short story title)
        subtitle_ko: Korean subtitle
        portrait: Portrait glyph reference (e.g. "art:case")
        theme: Background music theme
        excerpt_en: English excerpt (full chapter text)
        excerpt_ko: Korean excerpt (full chapter text)
        duration_ms: Auto-advance timeout in milliseconds
        next_screen: ScreenKind to advance to (default HUB)
        char_delay_ms: Per-character typing delay
    """

    character: str
    id: str
    title_en: str
    title_ko: str
    subtitle_en: str
    subtitle_ko: str
    portrait: str
    theme: str
    excerpt_en: str
    excerpt_ko: str
    duration_ms: int
    next_screen: str
    char_delay_ms: int = 60


def load_chapter(path: Path) -> ChapterData:
    """Load a chapter JSON file and return a ChapterData.

    Args:
        path: Path to a chapter JSON file (e.g. data/story/chapters/case.json)

    Returns:
        A new ChapterData instance.

    Raises:
        FileNotFoundError: If path does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    raw = json.loads(path.read_text(encoding="utf-8"))
    return ChapterData(
        character=raw["character"],
        id=raw["id"],
        title_en=raw["title_en"],
        title_ko=raw["title_ko"],
        subtitle_en=raw.get("subtitle_en", ""),
        subtitle_ko=raw.get("subtitle_ko", ""),
        portrait=raw.get("portrait", ""),
        theme=raw.get("theme", "matrix_rain"),
        excerpt_en=raw["excerpt_en"],
        excerpt_ko=raw["excerpt_ko"],
        duration_ms=raw.get("duration_ms", 12000),
        next_screen=raw.get("next_screen", "HUB"),
        char_delay_ms=raw.get("char_delay_ms", 30),
    )


def chapter_for_character(character: str, data_dir: Path) -> ChapterData:
    """Return the chapter for the given character id.

    Args:
        character: "novice" | "veteran" | "heretic" | "suit" | "wigan" | "angie" | "sally"
        data_dir: Project data directory (containing story/chapters/)

    Returns:
        The matching ChapterData. Falls back to novice if unknown.
    """
    mapping = {
        "novice": "case",
        "veteran": "sil",
        "heretic": "kas",
        "suit": "suit",
        "wigan": "wigan",
        "angie": "angie",
        "sally": "sally",
        "3jane": "3jane",
        "neuromancer": "neuromancer",
    }
    name = mapping.get(character, "case")
    return load_chapter(data_dir / "story" / "chapters" / f"{name}.json")


def tick_chapter(
    chapter: ChapterData,
    elapsed_ms: float,
    typed_chars: int,
) -> int:
    """Advance typing animation by elapsed_ms.

    Args:
        chapter: The chapter being displayed.
        elapsed_ms: Total elapsed milliseconds since the screen opened.
        typed_chars: Currently-typed character count.

    Returns:
        The new typed_chars count.
    """
    if chapter.char_delay_ms <= 0:
        return len(chapter.excerpt_en)
    new_count = int(elapsed_ms / chapter.char_delay_ms)
    return min(new_count, len(chapter.excerpt_en))


def render_chapter(
    console: tcod.console.Console,
    chapter: ChapterData,
    translator: Translator,
    typed_chars: int,
    elapsed_ms: float,
) -> None:
    """Render the chapter screen.

    Layout:
        - Top bar: title + subtitle
        - Left column: portrait glyph
        - Right column: typing-effect excerpt text
        - Bottom bar: progress bar + controls hint

    Args:
        console: tcod console to draw onto.
        chapter: The chapter to display.
        translator: i18n translator (for display language).
        typed_chars: Number of characters to reveal.
        elapsed_ms: Total elapsed milliseconds (used for progress bar).
    """
    width, height = console.width, console.height
    console.clear()

    is_ko = translator.lang == "ko"
    title = chapter.title_ko if is_ko else chapter.title_en
    subtitle = chapter.subtitle_ko if is_ko else chapter.subtitle_en
    excerpt = chapter.excerpt_ko if is_ko else chapter.excerpt_en

    # Top bar (border + title)
    title_text = f" CHAPTER — {title} "
    console.print(0, 0, "═" * width)
    console.print(2, 0, title_text)
    if subtitle:
        console.print(width - len(subtitle) - 2, 0, f" {subtitle} ")

    # Left column: portrait
    portrait_x = 2
    portrait_y = 4
    portrait_lines = [
        "┌─────────┐",
        "│         │",
        "│   ◉P◉   │",
        "│         │",
        "│  K/S/K  │",
        "│ 1/3/5-up│",
        "│         │",
        "└─────────┘",
    ]
    for i, line in enumerate(portrait_lines):
        console.print(portrait_x, portrait_y + i, line)

    # Right column: excerpt with typing effect
    text_x = 18
    text_y = 3
    text_width = width - text_x - 2
    revealed = excerpt[:typed_chars]

    # Word-wrap to text_width
    wrapped_lines: list[str] = []
    for paragraph in revealed.split("\n"):
        if not paragraph:
            wrapped_lines.append("")
            continue
        words = paragraph.split(" ")
        current = ""
        for word in words:
            test = (current + " " + word).strip()
            if len(test) > text_width and current:
                wrapped_lines.append(current)
                current = word
            else:
                current = test
        if current:
            wrapped_lines.append(current)

    max_y = height - 5
    for i, line in enumerate(wrapped_lines[:max_y]):
        console.print(text_x, text_y + i, line)

    # Bottom: progress bar
    progress = min(elapsed_ms / chapter.duration_ms, 1.0)
    bar_width = width - 4
    filled = int(bar_width * progress)
    bar = "█" * filled + "░" * (bar_width - filled)
    console.print(2, height - 3, f" [{bar}] {int(progress * 100):3d}%")
    console.print(
        2,
        height - 2,
        " [ENTER] Continue   [SKIP] Skip Chapter   [ESC] Back",
    )
    console.print(0, height - 1, "═" * width)


def _console_to_text(console: tcod.console.Console) -> str:
    """Convert a tcod console buffer to plain text (one char per cell).

    Used by tests and headless demos. Public tests rely on this helper
    existing in the module.
    """
    lines: list[str] = []
    for y in range(console.height):
        chars: list[str] = []
        for x in range(console.width):
            code = int(console.ch[x, y])
            chars.append(chr(code) if 0 < code < 0x110000 else " ")
        lines.append("".join(chars).rstrip())
    return "\n".join(lines)
