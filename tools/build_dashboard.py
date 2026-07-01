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
    """Pull mission / chapter / character / event / reaction counts.

    Wires metadata → novel → story events → stages into the
    dashboard so the HTML stat-pills stay in lockstep with the
    actual disk state.

    Stat keys (each consumed by ``dashboard/story.html``):
      - missions: int — total missions in missions.json
      - stories / html_files / en_files / ko_files / complete_pairs:
        short-stories catalogue
      - arcs / chapters: character arc JSONs
      - characters: list[str] — main jockeys
      - aftermath_events: int — Phase 6+ content (12)
      - reactions: int — NPC reactions (25)
      - reaction_characters: list[str] — characters with reactions (6)
      - event_triggers: list[str] — all EventTrigger enum values (9)
      - total_rewards: int — total StoryReward items across events
      - hub_visit_events: int — events with hub_visited trigger
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
        "characters": ["Case", "Sil", "Kas", "Armitage"],
        "aftermath_events": 0,
        "reactions": 0,
        "reaction_characters": [],
        "event_triggers": [],
        "total_rewards": 0,
        "hub_visit_events": 0,
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

    # Phase 6+: aftermath events, reactions, rewards.
    ap = repo / "prototype" / "data" / "story" / "aftermath.json"
    if ap.exists():
        try:
            am = json.loads(ap.read_text(encoding="utf-8"))
            if isinstance(am, dict):
                out["aftermath_events"] = len(am)
                out["total_rewards"] = sum(
                    len(v.get("rewards", []))
                    for v in am.values()
                    if isinstance(v, dict)
                )
                out["hub_visit_events"] = sum(
                    1
                    for v in am.values()
                    if isinstance(v, dict) and v.get("trigger") == "hub_visited"
                )
        except json.JSONDecodeError:
            pass

    rp = repo / "prototype" / "data" / "story" / "reactions.json"
    if rp.exists():
        try:
            rj = json.loads(rp.read_text(encoding="utf-8"))
            if isinstance(rj, dict):
                out["reactions"] = len(rj)
                out["reaction_characters"] = sorted(
                    {
                        v.get("character", "")
                        for v in rj.values()
                        if isinstance(v, dict) and v.get("character")
                    }
                )
        except json.JSONDecodeError:
            pass

    # Discover all EventTrigger values from the enum source.
    out["event_triggers"] = _collect_event_trigger_names(repo)

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
    for c in ("case", "sil", "kas", "suit"):
        p = repo / "prototype" / "data" / "story" / "chapters" / f"{c}.json"
        if not p.exists():
            p = repo / "prototype" / "data" / "chapters" / f"{c}.json"
        if p.exists():
            out["arcs"] += 1
            out["chapters"] += 1
    return out


def _collect_event_trigger_names(repo: Path) -> list[str]:
    """Extract all EventTrigger enum values from the event_story module.

    Reads the source file rather than importing (avoids the entire
    game's import chain during this build step). Falls back to a
    hard-coded list if the source can't be found / parsed.
    """
    import re as _re

    fallback = [
        "npc_choice",
        "npc_greeting",
        "combat_end",
        "node_enter",
        "story_milestone",
        "chapter_complete",
        "vendor_unlocked",
        "hub_visited",
        "dialogue_completed",
    ]
    src = repo / "prototype" / "src" / "roguelike_sprawl" / "engine" / "event_story.py"
    if not src.exists():
        return fallback
    try:
        text = src.read_text(encoding="utf-8")
    except OSError:
        return fallback
    # Match the EventTrigger class body and pull `NAME = "value"` lines.
    class_re = _re.compile(
        r"^class\s+EventTrigger\b.*?:\s*$(.*?)(?=^class\s|\Z)",
        _re.MULTILINE | _re.DOTALL,
    )
    member_re = _re.compile(
        r"^\s{4}(\w+)\s*=\s*['\"]([^'\"]+)['\"]", _re.MULTILINE
    )
    match = class_re.search(text)
    if not match:
        return fallback
    return [v for _, v in member_re.findall(match.group(1))] or fallback


def load_event_dialogues_stats(repo: Path) -> dict[str, object]:
    """Count NPCs / dialogues / lines / choices in event_dialogues.json.

    Drives the event-viewer stat pills in ``dashboard/story.html``.
    """
    out: dict[str, object] = {
        "npcs": 0,
        "dialogues": 0,
        "lines": 0,
        "choices": 0,
        "characters": [],
        "_generated_at": "",
    }
    p = repo / "design" / "story" / "event_dialogues.json"
    if not p.exists():
        return out
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return out
    if not isinstance(data, dict):
        return out

    npcs = data.get("npcs", {})
    if isinstance(npcs, dict):
        out["npcs"] = len(npcs)
        out["characters"] = sorted(npcs.keys())

    dialogues = data.get("dialogues", {})
    if isinstance(dialogues, dict):
        out["dialogues"] = len(dialogues)
        for d in dialogues.values():
            if not isinstance(d, dict):
                continue
            out["lines"] += len(d.get("lines", []) or [])
            out["choices"] += sum(
                len(line.get("choices", []) or [])
                for line in (d.get("lines", []) or [])
                if isinstance(line, dict)
            )
    elif isinstance(dialogues, list):
        # Legacy: dialogues as list of dicts.
        out["dialogues"] = len(dialogues)
        for d in dialogues:
            if not isinstance(d, dict):
                continue
            out["lines"] += len(d.get("lines", []) or [])
            out["choices"] += sum(
                len(line.get("choices", []) or [])
                for line in (d.get("lines", []) or [])
                if isinstance(line, dict)
            )
    return out


def load_stages_stats(repo: Path) -> dict[str, object]:
    """Count stages / transitions / chapter-states from the run module.

    Mirrors ``dashboard/stages.html`` so the dashboard always reflects
    the real state of the run state machine.
    """
    out: dict[str, object] = {
        "stages": 0,
        "stage_enum": 0,
        "transitions": 0,
        "missions": 0,
        "chapter_states": 0,
        "objectives": 0,
        "_generated_at": "",
    }

    # Stage enum count
    src = repo / "prototype" / "src" / "roguelike_sprawl" / "run" / "state.py"
    if src.exists():
        try:
            text = src.read_text(encoding="utf-8")
        except OSError:
            text = ""
        # Use a regex-based parser that's robust to comments and
        # arbitrary whitespace.
        import re as _re

        pattern = _re.compile(
            r"^class\s+(\w+).*?:\s*$(.*?)(?=^class\s|\Z)",
            _re.MULTILINE | _re.DOTALL,
        )
        member_re = _re.compile(
            r"^\s{4}(\w+)\s*=\s*['\"]([^'\"]+)['\"]", _re.MULTILINE
        )

        for match in pattern.finditer(text):
            class_name = match.group(1)
            body = match.group(2)
            members = member_re.findall(body)
            if class_name == "Stage":
                out["stages"] = len(members)
                out["stage_enum"] = len(members)
            elif class_name == "ChapterState":
                out["chapter_states"] = len(members)
            elif class_name == "ObjectiveKind":
                out["objectives"] = len(members)

    # Transitions: count `STAGE_TRANSITIONS` literal (fallback: derive
    # from Stage-flow JSON if it exists).
    missions_p = repo / "prototype" / "data" / "missions" / "missions.json"
    if missions_p.exists():
        try:
            d = json.loads(missions_p.read_text(encoding="utf-8"))
            if isinstance(d, dict):
                out["missions"] = len(d)
        except json.JSONDecodeError:
            pass
    out["transitions"] = out["stages"]  # rough 1:1 estimate

    return out


def load_run_stats(repo: Path) -> dict[str, object]:
    """Walk prototype/src/run/state.py for Stage / ChapterState / Phase enums.

    The Stage enum lists every in-game stage (10 entries: PENDING /
    MEET_NPC / EXTRACT_DATA / DEFEAT_ICE / JACK_OUT / REWARD /
    DEBRIEF / COMPLETE / DEATH_RESTART / FAILED), of which
    stage_structure.json only enumerates 9 (DEBRIEF is marked
    optional in the source).  Pulling the enum straight from
    state.py keeps the dashboard honest when the implementation
    grows new phases.
    """
    out: dict[str, object] = {
        "stage_enum_count": 0,
        "stage_enum_names": [],
        "stage_optional": [],
        "chapter_state_enum_count": 0,
        "chapter_state_enum_names": [],
        "objective_kind_enum_count": 0,
        "objective_kind_enum_names": [],
        "source": "",
        "_generated_at": "",
    }
    p = repo / "prototype" / "src" / "roguelike_sprawl" / "run" / "state.py"
    if not p.exists():
        return out
    out["source"] = str(p.relative_to(repo))
    src = p.read_text(encoding="utf-8")

    def _enum_block(name: str) -> list[str]:
        m = re.search(
            rf"^class\s+{name}\s*\(\s*StrEnum\s*\):.*?(?=^\nclass\s+\w+|\Z)",
            src, re.M | re.S,
        )
        if not m:
            return []
        block = m.group(0)
        return re.findall(r"^\s+([A-Z][A-Z0-9_]*)\s*=\s*\"[a-z0-9_]+\"",
                           block, re.M)

    out["stage_enum_names"] = _enum_block("Stage")
    out["stage_enum_count"] = len(out["stage_enum_names"])  # type: ignore[assignment]
    # Per docstring: DEBRIEF is optional.  Mark any literal that the
    # docstring says is optional / conditional.
    optional = []
    for name in out["stage_enum_names"]:  # type: ignore[union-attr]
        # Match 'Foo (optional)' or '(debatable)' / '(conditional)'.
        m = re.search(
            rf"^\s+{name}\s*=\s*\"[a-z_]+\"\s*#\s*(optional|conditional|debatable)",
            src, re.M,
        )
        if m:
            optional.append(name)
    out["stage_optional"] = optional

    out["chapter_state_enum_names"] = _enum_block("ChapterState")
    out["chapter_state_enum_count"] = (
        len(out["chapter_state_enum_names"])  # type: ignore[assignment]
    )
    out["objective_kind_enum_names"] = _enum_block("ObjectiveKind")
    out["objective_kind_enum_count"] = (
        len(out["objective_kind_enum_names"])  # type: ignore[assignment]
    )
    return out


def load_character_stats(repo: Path) -> dict[str, object]:
    """Pull canonical character data from design/story/characters.md.

    Source markdown uses a table format::

        ## 1. 케이 (Case) — Novice / 초짜
        | **나이** | 22 |
        | **데크** | Ono-Sendai Cyberspace 7 (T1) |
        ...

    We regex the section heading + every subsequent '| **<key>** | <val> |'
    row until the next '## ' / end-of-file.  Falls back to the
    original case.md / sil.md / kas.md if those exist.
    """
    out: dict[str, object] = {
        "characters": [],
        "source": "",
        "_generated_at": "",
    }
    md_path = repo / "design" / "story" / "characters.md"
    if not md_path.exists():
        return out
    out["source"] = str(md_path.relative_to(repo))
    text = md_path.read_text(encoding="utf-8")
    # Split on '## N. <name> ...' headings; each becomes a character
    # entry if the section header contains 'Novice' / 'Veteran' / 'Heretic'.
    section_re = re.compile(
        r"^##\s+\d+\.\s+([^\n]+?)\s*\(([^)]+)\)\s*[—-]\s*(Novice|Veteran|Heretic)",
        re.M,
    )
    matches = list(section_re.finditer(text))
    arc_to_key = {"Novice": "novice", "Veteran": "veteran", "Heretic": "heretic"}
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end]
        entry: dict[str, object] = {
            "name_ko": m.group(1).strip(),
            "name_en": m.group(2).strip(),
            "arc": arc_to_key[m.group(3)],
            "arc_label": m.group(3),
            "attributes": {},
        }
        # Pull known attributes via '| **<key>** | <val> |' rows.
        for line in body.splitlines():
            row = re.match(
                r"\s*\|\s*\*\*(?P<k>[^*]+)\*\*\s*\|\s*(?P<v>[^|]+?)\s*\|\s*$",
                line,
            )
            if not row:
                continue
            key = row.group("k").strip().lower().replace(" ", "_")
            val = row.group("v").strip().strip("*")
            entry["attributes"][key] = val  # type: ignore[index]
        out["characters"].append(entry)  # type: ignore[attr-defined]
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

    # Missions: prefer the live missions.json (canonical source) over
    # the legacy stage_structure.json snapshot. Fall back to the snapshot
    # only when the live file is missing.
    missions_p = repo / "prototype" / "data" / "missions" / "missions.json"
    if missions_p.exists():
        try:
            d = json.loads(missions_p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            d = {}
        if isinstance(d, dict):
            out["missions"] = len(d)
    if out["missions"] == 0:
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
    "event_dialogues_stats.json": load_event_dialogues_stats,
    "stages_stats.json": load_stages_stats,
    "cyberspace_stats.json": load_cyberspace_stats,
    "journey_stats.json": load_journey_stats,
    "index_stats.json": load_index_stats,
    "character_stats.json": load_character_stats,
    "run_stats.json": load_run_stats,
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
