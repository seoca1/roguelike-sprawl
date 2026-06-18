"""Tests for dashboard prologue viewer data + HTML structure.

Verifies that:
1. prologue_data.json is valid and complete
2. dashboard/index.html references the JSON
3. Character tabs / lang toggle present
4. All 3 characters represented
5. Endings (A + B) present for all characters
6. Dialogue lines have both en + ko
"""

from __future__ import annotations

import json
from pathlib import Path

DASHBOARD = Path(__file__).parent.parent.parent.parent / "dashboard" / "story.html"
DATA = Path(__file__).parent.parent.parent.parent / "design" / "story" / "prologue_data.json"


class TestDataFile:
    """prologue_data.json is valid."""

    def test_data_file_exists(self) -> None:
        assert DATA.exists(), f"Missing: {DATA}"

    def test_data_is_valid_json(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        assert isinstance(data, dict)

    def test_data_has_three_characters(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        chars = data["characters"]
        assert set(chars.keys()) == {"novice", "veteran", "heretic"}

    def test_all_characters_have_bilingual(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        for cid, char in data["characters"].items():
            for f in ("name", "archetype", "origin", "deck", "weapon", "motivation", "flavor"):
                assert f"{f}_en" in char, f"{cid}: missing {f}_en"
                assert f"{f}_ko" in char, f"{cid}: missing {f}_ko"
                assert char[f"{f}_en"], f"{cid}: empty {f}_en"
                assert char[f"{f}_ko"], f"{cid}: empty {f}_ko"

    def test_scenes_have_dialogue(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        for scene in data["scenes"]:
            assert "lines" in scene
            assert len(scene["lines"]) > 0

    def test_character_select_has_three_choices(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        select = next(s for s in data["scenes"] if s["id"] == "finn_office")
        assert "choice" in select
        options = select["choice"]["options"]
        assert len(options) == 3
        chars = {opt["character"] for opt in options}
        assert chars == {"novice", "veteran", "heretic"}

    def test_each_character_has_two_endings(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        endings = data["endings"]
        for cid in ("novice", "veteran", "heretic"):
            assert cid in endings
            ids = {e["id"] for e in endings[cid]}
            assert ids == {"A", "B"}, f"{cid} endings: {ids}"

    def test_ending_lines_bilingual(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        for cid, endings in data["endings"].items():
            for end in endings:
                for line in end["lines"]:
                    assert line.get("text_en"), f"{cid} ending {end['id']}: empty text_en"
                    assert line.get("text_ko"), f"{cid} ending {end['id']}: empty text_ko"


class TestDashboardHtml:
    """dashboard/index.html structure."""

    def test_dashboard_exists(self) -> None:
        assert DASHBOARD.exists()

    def test_dashboard_references_prologue_data(self) -> None:
        html = DASHBOARD.read_text(encoding="utf-8")
        assert "prologue_data.json" in html

    def test_dashboard_has_three_char_tabs(self) -> None:
        html = DASHBOARD.read_text(encoding="utf-8")
        assert 'data-char="novice"' in html
        assert 'data-char="veteran"' in html
        assert 'data-char="heretic"' in html

    def test_dashboard_has_three_lang_buttons(self) -> None:
        html = DASHBOARD.read_text(encoding="utf-8")
        assert 'data-lang="ko"' in html
        assert 'data-lang="en"' in html
        assert 'data-lang="both"' in html

    def test_dashboard_has_char_info_fields(self) -> None:
        html = DASHBOARD.read_text(encoding="utf-8")
        for f in ("age", "origin", "deck", "weapon", "motivation"):
            assert f'data-field="{f}"' in html, f"Missing char-info field: {f}"

    def test_dashboard_has_prologue_endings_section(self) -> None:
        html = DASHBOARD.read_text(encoding="utf-8")
        assert 'id="prologueEndings"' in html

    def test_dashboard_has_prologue_scenes_section(self) -> None:
        html = DASHBOARD.read_text(encoding="utf-8")
        assert 'id="prologueScenes"' in html

    def test_dashboard_has_javascript_loader(self) -> None:
        html = DASHBOARD.read_text(encoding="utf-8")
        # JS should fetch the JSON
        assert "fetch(" in html
        assert "render()" in html

    def test_dashboard_styles_present(self) -> None:
        html = DASHBOARD.read_text(encoding="utf-8")
        for cls in (
            "prologue-viewer",
            "char-tab",
            "lang-btn",
            "char-info",
            "scene",
            "dialogue-line",
            "ending-block",
        ):
            assert f'"{cls}"' in html or f".{cls}" in html or f"class=\"{cls}" in html, f"Missing style class: {cls}"


class TestDataAndCodeConsistency:
    """JSON data and original_story.py are consistent."""

    def test_choice_option_keys_match(self) -> None:
        """3 choice keys (1, 2, 3) map to novice/veteran/heretic."""
        data = json.loads(DATA.read_text(encoding="utf-8"))
        select = next(s for s in data["scenes"] if s["id"] == "finn_office")
        expected = {"1": "novice", "2": "veteran", "3": "heretic"}
        for opt in select["choice"]["options"]:
            assert expected[opt["key"]] == opt["character"]

    def test_each_character_has_finn_response(self) -> None:
        """Each character has a unique Finn response in the choice."""
        data = json.loads(DATA.read_text(encoding="utf-8"))
        select = next(s for s in data["scenes"] if s["id"] == "finn_office")
        responses = [opt["response_en"] for opt in select["choice"]["options"]]
        # All 3 should be unique (no duplicates)
        assert len(set(responses)) == 3, "All 3 responses should be unique"

    def test_ending_total_six(self) -> None:
        """3 characters × 2 endings = 6 endings total."""
        data = json.loads(DATA.read_text(encoding="utf-8"))
        total = sum(len(e) for e in data["endings"].values())
        assert total == 6


class TestQuoteFormatting:
    """Original Gibson quote is preserved."""

    def test_opening_quote_matches_neuromancer(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        quote = data["setting"]["openning_quote_en"]
        # First line of Neuromancer (1984)
        assert "television" in quote.lower()
        assert "dead channel" in quote.lower()

    def test_opening_quote_source_attributed(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        source = data["setting"]["openning_quote_source"]
        assert "Gibson" in source
        assert "Neuromancer" in source
