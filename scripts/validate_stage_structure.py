"""Validate stage_structure.json structure and content.

Ensures:
- All 6 stages present (pending, meet_npc, extract_data, defeat_ice, complete, failed)
- All transitions reference valid stages
- All missions reference valid stage ids
- Death flow has steps
- Hub loop has ASCII art

Run: python scripts/validate_stage_structure.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "design" / "systems" / "stage_structure.json"

REQUIRED_STAGES = (
    "pending",
    "meet_npc",
    "extract_data",
    "defeat_ice",
    "complete",
    "failed",
)
REQUIRED_STAGE_FIELDS = (
    "id",
    "name_en",
    "name_ko",
    "type",
    "is_terminal",
    "objective_kind",
    "description_en",
    "description_ko",
    "ascii_art",
)
REQUIRED_TRANSITION_FIELDS = ("from", "to", "trigger_en", "trigger_ko", "system")
REQUIRED_MISSION_FIELDS = (
    "id",
    "title_en",
    "title_ko",
    "fixer",
    "arc",
    "stages",
    "primary_objective_en",
    "primary_objective_ko",
    "rewards",
)


def fail(msg: str) -> None:
    print(f"  [FAIL] {msg}")
    raise SystemExit(1)


def ok(msg: str) -> None:
    print(f"  [OK] {msg}")


def validate(data: dict) -> None:
    if "stages" not in data:
        fail("Missing 'stages' top-level field")
    if "transitions" not in data:
        fail("Missing 'transitions' top-level field")
    if "missions" not in data:
        fail("Missing 'missions' top-level field")
    ok("Top-level structure present")

    # Stages
    stages = data["stages"]
    stage_ids = {s["id"] for s in stages}
    for sid in REQUIRED_STAGES:
        if sid not in stage_ids:
            fail(f"Missing required stage: {sid}")
    for stage in stages:
        for f in REQUIRED_STAGE_FIELDS:
            if f not in stage:
                fail(f"stage {stage.get('id', '?')}: missing {f}")
        if not stage["ascii_art"]:
            fail(f"stage {stage['id']}: empty ascii_art")
    ok(f"All {len(stages)} stages valid (including {len(REQUIRED_STAGES)} required)")

    # Stage IDs unique
    assert len(stage_ids) == len(stages), "Duplicate stage ids"
    ok("All stage ids unique")

    # Transitions
    transitions = data["transitions"]
    for i, t in enumerate(transitions):
        for f in REQUIRED_TRANSITION_FIELDS:
            if f not in t:
                fail(f"transition {i}: missing {f}")
        if t["from"] != "any" and t["from"] not in stage_ids:
            fail(f"transition {i}: from '{t['from']}' not a valid stage")
        if t["to"] not in stage_ids:
            fail(f"transition {i}: to '{t['to']}' not a valid stage")
    ok(f"All {len(transitions)} transitions valid")

    # Verify each non-terminal stage has a transition out
    non_terminal = [s for s in stages if not s["is_terminal"]]
    for s in non_terminal:
        if s["id"] == "pending":
            # Has multiple out-transitions (one per mission)
            continue
        has_out = any(t["from"] == s["id"] for t in transitions)
        if not has_out:
            fail(f"non-terminal stage '{s['id']}' has no outgoing transition")
    ok("All non-terminal stages have transitions")

    # Missions
    missions = data["missions"]
    if len(missions) < 1:
        fail("Need at least 1 mission")
    for m in missions:
        for f in REQUIRED_MISSION_FIELDS:
            if f not in m:
                fail(f"mission {m.get('id', '?')}: missing {f}")
        for stage_id in m["stages"]:
            if stage_id not in stage_ids:
                fail(f"mission {m['id']}: stage '{stage_id}' not valid")
        if not m["stages"]:
            fail(f"mission {m['id']}: no stages")
    ok(f"All {len(missions)} missions valid")

    # Death flow
    if "death_flow" not in data:
        fail("Missing 'death_flow'")
    else:
        df = data["death_flow"]
        if "steps" not in df or not df["steps"]:
            fail("death_flow must have steps")
        for step in df["steps"]:
            for f in ("id", "name_en", "name_ko", "description_en", "description_ko"):
                if f not in step:
                    fail(f"death_flow step: missing {f}")
    ok("Death flow valid")

    # Hub loop
    if "hub_loop" not in data:
        fail("Missing 'hub_loop'")
    else:
        hl = data["hub_loop"]
        if "ascii_art" not in hl or not hl["ascii_art"]:
            fail("hub_loop must have ascii_art")
    ok("Hub loop valid")


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
