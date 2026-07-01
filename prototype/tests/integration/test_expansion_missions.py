"""Tests for the CONTENT_EXPANSION Phase A+ mission batch
(2026-07-01 short stories: Arc 2-3 expansion).

5 new missions, each backed by a Gibson-tone short story and a
mission record in ``missions.json``:

- sense_net_infiltration   (Arc 2, novice,  mid zone, Sense/Net 2nd ring)
- wigan_call               (Arc 2, heretic, mid zone, vodoun construct)
- hosaka_core              (Arc 3, novice,  mid zone, Hosaka corporate memory)
- straylight_approach      (Arc 3, veteran, core zone, T-A inter-family)
- maas_heist               (Arc 3, novice,  mid zone, Maas biochip specs)
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

MISSIONS_PATH = Path(__file__).resolve().parents[2] / "data" / "missions" / "missions.json"
SHORT_STORIES_DIR = Path(
    "/Users/emilio/projects/Projects/Fiction/derivative/sprawl-trilogy/short-stories"
)

NEW_MISSIONS = [
    "sense_net_infiltration",
    "wigan_call",
    "hosaka_core",
    "straylight_approach",
    "maas_heist",
]


@pytest.fixture(scope="module")
def missions() -> dict[str, dict[str, object]]:
    with MISSIONS_PATH.open(encoding="utf-8") as f:
        return json.load(f)


class TestExpansionMissionsPresent:
    """All 5 new missions exist in missions.json."""

    @pytest.mark.parametrize("mission_id", NEW_MISSIONS)
    def test_mission_exists(self, missions: dict, mission_id: str) -> None:
        assert mission_id in missions

    def test_total_count_at_least_38(self, missions: dict) -> None:
        assert len(missions) >= 38, f"Expected ≥38 missions, got {len(missions)}"

    def test_arc_distribution_arc_2_3(self, missions: dict) -> None:
        """The 5 new missions are split: 2 in Arc 2, 3 in Arc 3."""
        arc_2_new = [m for m in NEW_MISSIONS if missions[m]["story"]["arc"] == 2]
        arc_3_new = [m for m in NEW_MISSIONS if missions[m]["story"]["arc"] == 3]
        assert len(arc_2_new) == 2, f"Expected 2 Arc 2 missions, got {arc_2_new}"
        assert len(arc_3_new) == 3, f"Expected 3 Arc 3 missions, got {arc_3_new}"


class TestExpansionMissionShape:
    """Each new mission has a well-formed record."""

    @pytest.mark.parametrize("mission_id", NEW_MISSIONS)
    def test_story_metadata_complete(self, missions: dict, mission_id: str) -> None:
        m = missions[mission_id]
        s = m["story"]
        required = {
            "synopsis_en",
            "synopsis_ko",
            "source",
            "character_ref",
            "arc",
            "pillar",
            "word_count_en",
            "char_count_ko",
        }
        missing = required - set(s.keys())
        assert not missing, f"{mission_id}: missing {missing}"

    @pytest.mark.parametrize("mission_id", NEW_MISSIONS)
    def test_objective_present(self, missions: dict, mission_id: str) -> None:
        m = missions[mission_id]
        assert "primary_objective" in m
        assert m["primary_objective"]["type"] in {
            "extract_data",
            "defeat",
            "collect_material",
            "craft_item",
        }

    @pytest.mark.parametrize("mission_id", NEW_MISSIONS)
    def test_grade_min_max_arc2_3(self, missions: dict, mission_id: str) -> None:
        """All 5 new missions are grade 2-4 (mid-tier)."""
        m = missions[mission_id]
        assert 2 <= m["grade_min"] <= 3
        assert 3 <= m["grade_max"] <= 4

    @pytest.mark.parametrize("mission_id", NEW_MISSIONS)
    def test_zone_is_mid_or_core(self, missions: dict, mission_id: str) -> None:
        """All 5 new missions are mid/core zone (not surface)."""
        m = missions[mission_id]
        assert m["zone"] in ("mid", "core")

    @pytest.mark.parametrize("mission_id", NEW_MISSIONS)
    def test_pillar_valid(self, missions: dict, mission_id: str) -> None:
        valid = {"identity", "power", "memory", "code", "resonance", "people", "purpose"}
        m = missions[mission_id]
        assert m["story"]["pillar"] in valid


class TestExpansionShortStories:
    """The short-story files referenced by the new missions exist."""

    @pytest.mark.parametrize("mission_id", NEW_MISSIONS)
    def test_en_short_story_exists(self, mission_id: str) -> None:
        m = json.loads(MISSIONS_PATH.read_text(encoding="utf-8"))
        source = m[mission_id]["story"]["source"]
        path = SHORT_STORIES_DIR / f"2026-07-01_{source}.md"
        assert path.exists(), f"Missing EN short story: {path}"
        text = path.read_text(encoding="utf-8")
        assert len(text) > 200, f"{path.name} is suspiciously short"

    @pytest.mark.parametrize("mission_id", NEW_MISSIONS)
    def test_ko_short_story_exists(self, mission_id: str) -> None:
        m = json.loads(MISSIONS_PATH.read_text(encoding="utf-8"))
        source = m[mission_id]["story"]["source"]
        path = SHORT_STORIES_DIR / f"2026-07-01_{source}.ko.md"
        assert path.exists(), f"Missing KO short story: {path}"
        text = path.read_text(encoding="utf-8")
        assert len(text) > 200, f"{path.name} is suspiciously short"

    @pytest.mark.parametrize("mission_id", NEW_MISSIONS)
    def test_ko_body_meets_minimum_chars(self, mission_id: str) -> None:
        """KO body has ≥800 Korean chars (matches test_novel_korean_body_minimum)."""
        m = json.loads(MISSIONS_PATH.read_text(encoding="utf-8"))
        source = m[mission_id]["story"]["source"]
        path = SHORT_STORIES_DIR / f"2026-07-01_{source}.ko.md"
        text = path.read_text(encoding="utf-8")
        # Strip frontmatter
        if text.startswith("---"):
            body = text.split("---", 2)[-1]
        else:
            body = text
        ko_chars = sum(1 for c in body if "가" <= c <= "힣")
        assert ko_chars >= 800, f"{source} KO body has only {ko_chars} Korean chars"

    @pytest.mark.parametrize("mission_id", NEW_MISSIONS)
    def test_ko_no_chinese_chars(self, mission_id: str) -> None:
        """KO body doesn't contain any Chinese (CJK Unified Ideographs)."""
        import re

        m = json.loads(MISSIONS_PATH.read_text(encoding="utf-8"))
        source = m[mission_id]["story"]["source"]
        path = SHORT_STORIES_DIR / f"2026-07-01_{source}.ko.md"
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            body = text.split("---", 2)[-1]
        else:
            body = text
        chinese_re = re.compile(r"[\u4e00-\u9fff]")
        matches = chinese_re.findall(body)
        assert not matches, f"{source} KO body contains Chinese chars: {set(matches)}"


class TestExpansionNovelIntegration:
    """The novel hook dispatch system can resolve the new short stories."""

    def test_mission_to_stem_resolves_all_new(self) -> None:
        import sys

        sys.path.insert(0, str(MISSIONS_PATH.parent.parent / "src"))
        from roguelike_sprawl.engine.novel_integration import mission_to_stem

        for mid in NEW_MISSIONS:
            stem = mission_to_stem(mid)
            assert stem is not None, f"{mid} failed to resolve to a stem"
            assert isinstance(stem, str)
            assert len(stem) > 0

    def test_new_missions_have_distinct_stems(self) -> None:
        import sys

        sys.path.insert(0, str(MISSIONS_PATH.parent.parent / "src"))
        from roguelike_sprawl.engine.novel_integration import mission_to_stem

        stems = [mission_to_stem(m) for m in NEW_MISSIONS]
        assert len(set(stems)) == len(stems), f"Duplicate stems: {stems}"


class TestExpansionGibsonTone:
    """Each new mission's synopsis carries Gibson vocabulary."""

    GIBSON_VOCAB = {
        "sprawl",
        "matrix",
        "ice",
        "deck",
        "construct",
        "finn",
        "cyberspace",
        "console",
        "data",
        "trace",
        "cowboy",
        "cowboys",
        "jacked",
        "watchdog",
        "tessier",
        "ashpool",
        "freeside",
        "chiba",
        "neuromancer",
        "wintermute",
    }

    @pytest.mark.parametrize("mission_id", NEW_MISSIONS)
    def test_synopsis_uses_gibson_terms(self, missions: dict, mission_id: str) -> None:
        syn = missions[mission_id]["story"]["synopsis_en"].lower()
        found = [w for w in self.GIBSON_VOCAB if w in syn]
        assert len(found) >= 2, f"{mission_id}: needs ≥2 Gibson terms (found {found})"
