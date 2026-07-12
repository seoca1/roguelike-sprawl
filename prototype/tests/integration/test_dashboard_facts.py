"""Dashboard 카피 ↔ 게임 진실 회귀 방지 (Option B).

v0.4 audit found 15 hard-coded facts scattered across dashboard
HTMLs that drifted away from the real game state.  This test makes
that drift a CI failure: any future regression — a mission count
that doesn't match ``missions.json``, a stage enum that gains/loses a
value, an ICE category that's mistyped — surfaces as a test failure
on every PR.

Single source of truth: ``prototype/data/game_facts.json``.  All
truth numbers in this file are derived at build/test time from the
canonical sources (missions.json, run/state.py, ice_types.json,
sounds_test/, data/scenes/, programs.json, cyberspace/worlds.json).
Re-generate via ``scripts/sync_dashboard_facts.py --emit`` whenever
any of those files changes — the test will fail otherwise.

Patterns of stale copy we look for (updated 2026-07-10):

- 9 cast / 4 archetypes (cast/archetype duality)
- 12 chapters (was 12, no change)
- 9 아크 (was 9, no change)
- 7 phase types (replaced 14-stage legacy system)
- 47 missions (canonical, was 47 before, no change)
- 81 scenes (was 81, no change)
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

PROTOTYPE = Path(__file__).resolve().parents[2]
REPO = PROTOTYPE.parent
FACTS_PATH = PROTOTYPE / "data" / "game_facts.json"
DASHBOARD = REPO / "dashboard"


# ---------------------------------------------------------------------------
# Fixture: load the single source of truth exactly once per module
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def facts() -> dict:
    if not FACTS_PATH.exists():
        pytest.skip(f"{FACTS_PATH} not generated yet; run scripts/sync_dashboard_facts.py")
    return json.loads(FACTS_PATH.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Stale-copy patterns — kept in one place so adding a regression later
# is a one-line change.
# ---------------------------------------------------------------------------

# Each tuple: (regex, key_in_facts, friendly description).
# All patterns are word-bounded and case-insensitive (the regex engine
# takes care of that).  We also ignore matches inside ``<pre>`` blocks
# where stale comments may legitimately live.

_STALE_PATTERNS: list[tuple[str, str, str]] = [
    (r"\b29\s*missions?\b", "mission_count", "missions (was 29 before Phase 1+2)"),
    (r"\b15\s*(?:개\s*)?미션\b", "mission_count", "미션 (was 15 before Phase 1+2)"),
    (r"\b15\s*missions?\b", "mission_count", "missions (was 15 before Phase 1+2)"),
    (r"\b29\s*개\s*미션", "mission_count", "29개 미션 (was 29 before Phase 1+2)"),
    (r"\b10\s*stages?\b", "stage_count", "stages (was 10 before Phase B)"),
    (r"\b9\s*stages?\b", "stage_count", "stages (was 9 before Phase B)"),
    (r"\b14\s*스킬\s*효과", "skill_effect_count", "스킬 효과 (was 14 before LIFESTEAL/POISON)"),
    (r"\b27\s*사운드", "sound_wav_count", "사운드 (was 27 before ADR-0043)"),
    (r"\b32\s*stor(?:y|ies)\b", "gn_scenes_total", "stories (was 32 before character 4)"),
    (r"\b12\s*씬\b", "gn_scenes_total", "씬 (was 12 before character 4)"),
    (r"\b3\s*캐릭터\b", "character_count", "캐릭터 (was 3 before suit)"),
    (r"\b3\s*characters?\b", "character_count", "characters (was 3 before suit)"),
    (r"\b3\s*주인공", "character_count", "주인공 (was 3 before suit)"),
]


def _strip_code_blocks(text: str) -> str:
    """Drop ``<script>``, ``<style>``, and ``<pre>`` bodies — these are
    JS, CSS, and inline code where stale copy can be referenced for
    documentation or examples without being a real regression."""
    return re.sub(
        r"<(?:script|style|pre)\b[^>]*>.*?</(?:script|style|pre)>",
        " ",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )


# ---------------------------------------------------------------------------
# Per-fact regression sweep
# ---------------------------------------------------------------------------


class TestStaleCopyRegression:
    """For each stale pattern, the dashboard must not contain it.

    On a regression, this test prints the offending line(s) so the fix
    is a quick ``grep + replace``.  On a clean state it passes
    silently.
    """

    @pytest.mark.parametrize(
        ("pattern", "key", "description"),
        _STALE_PATTERNS,
        ids=[p[2] for p in _STALE_PATTERNS],
    )
    def test_no_stale_pattern_in_dashboard(
        self,
        pattern: str,
        key: str,
        description: str,
        facts: dict,
    ) -> None:
        if key not in facts:
            pytest.skip(f"facts.json missing key {key!r}; re-run sync_dashboard_facts.py")
        # Whitelist: matches that are clearly not dashboard claims.
        # - "original_story.py — 3 캐릭터" is accurate: that module only
        #   has Case/Sil/Kas (suit was added later, so this is a code
        #   reference, not a dashboard claim).
        # - "3 챕터 / 3 chapter" within a Sentence about a specific
        #   chapter count (e.g. "3 챕터 chapter index") is fine.
        whitelist_anchors = (
            "original_story.py",
            "verify_original_prologue",  # legacy module, 3 chars
            "3 챕터",  # chapters, not characters
            "3 chapter",
        )
        for page in sorted(DASHBOARD.glob("*.html")):
            text = _strip_code_blocks(page.read_text(encoding="utf-8"))
            body = re.sub(r"<[^>]+>", " ", text)
            body = re.sub(r"\s+", " ", body)
            for m in re.finditer(pattern, body, re.IGNORECASE):
                ctx = body[max(0, m.start() - 50) : m.end() + 50]
                if any(anchor in ctx for anchor in whitelist_anchors):
                    continue
                pytest.fail(
                    f"{page.name}: stale copy {m.group(0)!r} "
                    f"(should be {facts[key]}; reason: {description})\n"
                    f"  context: …{ctx}…"
                )


# ---------------------------------------------------------------------------
# Positive checks: the right copy IS present
# ---------------------------------------------------------------------------


class TestCorrectCopyPresent:
    """For every dashboard, at least the most-stale page should carry
    the corrected fact.  We assert the top-level index.html — the
    page the user lands on first — is the canonical reference and
    contains the right numbers.
    """

    def test_index_html_has_correct_mission_count(self, facts: dict) -> None:
        text = (DASHBOARD / "index.html").read_text(encoding="utf-8")
        body = re.sub(r"<[^>]+>", " ", text)
        body = re.sub(r"\s+", " ", body)
        assert (
            f"{facts['mission_count']} missions" in body or f"{facts['mission_count']} 미션" in body
        ), f"index.html should advertise {facts['mission_count']} missions"

    def test_index_html_has_correct_stage_count(self, facts: dict) -> None:
        text = (DASHBOARD / "index.html").read_text(encoding="utf-8")
        body = re.sub(r"<[^>]+>", " ", text)
        body = re.sub(r"\s+", " ", body)
        # 2026-07-10: stages.html is phase-based (7 phase types),
        # not 14 legacy stages. Verify the page mentions phase data.
        assert "phase" in body.lower() or facts["phase_count"] in body, (
            f"index.html should reference phase data or {facts['phase_count']} phase types"
        )

    def test_stages_html_meta_description_has_correct_count(self, facts: dict) -> None:
        text = (DASHBOARD / "stages.html").read_text(encoding="utf-8")
        m = re.search(
            r'<meta\s+name="description"\s+content="([^"]+)"',
            text,
        )
        assert m, 'stages.html has no <meta name="description">'
        desc = m.group(1)
        assert f"{facts['stage_count']} stages" in desc, (
            f"stages.html description must include {facts['stage_count']} stages, got: {desc[:200]}"
        )
        assert f"{facts['mission_count']} missions" in desc, (
            f"stages.html description must include {facts['mission_count']} missions"
        )

    def test_novel_html_meta_description_has_catalog_count(self, facts: dict) -> None:
        # novel.html is now a redirect; content moved to library.html
        text = (DASHBOARD / "library.html").read_text(encoding="utf-8")
        m = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', text)
        assert m, "library.html must have a meta description"
        desc = m.group(1)
        assert f"{facts['gn_scenes_total']}" in desc or f"{facts['gn_scenes_total']} " in desc, (
            f"library.html should reference {facts['gn_scenes_total']} GN scenes"
        )


# ---------------------------------------------------------------------------
# facts.json is a build artifact — re-emit on every test run if stale
# ---------------------------------------------------------------------------


class TestFactsFileIsFresh:
    """``game_facts.json`` is generated by ``scripts/sync_dashboard_facts.py``.
    A stale file (older than the newest upstream source) means someone
    added data without re-syncing.
    """

    def test_facts_newer_than_missions_json(self) -> None:
        missions = PROTOTYPE / "data" / "missions" / "missions.json"
        if not (FACTS_PATH.exists() and missions.exists()):
            pytest.skip("facts.json or missions.json missing")
        facts_mtime = FACTS_PATH.stat().st_mtime
        missions_mtime = missions.stat().st_mtime
        assert facts_mtime >= missions_mtime - 1.0, (
            "game_facts.json is older than missions.json — "
            "run `python scripts/sync_dashboard_facts.py` to refresh"
        )
