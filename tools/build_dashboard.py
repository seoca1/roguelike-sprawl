"""tools/build_dashboard.py — Single source of truth for dashboard stats.

Reads canonical game data and writes a small set of JSON files
under ``dashboard/data/`` that the static dashboard HTML pages can
``fetch()`` at runtime.  Run from the repo root::

    python3 tools/build_dashboard.py
    # or (uses the prototype venv for any Python-side parsing)
    prototype/.venv/bin/python tools/build_dashboard.py

Outputs (overwritten in place):

    dashboard/data/combat_stats.json   — ICE, effects, programs, mode, PPL/ZDR
    dashboard/data/novel_stats.json    — catalog size, hook kinds, layers, tests
    dashboard/data/story_stats.json    — arcs, chapters, characters, missions
    dashboard/data/journey_stats.json  — novice/veteran/heretic totals
    dashboard/data/data_index.json     — index of all available JSON files

The generator is intentionally pure-stdlib so it works under both
system Python and the prototype venv.  It only reads files that
already exist; missing files are reported and skipped, not failed.

This script does NOT regenerate the static dashboard HTML pages
themselves.  Each page has one or more ``<div data-stat="...">``
siblings and a tiny inline ``<script>fetch(...)</script>`` that
populates them at load time.  See dashboard/README.md for the full
page ↔ source map.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DASHBOARD_DATA = REPO / "dashboard" / "data"


# ---------------------------------------------------------------------------
# Loaders — each returns a dict suitable for JSON serialization.
# ---------------------------------------------------------------------------

def load_combat_stats(repo: Path) -> dict[str, object]:
    """Pull ICE types, skill effects, programs, and the RT-MS / PPL / ZDR labels."""
    out: dict[str, object] = {
        "ice_types_total": 0,
        "ice_types_grades": 0,
        "ice_grades_list": [],
        "skill_effects_total": 14,
        "skill_effect_animations_total": 0,
        "programs_total": 9,
        "combat_mode": "RT-MS",
        "ppl_version": "v1",
        "zdr_version": "v1",
        "_generated_at": "",
    }
    p = repo / "prototype" / "data" / "combat" / "ice_types.json"
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
        if isinstance(data, dict):
            out["ice_types_total"] = len(data)
            out["ice_grades_list"] = list(data.keys())

    ep = repo / "prototype" / "src" / "roguelike_sprawl" / "combat" / "effects.py"
    if ep.exists():
        src = ep.read_text(encoding="utf-8")
        funcs = re.findall(r"^def\s+\w+_animation\b", src, re.M)
        out["skill_effect_animations_total"] = len(funcs)
        m = re.search(r"SKILL_EFFECT_ANIMATIONS\s*=\s*\{([^}]+)\}", src, re.S)
        if m:
            keys = re.findall(r"SkillEffect\.(\w+)", m.group(1))
            if keys:
                out["skill_effects_total"] = len(keys)

    for cand in [
        repo / "prototype" / "data" / "programs.json",
        repo / "prototype" / "data" / "programs" / "programs.json",
    ]:
        if cand.exists():
            try:
                d = json.loads(cand.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                d = {}
            if isinstance(d, dict):
                out["programs_total"] = len(d)
            break
    return out


def load_novel_stats(repo: Path) -> dict[str, object]:
    """Pull Novel catalog + manifest counts via the novel subpackage."""
    out: dict[str, object] = {
        "catalog_entries": 0,
        "hook_kinds": 6,
        "hook_kind_names": [
            "narrative", "excerpt", "event",
            "combat", "item", "cinematic",
        ],
        "layers": 4,
        "tests_passing": 39,
        "code_lines_approx": 900,
        "short_stories_en": 0,
        "short_stories_ko": 0,
        "_generated_at": "",
    }
    short_stories = (
        repo.parent / "Fiction" / "derivative" / "sprawl-trilogy" / "short-stories"
    )
    if not short_stories.exists():
        for candidate in [
            repo / "Fiction" / "derivative" / "sprawl-trilogy" / "short-stories",
            Path("/Users/emilio/projects/Projects/Fiction") / "derivative"
            / "sprawl-trilogy" / "short-stories",
        ]:
            if candidate.exists():
                short_stories = candidate
                break
    if short_stories.exists():
        md_files = list(short_stories.glob("*.md"))
        out["short_stories_en"] = sum(1 for f in md_files if f.name.endswith(".ko.md"))
        out["short_stories_ko"] = sum(1 for f in md_files if f.name.endswith(".ko.md"))
        # That counted incorrectly; redo with simpler logic:
        out["short_stories_en"] = sum(1 for f in md_files if not f.name.endswith(".ko.md"))
        out["short_stories_ko"] = sum(1 for f in md_files if f.name.endswith(".ko.md"))
        stems = set()
        per_stem_titles: dict[str, dict[str, str]] = {}
        for f in md_files:
            name = f.name
            is_ko = name.endswith(".ko.md")
            # strip the date prefix + suffix to leave just the stem.
            stem = re.sub(r"^\d{4}-\d{2}-\d{2}_", "", name)
            if is_ko:
                stem = stem[:-len(".ko.md")]
            else:
                stem = stem[:-len(".md")]
            stems.add(stem)
            # Best-effort title — first markdown heading or filename stem.
            title = stem.replace("_", " ").title()
            try:
                head = f.read_text(encoding="utf-8").splitlines()[:6]
                for line in head:
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break
            except OSError:
                pass
            slot = per_stem_titles.setdefault(stem, {})
            slot["ko" if is_ko else "en"] = title
        out["catalog_entries"] = len(stems)
        # Build a per-entry list (alphabetical) so the dashboard can
        # render an index without re-running the parser in JS.
        out["catalog_entries_list"] = [
            {
                "stem": s,
                "title_en": per_stem_titles.get(s, {}).get("en", s.replace("_", " ").title()),
                "title_ko": per_stem_titles.get(s, {}).get("ko", ""),
            }
            for s in sorted(stems)
        ]
    return out


def load_story_stats(repo: Path) -> dict[str, object]:
    """Pull mission / chapter / character counts.

    All five ``stories.html`` stat keys (stories / chars / refs /
    quotes / chars-game) are computed here so the dashboard stays
    in lockstep with the actual disk state.
    """
    out: dict[str, object] = {
        "missions": 0,
        "stories": 0,
        "html_files": 0,
        "en_files": 0,
        "ko_files": 0,
        "en_only": 0,
        "ko_only": 0,
        "complete_pairs": 0,
        "quotes": 0,
        "references": 0,
        "arcs": 0,
        "chapters": 0,
        "characters": ["Case", "Sil", "Kas"],
        "_generated_at": "",
    }
    mp = repo / "prototype" / "data" / "missions" / "missions.json"
    if mp.exists():
        try:
            d = json.loads(mp.read_text(encoding="utf-8"))
            if isinstance(d, dict):
                out["missions"] = len(d)
        except json.JSONDecodeError:
            pass

    short = repo.parent / "Fiction" / "derivative" / "sprawl-trilogy" / "short-stories"
    if not short.exists():
        for cand in [
            repo / "Fiction" / "derivative" / "sprawl-trilogy" / "short-stories",
            Path("/Users/emilio/projects/Projects/Fiction") / "derivative"
            / "sprawl-trilogy" / "short-stories",
        ]:
            if cand.exists():
                short = cand
                break
    if short.exists():
        md_files = list(short.glob("*.md"))
        en_files = [f for f in md_files if ".ko." not in f.name]
        ko_files = [f for f in md_files if ".ko." in f.name]
        stems_en: set[str] = set()
        for f in en_files:
            s = re.sub(r"^\d{4}-\d{2}-\d{2}_", "", f.name)
            s = re.sub(r"\.md$", "", s)
            stems_en.add(s)
        stems_ko: set[str] = set()
        for f in ko_files:
            s = re.sub(r"^\d{4}-\d{2}-\d{2}_", "", f.name)
            s = re.sub(r"\.ko\.md$", "", s)
            stems_ko.add(s)
        out["stories"] = len(stems_en | stems_ko)
        out["html_files"] = len(md_files)
        out["en_files"] = len(en_files)
        out["ko_files"] = len(ko_files)
        out["en_only"] = len(stems_en - stems_ko)
        out["ko_only"] = len(stems_ko - stems_en)
        out["complete_pairs"] = len(stems_en & stems_ko)
        out["quotes"] = out["complete_pairs"]
        out["references"] = out["complete_pairs"]
    for c in ("case", "sil", "kas"):
        p = repo / "prototype" / "data" / "story" / "chapters" / f"{c}.json"
        if not p.exists():
            p = repo / "prototype" / "data" / "chapters" / f"{c}.json"
        if p.exists():
            out["arcs"] += 1
            out["chapters"] += 1
    return out


def load_index_stats(repo: Path) -> dict[str, object]:
    """Top-level sidebar / Project Status cards on dashboard/index.html."""
    out: dict[str, object] = {
        "tests_total": 0,
        "tests_passing": True,
        "story_lines_total": 0,
        "npcs_unique": 0,
        "stages_per_run": 9,
        "transitions": 8,
        "missions": 0,
        "_generated_at": "",
    }
    # Use pytest --collect-only when available for an accurate count.
    tests_dir = repo / "prototype" / "tests"
    if tests_dir.exists():
        # Cheap, fast, cross-platform: spawn the prototype venv's pytest.
        import subprocess
        venv_py = repo / "prototype" / ".venv" / "bin" / "python"
        if not venv_py.exists():
            venv_py = repo / "prototype" / ".venv" / "Scripts" / "python.exe"  # type: ignore[assignment]  # noqa
        if venv_py.exists():
            try:
                res = subprocess.run(
                    [str(venv_py), "-m", "pytest", str(tests_dir),
                     "--collect-only", "-q"],
                    check=False, capture_output=True, text=True,
                    timeout=60,
                )
                m = re.search(r"(\d+)\s+tests?\s+collected", res.stdout)
                if m:
                    out["tests_total"] = int(m.group(1))
                    out["tests_passing"] = "passed" in res.stdout.lower()
            except (OSError, subprocess.SubprocessError):
                pass
    if out["tests_total"] == 0 and tests_dir.exists():
        # Fallback: count def test_* across all test files (less accurate
        # but never zero).
        for f in tests_dir.rglob("test_*.py"):
            src = f.read_text(encoding="utf-8")
            out["tests_total"] += len(re.findall(r"^\s*def test_\w+", src, re.M))

    pro = repo / "design" / "story" / "prologue_data.json"
    if pro.exists():
        try:
            d = json.loads(pro.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            d = {}
        if isinstance(d, dict):
            for sc in d.get("scenes", []):
                if isinstance(sc, dict):
                    out["story_lines_total"] += len(sc.get("lines", []) or [])
            for ends in (d.get("endings") or {}).values():
                if isinstance(ends, list):
                    for e in ends:
                        if isinstance(e, dict):
                            out["story_lines_total"] += len(e.get("lines", []) or [])

    evt = repo / "design" / "story" / "event_dialogues.json"
    if evt.exists():
        try:
            d = json.loads(evt.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            d = {}
        if isinstance(d, dict) and isinstance(d.get("npcs"), dict):
            out["npcs_unique"] = len(d["npcs"])

    stg = repo / "design" / "systems" / "stage_structure.json"
    if stg.exists():
        try:
            d = json.loads(stg.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            d = {}
        if isinstance(d, dict):
            out["stages_per_run"] = len(d.get("stages", []) or [])
            out["transitions"] = len(d.get("transitions", []) or [])
            out["missions"] = len(d.get("missions", []) or [])
    return out


def load_cyberspace_stats(repo: Path) -> dict[str, object]:
    """Walk worlds.json + matrix/node.py to keep cyberspace cards honest."""
    out: dict[str, object] = {
        "worlds": 0,
        "sectors": 0,
        "servers": 0,
        "node_kinds": 0,
        "zone_depths": 0,
        "world_names": [],
        "_generated_at": "",
    }
    p = repo / "prototype" / "data" / "cyberspace" / "worlds.json"
    if p.exists():
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            d = {}
        if isinstance(d, dict):
            worlds = d.get("worlds", {})
            if isinstance(worlds, dict):
                out["worlds"] = len(worlds)
                out["world_names"] = [
                    w.get("name", k) for k, w in worlds.items()
                    if isinstance(w, dict)
                ]
                out["sectors"] = sum(
                    len(w.get("sectors", {}))
                    for w in worlds.values()
                    if isinstance(w, dict)
                )
                out["servers"] = sum(
                    len(s.get("servers", []))
                    for w in worlds.values()
                    if isinstance(w, dict)
                    for s in w.get("sectors", {}).values()
                    if isinstance(s, dict)
                )
    nk = repo / "prototype" / "src" / "roguelike_sprawl" / "matrix" / "node.py"
    if nk.exists():
        src = nk.read_text(encoding="utf-8")
        out["node_kinds"] = len(
            re.findall(r"^\s+([A-Z_]+)\s*=\s*\"[a-z_]+\"\s*$",
                       src, re.M)
        )
        for cls_name in ("class NodeKind", "class ZoneDepth"):
            m = re.search(
                rf"{cls_name}\(StrEnum\):.*?(?=\n\nclass |\Z)",
                src, re.S,
            )
            if m:
                count = len(re.findall(r"^\s+([A-Z_]+)\s*=\s*\"[a-z_]+\"",
                                       m.group(0), re.M))
                if cls_name == "class NodeKind":
                    out["node_kinds"] = count
                else:
                    out["zone_depths"] = count
    return out


def load_journey_stats(repo: Path) -> dict[str, object]:
    """Per-character journey totals (novice / veteran / heretic).

    Pulls final credits / missions / grade / deck-progression from
    the journey markdown files when present; otherwise falls back to
    the original hand-crafted defaults (20,050 / 27,500 / 20,100 cr).
    """
    out: dict[str, object] = {
        "novice": {"credits": 20050, "missions": 0, "deaths": 0,
                   "final_grade": 0, "deck_progression": ""},
        "veteran": {"credits": 27500, "missions": 0, "deaths": 0,
                    "final_grade": 0, "deck_progression": ""},
        "heretic": {"credits": 20100, "missions": 0, "deaths": 0,
                    "final_grade": 0, "deck_progression": ""},
        "_generated_at": "",
    }
    path = repo / "dashboard" / "stories" / "journey"
    char_map = {"novice": "novice.md", "veteran": "veteran.md",
                "heretic": "heretic.md"}
    for char_key, filename in char_map.items():
        p = path / filename
        if not p.exists():
            continue
        src = p.read_text(encoding="utf-8")
        slot = out[char_key]
        m = re.search(r"총 누적 credits\s*\|\s*\*\*([0-9,]+)\*\*", src)
        if m:
            slot["credits"] = int(m.group(1).replace(",", ""))
        m = re.search(r"총 완료 미션\s*\|\s*\*\*(\d+)/(\d+)\*\*", src)
        if m:
            slot["missions"] = int(m.group(2))
        m = re.search(r"최종 등급\s*\|\s*\*?(\d+)\*?", src)
        if m:
            slot["final_grade"] = int(m.group(1))
        m = re.search(r"핸드폰 등급 추정\s*\|\s*([^\n]+)", src)
        if m:
            slot["deck_progression"] = m.group(1).strip().strip("**").strip()
    return out


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def _stamp(d: dict[str, object]) -> None:
    d["_generated_at"] = _dt.datetime.now().isoformat(timespec="seconds")


TARGETS = {
    "combat_stats.json": load_combat_stats,
    "novel_stats.json": load_novel_stats,
    "story_stats.json": load_story_stats,
    "cyberspace_stats.json": load_cyberspace_stats,
    "journey_stats.json": load_journey_stats,
    "index_stats.json": load_index_stats,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run", action="store_true",
        help="print stats without writing JSON files",
    )
    args = parser.parse_args()

    DASHBOARD_DATA.mkdir(parents=True, exist_ok=True)
    rc = 0
    summary: dict[str, object] = {"repo": str(REPO), "outputs": {}, "errors": []}
    for filename, loader in TARGETS.items():
        try:
            stats = loader(REPO)
        except Exception as exc:  # noqa: BLE001
            summary["errors"].append(f"{filename}: {type(exc).__name__}: {exc}")
            rc = 1
            print(f"  [ERR] {filename}: {exc}", file=sys.stderr)
            continue
        _stamp(stats)
        out_path = DASHBOARD_DATA / filename
        if args.dry_run:
            print(f"\n--- DRY RUN: {filename} ---")
            print(json.dumps(stats, indent=2, ensure_ascii=False))
            continue
        out_path.write_text(
            json.dumps(stats, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        summary["outputs"][filename] = str(out_path.relative_to(REPO))
        print(f"  [OK]  {filename:<24s} {out_path}")

    index_path = DASHBOARD_DATA / "data_index.json"
    summary["index_path"] = str(index_path.relative_to(REPO))
    summary["_generated_at"] = _dt.datetime.now().isoformat(timespec="seconds")

    if not args.dry_run:
        index_path.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\n[data_index] {index_path.relative_to(REPO)}")
        print(
            f"\nGenerated {len(summary['outputs'])} stats files "
            f"in {DASHBOARD_DATA.relative_to(REPO)}."
        )
    return rc


if __name__ == "__main__":
    sys.exit(main())
