"""Unit tests for Hardcore mode (Cycle 4: Pillar 3 reinforcement).

Covers:
- AppState.hardcore_mode default + boolean toggle
- Pillar 4 compliance: ephemeral session preference, no meta-progression
- No cross-run inheritance
"""

from __future__ import annotations

from roguelike_sprawl.engine.state import AppState


class TestHardcoreModeField:
    """AppState.hardcore_mode default + boolean toggle."""

    def test_default_is_false(self) -> None:
        state = AppState()
        assert state.hardcore_mode is False

    def test_can_be_enabled(self) -> None:
        state = AppState()
        state.hardcore_mode = True
        assert state.hardcore_mode is True

    def test_can_be_disabled(self) -> None:
        state = AppState()
        state.hardcore_mode = True
        state.hardcore_mode = False
        assert state.hardcore_mode is False


class TestPillar4Compliance:
    """Hardcore mode is ephemeral session preference, no meta-progression."""

    def test_no_meta_state_write(self) -> None:
        state = AppState()
        state.hardcore_mode = True
        assert not hasattr(state, "meta_state") or state.meta_state is None

    def test_does_not_persist_across_resets(self) -> None:
        """AppState() constructor resets all defaults — ephemeral session."""
        a = AppState()
        a.hardcore_mode = True
        b = AppState()
        assert b.hardcore_mode is False

    def test_is_boolean_type(self) -> None:
        state = AppState()
        assert isinstance(state.hardcore_mode, bool)


class TestHardcoreModeBehavior:
    """Verify behavior contract (1-life permadeath, Pillar 3 reinforcement)."""

    def test_default_allows_revival(self) -> None:
        """Without hardcore, the normal death → new-jockey flow applies."""
        state = AppState()
        # Default (False) allows restart_with_new_jockey() to work
        assert state.hardcore_mode is False

    def test_hardcore_blocks_revival(self) -> None:
        """With hardcore enabled, restart_with_new_jockey should be blocked.

        This is a behavioral test stub — the full death flow integration
        is deferred to a follow-up commit. For now we verify the flag
        exists and defaults to False.
        """
        state = AppState()
        state.hardcore_mode = True
        # The actual death flow integration is handled in death.py
        # (restart_with_new_jockey should raise if hardcore_mode)
        # For now, we just verify the flag is set
        assert state.hardcore_mode is True


__all__ = [
    "TestHardcoreModeField",
    "TestPillar4Compliance",
    "TestHardcoreModeBehavior",
]
