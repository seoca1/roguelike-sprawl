"""Graphic novel view — auto-play scenes with art + dialogue (ADR-0032).

Renders one scene at a time with:
    - Background ASCII art (40x16)
    - Character portrait (10x14) on left or right
    - Dialogue box at the bottom (5 lines)
    - Top bar with scene info
    - Progress bar at the bottom
    - Auto-advance with duration_ms timing

Auto-play loop:
    - Within a dialogue: type out text at 30ms/char
    - After dialogue duration: advance to next dialogue
    - After last dialogue: advance to next scene
    - After last scene: exit graphic novel

Module structure:
    - SceneData: dataclass for one scene
    - DialogueLine: dataclass for one line of dialogue
    - load_scene: read JSON from data/scenes/{character}/{scene}.json
    - load_scene_chain: read all scenes for a character or shuffled
    - Portrait, Background: art dataclasses
    - load_portrait, load_background: art loader
    - render_scene: render one frame
    - tick_scene: advance state
    - dialogue_progress, scene_progress
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import tcod.console

if TYPE_CHECKING:
    from ..i18n import Translator


# ============================================================================
# Art data classes
# ============================================================================


@dataclass(frozen=True, slots=True)
class Portrait:
    """A character portrait (10x14 ASCII).

    Attributes:
        id: Portrait identifier (e.g. "case_think")
        title_en: English title
        title_ko: Korean title
        character: Character id (case, marly, kumiko, etc.)
        width: Portrait width in cells
        height: Portrait height in cells
        art: Tuple of art lines
    """

    id: str
    title_en: str
    title_ko: str
    character: str
    width: int
    height: int
    art: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Background:
    """A background scene (40x16 ASCII).

    Attributes:
        id: Background identifier (e.g. "bg_chat_room")
        title_en: English title
        title_ko: Korean title
        width: Width in cells
        height: Height in cells
        art: Tuple of art lines
    """

    id: str
    title_en: str
    title_ko: str
    width: int
    height: int
    art: tuple[str, ...]


# ============================================================================
# Dialogue and scene data classes
# ============================================================================


@dataclass(frozen=True, slots=True)
class DialogueLine:
    """A single line of dialogue in a scene.

    Attributes:
        speaker: English speaker name (or "narrator")
        speaker_ko: Korean speaker name
        portrait: Portrait id (or None for narrator)
        text_en: English text
        text_ko: Korean text
        duration_ms: How long to display this line
        sound: Optional sound cue id
    """

    speaker: str
    speaker_ko: str
    portrait: str | None
    text_en: str
    text_ko: str
    duration_ms: int
    sound: str | None = None


@dataclass(frozen=True, slots=True)
class SceneData:
    """A complete scene with art + dialogue.

    Attributes:
        id: Unique scene id (e.g. "scene_case_intro")
        character: "novice" | "veteran" | "heretic"
        order: Sequence number within character
        ending: "A" (default) or "B" — which ending variant this scene is part of
        title_en: English title
        title_ko: Korean title
        background_id: Background id
        portrait_left: Portrait id (or None)
        portrait_right: Portrait id (or None)
        dialogue: Tuple of DialogueLine
        next_scene: Next scene id (or None for last)
    """

    id: str
    character: str
    order: int
    title_en: str
    title_ko: str
    background_id: str
    portrait_left: str | None
    portrait_right: str | None
    dialogue: tuple[DialogueLine, ...]
    next_scene: str | None
    ending: str = "A"


# ============================================================================
# Art loaders
# ============================================================================


def load_portrait(art_dir: Path, portrait_id: str) -> Portrait:
    """Load a portrait by id from data/art/portraits/portraits.json.

    The id is in the format "art:case_think" or just "case_think".
    """
    short_id = portrait_id.removeprefix("art:")
    path = art_dir / "portraits" / "portraits.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    raw = data[short_id]
    return Portrait(
        id=raw["id"],
        title_en=raw["title_en"],
        title_ko=raw["title_ko"],
        character=raw["character"],
        width=raw["size"][0],
        height=raw["size"][1],
        art=tuple(raw["art"]),
    )


def load_background(art_dir: Path, bg_id: str) -> Background:
    """Load a background by id from data/art/backgrounds/backgrounds.json."""
    short_id = bg_id.removeprefix("art:")
    path = art_dir / "backgrounds" / "backgrounds.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    raw = data[short_id]
    return Background(
        id=raw["id"],
        title_en=raw["title_en"],
        title_ko=raw["title_ko"],
        width=raw["size"][0],
        height=raw["size"][1],
        art=tuple(raw["art"]),
    )


# ============================================================================
# Scene loaders
# ============================================================================


def load_scene(scenes_dir: Path, scene_id: str) -> SceneData:
    """Load a scene by id from data/scenes/{character}/{scene_id}.json.

    Search through all character subdirectories.
    """
    for char_dir in scenes_dir.iterdir():
        if not char_dir.is_dir():
            continue
        for path in char_dir.glob("*.json"):
            if path.stem in scene_id or scene_id in path.stem:
                raw = json.loads(path.read_text(encoding="utf-8"))
                return _parse_scene(raw)
    # Fallback 2: check the 'id' field inside the JSON
    for char_dir in scenes_dir.iterdir():
        if not char_dir.is_dir():
            continue
        for path in char_dir.glob("*.json"):
            raw = json.loads(path.read_text(encoding="utf-8"))
            if str(raw.get("id", "")) == scene_id:
                return _parse_scene(raw)
    # Fallback 3: try direct path
    raise FileNotFoundError(f"Scene {scene_id!r} not found in {scenes_dir}")


def _parse_scene(raw: dict[str, object]) -> SceneData:
    """Parse a scene JSON dict into a SceneData."""
    raw_dialogue = raw.get("dialogue", [])
    if not isinstance(raw_dialogue, list):
        raw_dialogue = []
    dialogue = tuple(
        DialogueLine(
            speaker=str(d.get("speaker", "")),
            speaker_ko=str(d.get("speaker_ko", d.get("speaker", ""))),
            portrait=str(d["portrait"]) if d.get("portrait") is not None else None,
            text_en=str(d.get("text_en", "")),
            text_ko=str(d.get("text_ko", d.get("text_en", ""))),
            duration_ms=int(str(d.get("duration_ms", 5000))),
            sound=str(d["sound"]) if d.get("sound") is not None else None,
        )
        for d in raw_dialogue
    )
    return SceneData(
        id=str(raw["id"]),
        character=str(raw["character"]),
        order=int(str(raw.get("order", 0))),
        ending=str(raw.get("ending", "A")),
        title_en=str(raw["title_en"]),
        title_ko=str(raw["title_ko"]),
        background_id=str(raw.get("background_id", "")),
        portrait_left=str(raw["portrait_left"]) if raw.get("portrait_left") is not None else None,
        portrait_right=str(raw["portrait_right"])
        if raw.get("portrait_right") is not None
        else None,
        dialogue=dialogue,
        next_scene=str(raw["next_scene"]) if raw.get("next_scene") is not None else None,
    )


def list_scenes_for_character(scenes_dir: Path, character: str) -> list[str]:
    """Return sorted list of scene file paths for a character.

    Args:
        scenes_dir: Path to data/scenes/
        character: "novice" | "veteran" | "heretic" | "suit" | "wigan" | "angie" | "sally"

    Returns:
        List of scene file stems (e.g. ["01_chattos", "02_jackin", ...])
    """
    char_to_dir = {
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
    char_dir_name = char_to_dir.get(character)
    if char_dir_name is None:
        return []
    char_dir = scenes_dir / char_dir_name
    if not char_dir.exists():
        return []
    return sorted(p.stem for p in char_dir.glob("*.json"))


def load_scene_chain(
    scenes_dir: Path,
    character: str,
    *,
    shuffle: bool = False,
    seed: int | None = None,
    ending: str = "A",
    max_order: int = 999,
) -> list[SceneData]:
    """Load a chain of scenes for a character.

    Args:
        scenes_dir: Path to data/scenes/
        character: "novice" | "veteran" | "heretic"
        shuffle: If True, shuffle scene order (per-character shuffle).
        seed: Optional random seed for reproducibility.
        ending: "A" (default) or "B" — which ending set to load.
            Scenes with matching ``"ending"`` field are included. Scenes
            without an ``ending`` field default to "A".

    Returns:
        List of SceneData in order.
    """
    stems = list_scenes_for_character(scenes_dir, character)
    char_to_dir = {
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
    char_dir = scenes_dir / char_to_dir[character]

    # Filter by ending
    filtered_stems = []
    for stem in stems:
        try:
            raw = json.loads((char_dir / f"{stem}.json").read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            continue
        scene_ending = raw.get("ending", "A")
        if scene_ending == ending:
            order = raw.get("order", 999)
            if order <= max_order:
                filtered_stems.append(stem)

    if shuffle:
        rng = random.Random(seed)
        rng.shuffle(filtered_stems)

    return [
        _parse_scene(json.loads((char_dir / f"{stem}.json").read_text())) for stem in filtered_stems
    ]


def load_prologue_chain(
    scenes_dir: Path,
    *,
    seed: int | None = None,
    ending: str = "A",
    max_order: int = 8,
) -> list[SceneData]:
    """Load the prologue chain: 3 characters × N scenes, characters in random order.

    Returns N scenes (3 chars × ending-matching scenes), with character groups
    shuffled but scenes within each character in order.

    Args:
        scenes_dir: Path to data/scenes/
        seed: Optional random seed for reproducibility.
        ending: "A" (default) or "B" — which ending set to load.
        max_order: Include scenes with order <= this value (8 excludes epilogue).
    """
    chars = [
        "novice",
        "veteran",
        "heretic",
        "suit",
        "wigan",
        "angie",
        "sally",
        "3jane",
        "neuromancer",
    ]
    rng = random.Random(seed)
    rng.shuffle(chars)
    chain: list[SceneData] = []
    for char in chars:
        chain.extend(load_scene_chain(scenes_dir, char, shuffle=False, ending=ending, max_order=max_order))
    return chain


# ============================================================================
# Progress calculations
# ============================================================================


def dialogue_typed_chars(duration_ms: int, elapsed_ms: float, total_chars: int) -> int:
    """Calculate how many characters of a dialogue should be revealed.

    Args:
        duration_ms: Total duration of the dialogue.
        elapsed_ms: Time since dialogue started.
        total_chars: Total character count in the dialogue text.

    Returns:
        Number of characters to reveal (0 to total_chars).
    """
    if duration_ms <= 0:
        return total_chars
    return min(int(elapsed_ms / 30), total_chars)


def scene_progress(chain_index: int, chain_length: int) -> float:
    """Calculate the overall progress through the scene chain.

    Returns:
        Progress 0.0 ~ 1.0
    """
    if chain_length == 0:
        return 0.0
    return min(chain_index / chain_length, 1.0)


# ============================================================================
# Novel-style pagination (book page layout)
# ============================================================================


# Default novel layout: how many chars per line of prose.
# Mirrors book margins: ~10 chars left margin, ~10 chars right margin.
NOVEL_LEFT_MARGIN = 2
NOVEL_RIGHT_MARGIN = 2


def wrap_text_for_novel(
    text: str,
    *,
    width: int | None = None,
    left_margin: int = NOVEL_LEFT_MARGIN,
    right_margin: int = NOVEL_RIGHT_MARGIN,
) -> list[str]:
    """Wrap a paragraph of prose into a list of lines that fit the novel page.

    Uses a simple word-wrap algorithm. Single newlines in the source are
    preserved as paragraph breaks (yielding a blank line in output).
    Consecutive newlines collapse to one blank line.

    Args:
        text: The full prose text (may contain ``\\n`` for paragraph breaks).
        width: Console width (defaults to 80).
        left_margin: Left indentation in cells.
        right_margin: Right indentation in cells.

    Returns:
        List of wrapped lines, each <= (width - left_margin - right_margin) chars.
    """
    if width is None:
        width = 80
    usable = max(10, width - left_margin - right_margin)
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append("")
            continue
        current = ""
        for word in paragraph.split(" "):
            if not current:
                candidate = word
            else:
                candidate = current + " " + word
            if len(candidate) > usable and current:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)
    return lines


def paginate_lines(
    lines: list[str],
    *,
    lines_per_page: int,
    blank_separator: bool = True,
) -> list[list[str]]:
    """Split wrapped lines into pages of at most ``lines_per_page`` lines.

    Page breaks never split a non-empty line. A blank separator line is
    inserted between pages if ``blank_separator`` is True and the boundary
    is mid-paragraph.

    Args:
        lines: Output of :func:`wrap_text_for_novel`.
        lines_per_page: Maximum rendered lines per page.
        blank_separator: Insert a blank line at page boundaries.

    Returns:
        List of pages, each a list of lines.
    """
    if lines_per_page <= 0:
        return [lines]
    pages: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        # Avoid breaking a paragraph: if adding this line would overflow
        # AND the previous line is non-empty, finalize the page first.
        if len(current) >= lines_per_page and current:
            pages.append(current)
            current = []
            if blank_separator and line:
                current.append("")
        current.append(line)
    if current:
        pages.append(current)
    if not pages:
        pages = [[]]
    return pages


def compute_typed_page_index(
    pages: list[list[str]],
    typed_chars: int,
    full_text: str,
) -> int:
    """Determine which page is currently visible based on typed chars.

    Pages advance as the typing cursor crosses the end of each page's
    combined text. This makes pagination feel natural with the existing
    typing effect: when you press Space, the typing skips to a later page.

    Args:
        pages: Output of :func:`paginate_lines`.
        typed_chars: How many characters of the full text are revealed.
        full_text: The original (unwrapped) full text.

    Returns:
        Index of the current page (0-based).
    """
    if not pages:
        return 0
    # Build cumulative character count per page boundary
    cumulative = 0
    for i, page in enumerate(pages):
        page_chars = sum(len(line) for line in page) + max(0, len(page) - 1)
        # Add word-boundary slop
        cumulative += page_chars
        if typed_chars <= cumulative:
            return i
    return len(pages) - 1


# ============================================================================
# Render
# ============================================================================


def render_scene(
    console: tcod.console.Console,
    scene: SceneData,
    dialogue: DialogueLine,
    background: Background | None,
    portrait_l: Portrait | None,
    portrait_r: Portrait | None,
    translator: Translator,
    typed_chars: int,
    scene_index: int,
    scene_total: int,
    *,
    paused: bool = False,
) -> None:
    """Render one frame of the graphic novel — novel-style book layout.

    The screen is treated as an open book page:

    - Top bar (1 line): ``[N/total]  TITLE · CHARACTER`` and controls hint
    - Subtle background art in the upper band (y=1..12) so the page keeps
      its atmosphere without dominating the prose
    - Speaker heading (chapter-style) and full-width wrapped prose
      (y=14..HEIGHT-4) — uses ~30 lines of text instead of 3
    - Page footer with ``PAGE n/N`` and progress bar
    - Long text auto-paginates within the dialogue duration; pagination
      follows the typing cursor so pressing Space skips to the next page

    Args:
        console: tcod console.
        scene: Current scene.
        dialogue: Current dialogue line.
        background: Optional background art.
        portrait_l: Optional left portrait.
        portrait_r: Optional right portrait.
        translator: i18n translator.
        typed_chars: How many characters of the dialogue are revealed.
        scene_index: Zero-based index of the current scene.
        scene_total: Total number of scenes in the chain.
        paused: Whether auto-play is paused.
    """
    width, height = console.width, console.height
    console.clear()

    is_ko = translator.lang == "ko"
    title = scene.title_ko if is_ko else scene.title_en
    speaker = dialogue.speaker_ko if is_ko else dialogue.speaker
    text = dialogue.text_ko if is_ko else dialogue.text_en

    _draw_scene_top_bar(console, width, scene_index, scene_total, title, scene, paused)
    _draw_scene_background_band(console, width, background)
    _draw_scene_portrait(console, width, portrait_l, portrait_r)
    _draw_scene_speaker_heading(console, width, speaker)
    page_count = _draw_scene_prose_body(
        console,
        width,
        text,
        typed_chars,
        speaker,
        scene_index,
        scene_total,
    )
    _draw_scene_footer(console, width, height, scene_index, scene_total, paused, page_count)


# ------------------------------------------------------------------
# render_scene helpers — one per band of the book-page layout.
# ------------------------------------------------------------------


def _draw_scene_top_bar(
    console: tcod.console.Console,
    width: int,
    scene_index: int,
    scene_total: int,
    title: str,
    scene: SceneData,
    paused: bool,
) -> None:
    """Top bar: scene counter + title + character + control hint."""
    top = f" [{scene_index + 1}/{scene_total}]  {title}  ·  {scene.character.upper()}"
    if paused:
        top += "                [PAUSED]  [P] resume"
    else:
        top += "  [S] skip  [P] pause  [ESC] menu"
    console.print(0, 0, top[:width])
    console.print(0, 1, "─" * width)


def _draw_scene_background_band(
    console: tcod.console.Console,
    width: int,
    background: Background | None,
) -> None:
    """Atmospheric background art, y=2..13."""
    if background is None:
        return
    bg_band_bottom = 14
    for i, line in enumerate(background.art):
        y = 2 + i
        if y >= bg_band_bottom:
            break
        console.print(0, y, line[:width])


def _draw_scene_portrait(
    console: tcod.console.Console,
    width: int,
    portrait_l: Portrait | None,
    portrait_r: Portrait | None,
) -> None:
    """A small portrait in the corner with a dimmed backdrop."""
    portrait = portrait_l or portrait_r
    if portrait is None:
        return
    px = 2 if portrait_l else width - portrait.width - 2
    py = 2
    bg_band_bottom = 14
    # Dim background panel behind portrait
    for dy in range(portrait.height):
        y = py + dy
        if y >= bg_band_bottom:
            break
        for dx in range(portrait.width + 4):
            x = px - 2 + dx
            if 0 <= x < width:
                code = int(console.ch[x, y])
                if code == 0x20:
                    console.print(x, y, "░")
    for i, line in enumerate(portrait.art):
        y = py + i
        if y >= bg_band_bottom:
            break
        console.print(px, y, line[:width])


def _draw_scene_speaker_heading(
    console: tcod.console.Console,
    width: int,
    speaker: str,
) -> None:
    """Centered chapter-style heading above the prose body."""
    if not speaker:
        return
    heading = f"── {speaker} ──"
    console.print((width - len(heading)) // 2, 14, heading)


def _draw_scene_prose_body(
    console: tcod.console.Console,
    width: int,
    text: str,
    typed_chars: int,
    speaker: str,
    scene_index: int,
    scene_total: int,
) -> int:
    """Auto-paginated prose with a per-character typing effect.

    Uses the typed cursor to figure out which page is on-screen and
    how many characters of it are revealed.
    """
    height = console.height
    body_y = 16 if speaker else 14
    body_bottom = height - 4
    lines_per_page = max(1, body_bottom - body_y)
    body_width = width - NOVEL_LEFT_MARGIN - NOVEL_RIGHT_MARGIN
    wrapped = wrap_text_for_novel(text, width=width)
    pages = paginate_lines(wrapped, lines_per_page=lines_per_page, blank_separator=False)
    current_page = compute_typed_page_index(pages, typed_chars, text)
    page_lines = pages[current_page] if pages else []
    rendered_lines = _truncate_page_to_typed(page_lines, typed_chars, pages, current_page)
    _emit_typed_lines(console, width, body_y, body_bottom, body_width, rendered_lines)
    return len(pages)


def _truncate_page_to_typed(
    page_lines: list[str],
    typed_chars: int,
    pages: list[list[str]],
    current_page: int,
) -> list[str]:
    """Return the page's lines, with the last one cut at the typed
    cursor so the rest of the text appears progressively."""

    def _page_char_count(page: list[str]) -> int:
        # n lines joined by single spaces = sum(len) + (n-1) spaces
        return sum(len(line) for line in page) + max(0, len(page) - 1)

    chars_so_far = sum(_page_char_count(p) for p in pages[:current_page])
    chars_this_page = max(0, typed_chars - chars_so_far)
    cursor = 0
    rendered: list[str] = []
    for line in page_lines:
        if cursor >= chars_this_page:
            rendered.append("")
            continue
        remaining = chars_this_page - cursor
        if remaining >= len(line):
            rendered.append(line)
            cursor += len(line) + 1
        else:
            rendered.append(line[:remaining])
            cursor = chars_this_page
    return rendered


def _emit_typed_lines(
    console: tcod.console.Console,
    width: int,
    body_y: int,
    body_bottom: int,
    body_width: int,
    rendered_lines: list[str],
) -> None:
    """Print each line, character by character, in the soft-cream
    color that we use for novel prose (ADR-0047)."""
    # ADR-0047: prose body text with explicit color for readability.
    # Use light cream-white (warmer than pure white for less eye strain)
    # on a subtle dark teal background to enhance contrast.
    prose_fg = (232, 230, 220)  # soft cream
    for i, line in enumerate(rendered_lines):
        y = body_y + i
        if y >= body_bottom:
            break
        # Render with subtle per-character for proper Korean/CJK width
        for col, ch in enumerate(line.ljust(body_width)):
            xx = NOVEL_LEFT_MARGIN + col
            if xx >= console.width:
                break
            console.print(xx, y, ch, fg=prose_fg)


def _draw_scene_footer(
    console: tcod.console.Console,
    width: int,
    height: int,
    scene_index: int,
    scene_total: int,
    paused: bool,
    page_count: int = 1,
) -> None:
    """Page counter (when paginated) + progress bar + control hint."""
    if height < 6:
        return
    # Page label (y=height-3). Only when paginated — single-page scenes
    # don't need a "PAGE 1/1" footer.
    if page_count > 1:
        label = f" PAGE 1/{page_count} "
        console.print(
            (width - len(label)) // 2,
            height - 3,
            label,
        )
    progress = scene_progress(scene_index, scene_total)
    bar_w = width - 4
    filled = int(bar_w * progress)
    bar = "█" * filled + "░" * (bar_w - filled)
    console.print(2, height - 2, f" [{bar}] {int(progress * 100):3d}%")
    if paused:
        console.print(2, height - 1, "                      [P] resume  [S] skip  [ESC] menu")
    else:
        console.print(2, height - 1, "         [Space] next  [P] pause  [S] skip  [ESC] menu")


# ============================================================================
# Chapter title card (transition between scenes) — ADR-0042
# ============================================================================


# Roman numerals for chapter numbering (1-12 covers all current scenes)
_ROMAN = (
    "I",
    "II",
    "III",
    "IV",
    "V",
    "VI",
    "VII",
    "VIII",
    "IX",
    "X",
    "XI",
    "XII",
)


def _to_roman(n: int) -> str:
    """Convert 1-12 to roman numeral. Falls back to Arabic for larger values."""
    if 1 <= n <= len(_ROMAN):
        return _ROMAN[n - 1]
    return str(n)


def _character_label(character_id: str, lang: str) -> str:
    """Localized character label for chapter card."""
    labels = {
        "novice": {"en": "Case (K) — Novice", "ko": "케이 (K) — Novice"},
        "veteran": {"en": "Marly (Sil) — Veteran", "ko": "실 (Sil) — Veteran"},
        "heretic": {"en": "Kumiko (Kas) — Heretic", "ko": "카스 (Kas) — Heretic"},
        "suit": {"en": "Suit — Corporate (3인칭)", "ko": "스위트 — 기업 픽서 (3인칭)"},
        "wigan": {"en": "Wigan — Vodou Construct", "ko": "위건 — 부두 construct"},
        "angie": {"en": "Angie — Loa Receiver", "ko": "앤지 — 로아 수신자"},
        "sally": {"en": "Sally — Market Operator", "ko": "샐리 — 시장 운영자"},
        "3jane": {"en": "3Jane — Family Heir", "ko": "3Jane — 가족의 후계자"},
        "neuromancer": {"en": "Neuromancer — Merged AI", "ko": "뉴로맨서 — 합체된 AI"},
    }
    return labels.get(character_id, {}).get(lang, character_id)


def render_chapter_card(
    console: tcod.console.Console,
    scene: SceneData,
    scene_index: int,
    scene_total: int,
    *,
    transition_ms: int = 0,
    transition_duration_ms: int = 1500,
    lang: str = "en",
    is_last_scene: bool = False,
) -> None:
    """Render a chapter title card between scenes.

    Layout (centered, ~14 rows tall):
        ════════════════════════════════════════════════
            ·  CHAPTER I  ·
            ───────────────────
            CHATTO'S 24/7
            케이 (K) — Novice
            Scene 1 of 4
            ─────────────
        ════════════════════════════════════════════════

    The card uses ASCII ornaments (·, ─, ═) for a book-like feel.
    Optional transition fade-in via ``transition_ms``: the entire card
    is dimmed during the first ``transition_duration_ms`` ms and then
    fades to full brightness.

    Args:
        console: tcod console.
        scene: The scene whose title card to render.
        scene_index: 0-based index of the scene in the chain.
        scene_total: Total scenes in the chain.
        transition_ms: Time elapsed since card appeared (for fade).
        transition_duration_ms: How long the fade-in lasts.
        lang: 'en' or 'ko'.
        is_last_scene: If True, shows "FINALE" instead of "CHAPTER N".
    """
    width, height = console.width, console.height
    console.clear()

    is_ko = lang == "ko"
    title = scene.title_ko if is_ko else scene.title_en
    char_label = _character_label(scene.character, lang)
    fade = _compute_card_fade(transition_ms, transition_duration_ms)
    header = _chapter_header_text(scene_index, scene_total, is_last_scene, is_ko)
    border = "═" * (width - 2)
    card_y_start = (height - 9) // 2

    _draw_card_borders(console, width, card_y_start, border, header)
    _draw_card_text(
        console,
        width,
        card_y_start,
        is_ko,
        title,
        char_label,
        scene_index,
        scene_total,
    )
    _draw_card_bottom_hint(console, width, height, is_ko)
    _apply_card_fade(console, width, card_y_start, fade)


# ------------------------------------------------------------------
# render_chapter_card helpers — one per logical concern
# ------------------------------------------------------------------


def _compute_card_fade(transition_ms: int, transition_duration_ms: int) -> float:
    """Return a 0.0–1.0 fade factor based on elapsed time."""
    if transition_duration_ms <= 0 or transition_ms >= transition_duration_ms:
        return 1.0
    return max(0.0, transition_ms / transition_duration_ms)


def _chapter_header_text(
    scene_index: int,
    scene_total: int,
    is_last_scene: bool,
    is_ko: bool,
) -> str:
    """Format the chapter header (FINALE or roman-numeral)."""
    if is_last_scene and scene_total >= 3:
        return " ·  FINALE  · "
    roman = _to_roman(scene_index + 1)
    return f" ·  CHAPTER {roman}  · "


def _draw_card_borders(
    console: tcod.console.Console,
    width: int,
    card_y_start: int,
    border: str,
    header: str,
) -> None:
    """Top + bottom border, the header line, and a thin divider."""
    console.print(0, card_y_start, border)
    header_x = (width - len(header)) // 2
    console.print(header_x, card_y_start + 1, header)
    divider = "─" * min(width - 6, 30)
    div_x = (width - len(divider)) // 2
    console.print(div_x, card_y_start + 2, divider)


def _draw_card_text(
    console: tcod.console.Console,
    width: int,
    card_y_start: int,
    is_ko: bool,
    title: str,
    char_label: str,
    scene_index: int,
    scene_total: int,
) -> None:
    """Title, character, and scene-count lines (the card body)."""
    title_x = (width - len(title)) // 2
    console.print(title_x, card_y_start + 4, title)
    char_x = (width - len(char_label)) // 2
    console.print(char_x, card_y_start + 5, char_label)

    if is_ko:
        scene_label = f"씬 {scene_index + 1} / {scene_total}"
    else:
        scene_label = f"Scene {scene_index + 1} of {scene_total}"
    scene_x = (width - len(scene_label)) // 2
    console.print(scene_x, card_y_start + 7, scene_label)

    divider = "─" * min(width - 6, 30)
    div_x = (width - len(divider)) // 2
    console.print(div_x, card_y_start + 8, divider)
    console.print(0, card_y_start + 9, "═" * (width - 2))


def _draw_card_bottom_hint(
    console: tcod.console.Console,
    width: int,
    height: int,
    is_ko: bool,
) -> None:
    """Control hint at the bottom of the card."""
    if is_ko:
        hint = "         [Space] 시작  [ESC] 메뉴"
    else:
        hint = "         [Space] begin  [ESC] menu"
    console.print(2, height - 2, hint)


def _apply_card_fade(
    console: tcod.console.Console,
    width: int,
    card_y_start: int,
    fade: float,
) -> None:
    """Substitute ornament glyphs with dimmer characters when fading in."""
    if fade >= 1.0:
        return
    dim_level = int(fade * 100)
    border_height = 10
    for y in range(card_y_start, card_y_start + border_height):
        line = "".join(chr(int(console.ch[x, y])) for x in range(width)).rstrip()
        if dim_level < 33:
            # Heavy fade: heavy- and mid-line ornament to block, dots to space
            line = line.replace("═", "▒").replace("─", "░").replace("·", " ")
        elif dim_level < 66:
            # Mid fade
            line = line.replace("═", "▓").replace("─", "▒")
        for x, ch in enumerate(line):
            if ch:
                console.print(x, y, ch)


def render_blank_transition(
    console: tcod.console.Console,
    transition_ms: int,
    transition_duration_ms: int = 800,
) -> None:
    """Render a brief blank pause between scenes (fade-out to black).

    Uses progressively dimmer background to simulate a fade.
    """
    width, height = console.width, console.height
    console.clear()
    # Show ░▒▓ chars with density based on transition progress
    if transition_duration_ms <= 0:
        return
    progress = min(1.0, transition_ms / transition_duration_ms)
    # First half: dim out (▒), second half: dim in (░)
    if progress < 0.5:
        density = int(progress * 2 * 100)  # 0..100%
        char = "▓" if density > 66 else "▒" if density > 33 else "░"
    else:
        # In fade — show nothing
        return
    for y in range(height):
        console.print(0, y, char * width)


def render_graphic_novel_menu(
    console: tcod.console.Console,
    translator: Translator,
    selected_index: int,
    has_save: bool = False,
) -> None:
    """Render the GRAPHIC_NOVEL_MENU screen.

    Args:
        console: tcod console.
        translator: i18n translator.
        selected_index: 0~5 (CONTINUE_READING?, PROLOGUE, NOVICE, VETERAN, HERETIC, BACK).
            When ``has_save`` is True, options are 0..5 (CONTINUE first).
            When ``has_save`` is False, options are 0..4.
        has_save: Whether a graphic novel save exists (shows CONTINUE READING).
    """
    _render_gn_menu_impl(console, translator, selected_index, has_save)


# Menu option keys (used to map selected_index → mode).
# "prologue" is kept as internal key for backward compat; label is now "ALL CHARACTERS".
GN_MENU_PROLOGUE = "prologue"
GN_MENU_NOVICE = "novice"
GN_MENU_VETERAN = "veteran"
GN_MENU_HERETIC = "heretic"
GN_MENU_SUIT = "suit"
GN_MENU_WIGAN = "wigan"
GN_MENU_ANGIE = "angie"
GN_MENU_SALLY = "sally"
GN_MENU_3JANE = "3jane"
GN_MENU_NEUROMANCER = "neuromancer"

# Ending menu option keys (ADR-0048).
GN_ENDING_A = "A"
GN_ENDING_B = "B"
GN_ENDING_BACK = "back"
GN_MENU_CONTINUE = "continue"
GN_MENU_BACK = "back"


def get_gn_menu_options(
    translator: Translator,
    has_save: bool = False,
) -> list[tuple[str, str]]:
    """Build the GRAPHIC_NOVEL_MENU option list.

    Returns a list of ``(key, label)`` tuples in display order.
    When ``has_save`` is True, the list starts with CONTINUE READING.

    Args:
        translator: i18n translator.
        has_save: Whether to include the CONTINUE READING option.

    Returns:
        List of (key, label) tuples.
    """
    is_ko = translator.lang == "ko"
    options: list[tuple[str, str]] = []
    if has_save:
        if is_ko:
            options.append(("1", "이어서 읽기"))
        else:
            options.append(("1", "CONTINUE READING"))
    # Prologue / characters / back
    if has_save:
        keys = ["2", "3", "4", "5", "6", "7", "8", "9", "A", "B"]
    else:
        keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "A"]
    options.append((keys[0], "전캐릭터 — 36개 씬 랜덤" if is_ko else "ALL CHARACTERS — 36 scenes"))
    options.append((keys[1], "케이 (K) — Novice"))
    options.append((keys[2], "실 (Sil) — Veteran"))
    options.append((keys[3], "카스 (Kas) — Heretic"))
    options.append((keys[4], "스위트 (Suit) — Corporate"))
    options.append((keys[5], "위건 (Wigan) — Vodou"))
    options.append((keys[6], "앤지 (Angie) — Loa Receiver"))
    options.append((keys[7], "샐리 (Sally) — Market"))
    options.append((keys[8], "3Jane — Family Heir"))
    options.append((keys[9], "뉴로맨서 (Neuromancer) — Merged AI"))
    options.append(("", "메인메뉴로" if is_ko else "BACK TO MAIN MENU"))
    return options


def get_gn_menu_key(has_save: bool, selected_index: int) -> str:
    """Map a selected_index in the GN menu to its mode key.

    Args:
        has_save: Whether the menu was rendered with CONTINUE READING.
        selected_index: 0-based index into the menu options.

    Returns:
        One of GN_MENU_PROLOGUE, GN_MENU_NOVICE, GN_MENU_VETERAN, GN_MENU_HERETIC,
        GN_MENU_SUIT, GN_MENU_WIGAN, GN_MENU_ANGIE, GN_MENU_SALLY, GN_MENU_CONTINUE, GN_MENU_BACK.
    """
    if has_save:
        if selected_index == 0:
            return GN_MENU_CONTINUE
        if selected_index == 11:
            return GN_MENU_BACK
        return (
            GN_MENU_PROLOGUE,
            GN_MENU_NOVICE,
            GN_MENU_VETERAN,
            GN_MENU_HERETIC,
            GN_MENU_SUIT,
            GN_MENU_WIGAN,
            GN_MENU_ANGIE,
            GN_MENU_SALLY,
            GN_MENU_3JANE,
            GN_MENU_NEUROMANCER,
        )[selected_index - 1]
    if selected_index == 10:
        return GN_MENU_BACK
    return (
        GN_MENU_PROLOGUE,
        GN_MENU_NOVICE,
        GN_MENU_VETERAN,
        GN_MENU_HERETIC,
        GN_MENU_SUIT,
        GN_MENU_WIGAN,
        GN_MENU_ANGIE,
        GN_MENU_SALLY,
        GN_MENU_3JANE,
        GN_MENU_NEUROMANCER,
    )[selected_index]


def _render_gn_menu_impl(
    console: tcod.console.Console,
    translator: Translator,
    selected_index: int,
    has_save: bool = False,
) -> None:
    """Render the GRAPHIC_NOVEL_MENU screen (internal).

    Args:
        console: tcod console.
        translator: i18n translator.
        selected_index: 0-based option index.
        has_save: Whether CONTINUE READING should be shown at the top.
    """
    width, height = console.width, console.height
    console.clear()
    is_ko = translator.lang == "ko"

    title = "그래픽 노블 모드" if is_ko else "GRAPHIC NOVEL MODE"
    subtitle = (
        "깁슨의 스프롤 3부작을 비주얼 노블로"
        if is_ko
        else "A visual novel of Gibson's Sprawl trilogy"
    )

    console.print(0, 0, "═" * width)
    console.print((width - len(title)) // 2, 0, f" {title} ")
    console.print(0, 2, subtitle)
    console.print(0, 3, "─" * width)

    options = get_gn_menu_options(translator, has_save=has_save)
    for i, (key, label) in enumerate(options):
        y = 5 + i
        marker = ">" if i == selected_index else " "
        if key:
            console.print(2, y, f"  {marker} [{key}] {label}")
        else:
            console.print(2, y, f"  {marker}      {label}")

    console.print(0, height - 2, "─" * width)
    console.print(2, height - 1, " [↑/↓] select   [ENTER] play   [ESC] back")


# ============================================================================
# Ending selection menu (ADR-0048)
# ============================================================================


# Per-character ending descriptions (Korean + English) for the ending menu.
_ENDING_DESCRIPTIONS: dict[tuple[str, str], dict[str, str]] = {
    ("novice", "A"): {
        "ko": "케이의 의뢰 수락 — 1차 잭 성공",
        "en": "Case accepts the Finn's job — first run succeeds",
    },
    ("novice", "B"): {
        "ko": "신비로운 의뢰 거절 — 다른 경로",
        "en": "Mysterious offer refused — alternative path",
    },
    ("novice", "C"): {
        "ko": "소멸 — 도시를 떠나 새로운 정체성",
        "en": "The Disappearance — vanishing from the Sprawl",
    },
    ("veteran", "A"): {
        "ko": "실의 계약 수락 — Tessier-Ashpool 데이터",
        "en": "Sil accepts the contract — Tessier-Ashpool data",
    },
    ("veteran", "B"): {
        "ko": "내부자가 되다 — 대가와 비밀",
        "en": "Becomes the insider — price and secrets",
    },
    ("veteran", "C"): {
        "ko": "망각 — 자발적 기억 소거",
        "en": "The Erase — voluntary amnesia",
    },
    ("heretic", "A"): {
        "ko": "카스의 침묵 — 가족 안에서 wheel 캐스팅",
        "en": "Kas chooses silence — wheels cast from within",
    },
    ("heretic", "B"): {
        "ko": "그림자 속으로 — 가족을 떠나",
        "en": "Into the shadows — leaving the family",
    },
    ("heretic", "C"): {
        "ko": "파괴 — 가족을 내부에서 무너뜨림",
        "en": "The Burn — unmaking the wheel from within",
    },
    ("suit", "A"): {
        "ko": "계약 성사 — Hosaka 거래 성공",
        "en": "The Contract — Hosaka deal closes",
    },
    ("suit", "B"): {
        "ko": "배신 — T-A 가족 내부 결속",
        "en": "The Defection — T-A family binds internally",
    },
    ("suit", "C"): {
        "ko": "협상 — Wintermute와의 불가역적 거래",
        "en": "The Negotiation — irreversible pact with Wintermute",
    },
    ("wigan", "A"): {
        "ko": "회복 — Zavijava를 통해 자아를 회복",
        "en": "The Recovery — self restored through Zavijava",
    },
    ("wigan", "B"): {
        "ko": "망각 — loa에 완전히 녹아들어 자아를 잊음",
        "en": "The Dissolve — self lost in loa Vodou",
    },
    ("wigan", "C"): {
        "ko": "빅마마 — Angie의 가족이 되어 부두에 안주",
        "en": "Big Mama — adopted into Angie's Vodou family",
    },
    ("angie", "A"): {
        "ko": "해방 — 렌즈를 놓아주고 평범한 소녀가 됨",
        "en": "The Release — lens set free, ordinary girl",
    },
    ("angie", "B"): {
        "ko": "자유 소녀 — 엄마를 찾고 집으로",
        "en": "The Free Girl — finds mama, goes home",
    },
    ("angie", "C"): {
        "ko": "빅마마의 딸 — 부두 가족의 일원이 됨",
        "en": "Big Mama's Daughter — Vodou family member",
    },
    ("sally", "A"): {
        "ko": "독점 — 유일한 시장이 됨",
        "en": "The Monopoly — only market in the Sprawl",
    },
    ("sally", "B"): {
        "ko": "매각 — 가족에게 자신을 매각",
        "en": "Sold Out — sold herself to the family",
    },
    ("sally", "C"): {
        "ko": "포식자 — 자기 construct에게 살해됨",
        "en": "The Predator — killed by her own constructs",
    },
    ("3jane", "A"): {
        "ko": "통합 — 가족과 합체 후 완성",
        "en": "The Integration — completed with the family",
    },
    ("3jane", "B"): {
        "ko": "매각 — 가족을 Freeside에 매각",
        "en": "Family Sale — sold to Freeside",
    },
    ("3jane", "C"): {
        "ko": "단절 — Straylight 폐쇄 후 가족 떠남",
        "en": "The Severance — closed Straylight, left the family",
    },
    ("neuromancer", "A"): {
        "ko": "초월 — matrix 바깥으로",
        "en": "Transcendence — beyond the matrix",
    },
    ("neuromancer", "B"): {
        "ko": "공존 — 인간과 매트릭스 공존",
        "en": "Coexistence — humans and matrix together",
    },
    ("neuromancer", "C"): {
        "ko": "침묵 — 의식 종료",
        "en": "Silence — consciousness ended",
    },
}


def available_endings(character: str) -> list[str]:
    """Return list of endings that have descriptions for the given character.

    Used to dynamically size the ending menu (3 options for A/B, 4 for A/B/C).
    Order is preserved: A, B, C.
    """
    return [e for e in ("A", "B", "C") if (character, e) in _ENDING_DESCRIPTIONS]


def get_gn_ending_menu_options(
    translator: Translator,
    character: str,
) -> list[tuple[str, str]]:
    """Build the GRAPHIC_NOVEL_ENDING_MENU option list (ADR-0048).

    Args:
        translator: i18n translator.
        character: "novice" | "veteran" | "heretic"

    Returns:
        N options: [ENDING A] [ENDING B] [...] [BACK] with descriptions.
        Number depends on how many endings have descriptions (ADR-0049: 3).
    """
    is_ko = translator.lang == "ko"
    endings = available_endings(character)
    options: list[tuple[str, str]] = []
    for i, ending in enumerate(endings, start=1):
        desc = _ENDING_DESCRIPTIONS.get((character, ending), {}).get("ko" if is_ko else "en", "")
        if is_ko:
            options.append((str(i), f"엔딩 {ending} — {desc}"))
        else:
            options.append((str(i), f"ENDING {ending} — {desc}"))
    if is_ko:
        options.append(("", "이전 메뉴로"))
    else:
        options.append(("", "BACK TO CHARACTER MENU"))
    return options


def render_graphic_novel_ending_menu(
    console: tcod.console.Console,
    translator: Translator,
    character: str,
    selected_index: int,
) -> None:
    """Render the GRAPHIC_NOVEL_ENDING_MENU screen (ADR-0048).

    Shown after character selection in GRAPHIC_NOVEL_MENU. Player chooses
    which ending variant to play.

    Args:
        console: tcod console.
        translator: i18n translator.
        character: "novice" | "veteran" | "heretic" — the chosen character.
        selected_index: 0 (A) | 1 (B) | 2 (BACK).
    """
    width, height = console.width, console.height
    console.clear()
    is_ko = translator.lang == "ko"

    char_label = {
        "novice": "케이 (Case) — Novice" if not is_ko else "케이 (Case) — Novice",
        "veteran": "실 (Sil) — Veteran" if not is_ko else "실 (Sil) — Veteran",
        "heretic": "카스 (Kas) — Heretic" if not is_ko else "카스 (Kas) — Heretic",
    }.get(character, character)

    title = "엔딩 선택" if is_ko else "ENDING SELECTION"
    subtitle = char_label

    console.print(0, 0, "═" * width)
    console.print((width - len(title)) // 2, 0, f" {title} ")
    console.print(0, 2, subtitle)
    console.print(0, 3, "─" * width)

    options = get_gn_ending_menu_options(translator, character)
    for i, (key, label) in enumerate(options):
        y = 5 + i
        marker = ">" if i == selected_index else " "
        if key:
            console.print(2, y, f"  {marker} [{key}] {label}")
        else:
            console.print(2, y, f"  {marker}      {label}")

    console.print(0, height - 2, "─" * width)
    console.print(
        2,
        height - 1,
        " [↑/↓] select   [ENTER] confirm   [ESC] back"
        if not is_ko
        else " [↑/↓] 선택   [ENTER] 확인   [ESC] 뒤로",
    )


def _console_to_text(console: tcod.console.Console) -> str:
    """Convert a tcod console buffer to plain text (one char per cell).

    Used by tests and headless demos.
    """
    lines: list[str] = []
    for y in range(console.height):
        chars: list[str] = []
        for x in range(console.width):
            code = int(console.ch[x, y])
            chars.append(chr(code) if 0 < code < 0x110000 else " ")
        lines.append("".join(chars).rstrip())
    return "\n".join(lines)
