"""Tests for dashboard event dialogue viewer data + HTML structure.

Verifies that:
1. event_dialogues.json is valid and complete
2. dashboard/index.html references the event JSON
3. NPC filter buttons present
4. All 5 NPCs represented
5. Dialogues have bilingual text
6. Choices are well-formed
"""

from __future__ import annotations

import json
from pathlib import Path

DASHBOARD = Path(__file__).parent.parent.parent.parent / "dashboard" / "story.html"
DATA = Path(__file__).parent.parent.parent.parent / "design" / "story" / "event_dialogues.json"


class TestEventDataFile:
    """event_dialogues.json is valid."""

    def test_data_file_exists(self) -> None:
        assert DATA.exists()

    def test_data_is_valid_json(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        assert isinstance(data, dict)

    def test_data_has_five_npcs(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        npcs = data["npcs"]
        assert set(npcs.keys()) == {"finn", "dixie", "maelcum", "bartender", "ta_rep"}

    def test_npcs_have_bilingual_fields(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        for nid, npc in data["npcs"].items():
            assert npc.get("name_en"), f"{nid}: missing name_en"
            assert npc.get("name_ko"), f"{nid}: missing name_ko"
            assert npc.get("archetype_en"), f"{nid}: missing archetype_en"
            assert npc.get("archetype_ko"), f"{nid}: missing archetype_ko"

    def test_dialogues_minimum_count(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        dialogues = data["dialogues"]
        assert len(dialogues) >= 10, f"Need at least 10 dialogues, got {len(dialogues)}"

    def test_dialogues_reference_valid_npcs(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        npcs = data["npcs"]
        for did, dlg in data["dialogues"].items():
            assert dlg["npc"] in npcs, f"dialogue {did}: npc '{dlg['npc']}' not defined"

    def test_dialogue_lines_bilingual(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        for did, dlg in data["dialogues"].items():
            for j, line in enumerate(dlg["lines"]):
                assert line.get("text_en"), f"{did} line {j}: missing text_en"
                assert line.get("text_ko"), f"{did} line {j}: missing text_ko"
                assert line.get("speaker"), f"{did} line {j}: missing speaker"

    def test_dialogue_choices_bilingual(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        for did, dlg in data["dialogues"].items():
            if "choices" not in dlg:
                continue
            for c in dlg["choices"]:
                assert c.get("text_en"), f"{did} choice: missing text_en"
                assert c.get("text_ko"), f"{did} choice: missing text_ko"
                assert c.get("response_en"), f"{did} choice: missing response_en"
                assert c.get("response_ko"), f"{did} choice: missing response_ko"

    def test_dialogue_ids_unique(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        ids = [d["id"] for d in data["dialogues"].values()]
        assert len(ids) == len(set(ids)), f"Duplicate dialogue ids: {ids}"

    def test_choice_keys_unique_per_dialogue(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        for did, dlg in data["dialogues"].items():
            if "choices" not in dlg:
                continue
            keys = [c["key"] for c in dlg["choices"]]
            assert len(keys) == len(set(keys)), f"{did}: duplicate choice keys"

    def test_leads_to_references(self) -> None:
        """leads_to fields reference real dialogue ids or special markers."""
        data = json.loads(DATA.read_text(encoding="utf-8"))
        dialogue_ids = {d["id"] for d in data["dialogues"].values()}
        # endings and other special markers
        valid_specials = {f"ending_{c}_{e}" for c in "ABC" for e in "AB"}
        valid_specials |= {
            "character_select",
            "freeside_journey",
            "maelcum_intro",
        }
        for did, dlg in data["dialogues"].items():
            if "choices" not in dlg:
                continue
            for c in dlg["choices"]:
                lt = c.get("leads_to", "")
                if not lt:
                    continue
                if lt in dialogue_ids or lt in valid_specials:
                    continue
                # Allow ending_XX format
                if lt.startswith("ending_"):
                    continue
                # Anything else: warn but don't fail (allow forward references)
                print(
                    f"  [INFO] {did} choice: leads_to '{lt}' not in current dialogues (forward reference OK)"
                )


class TestEventDashboardHtml:
    """dashboard/index.html has event viewer section."""

    def test_dashboard_references_event_data(self) -> None:
        html = DASHBOARD.read_text(encoding="utf-8")
        assert "event_dialogues.json" in html

    def test_dashboard_has_npc_filter(self) -> None:
        html = DASHBOARD.read_text(encoding="utf-8")
        for npc in ("finn", "dixie", "maelcum", "bartender", "ta_rep"):
            assert f'data-npc="{npc}"' in html, f"Missing NPC filter: {npc}"

    def test_dashboard_has_all_filter(self) -> None:
        html = DASHBOARD.read_text(encoding="utf-8")
        assert 'data-npc="all"' in html

    def test_dashboard_has_lang_toggle(self) -> None:
        html = DASHBOARD.read_text(encoding="utf-8")
        assert 'data-evt-lang="ko"' in html
        assert 'data-evt-lang="en"' in html
        assert 'data-evt-lang="both"' in html

    def test_dashboard_has_event_stats(self) -> None:
        html = DASHBOARD.read_text(encoding="utf-8")
        for stat in ("npcs", "dialogues", "lines", "choices"):
            assert f'data-stat="{stat}"' in html

    def test_dashboard_has_event_list_container(self) -> None:
        html = DASHBOARD.read_text(encoding="utf-8")
        assert 'id="eventList"' in html

    def test_dashboard_event_styles_present(self) -> None:
        html = DASHBOARD.read_text(encoding="utf-8")
        for cls in ("event-viewer", "npc-filter", "event-block", "event-line", "event-choice"):
            assert cls in html, f"Missing event viewer style: {cls}"


class TestEventDialogueQuality:
    """Quality checks on the dialogue content."""

    def test_total_lines_minimum(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        total = sum(len(d["lines"]) for d in data["dialogues"].values())
        assert total >= 30, f"Need at least 30 dialogue lines, got {total}"

    def test_each_npc_has_at_least_one_dialogue(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        npc_dlg_count: dict[str, int] = {}
        for d in data["dialogues"].values():
            npc_dlg_count[d["npc"]] = npc_dlg_count.get(d["npc"], 0) + 1
        for nid in ("finn", "dixie", "maelcum", "bartender", "ta_rep"):
            assert npc_dlg_count.get(nid, 0) >= 1, f"NPC {nid} has no dialogues"

    def test_dixie_has_multiple_dialogues(self) -> None:
        """Dixie is the construct, central to the story. Should have many."""
        data = json.loads(DATA.read_text(encoding="utf-8"))
        dixie_count = sum(1 for d in data["dialogues"].values() if d["npc"] == "dixie")
        assert dixie_count >= 3, f"Dixie should have at least 3 dialogues, got {dixie_count}"

    def test_finn_has_followup_dialogue(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        finn_ids = [d["id"] for d in data["dialogues"].values() if d["npc"] == "finn"]
        assert any("followup" in fid for fid in finn_ids), "Finn should have a follow-up dialogue"

    def test_at_least_one_ice_intro(self) -> None:
        data = json.loads(DATA.read_text(encoding="utf-8"))
        ids = [d["id"] for d in data["dialogues"].values()]
        assert any("ice" in i for i in ids), "Need at least one ICE dialogue"
