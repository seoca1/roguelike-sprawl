#!/usr/bin/env python3
"""Find broken wikilinks in roguelike_sprawl with file:line:target detail."""

import re
from pathlib import Path

ROOT = Path(".")
EXCLUDE = {".git", "node_modules", ".obsidian", ".pytest_cache", "__pycache__", "_archive", "_inventory", ".venv", "prototype"}


def md_files():
    for p in ROOT.rglob("*.md"):
        if not any(e in p.parts for e in EXCLUDE):
            yield p


def strip(text):
    return re.sub(
        r"\A---\n.*?\n---\n",
        "",
        re.sub(r"`[^`]+`", "", re.sub(r"```.*?```", "", text, flags=re.DOTALL)),
        flags=re.DOTALL,
    )


WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
MDLINK = re.compile(r"\[([^\]]+)\]\(([^)]+\.md)(?:#[^)]*)?\)")


def main():
    files = list(md_files())
    stems = {p.stem: p for p in files}

    broken = []
    for f in files:
        txt = strip(f.read_text(errors="ignore"))
        lines = txt.splitlines()
        for i, line in enumerate(lines, 1):
            for m in WIKILINK.finditer(line):
                w = m.group(1).strip()
                if not w or w in {"wikilink", "...", "…"}:
                    continue
                try:
                    ok = (f.parent / (w + ".md")).resolve().exists()
                except Exception:
                    ok = False
                if not ok:
                    ok = w in stems
                if ok:
                    continue
                broken.append((str(f.relative_to(ROOT)), i, w, line.strip()[:100]))

    print(f"=== BROKEN WIKILINKS (project-scoped, excluding prototype/, inline code stripped) ===\n")
    print(f"Total: {len(broken)}\n")
    for f, ln, w, txt in broken:
        print(f"{f}:{ln}")
        print(f"  target: [[{w}]]")
        print(f"  text:   {txt}")
        print()


if __name__ == "__main__":
    main()
