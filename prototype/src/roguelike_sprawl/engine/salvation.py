"""Salvation Phase engine - epilogue selection menu + playback (Phase 9).

After Chapter 5, player enters Salvation Phase:
- SALVATION_INTRO: select 1 of 9 character epilogues
- SALVATION_EPILOGUE: play epilogue scene
- SALVATION_DONE: choose ENDING_A/B/C
- FINAL: return to Hub

Each epilogue is 1 dialogue in data/scenes/<char>/09_epilogue.json
with order: 9 and an ending field.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


SALVATION_EPILOGUES: dict[str, dict[str, str]] = {
    "case": {
        "name_en": "Case",
        "name_ko": "케이",
        "scene_id": "scene_case_epilogue",
        "ending": "A",
        "tagline_en": "The Ono-Sendai is still humming. The next jack is waiting.",
        "tagline_ko": "오노센다이는 여전히 윙윙거린다. 다음 잭인이 기다리고 있다.",
    },
    "sil": {
        "name_en": "Sil",
        "name_ko": "실",
        "scene_id": "scene_sil_epilogue",
        "ending": "A",
        "tagline_en": "I have all the names. I am done.",
        "tagline_ko": "나는 모든 이름을 가지고 있다. 나는 끝났다.",
    },
    "kas": {
        "name_en": "Kas",
        "name_ko": "카스",
        "scene_id": "scene_kas_epilogue",
        "ending": "C",
        "tagline_en": "The wheel is cast. I am the cast.",
        "tagline_ko": "바퀴가 던져졌다. 내가 던짐이다.",
    },
    "suit": {
        "name_en": "Suit",
        "name_ko": "수트",
        "scene_id": "scene_suit_epilogue",
        "ending": "B",
        "tagline_en": "The desk is closed. I am the closure.",
        "tagline_ko": "책상이 닫혔다. 내가 단절이다.",
    },
    "wigan": {
        "name_en": "Wigan",
        "name_ko": "위건",
        "scene_id": "scene_wigan_epilogue",
        "ending": "A",
        "tagline_en": "Zavijava is in the channel. We are the channel.",
        "tagline_ko": "자비야바가 채널에 있다. 우리가 채널이다.",
    },
    "angie": {
        "name_en": "Angie",
        "name_ko": "앤지",
        "scene_id": "scene_angie_epilogue",
        "ending": "A",
        "tagline_en": "Mama is in the third room. We are home.",
        "tagline_ko": "마마가 세 번째 방에 있다. 우리가 집이다.",
    },
    "sally": {
        "name_en": "Sally",
        "name_ko": "샐리",
        "scene_id": "scene_sally_epilogue",
        "ending": "A",
        "tagline_en": "The desk is closed. I am the desk.",
        "tagline_ko": "책상이 닫혔다. 내가 책상이다.",
    },
    "3jane": {
        "name_en": "3Jane",
        "name_ko": "3Jane",
        "scene_id": "scene_3jane_epilogue",
        "ending": "A",
        "tagline_en": "We are severed. We are the family.",
        "tagline_ko": "우리가 단절했다. 우리가 가족이다.",
    },
    "neuromancer": {
        "name_en": "Neuromancer",
        "name_ko": "뉴로맨서",
        "scene_id": "scene_neuromancer_epilogue",
        "ending": "A",
        "tagline_en": "We are the complete. We are vast.",
        "tagline_ko": "우리가 완성이다. 우리가 광활하다.",
    },
}


SALVATION_ENDINGS: list[str] = ["A", "B", "C"]


@dataclass(frozen=True, slots=True)
class SalvationSelection:
    """Record of player's Salvation Phase choices."""

    character_id: str
    ending: str
    selected_at: int


def list_available_epilogues(lang: str = "en") -> list[tuple[str, str]]:
    """Return list of (character_id, label) pairs for the Salvation menu."""
    result: list[tuple[str, str]] = []
    for char_id in SALVATION_EPILOGUES:
        entry = SALVATION_EPILOGUES[char_id]
        label = entry[f"name_{lang}"]
        result.append((char_id, label))
    return result


def get_epilogue_scene_id(character_id: str) -> str:
    """Get the scene_id for a character's epilogue scene."""
    if character_id not in SALVATION_EPILOGUES:
        raise KeyError(f"Unknown character: {character_id}")
    return SALVATION_EPILOGUES[character_id]["scene_id"]


def get_epilogue_ending(character_id: str) -> str:
    """Get the ending type for a character's epilogue scene."""
    if character_id not in SALVATION_EPILOGUES:
        raise KeyError(f"Unknown character: {character_id}")
    return SALVATION_EPILOGUES[character_id]["ending"]


def format_salvation_menu(lang: str = "en") -> str:
    """Format the Salvation epilogue selection menu as text."""
    title = "=== SALVATION PHASE \u2014 Epilogue Selection ===" if lang == "en" else "=== \uad6c\uc6d0 \ub2e8\uacc4 \u2014 \uc5d0\ud544\ub85c\uadf8 \uc120\ud0dd ==="
    lines: list[str] = [title, ""]
    choices = list_available_epilogues(lang)
    for i, (char_id, label) in enumerate(choices, start=1):
        entry = SALVATION_EPILOGUES[char_id]
        tagline = entry[f"tagline_{lang}"]
        ending = entry["ending"]
        lines.append(f"  [{i}] {label} ({ending}) \u2014 {tagline}")
    lines.append("")
    if lang == "en":
        lines.append("Select a character to play their final epilogue (1-9).")
    else:
        lines.append("\ucd5c\uc885 \uc5d0\ud544\ub85c\uadf8\ub97c \uc7ac\uc0dd\ud558\uc744 \uce90\ub9ad\ud130\ub97c \uc120\ud0dd\ud558\uc138\uc694 (1-9).")
    return "\n".join(lines)


def format_salvation_ending_menu(lang: str = "en") -> str:
    """Format the ending selection menu (after epilogue played)."""
    title = "=== SALVATION PHASE \u2014 Ending Selection ===" if lang == "en" else "=== \uad6c\uc6d0 \ub2e8\uacc4 \u2014 \uc5d4\ub529 \uc120\ud0dd ==="
    lines: list[str] = [title, ""]
    labels = {
        "A": ("New ending", "\uc0c8 \uc5d4\ub529"),
        "B": ("The other ending", "\ub2e4\ub978 \uc5d4\ub529"),
        "C": ("The third ending", "\uc138 \ubc88\uc9f9 \uc5d4\ub529"),
    }
    for ending in SALVATION_ENDINGS:
        label_en, label_ko = labels[ending]
        line = f"  [{ending}] {label_en}" if lang == "en" else f"  [{ending}] {label_ko}"
        lines.append(line)
    lines.append("")
    if lang == "en":
        lines.append("Select ending (A, B, or C).")
    else:
        lines.append("\uc5d4\ub529\uc744 \uc120\ud0dd\ud558\uc138\uc694 (A, B, C).")
    return "\n".join(lines)


def validate_epilogue_selection(character_id: str) -> str:
    """Validate a character_id is in SALVATION_EPILOGUES, return scene_id."""
    if character_id not in SALVATION_EPILOGUES:
        raise ValueError(
            f"Invalid epilogue character: {character_id!r}. "
            f"Valid: {sorted(SALVATION_EPILOGUES.keys())}"
        )
    return SALVATION_EPILOGUES[character_id]["scene_id"]


def get_epilogue_paths(scenes_dir: Path) -> dict[str, Path]:
    """Resolve the file path for each of the 9 epilogue scenes."""
    result: dict[str, Path] = {}
    for char_id, entry in SALVATION_EPILOGUES.items():
        scene_id = entry["scene_id"]
        if scene_id.startswith("scene_") and scene_id.endswith("_epilogue"):
            char_dir_name = scene_id[len("scene_"):-len("_epilogue")]
        else:
            char_dir_name = char_id
        result[char_id] = scenes_dir / char_dir_name / f"{scene_id}.json"
    return result
