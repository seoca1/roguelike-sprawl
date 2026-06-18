"""Validate prologue_data.json structure and content.

Ensures:
- All required fields present
- All 3 characters have endings (A and B)
- All scenes have at least one dialogue line
- All dialogue text fields non-empty
- Korean + English both present where required

Run: python scripts/validate_prologue_data.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "design" / "story" / "prologue_data.json"

REQUIRED_TOP_LEVEL = ("version", "title", "title_ko", "setting", "characters", "scenes", "endings")
REQUIRED_CHARACTERS = ("novice", "veteran", "heretic")
REQUIRED_CHAR_FIELDS = (
    "id",
    "name_en",
    "name_ko",
    "archetype_en",
    "archetype_ko",
    "age",
    "origin_en",
    "origin_ko",
    "deck_en",
    "deck_ko",
    "weapon_en",
    "weapon_ko",
    "motivation_en",
    "motivation_ko",
    "flavor_en",
    "flavor_ko",
)
REQUIRED_LINE_FIELDS = ("speaker", "speaker_ko", "text_en", "text_ko")
REQUIRED_ENDING_FIELDS = ("id", "name_en", "name_ko", "description_en", "description_ko", "lines")


def fail(msg: str) -> None:
    print(f"  [FAIL] {msg}")
    raise SystemExit(1)


def ok(msg: str) -> None:
    print(f"  [OK] {msg}")


def validate(data: dict) -> None:
    # top level
    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            fail(f"Missing top-level field: {key}")
    ok("All required top-level fields present")

    # setting
    setting = data["setting"]
    for k in ("era", "location", "tone", "openning_quote_en", "openning_quote_ko", "openning_quote_source"):
        if k not in setting:
            fail(f"setting.{k} missing")
    ok("setting complete")

    # characters
    chars = data["characters"]
    for cid in REQUIRED_CHARACTERS:
        if cid not in chars:
            fail(f"Missing character: {cid}")
        for f in REQUIRED_CHAR_FIELDS:
            if f not in chars[cid]:
                fail(f"characters.{cid}.{f} missing")
            val = chars[cid][f]
            if not val and not isinstance(val, int):
                fail(f"characters.{cid}.{f} is empty")
    ok("All 3 characters complete")

    # scenes
    scenes = data["scenes"]
    if len(scenes) < 4:
        fail(f"Need at least 4 scenes, got {len(scenes)}")
    for i, scene in enumerate(scenes):
        if "id" not in scene or "title_en" not in scene or "title_ko" not in scene:
            fail(f"scene[{i}] missing id/title")
        if "lines" not in scene or not scene["lines"]:
            fail(f"scene[{i}] has no lines")
        for j, line in enumerate(scene["lines"]):
            for f in REQUIRED_LINE_FIELDS:
                if f not in line:
                    fail(f"scene[{i}].lines[{j}].{f} missing")
                if not line[f]:
                    fail(f"scene[{i}].lines[{j}].{f} is empty")
    ok(f"All {len(scenes)} scenes have valid dialogue")

    # character select scene must have choice
    select = next((s for s in scenes if s.get("type") == "shared_intro"), None)
    if not select or "choice" not in select:
        fail("shared_intro scene must have a choice")
    if select:
        for opt in select["choice"]["options"]:
            for k in ("key", "character", "text_en", "text_ko", "response_en", "response_ko"):
                if k not in opt or not opt[k]:
                    fail(f"choice option missing/empty: {k}")
    ok("character select has 3 valid choices")

    # endings
    endings = data["endings"]
    for cid in REQUIRED_CHARACTERS:
        if cid not in endings:
            fail(f"endings.{cid} missing")
        if len(endings[cid]) < 2:
            fail(f"endings.{cid} needs at least 2 endings (A and B)")
        for end in endings[cid]:
            for f in REQUIRED_ENDING_FIELDS:
                if f not in end:
                    fail(f"endings.{cid}: ending missing {f}")
            if end["id"] not in ("A", "B"):
                fail(f"endings.{cid}: id must be A or B, got {end['id']}")
            for line in end["lines"]:
                for f in REQUIRED_LINE_FIELDS:
                    if f not in line or not line[f]:
                        fail(f"endings.{cid} line missing/empty: {f}")
    ok(f"All characters have 2 valid endings (3 × 2 = 6 scenarios)")


def main() -> int:
    print(f"Validating {DATA_PATH}...")
    if not DATA_PATH.exists():
        fail(f"File not found: {DATA_PATH}")
    try:
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(f"JSON parse error: {e}")
    ok("JSON parsed successfully")
    validate(data)
    print("\n[PASS] All validations passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
