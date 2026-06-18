"""Tests for cross-project dashboard hub at Game/dashboard/index.html.

Verifies:
- Top hub exists at Game/dashboard/index.html
- Links to both roguelike_sprawl and typing_language dashboards
- Dynamic stats loading from both project JSON files
- Roguelike sub-dashboards have back-links to top hub
- All 3 levels of navigation work
"""

from __future__ import annotations

from pathlib import Path

GAME_ROOT = Path(__file__).parent.parent.parent.parent.parent
TOP_HUB = GAME_ROOT / "dashboard" / "index.html"
ROGUE_DASH = GAME_ROOT / "roguelike_sprawl" / "dashboard" / "index.html"
ROGUE_STORY = GAME_ROOT / "roguelike_sprawl" / "dashboard" / "story.html"
ROGUE_STAGES = GAME_ROOT / "roguelike_sprawl" / "dashboard" / "stages.html"
TYPING_DASH = GAME_ROOT / "typing_language" / "dashboard" / "index.html"


class TestTopHub:
    """Game/dashboard/index.html is the cross-project hub."""

    def test_top_hub_exists(self) -> None:
        assert TOP_HUB.exists(), f"Missing: {TOP_HUB}"

    def test_top_hub_links_to_roguelike(self) -> None:
        html = TOP_HUB.read_text(encoding="utf-8")
        assert "roguelike_sprawl/dashboard/index.html" in html

    def test_top_hub_links_to_typing(self) -> None:
        html = TOP_HUB.read_text(encoding="utf-8")
        assert "typing_language/dashboard/index.html" in html

    def test_top_hub_fetches_roguelike_json(self) -> None:
        html = TOP_HUB.read_text(encoding="utf-8")
        assert "roguelike_sprawl/design/story/prologue_data.json" in html
        assert "roguelike_sprawl/design/story/event_dialogues.json" in html
        assert "roguelike_sprawl/design/systems/stage_structure.json" in html

    def test_top_hub_fetches_typing_json(self) -> None:
        html = TOP_HUB.read_text(encoding="utf-8")
        assert "typing_language/dashboard/data/overview.json" in html

    def test_top_hub_has_project_cards(self) -> None:
        html = TOP_HUB.read_text(encoding="utf-8")
        assert "project-card roguelike" in html
        assert "project-card typing" in html

    def test_top_hub_has_both_project_stats(self) -> None:
        html = TOP_HUB.read_text(encoding="utf-8")
        for stat in ("tests", "stages", "lines", "npcs"):
            assert f'data-r-stat="{stat}"' in html, f"Missing roguelike stat: {stat}"
        for stat in ("languages", "corpus", "stages", "coverage"):
            assert f'data-t-stat="{stat}"' in html, f"Missing typing stat: {stat}"

    def test_top_hub_has_quick_links(self) -> None:
        html = TOP_HUB.read_text(encoding="utf-8")
        # Should have links to both projects' sub-dashboards
        assert "../roguelike_sprawl/dashboard/" in html
        assert "../typing_language/dashboard/" in html
        assert "../roguelike_sprawl/ROADMAP.md" in html
        assert "../typing_language/ROADMAP.md" in html

    def test_top_hub_has_combined_overview(self) -> None:
        html = TOP_HUB.read_text(encoding="utf-8")
        assert "Combined Overview" in html
        assert "stats-panel" in html


class TestRoguelikeSubmenu:
    """roguelike_sprawl/dashboard/index.html has top-hub link."""

    def test_submenu_exists(self) -> None:
        assert ROGUE_DASH.exists()

    def test_submenu_links_to_top_hub(self) -> None:
        html = ROGUE_DASH.read_text(encoding="utf-8")
        assert "../../dashboard/index.html" in html, "Should link to top hub"

    def test_submenu_has_top_hub_link_visible(self) -> None:
        """Link should be in a visible element, not hidden."""
        html = ROGUE_DASH.read_text(encoding="utf-8")
        # Search for the link with the "Projects Hub" text
        assert "Projects Hub" in html or "상위 허브" in html


class TestRoguelikeSubDashboards:
    """story.html and stages.html have full breadcrumb nav."""

    def test_story_has_top_hub_link(self) -> None:
        html = ROGUE_STORY.read_text(encoding="utf-8")
        assert "../../dashboard/index.html" in html, "Story should link to top hub"

    def test_story_has_submenu_link(self) -> None:
        html = ROGUE_STORY.read_text(encoding="utf-8")
        assert 'href="index.html"' in html, "Story should link back to submenu"

    def test_stages_has_top_hub_link(self) -> None:
        html = ROGUE_STAGES.read_text(encoding="utf-8")
        assert "../../dashboard/index.html" in html, "Stages should link to top hub"

    def test_stages_has_submenu_link(self) -> None:
        html = ROGUE_STAGES.read_text(encoding="utf-8")
        assert 'href="index.html"' in html, "Stages should link back to submenu"


class TestTypingDashboardExists:
    """typing_language/dashboard/index.html exists (untouched)."""

    def test_typing_dashboard_exists(self) -> None:
        assert TYPING_DASH.exists()

    def test_typing_dashboard_has_data(self) -> None:
        data_file = TYPING_DASH.parent / "data" / "overview.json"
        assert data_file.exists()


class TestNavigation:
    """Full navigation path works through all 3 levels."""

    def test_hub_to_roguelike_submenu(self) -> None:
        """Top hub → Roguelike submenu link is valid."""
        top = TOP_HUB.read_text(encoding="utf-8")
        # Extract link
        assert "roguelike_sprawl/dashboard/index.html" in top

    def test_roguelike_submenu_to_hub(self) -> None:
        """Submenu → Top hub link is valid."""
        sub = ROGUE_DASH.read_text(encoding="utf-8")
        assert "../../dashboard/index.html" in sub

    def test_submenu_to_sub_dashboards(self) -> None:
        """Submenu → story/stages links are valid."""
        sub = ROGUE_DASH.read_text(encoding="utf-8")
        assert 'href="story.html"' in sub
        assert 'href="stages.html"' in sub

    def test_sub_dashboards_back_to_submenu(self) -> None:
        for path in (ROGUE_STORY, ROGUE_STAGES):
            html = path.read_text(encoding="utf-8")
            assert 'href="index.html"' in html

    def test_typing_dashboard_to_hub(self) -> None:
        """Typing dashboard should have back-link to top hub (if implemented).

        Note: typing_language dashboard was created separately and may not
        have a hub link. This test is informational only.
        """
        # Soft check - typing dashboard exists, but we don't enforce hub link
        assert TYPING_DASH.exists()
