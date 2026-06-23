"""Tests for graphic novel save/restore (ADR-0044).

Covers:
    - GNProgress dataclass: to_dict/from_dict round-trip
    - save_gn_progress / load_gn_progress / has_gn_save / delete_gn_progress
    - Error cases: missing file, version mismatch, corrupted JSON
    - Atomic write (temp file + rename)
    - get_gn_menu_options: includes CONTINUE READING when save exists
    - get_gn_menu_key: maps selected_index → mode key
    - render_graphic_novel_menu: shows CONTINUE READING when has_save
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import tcod.console  # noqa: E402

from roguelike_sprawl.engine.graphic_novel_save import (  # noqa: E402
    DEFAULT_SAVE_PATH,
    GN_SAVE_VERSION,
    GNProgress,
    GNSaveEmptyError,
    GNSaveVersionMismatchError,
    delete_gn_progress,
    has_gn_save,
    load_gn_progress,
    make_progress,
    save_gn_progress,
)
from roguelike_sprawl.engine.graphic_novel_view import (  # noqa: E402
    GN_MENU_BACK,
    GN_MENU_CONTINUE,
    GN_MENU_HERETIC,
    GN_MENU_NOVICE,
    GN_MENU_PROLOGUE,
    GN_MENU_VETERAN,
    get_gn_menu_key,
    get_gn_menu_options,
    render_graphic_novel_menu,
)
from roguelike_sprawl.i18n import Translator  # noqa: E402

# ============================================================================
# GNProgress dataclass
# ============================================================================


class TestGNProgress:
    def test_minimal_construction(self) -> None:
        p = GNProgress(
            mode="novice",
            scene_index=2,
            dialogue_index=1,
            elapsed_in_dialogue_ms=1500.0,
            character_id="novice",
            chain_length=4,
            saved_at="2026-06-20T12:00:00Z",
        )
        assert p.mode == "novice"
        assert p.scene_index == 2
        assert p.dialogue_index == 1
        assert p.elapsed_in_dialogue_ms == 1500.0
        assert p.session_id  # auto-generated

    def test_session_id_unique(self) -> None:
        p1 = GNProgress(
            mode="novice",
            scene_index=0,
            dialogue_index=0,
            elapsed_in_dialogue_ms=0.0,
            character_id="novice",
            chain_length=4,
            saved_at="",
        )
        p2 = GNProgress(
            mode="novice",
            scene_index=0,
            dialogue_index=0,
            elapsed_in_dialogue_ms=0.0,
            character_id="novice",
            chain_length=4,
            saved_at="",
        )
        assert p1.session_id != p2.session_id

    def test_to_dict_from_dict_round_trip(self) -> None:
        original = GNProgress(
            mode="prologue",
            scene_index=3,
            dialogue_index=2,
            elapsed_in_dialogue_ms=7500.5,
            character_id="veteran",
            chain_length=12,
            saved_at="2026-06-20T15:30:00Z",
            session_id="abc123",
        )
        restored = GNProgress.from_dict(original.to_dict())
        assert restored.mode == original.mode
        assert restored.scene_index == original.scene_index
        assert restored.dialogue_index == original.dialogue_index
        assert restored.elapsed_in_dialogue_ms == original.elapsed_in_dialogue_ms
        assert restored.character_id == original.character_id
        assert restored.chain_length == original.chain_length
        assert restored.saved_at == original.saved_at
        assert restored.session_id == original.session_id


# ============================================================================
# Save/load persistence
# ============================================================================


class TestSaveLoad:
    def test_save_creates_file(self, tmp_path: Path) -> None:
        save_path = tmp_path / "gn_progress.json"
        progress = make_progress(
            mode="novice",
            scene_index=1,
            dialogue_index=0,
            elapsed_in_dialogue_ms=500.0,
            character_id="novice",
            chain_length=4,
        )
        result = save_gn_progress(progress, save_path=save_path)
        assert result == save_path
        assert save_path.exists()

    def test_save_file_is_valid_json(self, tmp_path: Path) -> None:
        save_path = tmp_path / "gn_progress.json"
        progress = make_progress(
            mode="veteran",
            scene_index=2,
            dialogue_index=1,
            elapsed_in_dialogue_ms=2000.0,
            character_id="veteran",
            chain_length=4,
        )
        save_gn_progress(progress, save_path=save_path)
        data = json.loads(save_path.read_text(encoding="utf-8"))
        assert data["version"] == GN_SAVE_VERSION
        assert data["progress"]["mode"] == "veteran"
        assert "saved_at" in data

    def test_load_round_trip(self, tmp_path: Path) -> None:
        save_path = tmp_path / "gn_progress.json"
        original = make_progress(
            mode="heretic",
            scene_index=3,
            dialogue_index=2,
            elapsed_in_dialogue_ms=12000.0,
            character_id="heretic",
            chain_length=4,
        )
        save_gn_progress(original, save_path=save_path)
        loaded = load_gn_progress(save_path=save_path)
        assert loaded.mode == "heretic"
        assert loaded.scene_index == 3
        assert loaded.dialogue_index == 2
        assert loaded.elapsed_in_dialogue_ms == 12000.0
        assert loaded.character_id == "heretic"
        assert loaded.chain_length == 4

    def test_has_gn_save_true_after_save(self, tmp_path: Path) -> None:
        save_path = tmp_path / "gn_progress.json"
        progress = make_progress(
            mode="novice",
            scene_index=0,
            dialogue_index=0,
            elapsed_in_dialogue_ms=0.0,
            character_id="novice",
            chain_length=4,
        )
        save_gn_progress(progress, save_path=save_path)
        assert has_gn_save(save_path=save_path) is True

    def test_has_gn_save_false_when_no_file(self, tmp_path: Path) -> None:
        save_path = tmp_path / "missing.json"
        assert has_gn_save(save_path=save_path) is False

    def test_delete_gn_progress(self, tmp_path: Path) -> None:
        save_path = tmp_path / "gn_progress.json"
        progress = make_progress(
            mode="novice",
            scene_index=0,
            dialogue_index=0,
            elapsed_in_dialogue_ms=0.0,
            character_id="novice",
            chain_length=4,
        )
        save_gn_progress(progress, save_path=save_path)
        assert delete_gn_progress(save_path=save_path) is True
        assert not save_path.exists()
        # Second delete returns False
        assert delete_gn_progress(save_path=save_path) is False


# ============================================================================
# Error handling
# ============================================================================


class TestSaveErrors:
    def test_load_missing_file_raises_empty_error(self, tmp_path: Path) -> None:
        save_path = tmp_path / "missing.json"
        with pytest.raises(GNSaveEmptyError):
            load_gn_progress(save_path=save_path)

    def test_load_version_mismatch_raises(self, tmp_path: Path) -> None:
        save_path = tmp_path / "gn_progress.json"
        # Write a save with wrong version
        payload = {
            "version": "0.0.0-fake",
            "saved_at": "2026-06-20T12:00:00Z",
            "progress": {
                "mode": "novice",
                "scene_index": 0,
                "dialogue_index": 0,
                "elapsed_in_dialogue_ms": 0.0,
                "character_id": "novice",
                "chain_length": 4,
                "saved_at": "",
                "session_id": "x",
            },
        }
        save_path.write_text(json.dumps(payload), encoding="utf-8")
        with pytest.raises(GNSaveVersionMismatchError):
            load_gn_progress(save_path=save_path)

    def test_load_corrupted_json_raises(self, tmp_path: Path) -> None:
        from roguelike_sprawl.engine.graphic_novel_save import GNSaveCorruptedError

        save_path = tmp_path / "gn_progress.json"
        save_path.write_text("not valid json {{", encoding="utf-8")
        with pytest.raises(GNSaveCorruptedError):
            load_gn_progress(save_path=save_path)

    def test_load_progress_missing_uses_defaults(self, tmp_path: Path) -> None:
        """When progress key is missing, GNProgress.from_dict uses defaults.

        This is a soft fallback — the version check has already passed,
        so the load should succeed with default values rather than crash.
        """
        save_path = tmp_path / "gn_progress.json"
        # Missing 'progress' key
        payload = {"version": GN_SAVE_VERSION, "saved_at": "2026-06-20T12:00:00Z"}
        save_path.write_text(json.dumps(payload), encoding="utf-8")
        loaded = load_gn_progress(save_path=save_path)
        assert loaded.mode == "prologue"  # default
        assert loaded.scene_index == 0  # default


# ============================================================================
# Atomic write
# ============================================================================


class TestAtomicWrite:
    def test_no_temp_files_left_on_success(self, tmp_path: Path) -> None:
        save_path = tmp_path / "gn_progress.json"
        progress = make_progress(
            mode="novice",
            scene_index=0,
            dialogue_index=0,
            elapsed_in_dialogue_ms=0.0,
            character_id="novice",
            chain_length=4,
        )
        save_gn_progress(progress, save_path=save_path)
        # No leftover temp files
        temps = list(tmp_path.glob(".gn_progress_*.json"))
        assert temps == []

    def test_overwrite_existing(self, tmp_path: Path) -> None:
        save_path = tmp_path / "gn_progress.json"
        p1 = make_progress(
            mode="novice",
            scene_index=0,
            dialogue_index=0,
            elapsed_in_dialogue_ms=0.0,
            character_id="novice",
            chain_length=4,
        )
        save_gn_progress(p1, save_path=save_path)
        p2 = make_progress(
            mode="veteran",
            scene_index=3,
            dialogue_index=2,
            elapsed_in_dialogue_ms=10000.0,
            character_id="veteran",
            chain_length=4,
        )
        save_gn_progress(p2, save_path=save_path)
        loaded = load_gn_progress(save_path=save_path)
        assert loaded.mode == "veteran"
        assert loaded.scene_index == 3


# ============================================================================
# Default save path
# ============================================================================


class TestDefaultPath:
    def test_default_save_path(self) -> None:
        # Should point to data/saves/gn_progress.json
        assert DEFAULT_SAVE_PATH.name == "gn_progress.json"
        assert "saves" in str(DEFAULT_SAVE_PATH)

    def test_has_save_default_returns_false_initially(self, tmp_path: Path, monkeypatch) -> None:
        # Use a tmp path to avoid clobbering real save

        monkeypatch.setattr(
            "roguelike_sprawl.engine.graphic_novel_save.DEFAULT_SAVE_PATH",
            tmp_path / "gn_progress.json",
        )
        assert has_gn_save() is False


# ============================================================================
# Menu integration
# ============================================================================


class TestGNMenuOptions:
    def test_options_without_save(self) -> None:
        tr = Translator("en", data_dir=Path("data/i18n"))
        options = get_gn_menu_options(tr, has_save=False)
        # 5 options: prologue, novice, veteran, heretic, back
        assert len(options) == 5
        labels = [o[1] for o in options]
        assert "ALL CHARACTERS — 12 scenes" in labels
        assert "BACK TO MAIN MENU" in labels

    def test_options_with_save_includes_continue(self) -> None:
        tr = Translator("en", data_dir=Path("data/i18n"))
        options = get_gn_menu_options(tr, has_save=True)
        # 6 options: continue, prologue, novice, veteran, heretic, back
        assert len(options) == 6
        labels = [o[1] for o in options]
        assert "CONTINUE READING" in labels
        assert "ALL CHARACTERS — 12 scenes" in labels
        # CONTINUE is first
        assert options[0][1] == "CONTINUE READING"

    def test_korean_labels(self) -> None:
        tr = Translator("ko", data_dir=Path("data/i18n"))
        options = get_gn_menu_options(tr, has_save=True)
        labels = [o[1] for o in options]
        assert "이어서 읽기" in labels
        assert "전캐릭터 — 12개 씬 랜덤" in labels
        assert "메인메뉴로" in labels


class TestGNMenuKey:
    def test_no_save_mapping(self) -> None:
        # Without save: 0..3 = modes, 4 = back
        assert get_gn_menu_key(has_save=False, selected_index=0) == GN_MENU_PROLOGUE
        assert get_gn_menu_key(has_save=False, selected_index=1) == GN_MENU_NOVICE
        assert get_gn_menu_key(has_save=False, selected_index=2) == GN_MENU_VETERAN
        assert get_gn_menu_key(has_save=False, selected_index=3) == GN_MENU_HERETIC
        assert get_gn_menu_key(has_save=False, selected_index=4) == GN_MENU_BACK

    def test_with_save_mapping(self) -> None:
        # With save: 0 = continue, 1..4 = modes, 5 = back
        assert get_gn_menu_key(has_save=True, selected_index=0) == GN_MENU_CONTINUE
        assert get_gn_menu_key(has_save=True, selected_index=1) == GN_MENU_PROLOGUE
        assert get_gn_menu_key(has_save=True, selected_index=2) == GN_MENU_NOVICE
        assert get_gn_menu_key(has_save=True, selected_index=3) == GN_MENU_VETERAN
        assert get_gn_menu_key(has_save=True, selected_index=4) == GN_MENU_HERETIC
        assert get_gn_menu_key(has_save=True, selected_index=5) == GN_MENU_BACK


class TestRenderGNMenuWithSave:
    def test_menu_shows_continue_when_save_exists(self) -> None:
        console = tcod.console.Console(80, 50, order="F")
        tr = Translator("en", data_dir=Path("data/i18n"))
        render_graphic_novel_menu(console, tr, selected_index=0, has_save=True)

        def to_text(c: tcod.console.Console) -> str:
            lines = []
            for y in range(c.height):
                chars = []
                for x in range(c.width):
                    code = int(c.ch[x, y])
                    chars.append(chr(code) if 0 < code < 0x110000 else " ")
                lines.append("".join(chars).rstrip())
            return "\n".join(lines)

        full = to_text(console)
        assert "CONTINUE READING" in full
        # And it's highlighted (> marker)
        for y in range(50):
            line = "".join(chr(int(console.ch[x, y])) for x in range(80)).rstrip()
            if "CONTINUE READING" in line:
                assert ">" in line
                break

    def test_menu_hides_continue_when_no_save(self) -> None:
        console = tcod.console.Console(80, 50, order="F")
        tr = Translator("en", data_dir=Path("data/i18n"))
        render_graphic_novel_menu(console, tr, selected_index=0, has_save=False)

        def to_text(c: tcod.console.Console) -> str:
            lines = []
            for y in range(c.height):
                chars = []
                for x in range(c.width):
                    code = int(c.ch[x, y])
                    chars.append(chr(code) if 0 < code < 0x110000 else " ")
                lines.append("".join(chars).rstrip())
            return "\n".join(lines)

        full = to_text(console)
        assert "CONTINUE READING" not in full
        assert "ALL CHARACTERS" in full
