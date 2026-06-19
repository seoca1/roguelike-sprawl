"""Tests for game settings (settings.py).

Validates:
- GameSettings defaults (quiet volume, KEYS off, etc.)
- 4 enums (ColorTheme, GlyphStyle, Language, SubtitleMode, Difficulty)
- Validation + apply_fixes
- Reset / clone
- JSON roundtrip (to_dict / from_dict)
- File save/load
- Apply to audio/combo/difficulty systems
- Settings summary
- About info
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from roguelike_sprawl.settings import (
    GAME_AUTHOR,
    GAME_NAME,
    GAME_VERSION,
    ColorTheme,
    Difficulty,
    GameSettings,
    GlyphStyle,
    Language,
    SubtitleMode,
    apply_audio_settings,
    apply_combo_settings,
    apply_difficulty_settings,
    apply_fixes,
    clone_settings,
    get_about_info,
    get_default_settings,
    get_settings_summary,
    load_settings_from_file,
    reset_settings,
    save_settings_to_file,
    settings_from_dict,
    settings_to_dict,
    validate_settings,
)

# ----------------------------------------------------------------------------
# Defaults
# ----------------------------------------------------------------------------


class TestDefaults:
    def test_default_master_volume(self) -> None:
        s = get_default_settings()
        # Quiet default (per project preference)
        assert s.master_volume == 0.2

    def test_default_keys_off(self) -> None:
        s = get_default_settings()
        # Per user request
        assert s.sound_categories["keys"] is False

    def test_default_sound_categories(self) -> None:
        s = get_default_settings()
        # 5 of 6 categories on by default
        on_count = sum(1 for v in s.sound_categories.values() if v)
        assert on_count == 5

    def test_default_language(self) -> None:
        s = get_default_settings()
        assert s.language == "both"

    def test_default_subtitle_mode(self) -> None:
        s = get_default_settings()
        assert s.subtitle_mode == "subtitle"

    def test_default_difficulty(self) -> None:
        s = get_default_settings()
        assert s.difficulty == "normal"

    def test_default_combo_window(self) -> None:
        s = get_default_settings()
        assert s.combo_window_ms == 3500

    def test_default_auto_save(self) -> None:
        s = get_default_settings()
        assert s.auto_save is True


# ----------------------------------------------------------------------------
# Enums
# ----------------------------------------------------------------------------


class TestEnums:
    def test_color_themes(self) -> None:
        assert ColorTheme.MATRIX.value == "matrix"
        assert ColorTheme.CYBERPUNK.value == "cyberpunk"
        assert ColorTheme.MONO.value == "mono"
        assert len(ColorTheme) == 3

    def test_glyph_styles(self) -> None:
        assert GlyphStyle.ASCII.value == "ascii"
        assert GlyphStyle.UNICODE.value == "unicode"

    def test_languages(self) -> None:
        assert Language.KOREAN.value == "ko"
        assert Language.ENGLISH.value == "en"
        assert Language.BOTH.value == "both"
        assert len(Language) == 3

    def test_subtitle_modes(self) -> None:
        assert SubtitleMode.OFF.value == "off"
        assert SubtitleMode.SUBTITLE.value == "subtitle"
        assert SubtitleMode.REPLACE.value == "replace"

    def test_difficulties(self) -> None:
        assert Difficulty.EASY.value == "easy"
        assert Difficulty.NORMAL.value == "normal"
        assert Difficulty.HARD.value == "hard"
        assert Difficulty.NIGHTMARE.value == "nightmare"
        assert len(Difficulty) == 4


# ----------------------------------------------------------------------------
# Validation
# ----------------------------------------------------------------------------


class TestValidation:
    def test_default_valid(self) -> None:
        s = get_default_settings()
        assert validate_settings(s) == []

    def test_invalid_volume(self) -> None:
        s = GameSettings(master_volume=5.0)
        errors = validate_settings(s)
        assert any("master_volume" in e for e in errors)

    def test_invalid_combo_window(self) -> None:
        s = GameSettings(combo_window_ms=999999)
        errors = validate_settings(s)
        assert any("combo_window_ms" in e for e in errors)

    def test_invalid_color_theme(self) -> None:
        s = GameSettings(color_theme="invalid")
        errors = validate_settings(s)
        assert any("color_theme" in e for e in errors)

    def test_invalid_difficulty(self) -> None:
        s = GameSettings(difficulty="ultra_hard")
        errors = validate_settings(s)
        assert any("difficulty" in e for e in errors)

    def test_apply_fixes_clamps_volume(self) -> None:
        s = GameSettings(master_volume=5.0)
        apply_fixes(s)
        assert s.master_volume == 1.0

    def test_apply_fixes_clamps_combo(self) -> None:
        s = GameSettings(combo_window_ms=999999)
        apply_fixes(s)
        assert s.combo_window_ms == 10000

    def test_apply_fixes_resets_invalid_enum(self) -> None:
        s = GameSettings(color_theme="invalid")
        apply_fixes(s)
        assert s.color_theme == "matrix"

    def test_apply_fixes_resets_invalid_difficulty(self) -> None:
        s = GameSettings(difficulty="ultra_hard")
        apply_fixes(s)
        assert s.difficulty == "normal"


# ----------------------------------------------------------------------------
# Reset / clone
# ----------------------------------------------------------------------------


class TestResetClone:
    def test_reset_to_defaults(self) -> None:
        s = GameSettings(master_volume=1.0, difficulty="nightmare")
        reset_settings(s)
        assert s.master_volume == 0.2
        assert s.difficulty == "normal"

    def test_clone_independent(self) -> None:
        s = GameSettings(master_volume=0.5)
        s2 = clone_settings(s)
        s2.master_volume = 1.0
        # Original unchanged
        assert s.master_volume == 0.5
        assert s2.master_volume == 1.0

    def test_clone_deep_copies_sound_categories(self) -> None:
        s = GameSettings()
        s2 = clone_settings(s)
        s2.sound_categories["keys"] = True
        # Original unchanged
        assert s.sound_categories["keys"] is False


# ----------------------------------------------------------------------------
# JSON serialization
# ----------------------------------------------------------------------------


class TestJSONSerialization:
    def test_to_dict_has_all_categories(self) -> None:
        s = get_default_settings()
        d = settings_to_dict(s)
        assert "audio" in d
        assert "display" in d
        assert "input" in d
        assert "language" in d
        assert "gameplay" in d
        assert "schema_version" in d

    def test_from_dict_default(self) -> None:
        s = settings_from_dict({})
        # Should return valid defaults
        assert validate_settings(s) == []

    def test_from_dict_ignores_invalid_keys(self) -> None:
        s = settings_from_dict(
            {
                "audio": {"master_volume": 0.5, "INVALID": "ignored"},
                "display": {"color_theme": "matrix"},
            }
        )
        assert s.master_volume == 0.5
        assert s.color_theme == "matrix"

    def test_roundtrip_preserves_values(self) -> None:
        s = GameSettings(
            master_volume=0.7,
            difficulty="hard",
            language="ko",
            color_theme="cyberpunk",
        )
        d = settings_to_dict(s)
        s2 = settings_from_dict(d)
        assert s2.master_volume == 0.7
        assert s2.difficulty == "hard"
        assert s2.language == "ko"
        assert s2.color_theme == "cyberpunk"

    def test_from_dict_fixes_invalid(self) -> None:
        s = settings_from_dict(
            {
                "audio": {"master_volume": 99.0},
                "gameplay": {"difficulty": "INVALID"},
            }
        )
        # Fixes applied
        assert s.master_volume == 1.0
        assert s.difficulty == "normal"


# ----------------------------------------------------------------------------
# File save/load
# ----------------------------------------------------------------------------


class TestFilePersistence:
    def test_save_and_load(self) -> None:
        s = get_default_settings()
        s.master_volume = 0.7
        s.difficulty = "hard"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            tmp_path = Path(f.name)
        try:
            assert save_settings_to_file(s, tmp_path, current_ms=1000) is True
            s2 = load_settings_from_file(tmp_path)
            assert s2.master_volume == 0.7
            assert s2.difficulty == "hard"
            assert s2.last_modified_ms == 1000
        finally:
            tmp_path.unlink()

    def test_load_missing_returns_defaults(self) -> None:
        s = load_settings_from_file(Path("/nonexistent/path/settings.json"))
        assert validate_settings(s) == []

    def test_load_corrupted_returns_defaults(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("NOT VALID JSON {{{")
            tmp_path = Path(f.name)
        try:
            s = load_settings_from_file(tmp_path)
            assert validate_settings(s) == []
        finally:
            tmp_path.unlink()

    def test_save_creates_parent_dirs(self) -> None:
        s = get_default_settings()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "subdir" / "settings.json"
            assert save_settings_to_file(s, path) is True
            assert path.exists()


# ----------------------------------------------------------------------------
# Apply to systems
# ----------------------------------------------------------------------------


class TestApplyAudio:
    def test_default_audio(self) -> None:
        s = get_default_settings()
        applied = apply_audio_settings(s)
        assert applied["master_volume"] == 0.2
        assert applied["muted"] is False

    def test_muted_returns_zero_volume(self) -> None:
        s = get_default_settings()
        s.muted = True
        applied = apply_audio_settings(s)
        assert applied["master_volume"] == 0.0
        assert applied["muted"] is True

    def test_categories_passed_through(self) -> None:
        s = get_default_settings()
        applied = apply_audio_settings(s)
        assert "keys" in applied["categories"]
        assert applied["categories"]["keys"] is False  # Per user request

    def test_relative_volumes(self) -> None:
        s = get_default_settings()
        s.master_volume = 1.0
        s.music_volume = 0.5
        applied = apply_audio_settings(s)
        # music should be half of master
        assert applied["music_volume"] == pytest.approx(0.5, abs=0.01)


class TestApplyCombo:
    def test_combo_window_from_settings(self) -> None:
        s = get_default_settings()
        s.combo_window_ms = 5000
        assert apply_combo_settings(s) == 5000


DIFFICULTY_CASES: list[tuple[str, float]] = [
    ("easy", 0.5),
    ("normal", 1.0),
    ("hard", 1.5),
    ("nightmare", 2.0),
]


class TestApplyDifficulty:
    @pytest.mark.parametrize("case_idx", list(range(len(DIFFICULTY_CASES))))
    def test_difficulty_multipliers(self, case_idx: int) -> None:
        diff, expected_taken = DIFFICULTY_CASES[case_idx]
        s = get_default_settings()
        s.difficulty = diff
        mults = apply_difficulty_settings(s)
        assert mults["damage_taken"] == expected_taken

    def test_unknown_difficulty_returns_normal(self) -> None:
        s = get_default_settings()
        s.difficulty = "INVALID"
        mults = apply_difficulty_settings(s)
        assert mults["damage_taken"] == 1.0


# ----------------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------------


class TestSummary:
    def test_summary_keys(self) -> None:
        s = get_default_settings()
        summary = get_settings_summary(s)
        assert "audio" in summary
        assert "display" in summary
        assert "input" in summary
        assert "language" in summary
        assert "gameplay" in summary

    def test_summary_audio(self) -> None:
        s = get_default_settings()
        summary = get_settings_summary(s)
        assert "master" in summary["audio"]
        assert "%" in summary["audio"]["master"]

    def test_summary_input(self) -> None:
        s = get_default_settings()
        summary = get_settings_summary(s)
        assert "confirm" in summary["input"]["bindings"]


# ----------------------------------------------------------------------------
# About
# ----------------------------------------------------------------------------


class TestAbout:
    def test_about_has_version(self) -> None:
        info = get_about_info()
        assert "version" in info
        assert info["name"] == "Roguelike Sprawl"
        assert info["author"] == "emilio"

    def test_about_has_counts(self) -> None:
        info = get_about_info()
        assert "settings_count" in info
        assert "achievements_count" in info
        assert "boss_types_count" in info

    def test_game_version(self) -> None:
        assert GAME_VERSION == "0.5.0"
        assert GAME_NAME == "Roguelike Sprawl"
        assert GAME_AUTHOR == "emilio"


# ----------------------------------------------------------------------------
# Customization
# ----------------------------------------------------------------------------


class TestCustomization:
    def test_change_volume(self) -> None:
        s = get_default_settings()
        s.master_volume = 0.8
        assert s.master_volume == 0.8

    def test_change_difficulty(self) -> None:
        s = get_default_settings()
        s.difficulty = "nightmare"
        assert s.difficulty == "nightmare"

    def test_change_color_theme(self) -> None:
        s = get_default_settings()
        s.color_theme = "cyberpunk"
        assert s.color_theme == "cyberpunk"

    def test_toggle_sound_category(self) -> None:
        s = get_default_settings()
        s.sound_categories["keys"] = True
        assert s.sound_categories["keys"] is True

    def test_remap_key(self) -> None:
        s = get_default_settings()
        s.key_bindings["confirm"] = "Space"
        assert s.key_bindings["confirm"] == "Space"


# ----------------------------------------------------------------------------
# Integration
# ----------------------------------------------------------------------------


class TestIntegration:
    def test_full_settings_cycle(self) -> None:
        """User changes settings, saves to file, loads back."""
        # 1. Start with defaults
        s = get_default_settings()
        # 2. User customizes
        s.master_volume = 0.8
        s.difficulty = "hard"
        s.color_theme = "cyberpunk"
        s.sound_categories["keys"] = True
        s.combo_window_ms = 4000
        # 3. Validate
        assert validate_settings(s) == []
        # 4. Save to file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            tmp_path = Path(f.name)
        try:
            save_settings_to_file(s, tmp_path, current_ms=5000)
            # 5. Load on new game
            s2 = load_settings_from_file(tmp_path)
            # 6. Verify all customizations preserved
            assert s2.master_volume == 0.8
            assert s2.difficulty == "hard"
            assert s2.color_theme == "cyberpunk"
            assert s2.sound_categories["keys"] is True
            assert s2.combo_window_ms == 4000
        finally:
            tmp_path.unlink()

    def test_user_can_reset_easily(self) -> None:
        s = get_default_settings()
        # Mess up settings
        s.master_volume = 1.0
        s.difficulty = "nightmare"
        s.color_theme = "mono"
        # Reset
        reset_settings(s)
        assert s.master_volume == 0.2
        assert s.difficulty == "normal"
        assert s.color_theme == "matrix"
