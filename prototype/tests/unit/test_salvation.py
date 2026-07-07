"""Tests for Salvation Phase engine (Phase 9).

Salvation Phase is entered after Chapter 5 completion:
- SALVATION_INTRO: select 1 of 9 character epilogues
- SALVATION_EPILOGUE: play epilogue scene
- SALVATION_DONE: choose ENDING_A/B/C
- FINAL: return to Hub
"""

from __future__ import annotations

from pathlib import Path

import pytest

from roguelike_sprawl.engine.salvation import (
    SALVATION_ENDINGS,
    SALVATION_EPILOGUES,
    SalvationSelection,
    format_salvation_ending_menu,
    format_salvation_menu,
    get_epilogue_ending,
    get_epilogue_paths,
    get_epilogue_scene_id,
    list_available_epilogues,
    validate_epilogue_selection,
)


class TestSalvationEpilogues:
    """SALVATION_EPILOGUES dict structure."""

    def test_all_nine_characters_defined(self) -> None:
        assert len(SALVATION_EPILOGUES) == 9

    def test_all_keys_are_character_ids(self) -> None:
        expected = {"case", "sil", "kas", "suit", "wigan", "angie", "sally", "3jane", "neuromancer"}
        assert set(SALVATION_EPILOGUES.keys()) == expected

    def test_all_entries_have_required_fields(self) -> None:
        required = {"name_en", "name_ko", "scene_id", "ending", "tagline_en", "tagline_ko"}
        for char_id, entry in SALVATION_EPILOGUES.items():
            missing = required - set(entry.keys())
            assert not missing, f"{char_id} missing fields: {missing}"

    def test_all_scene_ids_end_with_epilogue(self) -> None:
        for char_id, entry in SALVATION_EPILOGUES.items():
            assert entry["scene_id"].endswith("_epilogue"), (
                f"{char_id} scene_id should end with _epilogue: {entry['scene_id']}"
            )

    def test_all_endings_are_valid(self) -> None:
        for char_id, entry in SALVATION_EPILOGUES.items():
            assert entry["ending"] in SALVATION_ENDINGS, (
                f"{char_id} ending {entry['ending']} not in {SALVATION_ENDINGS}"
            )


class TestSalvationEndings:
    """SALVATION_ENDINGS list."""

    def test_three_endings(self) -> None:
        assert SALVATION_ENDINGS == ["A", "B", "C"]


class TestListAvailableEpilogues:
    """list_available_epilogues function."""

    def test_default_english(self) -> None:
        result = list_available_epilogues()
        assert len(result) == 9
        # First entry should be case
        assert result[0][0] == "case"
        # All entries have non-empty labels
        for char_id, label in result:
            assert len(label) > 0

    def test_korean_labels(self) -> None:
        result = list_available_epilogues(lang="ko")
        for char_id, label in result:
            # Korean labels: case=케이, sil=실, etc.
            assert char_id in SALVATION_EPILOGUES


class TestGetEpilogueSceneId:
    """get_epilogue_scene_id function."""

    def test_known_character(self) -> None:
        assert get_epilogue_scene_id("case") == "scene_case_epilogue"
        assert get_epilogue_scene_id("sally") == "scene_sally_epilogue"
        assert get_epilogue_scene_id("neuromancer") == "scene_neuromancer_epilogue"

    def test_unknown_raises_keyerror(self) -> None:
        with pytest.raises(KeyError):
            get_epilogue_scene_id("nonexistent")


class TestGetEpilogueEnding:
    """get_epilogue_ending function."""

    def test_known_character(self) -> None:
        assert get_epilogue_ending("kas") == "C"
        assert get_epilogue_ending("suit") == "B"
        assert get_epilogue_ending("case") == "A"

    def test_unknown_raises_keyerror(self) -> None:
        with pytest.raises(KeyError):
            get_epilogue_ending("nonexistent")


class TestFormatSalvationMenu:
    """format_salvation_menu function."""

    def test_english_contains_all_characters(self) -> None:
        menu = format_salvation_menu("en")
        for char_id in SALVATION_EPILOGUES:
            assert char_id.upper() in menu.upper() or SALVATION_EPILOGUES[char_id]["name_en"] in menu

    def test_korean_contains_korean_names(self) -> None:
        menu = format_salvation_menu("ko")
        assert "케이" in menu  # Case Korean
        assert "샐리" in menu  # Sally Korean

    def test_ends_with_prompt(self) -> None:
        menu = format_salvation_menu("en")
        assert "Select" in menu


class TestFormatSalvationEndingMenu:
    """format_salvation_ending_menu function."""

    def test_english_shows_a_b_c(self) -> None:
        menu = format_salvation_ending_menu("en")
        assert "[A]" in menu
        assert "[B]" in menu
        assert "[C]" in menu

    def test_korean_shows_a_b_c(self) -> None:
        menu = format_salvation_ending_menu("ko")
        assert "[A]" in menu
        assert "[B]" in menu
        assert "[C]" in menu


class TestValidateEpilogueSelection:
    """validate_epilogue_selection function."""

    def test_valid_returns_scene_id(self) -> None:
        assert validate_epilogue_selection("case") == "scene_case_epilogue"

    def test_invalid_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="Invalid epilogue character"):
            validate_epilogue_selection("nonexistent")


class TestGetEpiloguePaths:
    """get_epilogue_paths function."""

    def test_returns_nine_paths(self, tmp_path: Path) -> None:
        # Create 9 character directories with epilogue files
        for char_id in SALVATION_EPILOGUES:
            char_dir = tmp_path / char_id
            char_dir.mkdir()
            (char_dir / f"scene_{char_id}_epilogue.json").write_text("{}")
        paths = get_epilogue_paths(tmp_path)
        assert len(paths) == 9

    def test_paths_use_scene_id_pattern(self, tmp_path: Path) -> None:
        paths = get_epilogue_paths(tmp_path)
        assert paths["case"] == tmp_path / "case" / "scene_case_epilogue.json"
        assert paths["neuromancer"] == tmp_path / "neuromancer" / "scene_neuromancer_epilogue.json"

    def test_paths_constructed_even_if_files_missing(self, tmp_path: Path) -> None:
        # Don't create any files, just construct paths
        paths = get_epilogue_paths(tmp_path)
        # All 9 paths should be returned regardless
        assert len(paths) == 9
        assert not paths["case"].exists()


class TestSalvationSelection:
    """SalvationSelection dataclass."""

    def test_create(self) -> None:
        s = SalvationSelection(character_id="case", ending="A", selected_at=1)
        assert s.character_id == "case"
        assert s.ending == "A"
        assert s.selected_at == 1

    def test_frozen(self) -> None:
        s = SalvationSelection(character_id="case", ending="A", selected_at=1)
        with pytest.raises(Exception):
            s.character_id = "sally"  # type: ignore[misc]
