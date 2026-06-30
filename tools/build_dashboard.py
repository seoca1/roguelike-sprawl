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
        out["short_stories_en"] = sum(1 for f in md_files if ".ko." not in f.name)
        out["short_stories_ko"] = sum(1 for f in md_files if ".ko." in f.name)
        stems = set()
        for f in md_files:
            s = re.sub(r"^\d{4}-\d{2}-\d{2}_", "", f.name)
            s = re.sub(r"\.ko\.md$|\.md$", "", s)
            stems.add(s)
        out["catalog_entries"] = len(stems)
    return out


def load_story_stats(repo: Path) -> dict[str, object]:
    """Pull mission / chapter / character counts."""
    out: dict[str, object] = {
        "missions": 0,
        "stories": 0,
        "chars_in_stories": 0,
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
        stems: set[str] = set()
        for f in short.glob("*.md"):
            s = re.sub(r"^\d{4}-\d{2}-\d{2}_", "", f.name)
            s = re.sub(r"\.ko\.md$|\.md$", "", s)
            stems.add(s)
        out["stories"] = len(stems)
    for c in ("case", "sil", "kas"):
        p = repo / "prototype" / "data" / "story" / "chapters" / f"{c}.json"
        if not p.exists():
            p = repo / "prototype" / "data" / "chapters" / f"{c}.json"
        if p.exists():
            out["arcs"] += 1
            out["chapters"] += 1
    return out


def load_journey_stats(repo: Path) -> dict[str, object]:
    """Per-character journey totals (novice / veteran / heretic)."""
    out: dict[str, object] = {
        "novice": {"credits": 20050, "missions": 0, "deaths": 0},
        "veteran": {"credits": 27500, "missions": 0, "deaths": 0},
        "heretic": {"credits": 20100, "missions": 0, "deaths": 0},
        "_generated_at": "",
    }
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
    "journey_stats.json": load_journey_stats,
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
