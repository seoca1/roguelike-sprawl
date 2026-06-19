"""Tests for the Short Stories dashboard (dashboard/stories.html)."""

from __future__ import annotations

from pathlib import Path

DASHBOARD = Path(__file__).parent.parent.parent.parent / "dashboard" / "stories.html"


class TestStoriesDashboardStructure:
    """stories.html structure."""

    def test_exists(self) -> None:
        assert DASHBOARD.exists()

    def test_has_three_story_cards(self) -> None:
        """Three stories: Case, Marly, Kumiko."""
        html = DASHBOARD.read_text(encoding="utf-8")
        assert "잭아웃 후 30초" in html
        assert "루이지아나의 신" in html
        assert "매나리사의 자정" in html

    def test_has_pov_labels(self) -> None:
        html = DASHBOARD.read_text(encoding="utf-8")
        assert "1인칭" in html
        assert "3인칭" in html

    def test_has_source_quotes(self) -> None:
        html = DASHBOARD.read_text(encoding="utf-8")
        assert "television, tuned to a dead channel" in html
        assert "almost purely visual level" in html

    def test_has_game_character_links(self) -> None:
        """Each story links to a game character (K, Sil, Kas)."""
        html = DASHBOARD.read_text(encoding="utf-8")
        assert "케이 (K)" in html
        assert "실 (Sil)" in html
        assert "카스 (Kas)" in html

    def test_has_work_references(self) -> None:
        html = DASHBOARD.read_text(encoding="utf-8")
        assert "Neuromancer" in html
        assert "Count Zero" in html
        assert "Mona Lisa Overdrive" in html

    def test_has_status_final(self) -> None:
        html = DASHBOARD.read_text(encoding="utf-8")
        assert "Final" in html

    def test_has_links_to_fiction(self) -> None:
        """Links to Fiction/derivative/ files."""
        html = DASHBOARD.read_text(encoding="utf-8")
        assert "Fiction/derivative/" in html
        assert "Fiction/wiki/" in html

    def test_has_stats_panel(self) -> None:
        html = DASHBOARD.read_text(encoding="utf-8")
        # Production stats
        assert "Stories" in html
        assert "Korean Chars" in html
        assert "Wiki Refs" in html
        assert "Source Quotes" in html

    def test_has_system_docs_section(self) -> None:
        """Links to system docs (README, WRITING_PROCESS, STYLE_GUIDE, etc.)."""
        html = DASHBOARD.read_text(encoding="utf-8")
        assert "README" in html
        assert "WRITING_PROCESS" in html or "Writing Process" in html
        assert "STYLE_GUIDE" in html or "Style Guide" in html
        assert "TEMPLATES" in html or "Templates" in html
        assert "INDEX" in html

    def test_has_top_nav(self) -> None:
        html = DASHBOARD.read_text(encoding="utf-8")
        assert "Hub" in html
        assert "Roguelike" in html
        assert "Story" in html
        assert "Stages" in html
        assert "Short Stories" in html

    def test_current_page_highlighted(self) -> None:
        html = DASHBOARD.read_text(encoding="utf-8")
        assert "current" in html  # CSS class

    def test_bilingual(self) -> None:
        """Korean + English both present."""
        html = DASHBOARD.read_text(encoding="utf-8")
        assert "잭아웃" in html
        assert "Jack-Out" in html or "Jack Out" in html
