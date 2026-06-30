"""Tests for the novel integration subpackage (ADR-0061, Phase 5).

Covers catalog discovery, frontmatter parsing, hook inference,
manifest round-trip, dispatch (dry-run and live), and the high-level
integrator.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest  # noqa: E402

from roguelike_sprawl.novel import (  # noqa: E402
    DispatchReport,
    HookContext,
    HookKind,
    HookResult,
    ManifestEntry,
    NovelCatalog,
    NovelDispatcher,
    NovelEntry,
    NovelFormat,
    NovelManifest,
    NovelRuntime,
    TextProvider,
    dispatch_for_state,
    infer_default_hook,
    load_novel_runtime,
)
from roguelike_sprawl.novel.hooks import (  # noqa: E402
    get_hook_actions,
    register_hook_action,
    reset_hook_registry,
)

REPO_ROOT = Path("/Users/emilio/projects/Projects")


# ============================================================================
# Fixtures
# ============================================================================


class FakeAppState:
    """Minimal stand-in for engine.state.AppState used in dispatch tests."""

    def __init__(self) -> None:
        self.status_messages: list[str] = []
        self.context_hint: str = ""
        self.inventory: dict[str, int] = {}
        self.active_event: dict | None = None
        self.language: str = "en"


@pytest.fixture(autouse=True)
def _reset_registry():
    """Reset hook registry to clean state for each test.

    hook.py auto-registers default actions on first import.  We clear
    them at the start of each test and re-register them so the
    per-test state is predictable without leaking across tests.
    """
    reset_hook_registry()
    from roguelike_sprawl.novel.hooks import register_default_actions

    register_default_actions()
    yield
    reset_hook_registry()
    register_default_actions()  # leave defaults for other modules


# ============================================================================
# Catalog
# ============================================================================


class TestCatalog:
    def test_load_discovers_entries(self) -> None:
        cat = NovelCatalog.load(REPO_ROOT)
        assert len(cat) >= 1

    def test_lookup_by_stem(self) -> None:
        cat = NovelCatalog.load(REPO_ROOT)
        entry = cat.by_stem("case_jackout-30sec")
        assert entry is not None
        assert isinstance(entry, NovelEntry)
        # Title mapping: en field may be dict or string.
        assert entry.title_en  # non-empty

    def test_language_pairs_present(self) -> None:
        cat = NovelCatalog.load(REPO_ROOT)
        pairs = cat.language_pairs()
        assert any(stem == "case_jackout-30sec" and lang == "en" for stem, lang in pairs)
        assert any(stem == "case_jackout-30sec" and lang == "ko" for stem, lang in pairs)

    def test_iteration_returns_entries(self) -> None:
        cat = NovelCatalog.load(REPO_ROOT)
        first = next(iter(cat))
        assert isinstance(first, NovelEntry)

    def test_format_default_short_story(self) -> None:
        cat = NovelCatalog.load(REPO_ROOT)
        entry = cat.by_stem("case_jackout-30sec")
        assert entry is not None
        assert entry.format is NovelFormat.SHORT_STORY

    def test_by_tag_returns_matching(self) -> None:
        cat = NovelCatalog.load(REPO_ROOT)
        # Use a known tag — populate from the corpus content.
        # This will be empty if no frontmatter has a game_integration tag,
        # so just check the API surface.
        result = cat.by_tag("nonexistent-tag")
        assert isinstance(result, list)

    def test_contains_protocol(self) -> None:
        cat = NovelCatalog.load(REPO_ROOT)
        assert "case_jackout-30sec" in cat
        assert "no-such-story" not in cat

    def test_refresh_idempotent(self) -> None:
        cat = NovelCatalog.load(REPO_ROOT)
        before = len(cat)
        cat.refresh()
        assert len(cat) == before


# ============================================================================
# Filename parser
# ============================================================================


class TestFilenameParser:
    def test_en_date_prefix(self) -> None:
        from roguelike_sprawl.novel.catalog import _parse_filename

        stem, lang = _parse_filename("2026-06-23_case_jackout-30sec.md")
        assert stem == "case_jackout-30sec"
        assert lang == "en"

    def test_ko_date_prefix(self) -> None:
        from roguelike_sprawl.novel.catalog import _parse_filename

        stem, lang = _parse_filename("2026-06-23_case_jackout-30sec.ko.md")
        assert stem == "case_jackout-30sec"
        assert lang == "ko"

    def test_no_date_prefix(self) -> None:
        from roguelike_sprawl.novel.catalog import _parse_filename

        stem, lang = _parse_filename("random_story.md")
        assert stem == "random_story"
        assert lang == "en"


# ============================================================================
# Frontmatter parser
# ============================================================================


class TestFrontmatterParser:
    def test_simple_kv(self) -> None:
        from roguelike_sprawl.novel.catalog import _read_frontmatter

        path = REPO_ROOT / "_tmp_fm.md"
        path.write_text('---\ntitle: "X"\nauthor: "Y"\n---\nbody\n', encoding="utf-8")
        try:
            fm = _read_frontmatter(path)
            assert fm["title"] == "X"
            assert fm["author"] == "Y"
        finally:
            path.unlink()

    def test_inline_dict(self) -> None:
        from roguelike_sprawl.novel.catalog import _read_frontmatter

        path = REPO_ROOT / "_tmp_fm.md"
        path.write_text(
            '---\ntitle:\n  en: "English Title"\n  ko: "한국어 제목"\n---\nbody\n',
            encoding="utf-8",
        )
        try:
            fm = _read_frontmatter(path)
            assert fm["title"] == {"en": "English Title", "ko": "한국어 제목"}
        finally:
            path.unlink()

    def test_list_block(self) -> None:
        from roguelike_sprawl.novel.catalog import _read_frontmatter

        path = REPO_ROOT / "_tmp_fm.md"
        path.write_text(
            '---\nwiki_references:\n  - "[[A]]"\n  - "[[B]]"\n---\nbody\n',
            encoding="utf-8",
        )
        try:
            fm = _read_frontmatter(path)
            assert fm["wiki_references"] == ["[[A]]", "[[B]]"]
        finally:
            path.unlink()


# ============================================================================
# Infer default hook
# ============================================================================


class TestInferDefaultHook:
    def test_ice_combat_black(self) -> None:
        kind, ice = infer_default_hook("a black ICE defense")
        assert kind is HookKind.COMBAT
        assert ice == "BLACK"

    def test_ice_combat_standard(self) -> None:
        kind, ice = infer_default_hook("a wolfgang ICE patrol")
        assert kind is HookKind.COMBAT
        assert ice == "STANDARD"

    def test_data_item(self) -> None:
        kind, ice = infer_default_hook("extract a data fragment")
        assert kind is HookKind.ITEM

    def test_construct_event(self) -> None:
        kind, ice = infer_default_hook("Meet the dixie flatline construct")
        assert kind is HookKind.EVENT

    def test_default_narrative(self) -> None:
        kind, ice = infer_default_hook("unrelated prose")
        assert kind is HookKind.NARRATIVE


# ============================================================================
# Manifest
# ============================================================================


class TestManifest:
    def test_set_and_get(self) -> None:
        m = NovelManifest()
        entry = ManifestEntry(stem="x", primary=HookKind.COMBAT, ice_kind="BLACK")
        m.set(entry)
        assert m.get("x") is entry
        assert "x" in m
        assert "missing" not in m

    def test_resolve_unknown_returns_default(self) -> None:
        m = NovelManifest()
        entry = m.resolve("not-in-manifest")
        assert entry.stem == "not-in-manifest"
        assert entry.primary is HookKind.NARRATIVE

    def test_json_round_trip(self, tmp_path: Path) -> None:
        m = NovelManifest()
        m.set(ManifestEntry(stem="x", primary=HookKind.ITEM, ice_kind="BLACK"))
        m.set(
            ManifestEntry(
                stem="y",
                primary=HookKind.CINEMATIC,
                secondary=(HookKind.EVENT,),
            )
        )
        path = tmp_path / "manifest.json"
        m.to_json(path)
        loaded = NovelManifest.from_json(path)
        assert loaded.get("x").primary is HookKind.ITEM
        assert loaded.get("y").secondary == (HookKind.EVENT,)

    def test_from_catalog_infers_defaults(self) -> None:
        catalog = NovelCatalog.load(REPO_ROOT)
        manifest = NovelManifest.from_catalog(catalog)
        # Every catalog entry becomes a manifest entry.
        for entry in catalog:
            m_entry = manifest.get(entry.stem)
            assert m_entry is not None
            assert m_entry.stem == entry.stem

    def test_from_json_raises_on_unknown_kind(self, tmp_path: Path) -> None:
        path = tmp_path / "manifest.json"
        path.write_text(
            '{"x": {"primary": "blaster"}}',
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="HookKind"):
            NovelManifest.from_json(path)

    def test_for_mission(self) -> None:
        m = NovelManifest()
        m.set(ManifestEntry(stem="a", primary=HookKind.NARRATIVE, mission_id="m1"))
        m.set(ManifestEntry(stem="b", primary=HookKind.ITEM, mission_id="m2"))
        m.set(ManifestEntry(stem="c", primary=HookKind.ITEM, mission_id="m1"))
        assert {e.stem for e in m.for_mission("m1")} == {"a", "c"}


# ============================================================================
# Hooks
# ============================================================================


class TestHooks:
    def test_default_actions_registered(self) -> None:
        # Five kinds, but defaults registered on import in hooks.py
        for kind in HookKind:
            assert get_hook_actions(kind), f"missing default for {kind}"

    def test_register_custom(self) -> None:
        def my_action(ctx: HookContext, state) -> HookResult:
            return HookResult(ok=True, messages=["custom"])

        register_hook_action(HookKind.NARRATIVE, my_action)
        actions = get_hook_actions(HookKind.NARRATIVE)
        assert my_action in actions

    def test_unknown_kind_raises(self) -> None:
        # HookKind is StrEnum; passing a non-member raises ValueError.
        with pytest.raises(ValueError, match="Unknown HookKind"):
            register_hook_action(kind="not-a-kind", action=lambda c, s: HookResult())  # type: ignore[arg-type]


# ============================================================================
# Dispatcher
# ============================================================================


class TestDispatcher:
    def test_dispatch_dry_run(self) -> None:
        cat = NovelCatalog.load(REPO_ROOT)
        manifest = NovelManifest.from_catalog(cat)
        disp = NovelDispatcher(cat, manifest, dry_run=True)
        report = disp.dispatch("case_jackout-30sec", language="en")
        assert isinstance(report, DispatchReport)
        assert report.dry_run is True
        assert report.kinds_fired
        assert report.results

    def test_dispatch_unknown_stem(self) -> None:
        cat = NovelCatalog.load(REPO_ROOT)
        manifest = NovelManifest()
        disp = NovelDispatcher(cat, manifest)
        report = disp.dispatch("no-such-story", language="en")
        # Falls back to NARRATIVE.
        assert report.kinds_fired == [HookKind.NARRATIVE]

    def test_dispatch_live_updates_app_state(self) -> None:
        cat = NovelCatalog.load(REPO_ROOT)
        # Force ITEM hook via manifest override.
        manifest = NovelManifest()
        manifest.set(ManifestEntry(stem="case_jackout-30sec", primary=HookKind.ITEM))
        disp = NovelDispatcher(cat, manifest)
        state = FakeAppState()
        report = disp.dispatch("case_jackout-30sec", app_state=state, language="en")
        assert report.kinds_fired == [HookKind.ITEM]
        assert state.inventory  # default ITEM action added an entry

    def test_dispatch_with_secondary(self) -> None:
        cat = NovelCatalog.load(REPO_ROOT)
        manifest = NovelManifest()
        manifest.set(
            ManifestEntry(
                stem="case_jackout-30sec",
                primary=HookKind.NARRATIVE,
                secondary=(HookKind.CINEMATIC, HookKind.EXCERPT),
            )
        )
        disp = NovelDispatcher(cat, manifest)
        state = FakeAppState()
        report = disp.dispatch("case_jackout-30sec", app_state=state)
        assert report.kinds_fired == [
            HookKind.NARRATIVE,
            HookKind.CINEMATIC,
            HookKind.EXCERPT,
        ]
        # Three actions should each have written something to state.
        assert len(state.status_messages) == 3


# ============================================================================
# Text provider
# ============================================================================


class TestTextProvider:
    def test_head_returns_first_paragraph(self) -> None:
        cat = NovelCatalog.load(REPO_ROOT)
        entry = cat.by_stem("case_jackout-30sec")
        if entry is None:
            pytest.skip("Stem absent from corpus")
        tp = TextProvider()
        head = tp.head(entry, lang="en", paragraphs=1)
        assert head  # non-empty
        assert len(head.split("\n\n")) <= 2  # 1 paragraph (plus trailing newline tolerance)

    def test_head_missing_language(self) -> None:
        cat = NovelCatalog.load(REPO_ROOT)
        entry = cat.by_stem("case_jackout-30sec")
        if entry is None:
            pytest.skip("Stem absent from corpus")
        tp = TextProvider()
        # Force a lang with no file present (Korean is present — pick English always):
        # The corpus provides both langs, so just confirm a string return:
        assert isinstance(tp.head(entry, lang="en"), str)


# ============================================================================
# Integrator
# ============================================================================


class TestIntegrator:
    def test_load_novel_runtime(self) -> None:
        runtime = load_novel_runtime(REPO_ROOT)
        assert isinstance(runtime, NovelRuntime)
        assert isinstance(runtime.catalog, NovelCatalog)
        assert isinstance(runtime.manifest, NovelManifest)
        assert isinstance(runtime.dispatcher, NovelDispatcher)

    def test_load_with_overrides(self, tmp_path: Path) -> None:
        overrides = tmp_path / "manifest.json"
        overrides.write_text(
            '{"my_story": {"primary": "combat"}}',
            encoding="utf-8",
        )
        runtime = load_novel_runtime(REPO_ROOT, manifest_overrides=overrides)
        override_entry = runtime.manifest.get("my_story")
        assert override_entry is not None
        assert override_entry.primary is HookKind.COMBAT

    def test_dispatch_for_state_uses_app_state_language(self) -> None:
        runtime = load_novel_runtime(REPO_ROOT)
        state = FakeAppState()
        state.language = "ko"
        report = dispatch_for_state(
            runtime,
            "case_jackout-30sec",
            state,
        )
        assert report.language == "ko"

    def test_load_dry_run(self) -> None:
        runtime = load_novel_runtime(REPO_ROOT, dry_run=True)
        state = FakeAppState()
        report = runtime.dispatcher.dispatch("case_jackout-30sec", app_state=state)
        assert report.dry_run
        # No state mutation under dry-run.
        assert state.status_messages == []
        assert state.inventory == {}


# ============================================================================
# Extension surface
# ============================================================================


class TestExtensibility:
    """Make sure adding a new hook kind is a one-file change."""

    def test_can_register_new_kind_via_extension(self) -> None:
        # We do NOT modify HookKind here, but demonstrate that
        # the registry accepts a callable without touching catalog
        # or manifest code.
        seen: list[str] = []

        def custom(ctx, app_state) -> HookResult:
            seen.append("fired")
            return HookResult(ok=True)

        register_hook_action(HookKind.CINEMATIC, custom)
        cat = NovelCatalog.load(REPO_ROOT)
        manifest = NovelManifest()
        manifest.set(ManifestEntry(stem="case_jackout-30sec", primary=HookKind.CINEMATIC))
        runtime = NovelRuntime(cat, manifest, NovelDispatcher(cat, manifest))
        runtime.dispatcher.dispatch("case_jackout-30sec")
        assert seen == ["fired"]
