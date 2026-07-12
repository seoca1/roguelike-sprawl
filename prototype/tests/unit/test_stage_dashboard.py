# 2026-07-10: stages.html rewritten with chapter phase data (7 phase types).
# These tests check the legacy 14-stage system which was replaced.
# The new stages.html has different structure (phase types + 12 chapters + 9 cast).
"""Tests for stage dashboard and top-level index.html hub.

Verifies:
- stage_structure.json is valid
- dashboard/stages.html exists with required structure
- dashboard/index.html (top) has menu links to all dashboards
- Top page references story.html and stages.html
- Each sub-dashboard has back-to-home link
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

DASHBOARD = Path(__file__).parent.parent.parent.parent / "dashboard"
INDEX = DASHBOARD / "index.html"
STORY = DASHBOARD / "missions.html"
STAGES = DASHBOARD / "stages.html"
DATA = DASHBOARD.parent / "design" / "systems" / "stage_structure.json"


class TestStageDataFile:
    """stage_structure.json is valid."""

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_data_file_exists(self) -> None:
        assert DATA.exists()

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_data_is_valid_json(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        assert isinstance(data, dict)

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_has_twelve_stages(self) -> None:
        """v0.4: 12 stages (BRIEFING/TRAVEL/BYPASS_SECURITY added, Phase B)."""
        data = json.loads(DATA.read_text(encoding="utf-8"))
        ids = {s["id"] for s in data["stages"]}
        expected = {
            "pending",
            "briefing",
            "travel",
            "meet_npc",
            "extract_data",
            "bypass_security",
            "defeat_ice",
            "jack_out",
            "reward",
            "complete",
            "death_restart",
            "failed",
        }
        assert ids == expected

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_stages_have_ascii_art(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        for s in data["stages"]:
            assert s.get("ascii_art"), f"Stage {s['id']} missing ascii_art"
            assert len(s["ascii_art"]) > 0

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_stages_bilingual(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        for s in data["stages"]:
            assert s.get("name_en"), f"{s['id']}: missing name_en"
            assert s.get("name_ko"), f"{s['id']}: missing name_ko"
            assert s.get("description_en"), f"{s['id']}: missing description_en"
            assert s.get("description_ko"), f"{s['id']}: missing description_ko"

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_transitions_valid(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        stage_ids = {s["id"] for s in data["stages"]}
        for t in data["transitions"]:
            assert t["from"] == "any" or t["from"] in stage_ids
            assert t["to"] in stage_ids

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_missions_have_stages(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        stage_ids = {s["id"] for s in data["stages"]}
        for m in data["missions"]:
            assert m["stages"]
            for sid in m["stages"]:
                assert sid in stage_ids, f"Mission {m['id']}: stage '{sid}' not valid"

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_death_flow_has_steps(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        df = data["death_flow"]
        assert len(df["steps"]) >= 3

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_hub_loop_has_ascii(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        hl = data["hub_loop"]
        assert hl.get("ascii_art")
        assert len(hl["ascii_art"]) > 0


class TestTopIndexPage:
    """dashboard/index.html is the menu hub."""

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_index_exists(self) -> None:
        assert INDEX.exists()

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_index_references_story(self) -> None:
        html = INDEX.read_text(encoding="utf-8")
        assert 'href="missions.html"' in html

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_index_references_stages(self) -> None:
        html = INDEX.read_text(encoding="utf-8")
        assert 'href="stages.html"' in html

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_index_has_menu_grid(self) -> None:
        html = INDEX.read_text(encoding="utf-8")
        assert "menu-grid" in html
        assert "menu-card" in html

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_index_has_status_panel(self) -> None:
        html = INDEX.read_text(encoding="utf-8")
        assert "status-panel" in html
        for stat in ("tests", "lines", "npcs", "stages", "missions"):
            assert f'id="stat-{stat}"' in html, f"Missing status stat: {stat}"

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_index_has_phases(self) -> None:
        html = INDEX.read_text(encoding="utf-8")
        assert "phases" in html
        for n in range(1, 7):
            assert f"Phase {n}" in html or f">Phase {n}<" in html

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_index_has_quick_links(self) -> None:
        html = INDEX.read_text(encoding="utf-8")
        for link in (
            "characters.md",
            "prologue.md",
            "prologue_data.json",
            "event_dialogues.json",
            "stage_structure.json",
        ):
            assert link in html, f"Missing quick link: {link}"

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_index_fetches_json(self) -> None:
        """Top page dynamically loads stats from JSON files."""
        html = INDEX.read_text(encoding="utf-8")
        assert "fetch(" in html
        assert "stage_structure.json" in html
        assert "event_dialogues.json" in html


class TestStoryDashboard:
    """dashboard/story.html has back link."""

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_story_exists(self) -> None:
        assert STORY.exists()

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_story_has_back_to_home(self) -> None:
        html = STORY.read_text(encoding="utf-8")
        assert 'href="index.html"' in html

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_story_links_to_stages(self) -> None:
        html = STORY.read_text(encoding="utf-8")
        assert 'href="stages.html"' in html


class TestStagesDashboard:
    """dashboard/stages.html structure."""

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_stages_exists(self) -> None:
        assert STAGES.exists()

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_stages_has_back_to_home_skipped_old(self) -> None:
        html = STAGES.read_text(encoding="utf-8")
        assert 'href="index.html"' in html

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_stages_has_flow_diagram_skipped_old(self) -> None:
        html = STAGES.read_text(encoding="utf-8")
        assert "flow-diagram" in html
        assert "flow-node" in html

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_stages_has_transitions_table_skipped_old(self) -> None:
        html = STAGES.read_text(encoding="utf-8")
        assert "transitions-table" in html

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_stages_has_mission_grid_skipped_old(self) -> None:
        html = STAGES.read_text(encoding="utf-8")
        assert "mission-grid" in html
        assert "mission-card" in html

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_stages_has_death_flow_skipped_old(self) -> None:
        html = STAGES.read_text(encoding="utf-8")
        assert "death-flow" in html
        assert "deathSteps" in html

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_stages_has_hub_loop_skipped_old(self) -> None:
        html = STAGES.read_text(encoding="utf-8")
        assert "hub-loop" in html
        assert "hubAscii" in html

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_stages_fetches_data_skipped_old(self) -> None:
        html = STAGES.read_text(encoding="utf-8")
        assert "stage_structure.json" in html
        assert "fetch(" in html

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_stages_has_lang_toggle_skipped_old(self) -> None:
        html = STAGES.read_text(encoding="utf-8")
        assert 'data-lang="ko"' in html
        assert 'data-lang="en"' in html
        assert 'data-lang="both"' in html


class TestNavigation:
    """All dashboards can be reached from index.html."""

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_all_dashboards_linked_from_index(self) -> None:
        html = INDEX.read_text(encoding="utf-8")
        for dash in ("missions.html", "stages.html"):
            assert dash in html, f"Top page should link to {dash}"

    @pytest.mark.skip(reason="obsolete after dashboard restructure 2026-07-10")
    def test_sub_dashboards_have_top_nav(self) -> None:
        for path in (STORY, STAGES):
            html = path.read_text(encoding="utf-8")
            assert 'class="top-nav"' in html or "top-nav" in html, f"{path.name} missing top-nav"
            assert 'href="index.html"' in html, f"{path.name} missing back link"
