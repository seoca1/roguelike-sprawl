"""Novel pipeline triple-mapping validator (ADR-0061 follow-up).

The v0.4 dashboard audit discovered that the novel pipeline
relied on three independent sources of truth that could drift
apart silently:

1. ``prototype/data/missions/missions.json`` — every mission
   declares ``story.source`` (the Fiction stem it points at).
2. ``Fiction/derivative/sprawl-trilogy/short-stories/`` — the
   original derivative works (en + ko) referenced by that stem.
3. ``dashboard/stories/short-stories/`` — the regenerated
   dashboard HTML pages built by ``markdown_to_story_html.py``.

These tests assert that the three views stay in sync.  Run them
in CI on every PR so a Fiction rename, a mission source change,
or a stale alias regression all get caught before merge.

Test layout:

- ``TestTripleMapping``         — Mission ⇄ Fiction ⇄ Dashboard
- ``TestMissionDispatchCoverage``  — every mission source can be
                                    dispatched as a novel hook
- ``TestFictionPair``           — every Fiction .md has a .ko.md
- ``TestFrontmatterIntegrity``  — every Fiction file links back to
                                    its mission via game_integration
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Path resolution — pytest invokes from various cwds; resolve via this file.
# ---------------------------------------------------------------------------

PROTOTYPE = Path(__file__).resolve().parents[2]
REPO = PROTOTYPE.parent
FICTION_STORIES = Path(
    "/Users/emilio/projects/Projects/Fiction/derivative/sprawl-trilogy/short-stories"
)
DASH_STORIES = REPO / "dashboard" / "stories" / "short-stories"
MISSIONS_JSON = PROTOTYPE / "data" / "missions" / "missions.json"


# ---------------------------------------------------------------------------
# 5. End-to-end dispatch — every mission's hook fires a status message
# ---------------------------------------------------------------------------


class _DispatchEndToEnd:
    """Helper-based pytest class (must appear after helper functions).

    Wraps ``trigger_mission_completion_novel_hooks`` for every mission
    in missions.json.  Lives in TestNovelPipelineDispatch below after
    forwarding through a thin alias.
    """

    def _dispatch(self, mission_id: str) -> bool:
        """Return True if the mission hooks fired successfully."""
        sys.path.insert(0, str(PROTOTYPE / "src"))
        try:
            from roguelike_sprawl.engine.novel_integration import (
                mission_to_stem,
                trigger_mission_completion_novel_hooks,
            )
            from roguelike_sprawl.engine.state import AppState
        finally:
            sys.path.pop(0)

        state = AppState()
        stem = mission_to_stem(mission_id)
        if stem is None:
            return False
        before = len(state.status_messages)
        trigger_mission_completion_novel_hooks(state, mission_id)
        return len(state.status_messages) > before


class TestNovelPipelineDispatch:
    """End-to-end: a mission completion should fire the hook and
    produce a status message in the player's ``AppState``.  We
    iterate every mission in ``missions.json`` so a regression in
    *any* of the 38 mission pipelines is caught here rather than
    discovered by hand.
    """

    def test_every_mission_dispatches_at_least_one_status_message(self) -> None:
        """One single test loops over every mission so we get **one
        failure per regression** instead of N independent SKIPs.
        """
        helper = _DispatchEndToEnd()
        sources = _load_mission_sources()
        failed = []
        skipped = []
        for mission_id in sorted(sources):
            if helper._dispatch(mission_id):
                continue
            # Could mean stem is None, OR dispatch returned no messages.
            stem = _lookup_stem(mission_id)
            if stem is None:
                skipped.append(mission_id)
            else:
                failed.append(mission_id)
        assert not failed, (
            f"missions whose novel hook fired zero status messages: {failed}\n"
            f"  (skipped because stem unresolved: {skipped})"
        )


# ---------------------------------------------------------------------------
# Helpers (defined last so they can be used by the parametrize decorator
# above; required to satisfy pytest's collection-time evaluation).
# ---------------------------------------------------------------------------


def _load_mission_sources() -> dict[str, str]:
    """Return mission_id → story.source."""
    if not MISSIONS_JSON.exists():
        return {}
    data = json.loads(MISSIONS_JSON.read_text(encoding="utf-8"))
    return {
        mid: m["story"]["source"] for mid, m in data.items() if isinstance(m, dict) and "story" in m
    }


def _lookup_stem(mission_id: str) -> str | None:
    """Look up the Fiction stem for a mission via the integration layer."""
    sys.path.insert(0, str(PROTOTYPE / "src"))
    try:
        from roguelike_sprawl.engine.novel_integration import mission_to_stem
    finally:
        sys.path.pop(0)
    return mission_to_stem(mission_id)


def _fiction_stems() -> set[str]:
    """Stem of every EN .md file (date prefix removed)."""
    if not FICTION_STORIES.exists():
        return set()
    out: set[str] = set()
    for p in FICTION_STORIES.glob("*.md"):
        if p.stem.endswith(".ko"):
            continue
        out.add(re.sub(r"^\d{4}-\d{2}-\d{2}_", "", p.stem))
    return out


def _fiction_ko_stems() -> set[str]:
    if not FICTION_STORIES.exists():
        return set()
    out: set[str] = set()
    for p in FICTION_STORIES.glob("*.ko.md"):
        out.add(re.sub(r"^\d{4}-\d{2}-\d{2}_", "", p.stem[:-3]))
    return out


def _dashboard_en_stems() -> set[str]:
    if not DASH_STORIES.exists():
        return set()
    return {p.stem.replace("_en", "") for p in DASH_STORIES.glob("*_en.html")}


def _dashboard_ko_stems() -> set[str]:
    if not DASH_STORIES.exists():
        return set()
    return {p.stem.replace("_ko", "") for p in DASH_STORIES.glob("*_ko.html")}


def _dashboard_stem_to_fiction_stem_map() -> dict[str, str]:
    """Reverse mapping for dashboard pages: stem → Fiction stem.

    Used to recover the canonical Fiction stem from a dashboard stem
    when the mission source points at a hyphenated stem that became
    a dashboard stem verbatim (or vice versa).
    """
    return {stem: stem for stem in _dashboard_en_stems()}


# ---------------------------------------------------------------------------
# 1. Triple mapping — Mission ⇄ Fiction ⇄ Dashboard
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def mission_sources() -> dict[str, str]:
    return _load_mission_sources()


class TestTripleMapping:
    """Every mission ``story.source`` resolves in both Fiction and Dashboard."""

    def test_all_missions_have_story_field(self, mission_sources: dict[str, str]) -> None:
        assert len(mission_sources) >= 33, f"Expected ≥33 missions, got {len(mission_sources)}"

    def test_mission_sources_resolve_in_fiction(self, mission_sources: dict[str, str]) -> None:
        """Each mission source must map to a real Fiction short story."""
        stems = _fiction_stems()
        unresolved = sorted({src for src in mission_sources.values() if src not in stems})
        assert not unresolved, (
            f"Mission sources without matching Fiction .md: {unresolved}\n"
            f"  Available Fiction stems: {sorted(stems)[:5]} …"
        )

    def test_mission_sources_resolve_in_dashboard(self, mission_sources: dict[str, str]) -> None:
        """Each mission source must map to a real dashboard HTML page."""
        stems = _dashboard_en_stems()
        unresolved = sorted({src for src in mission_sources.values() if src not in stems})
        assert not unresolved, f"Mission sources without matching dashboard/*_en.html: {unresolved}"

    def test_dashboard_pages_have_mission_source(self, mission_sources: dict[str, str]) -> None:
        """Reverse direction: every dashboard page appears in some mission."""
        mission_stems = set(mission_sources.values())
        orphans = sorted(_dashboard_en_stems() - mission_stems)
        # Some dashboard pages are intentionally un-owned (e.g. free-form Fiction
        # stories that no mission points at).  aleph_fragment, mollys_razor,
        # ta_heist added 2026-07-08 as free-form Fiction without missions.
        # Tolerate up to 5 orphans but fail loudly if more appear.
        assert len(orphans) <= 5, f"Excess orphan dashboard pages (no mission source): {orphans}"

    def test_three_way_intersection(self, mission_sources: dict[str, str]) -> None:
        """The intersection of mission × fiction × dashboard should equal
        the number of distinct mission sources."""
        mission = set(mission_sources.values())
        fiction = _fiction_stems()
        dash = _dashboard_en_stems()
        triple = mission & fiction & dash
        # Each unique mission source must appear in both Fiction and dashboard.
        # (A source like ``case_jackout-30sec`` that's missing in one side will
        # surface via the ``resolve_in_*`` tests above.)
        assert len(triple) == len(mission), (
            f"3-way intersection smaller than mission source set: "
            f"|triple|={len(triple)} vs |mission|={len(mission)}; "
            f"in_mission_only={sorted(mission - fiction - dash)}, "
            f"missing_in_fiction={sorted(mission - fiction)}, "
            f"missing_in_dashboard={sorted(mission - dash)}"
        )


# ---------------------------------------------------------------------------
# 2. Mission dispatch coverage — every mission can fire its novel hook
# ---------------------------------------------------------------------------


class TestMissionDispatchCoverage:
    """For every mission, ``mission_to_stem`` must return a stem that
    the NovelDispatcher can resolve (i.e. the stem exists in the Fiction
    catalog).  This guards against three regressions at once:

    - mission source missing from Fiction (caught above too)
    - mission source typo that resolver can't normalize
    - NovelCatalog auto-discovery failure (the Fiction repo moved)
    """

    def test_dispatch_for_every_mission(self, mission_sources: dict[str, str]) -> None:
        # Local imports keep pytest collection fast on systems where the
        # prototype venv isn't active.
        sys.path.insert(0, str(PROTOTYPE / "src"))
        try:
            from roguelike_sprawl.engine.novel_integration import mission_to_stem
        finally:
            sys.path.pop(0)
        failed: list[tuple[str, str, str | None]] = []
        for mid, expected_src in mission_sources.items():
            try:
                stem = mission_to_stem(mid)
            except Exception as exc:  # pragma: no cover — defensive
                failed.append((mid, expected_src, f"raised {type(exc).__name__}: {exc}"))
                continue
            if stem is None:
                failed.append((mid, expected_src, "mission_to_stem returned None"))
            elif stem != expected_src:
                failed.append((mid, expected_src, f"got {stem!r}"))
        assert not failed, "mission_to_stem() failed for these missions:\n" + "\n".join(
            f"  {m}: src={s!r}  {why}" for m, s, why in failed
        )

    def test_dispatch_idempotent(self, mission_sources: dict[str, str]) -> None:
        """Calling ``mission_to_stem`` twice yields the same value."""
        sys.path.insert(0, str(PROTOTYPE / "src"))
        try:
            from roguelike_sprawl.engine.novel_integration import mission_to_stem
        finally:
            sys.path.pop(0)
        for mid in mission_sources:
            a = mission_to_stem(mid)
            b = mission_to_stem(mid)
            assert a == b, f"{mid}: dispatch non-idempotent ({a!r} vs {b!r})"


# ---------------------------------------------------------------------------
# 3. Fiction EN/KO pair completeness
# ---------------------------------------------------------------------------


class TestFictionPair:
    """Every Fiction EN short story should have a paired ``.ko.md``."""

    def test_no_orphan_english_files(self) -> None:
        en = _fiction_stems()
        ko = _fiction_ko_stems()
        orphans = sorted(en - ko)
        assert not orphans, (
            f"Fiction EN files without KO pair: {orphans}\n"
            f"  Run: python scripts/markdown_to_story_html.py --lang ko"
        )

    def test_no_orphan_korean_files(self) -> None:
        en = _fiction_stems()
        ko = _fiction_ko_stems()
        orphans = sorted(ko - en)
        assert not orphans, f"Fiction KO files without EN pair: {orphans}"


# ---------------------------------------------------------------------------
# 4. Fiction frontmatter game_integration
# ---------------------------------------------------------------------------


class TestFrontmatterIntegrity:
    """Every mission-backed Fiction file's frontmatter should reference
    its mission via ``game_integration.mission_id``."""

    @pytest.fixture(scope="module")
    def frontmatter_records(self) -> dict[str, dict]:
        """stem → parsed game_integration dict (frontmatter parsed naively)."""
        if not FICTION_STORIES.exists():
            return {}
        out: dict[str, dict] = {}
        for p in FICTION_STORIES.glob("*.md"):
            if p.stem.endswith(".ko"):
                continue
            stem = re.sub(r"^\d{4}-\d{2}-\d{2}_", "", p.stem)
            text = p.read_text(encoding="utf-8")
            try:
                fm = _parse_frontmatter(text)
            except Exception:
                continue
            gi = fm.get("game_integration")
            if isinstance(gi, dict):
                out[stem] = gi
        return out

    def test_mission_backed_fiction_has_game_integration(
        self, frontmatter_records: dict[str, dict]
    ) -> None:
        """Soft check: warn — don't fail — when a mission-backed Fiction
        file is missing ``game_integration``.

        The Fiction corpus lives in a separate repository, so the
        canonical fix is ``scripts/backfill_game_integration.py`` on
        that side.  We still want this guard in our pipeline so a
        regression surfaces in pytest output, but we don't fail the
        build over an out-of-tree metadata drift.
        """
        mission_sources = _load_mission_sources()
        mission_targets = {fm.get("mission_id") for fm in frontmatter_records.values()}
        missing = sorted(src for src in mission_sources.values() if src not in mission_targets)
        if missing:
            import warnings

            warnings.warn(
                f"Fiction stems without game_integration.mission_id "
                f"(run scripts/backfill_game_integration.py on Fiction repo "
                f"to fix): {missing}",
                stacklevel=2,
            )

    def test_game_integration_mission_id_matches_source(
        self,
        frontmatter_records: dict[str, dict],
        mission_sources: dict[str, str],
    ) -> None:
        """The mission_id declared in frontmatter must reverse-resolve to
        a mission whose ``story.source`` matches the file's stem."""
        for stem, gi in frontmatter_records.items():
            mid = gi.get("mission_id")
            if not mid:
                continue
            # Reverse lookup
            back = mission_sources.get(mid)
            assert back is not None, (
                f"stem={stem}: frontmatter.mission_id={mid!r} not in missions.json"
            )
            assert back == stem, (
                f"stem={stem}: mission_id={mid!r} but mission {mid}.story.source="
                f"{back!r} (expected {stem!r})"
            )

    def test_arc_field_in_range(
        self,
        frontmatter_records: dict[str, dict],
        mission_sources: dict[str, str],
    ) -> None:
        """Every mission-backed stem must have a valid ``arc`` (1-5)
        matching the mission arc in missions.json."""
        missions = json.loads(MISSIONS_JSON.read_text(encoding="utf-8"))
        for stem, gi in frontmatter_records.items():
            mid = gi.get("mission_id")
            if not mid:
                continue
            mission = missions.get(mid)
            if not mission:
                continue
            assert mission["story"]["arc"] == gi.get("arc"), (
                f"stem={stem}: frontmatter.arc={gi.get('arc')} but "
                f"mission {mid}.story.arc={mission['story']['arc']}"
            )
            assert 1 <= gi.get("arc", 0) <= 5, f"stem={stem}: arc={gi.get('arc')} not in 1-5"


# ---------------------------------------------------------------------------
# Naive YAML frontmatter parser (avoids PyYAML dependency at test time)
# ---------------------------------------------------------------------------


def _parse_frontmatter(text: str) -> dict:
    """Parse a tiny subset of YAML frontmatter sufficient for these tests.

    Supports indented key-value pairs and nested mappings two levels
    deep (``game_integration.mission_id``).  Returns an empty dict if
    the document has no frontmatter or parsing fails.
    """
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    body = text[3:end].strip()
    lines = body.split("\n")
    out: dict = {}
    stack = [out]  # stack of dicts being built
    indents = [0]  # indent levels for each frame
    for raw in lines:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        line = raw.strip()
        # Pop frames until indent fits.
        while stack and indents[-1] > indent:
            stack.pop()
            indents.pop()
        if line.startswith("- "):
            # list entry inside current dict — skipped for our subset
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        frame = stack[-1]
        if value == "":
            # New nested mapping.
            nested: dict = {}
            frame[key] = nested
            stack.append(nested)
            indents.append(indent)
        else:
            # Strip surrounding quotes / coercions for the common cases.
            v = value.strip("\"'")
            frame[key] = v
    return out
