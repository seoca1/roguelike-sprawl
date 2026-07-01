"""Tests for the engine ↔ novel hook bridge (ADR-0061).

Verifies that:

1. ``mission_to_stem`` correctly maps mission_ids → short-story stems
   using the live ``missions.json`` and the on-disk short-story corpus.
2. ``trigger_mission_completion_novel_hooks`` actually fires the
   dispatcher (status messages appended; report returned).
3. Missions with no ``story.source`` (or missing files) return
   ``None`` silently — no exceptions raised into gameplay code.
4. The ``NovelRuntime`` cache survives repeated calls (idempotent).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT_PROTOTYPE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_PROTOTYPE / "src"))

from roguelike_sprawl.engine import novel_integration  # noqa: E402
from roguelike_sprawl.engine.novel_integration import (  # noqa: E402
    mission_to_stem,
    reset_novel_runtime_cache,
    trigger_mission_completion_novel_hooks,
)


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    """Reset the module-level cache before every test for isolation."""
    reset_novel_runtime_cache()
    yield
    reset_novel_runtime_cache()


class _FakeStatusList:
    """Mimics the ``StatusMessageList`` interface enough for tests."""

    def __init__(self) -> None:
        self.items: list[str] = []

    def append(self, msg: str) -> None:
        self.items.append(msg)

    def __len__(self) -> int:
        return len(self.items)


class _FakeState:
    """Minimal AppState-like object for novel hook dispatch tests."""

    def __init__(self) -> None:
        self.status_messages = _FakeStatusList()
        self.language = "en"


class TestMissionToStem:
    """``mission_to_stem`` resolves mission_id → short-story stem."""

    def test_known_mission_first_jack(self) -> None:
        stem = mission_to_stem("first_jack")
        assert stem is not None
        assert isinstance(stem, str)
        assert len(stem) > 0

    def test_unknown_mission_returns_none(self) -> None:
        assert mission_to_stem("totally_nonexistent_mission_xyz") is None

    def test_idempotent(self) -> None:
        """Repeated lookups return the same value (cached)."""
        a = mission_to_stem("first_jack")
        b = mission_to_stem("first_jack")
        assert a == b

    def test_resolves_for_at_least_30_missions(self) -> None:
        """All 33 missions have story.source + on-disk files."""
        from roguelike_sprawl.engine.novel_integration import (
            _load_missions_raw,
        )

        raw = _load_missions_raw()
        resolved = sum(1 for mid in raw if mission_to_stem(mid) is not None)
        # Every mission must have a story.source on disk.
        assert resolved == len(raw), f"only {resolved}/{len(raw)} missions resolved"


class TestTriggerMissionCompletionNovelHooks:
    """End-to-end: trigger fires the dispatcher and updates state."""

    def test_returns_none_for_unknown_mission(self) -> None:
        state = _FakeState()
        result = trigger_mission_completion_novel_hooks(state, "no_such_mission_999")
        assert result is None
        # No spurious status messages for unknown missions.
        assert all("Novel" not in m for m in state.status_messages.items)

    def test_fires_hook_for_known_mission(self) -> None:
        state = _FakeState()
        result = trigger_mission_completion_novel_hooks(state, "first_jack")
        assert result is not None
        assert result["ok"] is True
        assert "stem" in result
        assert "kind" in result
        # Status message recorded.
        novel_msgs = [m for m in state.status_messages.items if "Novel" in m]
        assert len(novel_msgs) >= 1

    def test_idempotent_dispatch(self) -> None:
        """Second dispatch for the same mission still succeeds."""
        state = _FakeState()
        first = trigger_mission_completion_novel_hooks(state, "first_jack")
        second = trigger_mission_completion_novel_hooks(state, "first_jack")
        assert first is not None
        assert second is not None
        assert first["stem"] == second["stem"]

    def test_handles_missing_state_status(self) -> None:
        """State without status_messages does not raise."""

        class _NoStatus:
            language = "en"

        # Should NOT raise even without status_messages attribute.
        result = trigger_mission_completion_novel_hooks(_NoStatus(), "first_jack")
        assert result is not None
        assert result["ok"] is True

    def test_uses_korean_language_when_set(self) -> None:
        state = _FakeState()
        state.language = "ko"
        result = trigger_mission_completion_novel_hooks(state, "first_jack")
        assert result is not None
        assert result["ok"] is True
        # The dispatcher itself reads language from app_state; we just
        # assert that the call succeeded end-to-end.

    def test_cache_survives_across_dispatches(self) -> None:
        """Runtime cache is reused (no per-call reload)."""
        trigger_mission_completion_novel_hooks(_FakeState(), "first_jack")
        runtime_a = novel_integration._get_runtime()
        runtime_b = novel_integration._get_runtime()
        assert runtime_a is runtime_b  # identity check


class TestResetNovelRuntimeCache:
    """``reset_novel_runtime_cache`` clears module state for tests."""

    def test_resets_after_use(self) -> None:
        trigger_mission_completion_novel_hooks(_FakeState(), "first_jack")
        assert novel_integration._RUNTIME is not None
        reset_novel_runtime_cache()
        assert novel_integration._RUNTIME is None
        assert novel_integration._MISSIONS_RAW is None
