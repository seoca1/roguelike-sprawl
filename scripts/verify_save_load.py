"""Headless verification of save/load flow.

Demonstrates:
- Save current run to a slot
- Modify state
- Load from slot
- Verify state restoration
- List slots
- Delete slot

Usage:
    uv run python scripts/verify_save_load.py
    uv run python scripts/verify_save_load.py --slot 3
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from roguelike_sprawl.engine import (
    AppState,
    SaveManager,
    SaveSlotEmptyError,
)
from roguelike_sprawl.matrix.node import ZoneDepth
from roguelike_sprawl.missions.mission import Mission, Rewards
from roguelike_sprawl.run import Stage, start_run


def _make_state() -> AppState:
    """Build a test state with rich data."""
    state = AppState()
    state.run_state = start_run("first_jack")
    state.run_state.current_stage = Stage.DEFEAT_ICE
    state.run_state.completed_stages = (Stage.MEET_NPC, Stage.EXTRACT_DATA)
    state.run_state.mission_id = "first_jack"
    state.current_mission = Mission(
        id="first_jack",
        title="Test Mission",
        fixer="finn",
        arc=1,
        grade_min=1,
        grade_max=1,
        matrix_seed=42,
        zone=ZoneDepth.SURFACE,
        rewards=Rewards(credits=500, materials={"data_fragment": 2}),
    )
    state.inventory = {"ice_shard": 3, "data_fragment": 1}
    state.credits = 750
    state.current_node_id = "ice1"
    state.defeated_nodes = {"ice1"}
    state.extracted_nodes = {"data1"}
    state.mission_progress = {"defeat": 1, "extract_data": 1}
    state.player_grade = 2
    return state


def verify_save_load(slot: int) -> int:
    """Run the full save/load verification flow."""
    print("=" * 60)
    print("  SAVE/LOAD FLOW VERIFICATION")
    print("=" * 60)
    print()

    # Use a temp directory to not pollute the real save dir
    tmp_dir = Path(tempfile.mkdtemp(prefix="roguelike_save_test_"))
    print(f"[setup] using temp dir: {tmp_dir}")
    manager = SaveManager(save_dir=tmp_dir)
    print()

    # 1. Save
    print(f"[1] Save state to slot {slot}")
    state = _make_state()
    initial_credits = state.credits
    initial_inventory = dict(state.inventory)
    initial_stage = state.run_state.current_stage
    print(f"    credits={initial_credits}, inventory={initial_inventory}")
    print(f"    stage={initial_stage.value}, completed={[s.value for s in state.run_state.completed_stages]}")
    meta = manager.save(slot, state, elapsed_seconds=300)
    print(f"    ✓ saved: size={meta.size_bytes} bytes, compatible={meta.is_compatible}")

    # 2. Modify state
    print()
    print("[2] Modify state (simulate playing)")
    state.credits = 9999
    state.inventory = {}
    state.run_state.current_stage = Stage.PENDING
    print(f"    credits={state.credits}, inventory={state.inventory}")
    print(f"    stage={state.run_state.current_stage.value}")

    # 3. Load
    print()
    print(f"[3] Load from slot {slot}")
    new_state = AppState()
    manager.restore_state(slot, new_state)
    print(f"    credits={new_state.credits}, inventory={new_state.inventory}")
    print(f"    stage={new_state.run_state.current_stage.value}")

    # 4. Verify restoration
    print()
    print("[4] Verify restoration")
    assert new_state.credits == initial_credits, f"credits: {new_state.credits} != {initial_credits}"
    print(f"    ✓ credits restored: {new_state.credits}")
    assert new_state.inventory == initial_inventory
    print(f"    ✓ inventory restored: {new_state.inventory}")
    assert new_state.run_state.current_stage is initial_stage
    print(f"    ✓ stage restored: {new_state.run_state.current_stage.value}")
    assert new_state.run_state.completed_stages == (Stage.MEET_NPC, Stage.EXTRACT_DATA)
    print(f"    ✓ completed stages: {[s.value for s in new_state.run_state.completed_stages]}")
    assert new_state.player_grade == 2
    print(f"    ✓ player_grade: {new_state.player_grade}")
    assert new_state.current_mission is not None
    print(f"    ✓ mission: {new_state.current_mission.id}")

    # 5. List slots
    print()
    print("[5] List all slots")
    slots = manager.list_slots()
    for m in slots:
        if m.exists:
            print(
                f"    slot {m.slot}: stage={m.current_stage}, "
                f"credits={m.credits}, size={m.size_bytes}B, compat={m.is_compatible}"
            )
        else:
            print(f"    slot {m.slot}: empty")

    # 6. Get metadata
    print()
    print(f"[6] Get metadata for slot {slot}")
    meta = manager.get_metadata(slot)
    assert meta.exists
    assert meta.is_compatible
    print(
        f"    version={meta.version}, saved_at={meta.saved_at}, "
        f"mission={meta.mission_id}, stage={meta.current_stage}"
    )

    # 7. Test error cases
    print()
    print("[7] Test error cases")
    # Empty slot
    try:
        manager.load(2)  # Slot 2 is empty
        print("    [FAIL] empty slot should raise")
        return 1
    except SaveSlotEmptyError:
        print("    ✓ empty slot raises SaveSlotEmptyError")

    # 8. Delete
    print()
    print(f"[8] Delete slot {slot}")
    assert manager.delete(slot) is True
    assert manager.has_save(slot) is False
    print(f"    ✓ slot {slot} deleted")

    # 9. Test quick save/load
    print()
    print("[9] Quick save/load (slot 1)")
    qstate = _make_state()
    manager.quick_save(qstate)
    assert manager.has_save(1)
    loaded = AppState()
    manager.quick_load(loaded)
    assert loaded.credits == initial_credits
    print(f"    ✓ quick save/load roundtrip: credits={loaded.credits}")

    # Cleanup
    shutil.rmtree(tmp_dir)

    print()
    print("=" * 60)
    print("  ✅ ALL CHECKS PASSED")
    print("=" * 60)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify save/load flow")
    parser.add_argument(
        "--slot",
        type=int,
        default=1,
        choices=[1, 2, 3, 4, 5],
        help="Which slot to use (default: 1)",
    )
    args = parser.parse_args()
    return verify_save_load(slot=args.slot)


if __name__ == "__main__":
    sys.exit(main())
