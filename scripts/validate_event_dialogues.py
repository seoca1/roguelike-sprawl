"""Validate event_dialogues.json structure and content.

Ensures:
- All 5 NPCs present with required fields
- All dialogues have at least 2 lines
- All dialogue lines have speaker + bilingual text
- All choices have key + bilingual text + response

Run: python scripts/validate_event_dialogues.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "design" / "story" / "event_dialogues.json"

REQUIRED_NPCS = ("finn", "dixie", "maelcum", "bartender", "ta_rep")
REQUIRED_NPC_FIELDS = (
    "id",
    "name_en",
    "name_ko",
    "archetype_en",
    "archetype_ko",
    "portrait",
    "voice_tone",
    "voice_tone_ko",
)
REQUIRED_LINE_FIELDS = ("speaker", "speaker_ko", "text_en", "text_ko")
REQUIRED_CHOICE_FIELDS = ("key", "text_en", "text_ko", "response_en", "response_ko")


def fail(msg: str) -> None:
    print(f"  [FAIL] {msg}")
    raise SystemExit(1)


def ok(msg: str) -> None:
    print(f"  [OK] {msg}")


def validate(data: dict) -> None:
    if "npcs" not in data:
        fail("Missing 'npcs' top-level field")
    if "dialogues" not in data:
        fail("Missing 'dialogues' top-level field")
    ok("Top-level structure present")

    # NPCs
    npcs = data["npcs"]
    for nid in REQUIRED_NPCS:
        if nid not in npcs:
            fail(f"Missing NPC: {nid}")
        for f in REQUIRED_NPC_FIELDS:
            if f not in npcs[nid] or not npcs[nid][f]:
                fail(f"npcs.{nid}.{f} missing or empty")
    ok(f"All {len(REQUIRED_NPCS)} NPCs complete")

    # Dialogues
    dialogues = data["dialogues"]
    if len(dialogues) < 5:
        fail(f"Need at least 5 dialogues, got {len(dialogues)}")
    total_lines = 0
    total_choices = 0
    for did, dlg in dialogues.items():
        if "npc" not in dlg or dlg["npc"] not in npcs:
            fail(f"dialogue {did}: npc reference invalid")
        for f in ("id", "npc", "title_en", "title_ko", "context_en", "context_ko", "lines"):
            if f not in dlg:
                fail(f"dialogue {did}: missing {f}")
        if len(dlg["lines"]) < 2:
            fail(f"dialogue {did}: needs at least 2 lines")
        for j, line in enumerate(dlg["lines"]):
            for f in REQUIRED_LINE_FIELDS:
                if f not in line or not line[f]:
                    fail(f"dialogue {did} line {j}: {f} missing/empty")
        total_lines += len(dlg["lines"])

        if "choices" in dlg:
            for k, choice in enumerate(dlg["choices"]):
                for f in REQUIRED_CHOICE_FIELDS:
                    if f not in choice or not choice[f]:
                        fail(f"dialogue {did} choice {k}: {f} missing/empty")
                if not choice["key"].isdigit():
                    fail(f"dialogue {did} choice {k}: key must be digit, got {choice['key']}")
            total_choices += len(dlg["choices"])
    ok(f"All {len(dialogues)} dialogues valid ({total_lines} lines, {total_choices} choices)")

    # Cross-check NPC dialogues
    for did, dlg in dialogues.items():
        npc_id = dlg["npc"]
        npc = npcs[npc_id]
        # At least one line in this dialogue should mention the NPC's name
        all_text = " ".join(line["text_en"] for line in dlg["lines"])
        if dlg.get("choices"):
            all_text += " " + " ".join(c["text_en"] for c in dlg["choices"])
        # Soft check - warn if no name in text
        if npc["name_en"] not in all_text and npc_id != "ta_rep":
            print(f"  [WARN] dialogue {did}: NPC name '{npc['name_en']}' not in text")
    ok("Cross-references checked")


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
