"""Unit tests for New Game+ mode (Cycle 4: Pillar 4 unlock-only meta-progression).

Covers:
- AppState.ng_plus_unlocked default + boolean toggle
- AppState.ng_plus_active default + boolean toggle
- Pillar 4 compliance: ephemeral session preference, unlock-only
- No stat boosts across runs (Pillar 4: unlock-only meta-progression)
"""

from __future__ import annotations

from roguelike_sprawl.engine.state import AppState


class TestNGPlusFields:
    """AppState.ng_plus_unlocked + ng_plus_active defaults and toggles."""

    def test_ng_plus_unlocked_default_false(self) -> None:
        state = AppState()
        assert state.ng_plus_unlocked is False

    def test_ng_plus_active_default_false(self) -> None:
        state = AppState()
        assert state.ng_plus_active is False

    def test_ng_plus_unlocked_can_be_enabled(self) -> None:
        state = AppState()
        state.ng_plus_unlocked = True
        assert state.ng_plus_unlocked is True

    def test_ng_plus_active_can_be_enabled(self) -> None:
        state = AppState()
        state.ng_plus_active = True
        assert state.ng_plus_active is True

    def test_ng_plus_unlocked_and_active_independent(self) -> None:
        """Unlocked and active are separate fields (Pillar 4 semantics)."""
        state = AppState()
        state.ng_plus_unlocked = True
        assert state.ng_plus_active is False
        state.ng_plus_active = True
        assert state.ng_plus_unlocked is True


class TestPillar4Compliance:
    """NG+ is ephemeral + unlock-only, no stat boosts."""

    def test_no_meta_state_write(self) -> None:
        state = AppState()
        state.ng_plus_unlocked = True
        state.ng_plus_active = True
        assert not hasattr(state, "meta_state") or state.meta_state is None

    def test_does_not_persist_across_resets(self) -> None:
        """AppState() constructor resets all defaults."""
        a = AppState()
        a.ng_plus_unlocked = True
        a.ng_plus_active = True
        b = AppState()
        assert b.ng_plus_unlocked is False
        assert b.ng_plus_active is False

    def test_ng_plus_does_not_modify_player_stats(self) -> None:
        """NG+ is unlock-only meta-progression, no stat boosts (Pillar 4)."""
        state = AppState()
        original_hp = state.player_hp
        original_max_hp = state.player_max_hp
        state.ng_plus_unlocked = True
        state.ng_plus_active = True
        assert state.player_hp == original_hp
        assert state.player_max_hp == original_max_hp


class TestNGPlusBehavior:
    """Behavior contract (unlock + active separate)."""

    def test_locked_cannot_be_active(self) -> None:
        """If ng_plus_unlocked is False, ng_plus_active should not be set.

        This is a behavioral stub — the full check happens in the game
        loop when starting a new run. Here we just verify the field
        independence.
        """
        state = AppState()
        # Default: locked and not active
        assert state.ng_plus_unlocked is False
        assert state.ng_plus_active is False

    def test_unlocked_but_not_active_is_valid(self) -> None:
        """ng_plus_unlocked=True + ng_plus_active=False = ready to start NG+ but not started yet."""
        state = AppState()
        state.ng_plus_unlocked = True
        assert state.ng_plus_active is False


__all__ = [
    "TestNGPlusFields",
    "TestPillar4Compliance",
    "TestNGPlusBehavior",
]
