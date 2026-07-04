"""Tests for Mid/Core/TA zone expansion (Phase 7.2).

Validates the 9 new zone-specific missions added in 2026-07-04:
  - 3 MID zone missions (depth 4-8)
  - 3 CORE zone missions (depth 9-15)
  - 3 TA zone missions (depth 20-30)
"""

from __future__ import annotations

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


class TestZoneExpansion:
    @classmethod
    def setup_class(cls):
        with open(DATA_DIR / "missions" / "missions.json") as f:
            cls.missions = json.load(f)

    def test_mid_zone_has_3_new_missions(self):
        """3 new MID zone missions added."""
        mid_new = [
            m
            for m in self.missions.values()
            if isinstance(m, dict)
            and m.get("zone") == "mid"
            and m.get("id")
            in {
                "hosaka_corporate_infiltration",
                "sense_net_media_extract",
                "yakuza_loan_shark",
            }
        ]
        assert len(mid_new) == 3, f"Expected 3 new MID missions, got {len(mid_new)}"

    def test_core_zone_has_3_new_missions(self):
        core_new = [
            m
            for m in self.missions.values()
            if isinstance(m, dict)
            and m.get("zone") == "core"
            and m.get("id")
            in {
                "ta_payroll_archive",
                "maas_neural_extract",
                "construct_memory_rescue",
            }
        ]
        assert len(core_new) == 3, f"Expected 3 new CORE missions, got {len(core_new)}"

    def test_ta_zone_has_3_new_missions(self):
        ta_new = [
            m
            for m in self.missions.values()
            if isinstance(m, dict)
            and m.get("zone") == "ta"
            and m.get("id")
            in {
                "ta_straylight_archive",
                "ta_3jane_betrayal",
                "ta_wintermute_direct",
            }
        ]
        assert len(ta_new) == 3, f"Expected 3 new TA missions, got {len(ta_new)}"

    def test_zone_distribution_improved(self):
        """Total mission distribution should be healthier after expansion."""
        zone_counts = {}
        for m in self.missions.values():
            if isinstance(m, dict) and "zone" in m:
                zone_counts[m["zone"]] = zone_counts.get(m["zone"], 0) + 1

        # MID should be >= 5 (was 2, +3 new = 5)
        assert zone_counts.get("mid", 0) >= 5, f"MID missions: {zone_counts.get('mid', 0)}"

        # CORE should be >= 5 (was 3, +3 new = 6)
        assert zone_counts.get("core", 0) >= 5, f"CORE missions: {zone_counts.get('core', 0)}"

        # TA should be >= 3 (was 1, +3 new = 4)
        assert zone_counts.get("ta", 0) >= 3, f"TA missions: {zone_counts.get('ta', 0)}"

    def test_new_missions_have_required_story_metadata(self):
        """All new missions must have story metadata per ADR-0051."""
        new_ids = {
            "hosaka_corporate_infiltration",
            "sense_net_media_extract",
            "yakuza_loan_shark",
            "ta_payroll_archive",
            "maas_neural_extract",
            "construct_memory_rescue",
            "ta_straylight_archive",
            "ta_3jane_betrayal",
            "ta_wintermute_direct",
        }
        required = {"synopsis_en", "synopsis_ko", "source", "character_ref", "arc", "pillar"}
        for mid in new_ids:
            story = self.missions[mid].get("story", {})
            missing = required - set(story.keys())
            assert not missing, f"{mid} missing story fields: {missing}"

    def test_ta_wintermute_direct_has_highest_grade(self):
        """ta_wintermute_direct should be grade 5-6 (TA zone)."""
        mission = self.missions["ta_wintermute_direct"]
        assert mission["grade_min"] >= 5
        assert mission["grade_max"] >= 5

    def test_construct_memory_rescue_has_unique_objective(self):
        """construct_memory_rescue should have rescue_construct objective."""
        mission = self.missions["construct_memory_rescue"]
        obj_type = mission["primary_objective"]["type"]
        assert obj_type == "rescue_construct", f"Got {obj_type}"


class TestZoneIceExpansion:
    @classmethod
    def setup_class(cls):
        with open(DATA_DIR / "combat" / "ice_types.json") as f:
            cls.ice_types = json.load(f)

    def test_corporate_guard_added(self):
        """Mid zone ICE added."""
        assert "corporate_guard" in self.ice_types
        ice = self.ice_types["corporate_guard"]
        assert ice["zone"] == "mid"
        assert ice["tier"] == 2

    def test_archive_sentinel_added(self):
        """Core zone ICE added."""
        assert "archive_sentinel" in self.ice_types
        ice = self.ice_types["archive_sentinel"]
        assert ice["zone"] == "core"
        assert ice["tier"] == 4

    def test_wintermute_proxy_added(self):
        """TA zone boss ICE added."""
        assert "wintermute_proxy" in self.ice_types
        ice = self.ice_types["wintermute_proxy"]
        assert ice["zone"] == "ta"
        assert ice["tier"] == 6
        assert "wintermute_key" in [item["item"] for item in ice["loot_table"]]
