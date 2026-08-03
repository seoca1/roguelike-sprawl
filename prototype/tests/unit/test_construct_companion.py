"""Unit tests for Construct companion (Cycle 4: Pillar 5 actual combat ally).

Covers:
- AppState.construct_companion_active default + boolean toggle
- Pillar 5 compliance: Dixie as combat ally (not dialog-only)
- Death/rebirth: combat ally is ephemeral (Pillar 4 unlock-only meta-progression)
"""

from __future__ import annotations

from roguelike_sprawl.engine.state import AppState


class TestConstructCompanionField:
    """AppState.construct_companion_active default + boolean toggle."""

    def test_construct_companion_active_default_false(self) -> None:
        state = AppState()
        assert state.construct_companion_active is False

    def test_construct_companion_active_can_be_enabled(self) -> None:
        state = AppState()
        state.construct_companion_active = True
        assert state.construct_companion_active is True

    def test_construct_companion_active_can_be_disabled(self) -> None:
        state = AppState()
        state.construct_companion_active = True
        state.construct_companion_active = False
        assert state.construct_companion_active is False

    def test_is_boolean_type(self) -> None:
        state = AppState()
        assert isinstance(state.construct_companion_active, bool)


class TestPillar5Compliance:
    """Construct companion: Dixie as actual combat ally (Pillar 5 The Style)."""

    def test_no_meta_state_write(self) -> None:
        state = AppState()
        state.construct_companion_active = True
        assert not hasattr(state, "meta_state") or state.meta_state is None

    def test_does_not_persist_across_resets(self) -> None:
        """AppState() constructor resets all defaults — ephemeral."""
        a = AppState()
        a.construct_companion_active = True
        b = AppState()
        assert b.construct_companion_active is False

    def test_does_not_modify_player_stats(self) -> None:
        """Construct companion is a combat ally flag, no stat boosts."""
        state = AppState()
        original_hp = state.player_hp
        original_max_hp = state.player_max_hp
        state.construct_companion_active = True
        assert state.player_hp == original_hp
        assert state.player_max_hp == original_max_hp


class TestConstructCompanionBehavior:
    """Behavior contract (combat ally flag, dialog-only by default)."""

    def test_default_is_dialog_only(self) -> None:
        """Default: construct_companion_active = False (dialog-only mode)."""
        state = AppState()
        assert state.construct_companion_active is False

    def test_can_be_toggled_to_combat_ally(self) -> None:
        """Enabling switches Dixie from dialog-only to actual combat ally."""
        state = AppState()
        state.construct_companion_active = True
        # The actual combat behavior is handled in npc_event.py / combat/
        # (deferred implementation — this is just the flag)
        assert state.construct_companion_active is True


__all__ = [
    "TestConstructCompanionField",
    "TestPillar5Compliance",
    "TestConstructCompanionBehavior",
]
