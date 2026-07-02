"""Story Event view (ADR-0019: Aftermath + Character Reactions).

Renders the Story/Aftermath screen in the MAIN region. Used after
combat (victory/defeat) and on major story events.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import tcod.console

from .layout import (
    RegionId,
    clear_region,
    draw_controls,
    draw_dividers,
    draw_footer,
    draw_side,
    draw_title,
    make_shell,
)
from .state import AppState, ScreenKind


@dataclass(frozen=True, slots=True)
class Aftermath:
    """Loaded story content (ADR-0019)."""

    id: str
    importance: str
    trigger: str
    duration_ms: int
    narrative_en: str
    narrative_ko: str
    reaction_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Reaction:
    """Character reaction (ADR-0019)."""

    id: str
    character: str
    trigger: str
    text_en: str
    text_ko: str
    portrait: str


@dataclass(frozen=True, slots=True)
class StoryRegistry:
    """Loads aftermath + reactions from JSON files (ADR-0019)."""

    aftermaths: dict[str, Aftermath]
    reactions: dict[str, Reaction]

    @classmethod
    def load(cls, data_dir: Path) -> StoryRegistry:
        aftermaths_path = data_dir / "story" / "aftermath.json"
        reactions_path = data_dir / "story" / "reactions.json"
        return cls(
            aftermaths=_load_aftermaths(aftermaths_path),
            reactions=_load_reactions(reactions_path),
        )

    def get_aftermath(self, aftermath_id: str) -> Aftermath | None:
        return self.aftermaths.get(aftermath_id)

    def get_reaction(self, reaction_id: str) -> Reaction | None:
        return self.reactions.get(reaction_id)


def _load_aftermaths(path: Path) -> dict[str, Aftermath]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        raw: object = json.load(f)
    if not isinstance(raw, dict):
        return {}
    out: dict[str, Aftermath] = {}
    for key, value in raw.items():
        if not isinstance(value, dict):
            continue
        try:
            reactions = value.get("reaction_ids", ())
            if not isinstance(reactions, list):
                reactions = ()
            out[str(key)] = Aftermath(
                id=str(value.get("id", key)),
                importance=str(value.get("importance", "minor")),
                trigger=str(value.get("trigger", "")),
                duration_ms=int(value.get("duration_ms", 4000)),
                narrative_en=str(value.get("narrative_en", "")),
                narrative_ko=str(value.get("narrative_ko", "")),
                reaction_ids=tuple(str(r) for r in reactions),
            )
        except (TypeError, ValueError):
            continue
    return out


def _load_reactions(path: Path) -> dict[str, Reaction]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        raw: object = json.load(f)
    if not isinstance(raw, dict):
        return {}
    out: dict[str, Reaction] = {}
    for key, value in raw.items():
        if not isinstance(value, dict):
            continue
        try:
            out[str(key)] = Reaction(
                id=str(value.get("id", key)),
                character=str(value.get("character", "case")),
                trigger=str(value.get("trigger", "")),
                text_en=str(value.get("text_en", "")),
                text_ko=str(value.get("text_ko", "")),
                portrait=str(value.get("portrait", "player")),
            )
        except (TypeError, ValueError):
            continue
    return out


def render_story(
    console: tcod.console.Console,
    state: AppState,
    registry: StoryRegistry,
    aftermath_id: str = "aftermath_black_ice",
    *,
    elapsed_s: float = 0.0,
) -> None:
    """Render the Story Event screen in the MAIN region (ADR-0019).

    Shows the aftermath narrative + character reactions. Bilingual
    subtitles (en + ko) per ADR-0019.
    """
    shell = make_shell()
    main = shell[RegionId.MAIN]
    title = shell[RegionId.TITLE]
    side = shell[RegionId.SIDE]
    controls = shell[RegionId.CONTROLS]
    footer = shell[RegionId.FOOTER]

    # Clear
    for r in shell.values():
        clear_region(console, r)
    draw_dividers(console)

    # Title
    draw_title(
        console,
        title,
        title="STORY EVENT — Aftermath",
        subtitle=f"Importance: {state.story_importance or 'major'}  [{elapsed_s:.1f}s]",
    )

    # Main area: narrative
    after = registry.get_aftermath(aftermath_id) or _default_aftermath()
    y = 0
    console.print(
        x=main.x + 2,
        y=main.y + y,
        string="[Narrative]",
        fg=(180, 180, 180),
    )
    y += 1
    for line in after.narrative_en.split("\n"):
        if y >= main.h - 1:
            break
        console.print(
            x=main.x + 2,
            y=main.y + y,
            string=f"> {line[: main.w - 4]}",
            fg=(255, 255, 255),
        )
        y += 1
    y += 1
    if y < main.h - 4:
        console.print(
            x=main.x + 2,
            y=main.y + y,
            string="[한국어 자막]",
            fg=(180, 180, 180),
        )
        y += 1
        for line in after.narrative_ko.split("\n"):
            if y >= main.h - 1:
                break
            console.print(
                x=main.x + 2,
                y=main.y + y,
                string=f"> {line[: main.w - 4]}",
                fg=(255, 220, 100),
            )
            y += 1

    # Reactions (in main area, below narrative)
    y += 1
    if y < main.h - 5:
        console.print(
            x=main.x + 2,
            y=main.y + y,
            string="[Reactions]",
            fg=(180, 180, 180),
        )
        y += 1
        for rid in after.reaction_ids:
            if y >= main.h - 1:
                break
            react = registry.get_reaction(rid)
            if react is None:
                continue
            console.print(
                x=main.x + 2,
                y=main.y + y,
                string=f"[{react.character.title()}]",
                fg=(0, 255, 255),
            )
            y += 1
            console.print(
                x=main.x + 4,
                y=main.y + y,
                string=f"> {react.text_en[: main.w - 6]}",
                fg=(255, 255, 255),
            )
            y += 1
            console.print(
                x=main.x + 4,
                y=main.y + y,
                string=f"> {react.text_ko[: main.w - 6]}",
                fg=(255, 220, 100),
            )
            y += 1

    # Side panel
    draw_side(
        console,
        side,
        label="Context",
        lines=[
            f"Mission: {state.current_mission.title if state.current_mission else 'n/a'}",
            f"Player HP: {state.player_hp}/{state.player_max_hp}",
            f"PPL: {state.player_ppl}",
            f"Grade: {state.player_grade}-up",
        ],
    )

    # Controls
    draw_controls(
        console,
        controls,
        lines=[
            "[Space] Continue  [Esc] Skip  [Q] Quit",
        ],
    )

    # Footer
    draw_footer(
        console,
        footer,
        text=f"Step {state.demo_step}  T+{elapsed_s:.1f}s  Aftermath: {aftermath_id}",
    )


def _default_aftermath() -> Aftermath:
    """Fallback if no data loaded."""
    return Aftermath(
        id="default",
        importance="minor",
        trigger="",
        duration_ms=4000,
        narrative_en="Something happened in the matrix. Static. Silence.",
        narrative_ko="매트릭스에서 무언가가 일어났다. 정적. 침묵.",
        reaction_ids=(),
    )


def handle_story_input(event: object, state: AppState) -> bool:
    """Handle input on the Story Event screen. Returns False to quit."""
    from tcod.event import KeyDown, KeySym

    if not isinstance(event, KeyDown):
        return True
    if event.sym in (KeySym.ESCAPE, KeySym.SPACE, KeySym.RETURN):
        # Resume to hub (or main menu if no mission)
        state.screen = ScreenKind.HUB
        return True
    if event.sym is KeySym.Q:
        return False
    return True
