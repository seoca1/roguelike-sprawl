"""Tests for cross-project dashboard hub.

In dev (Game/ workspace layout), tests the full cross-project hub.
In CI (only roguelike_sprawl/ repo), tests only the roguelike sub-dashboards
and skips cross-project tests gracefully.
"""

from __future__ import annotations

from pathlib import Path

import pytest

# Repo root: 4 levels up from this file (tests/unit/test_*.py -> tests/ -> prototype/ -> repo)
REPO_ROOT = Path(__file__).parent.parent.parent.parent

# Dev workspace root: 5 levels up. Has both roguelike_sprawl/ and typing_language/.
# In CI clones, this is the runner workspace and may not have these paths.
DEV_ROOT = Path(__file__).parent.parent.parent.parent.parent

# Detect if we're in dev workspace (Game/... layout) or CI (just roguelike_sprawl/).
IS_DEV_WORKSPACE = (DEV_ROOT / "dashboard" / "index.html").exists()

# Top hub: dev workspace location
TOP_HUB = DEV_ROOT / "dashboard" / "index.html"

# Roguelike dashboards: always repo-relative
ROGUE_DASH = REPO_ROOT / "dashboard" / "index.html"
ROGUE_STORY = REPO_ROOT / "dashboard" / "missions.html"
ROGUE_STAGES = REPO_ROOT / "dashboard" / "stages.html"

# Typing dashboard: only in dev workspace
TYPING_DASH = DEV_ROOT / "typing_language" / "dashboard" / "index.html"


# Skip marker for CI
skip_in_ci = pytest.mark.skipif(
    not IS_DEV_WORKSPACE,
    reason="Cross-project tests require dev workspace (Game/dashboard/index.html)",
)


class TestTopHub:
    """Game/dashboard/index.html is the cross-project hub."""

    @skip_in_ci
    def test_top_hub_exists(self) -> None:
        assert TOP_HUB.exists(), f"Missing: {TOP_HUB}"

    @skip_in_ci
    def test_top_hub_links_to_roguelike(self) -> None:
        html = TOP_HUB.read_text(encoding="utf-8")
        assert "roguelike_sprawl/dashboard/index.html" in html

    @skip_in_ci
    def test_top_hub_links_to_typing(self) -> None:
        html = TOP_HUB.read_text(encoding="utf-8")
        assert "typing_language/dashboard/index.html" in html

    @skip_in_ci
    def test_top_hub_fetches_roguelike_json(self) -> None:
        html = TOP_HUB.read_text(encoding="utf-8")
        assert "roguelike_sprawl/design/story/prologue_data.json" in html
        assert "roguelike_sprawl/design/story/event_dialogues.json" in html
        assert "roguelike_sprawl/design/systems/stage_structure.json" in html

    @skip_in_ci
    def test_top_hub_fetches_typing_json(self) -> None:
        html = TOP_HUB.read_text(encoding="utf-8")
        assert "typing_language/dashboard/data/overview.json" in html

    @skip_in_ci
    def test_top_hub_has_project_cards(self) -> None:
        html = TOP_HUB.read_text(encoding="utf-8")
        assert "project-card roguelike" in html
        assert "project-card typing" in html

    @skip_in_ci
    def test_top_hub_has_both_project_stats(self) -> None:
        html = TOP_HUB.read_text(encoding="utf-8")
        for stat in ("tests", "stages", "lines", "npcs"):
            assert f'data-r-stat="{stat}"' in html, f"Missing roguelike stat: {stat}"
        for stat in ("languages", "corpus", "stages", "coverage"):
            assert f'data-t-stat="{stat}"' in html, f"Missing typing stat: {stat}"

    @skip_in_ci
    def test_top_hub_has_quick_links(self) -> None:
        html = TOP_HUB.read_text(encoding="utf-8")
        assert "../roguelike_sprawl/dashboard/" in html
        assert "../typing_language/dashboard/" in html
        assert "../roguelike_sprawl/ROADMAP.md" in html
        assert "../typing_language/ROADMAP.md" in html

    @skip_in_ci
    def test_top_hub_has_combined_overview(self) -> None:
        html = TOP_HUB.read_text(encoding="utf-8")
        assert "Combined Overview" in html
        assert "stats-panel" in html


class TestRoguelikeSubmenu:
    """roguelike_sprawl/dashboard/index.html is the roguelike submenu."""

    def test_submenu_exists(self) -> None:
        assert ROGUE_DASH.exists()

    @skip_in_ci
    def test_submenu_links_to_top_hub(self) -> None:
        html = ROGUE_DASH.read_text(encoding="utf-8")
        # v0.4: Hub link uses a JS-gated ../../  anchor (no longer
        # the broken ../../Game/dashboard/index.html path).
        assert 'id="projects-hub-link"' in html, "Should include hub link anchor"
        assert 'href="../../"' in html, "Hub href should be ../../"

    @skip_in_ci
    def test_submenu_has_top_hub_link_visible(self) -> None:
        html = ROGUE_DASH.read_text(encoding="utf-8")
        assert "🌐 Hub" in html or "Projects Hub" in html

    def test_submenu_has_sub_dashboards(self) -> None:
        """Submenu links to story, stages, stories dashboards (always present)."""
        html = ROGUE_DASH.read_text(encoding="utf-8")
        assert 'href="missions.html"' in html
        assert 'href="stages.html"' in html
        assert 'href="library.html"' in html

    def test_submenu_has_stories_card(self) -> None:
        """Submenu has a 'Short Stories' card."""
        html = ROGUE_DASH.read_text(encoding="utf-8")
        assert "Short Stories" in html or "단편" in html


class TestRoguelikeSubDashboards:
    """story.html and stages.html have full breadcrumb nav."""

    def test_story_exists(self) -> None:
        assert ROGUE_STORY.exists()

    def test_stages_exists(self) -> None:
        assert ROGUE_STAGES.exists()

    def test_story_has_submenu_link(self) -> None:
        html = ROGUE_STORY.read_text(encoding="utf-8")
        assert 'href="index.html"' in html, "Story should link back to submenu"

    def test_stages_has_submenu_link(self) -> None:
        html = ROGUE_STAGES.read_text(encoding="utf-8")
        assert 'href="index.html"' in html, "Stages should link back to submenu"

    @skip_in_ci
    def test_story_has_top_hub_link(self) -> None:
        html = ROGUE_STORY.read_text(encoding="utf-8")
        # v0.4: hub link is now a JS-gated ../../  anchor.
        assert 'id="projects-hub-link"' in html

    @skip_in_ci
    def test_stages_has_top_hub_link(self) -> None:
        html = ROGUE_STAGES.read_text(encoding="utf-8")
        assert 'id="projects-hub-link"' in html


class TestTypingDashboardExists:
    """typing_language/dashboard/index.html exists in dev workspace."""

    @skip_in_ci
    def test_typing_dashboard_exists(self) -> None:
        assert TYPING_DASH.exists()

    @skip_in_ci
    def test_typing_dashboard_has_data(self) -> None:
        data_file = TYPING_DASH.parent / "data" / "overview.json"
        assert data_file.exists()


class TestNavigation:
    """Full navigation path works through all 3 levels."""

    @skip_in_ci
    def test_hub_to_roguelike_submenu(self) -> None:
        top = TOP_HUB.read_text(encoding="utf-8")
        assert "roguelike_sprawl/dashboard/index.html" in top

    @skip_in_ci
    def test_roguelike_submenu_to_hub(self) -> None:
        sub = ROGUE_DASH.read_text(encoding="utf-8")
        # v0.4: hub link is now a JS-gated ../../  anchor.
        assert 'id="projects-hub-link"' in sub
        assert 'href="../../"' in sub

    def test_submenu_to_sub_dashboards(self) -> None:
        sub = ROGUE_DASH.read_text(encoding="utf-8")
        assert 'href="missions.html"' in sub
        assert 'href="stages.html"' in sub

    def test_sub_dashboards_back_to_submenu(self) -> None:
        for path in (ROGUE_STORY, ROGUE_STAGES):
            html = path.read_text(encoding="utf-8")
            assert 'href="index.html"' in html
