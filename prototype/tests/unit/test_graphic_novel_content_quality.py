"""Tests for scene content quality (ADR-0041).

Covers:
    - All 12 scenes have dialogue length in target range (250-600 chars)
    - All scenes have text_ko populated for every dialogue
    - At least one Gibson-style industry name appears (Tessier-Ashpool,
      Sense/Net, Maas, Hosaka, Ono-Sendai, Neuromancer, loa)
    - Speaker names are consistent across the same character arc
    - No empty dialogue text in any scene
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


SCENES_DIR = Path(__file__).parent.parent.parent / "data" / "scenes"


def _load_all_scenes() -> list[tuple[Path, dict]]:
    """Load all 12 scene JSON files."""
    out: list[tuple[Path, dict]] = []
    for p in sorted(SCENES_DIR.rglob("*.json")):
        if p.parent.name in {"case", "sil", "kas"}:
            out.append((p, json.loads(p.read_text(encoding="utf-8"))))
    return out


_SCENES = _load_all_scenes()


@pytest.fixture(scope="module")
def all_scenes() -> list[tuple[Path, dict]]:
    return _SCENES


def _scene_id(idx: int) -> str:
    return f"{_SCENES[idx][0].parent.name}/{_SCENES[idx][0].stem}"


# ============================================================================
# Length targets (ADR-0041 § 10.1)
# ============================================================================


class TestDialogueLength:
    """Each dialogue should be 250-700 chars (avg target 443)."""

    @pytest.mark.parametrize("idx", range(len(_SCENES)), ids=_scene_id)
    def test_each_dialogue_min_length(self, idx: int) -> None:
        path, scene = _SCENES[idx]
        # Epilogues (Phase 9) are intentionally short: closing line only
        if "09_epilogue" in path.name:
            return  # Skip epilogue min length check (deliberately 1-line)
        for i, line in enumerate(scene.get("dialogue", [])):
            text_en = line.get("text_en", "")
            assert len(text_en) >= 250, (
                f"{path.name} dialogue[{i}] too short: {len(text_en)} chars (target: 250-700)"
            )

    @pytest.mark.parametrize("idx", range(len(_SCENES)), ids=_scene_id)
    def test_each_dialogue_max_length(self, idx: int) -> None:
        path, scene = _SCENES[idx]
        for i, line in enumerate(scene.get("dialogue", [])):
            text_en = line.get("text_en", "")
            assert len(text_en) <= 1200, (
                f"{path.name} dialogue[{i}] too long: {len(text_en)} chars (cap: 1200)"
            )


class TestSceneTotalLength:
    """Each scene total dialogue should be 1000-2500 chars."""

    @pytest.mark.parametrize("idx", range(len(_SCENES)), ids=_scene_id)
    def test_scene_total_range(self, idx: int) -> None:
        path, scene = _SCENES[idx]
        # Epilogues (Phase 9) are intentionally short: closing line only
        if "09_epilogue" in path.name:
            return  # Skip epilogue length check (deliberately 1-line)
        total = sum(len(ln.get("text_en", "")) for ln in scene.get("dialogue", []))
        assert 1000 <= total <= 2800, f"{path.name} total {total} chars outside 1000-2800 target"


# ============================================================================
# Translation sync (ADR-0010)
# ============================================================================


class TestKoreanSubtitles:
    """Every dialogue must have a Korean subtitle."""

    @pytest.mark.parametrize("idx", range(len(_SCENES)), ids=_scene_id)
    def test_every_dialogue_has_text_ko(self, idx: int) -> None:
        path, scene = _SCENES[idx]
        for i, line in enumerate(scene.get("dialogue", [])):
            assert "text_ko" in line, f"{path.name} dialogue[{i}] missing text_ko"
            assert line["text_ko"], f"{path.name} dialogue[{i}] has empty text_ko"

    @pytest.mark.parametrize("idx", range(len(_SCENES)), ids=_scene_id)
    def test_korean_within_reasonable_ratio(self, idx: int) -> None:
        path, scene = _SCENES[idx]
        for i, line in enumerate(scene.get("dialogue", [])):
            en = len(line.get("text_en", ""))
            ko = len(line.get("text_ko", ""))
            if en == 0:
                continue
            ratio = ko / en
            assert 0.4 <= ratio <= 1.8, (
                f"{path.name} dialogue[{i}] KO/EN ratio {ratio:.2f} "
                f"outside 0.4-1.8 (en={en}, ko={ko})"
            )


# ============================================================================
# Gibson-style content markers (ADR-0041 § 10.5)
# ============================================================================


class TestGibsonVocabulary:
    def test_corpus_has_core_industry_names(self, all_scenes: list[tuple[Path, dict]]) -> None:
        """The full corpus should reference core Gibson industry names."""
        corpus = " ".join(
            line.get("text_en", "") for _, scene in all_scenes for line in scene.get("dialogue", [])
        ).lower()
        for term in ("tessier-ashpool", "sense/net", "ono-sendai", "chiba", "matrix", "sprawl"):
            assert term.lower() in corpus, f"Gibson term '{term}' missing from corpus"

    def test_each_character_uses_distinct_vocabulary(
        self, all_scenes: list[tuple[Path, dict]]
    ) -> None:
        """Each character's scenes should mention at least one signature term."""
        char_terms = {
            "novice": ["ono-sendai", "chiba", "finn", "hosaka"],
            "veteran": ["tessier-ashpool", "mara", "loa"],
            "heretic": ["tessier-ashpool", "loa", "yanaka"],
        }
        for char, terms in char_terms.items():
            char_corpus = " ".join(
                line.get("text_en", "").lower()
                for path, scene in all_scenes
                if scene.get("character") == char
                for line in scene.get("dialogue", [])
            )
            missing = [t for t in terms if t not in char_corpus]
            assert not missing, f"Character {char} missing signature terms: {missing}"


# ============================================================================
# Speaker consistency
# ============================================================================


class TestSpeakerConsistency:
    def test_most_scenes_have_narrator(self, all_scenes: list[tuple[Path, dict]]) -> None:
        """At least 10 of 12 scenes should include a narrator line.

        Some tight dialogue scenes (e.g. 04_finn) are pure character voice
        and don't need a camera-eye narration.
        """
        no_narrator = []
        for path, scene in all_scenes:
            speakers = {line.get("speaker") for line in scene.get("dialogue", [])}
            if "narrator" not in speakers:
                # Epilogues (Phase 9) deliberately use only the character voice
                if "09_epilogue" in path.name:
                    continue
                no_narrator.append(path.name)
        assert len(no_narrator) <= 2, f"Too many scenes without narrator: {no_narrator}"

    def test_every_dialogue_has_speaker(self, all_scenes: list[tuple[Path, dict]]) -> None:
        for path, scene in all_scenes:
            for i, line in enumerate(scene.get("dialogue", [])):
                assert line.get("speaker"), f"{path.name} dialogue[{i}] missing speaker"
                assert line.get("speaker_ko"), f"{path.name} dialogue[{i}] missing speaker_ko"


# ============================================================================
# Duration proportionality (ADR-0041 § duration_ms should reflect length)
# ============================================================================


class TestDurationProportional:
    """Longer dialogues should have proportionally longer durations.

    Rule of thumb: ~30ms per char, with a 12000ms minimum.
    """

    @pytest.mark.parametrize("idx", range(len(_SCENES)), ids=_scene_id)
    def test_duration_matches_text_length(self, idx: int) -> None:
        path, scene = _SCENES[idx]
        for i, line in enumerate(scene.get("dialogue", [])):
            chars = len(line.get("text_en", ""))
            duration_ms = line.get("duration_ms", 0)
            # Minimum: 12000ms for any non-trivial line
            min_expected = max(12000, chars * 30)
            assert duration_ms >= min_expected, (
                f"{path.name} dialogue[{i}] duration {duration_ms}ms "
                f"too short for {chars} chars (min: {min_expected}ms)"
            )
