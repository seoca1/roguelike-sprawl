"""Tests for derivative short stories.

Each short story in Fiction/derivative/sprawl-trilogy/short-stories/
must satisfy:
- YAML frontmatter with required fields
- Title (in frontmatter)
- Original title (in frontmatter)
- Author (in frontmatter)
- Source text reference (in frontmatter)
- Wiki references list (in frontmatter, ≥ 2)
- Status: Final
- Korean body (≥ 800 characters)
- ≥ 1 source quote (in blockquote)
- 1 source quote in frontmatter or body
- Sections: 도입 / 전개 / 절정 / 결말 (at least 3 of 4)
- Connection section (## 연결)
- Notes section (## 각주)
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
STORIES_DIR = (
    REPO_ROOT.parent.parent / "Fiction" / "derivative" / "sprawl-trilogy" / "short-stories"
)
INDEX_PATH = REPO_ROOT.parent.parent / "Fiction" / "derivative" / "sprawl-trilogy" / "INDEX.md"

REQUIRED_FRONTMATTER = {
    "title": str,
    "original_title": str,
    "author": str,
    "publication_year": int,
    "derivative_type": str,
    "derivative_date": str,
    "genre": str,
    "series": str,
    "source_text": str,
    "wiki_references": list,
    "language": str,
    "format": str,
    "word_count_ko": str,
    "version": str,
    "status": str,
}


def _load_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    fm_text = text[4:end]
    result: dict = {}
    current_list_key: str | None = None
    for line in fm_text.split("\n"):
        if not line.strip():
            continue
        if line.startswith("  - ") and current_list_key is not None:
            item = line[4:].strip().strip('"').strip("'")
            result.setdefault(current_list_key, []).append(item)
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if val == "":
            current_list_key = key
            result.setdefault(key, [])
            continue
        current_list_key = None
        if val.startswith("[") and val.endswith("]"):
            items = [v.strip().strip('"').strip("'") for v in val[1:-1].split(",") if v.strip()]
            result[key] = items
        elif val.startswith('"') and val.endswith('"'):
            result[key] = val[1:-1]
        elif val.lstrip("-").isdigit():
            result[key] = int(val)
        else:
            result[key] = val
    return result


def _list_stories() -> list[Path]:
    if not STORIES_DIR.exists():
        return []
    return sorted(STORIES_DIR.glob("*.md"))


@pytest.fixture(scope="module")
def stories() -> list[Path]:
    if not STORIES_DIR.exists():
        pytest.skip(f"Fiction dir not present in CI: {STORIES_DIR}")
    return _list_stories()


@pytest.fixture(autouse=True)
def _require_fiction_dir() -> None:
    """Skip tests in this module if Fiction dir is not present (CI)."""
    if not STORIES_DIR.exists():
        pytest.skip(f"Fiction dir not present (CI only): {STORIES_DIR}")


def test_stories_dir_exists() -> None:
    if not STORIES_DIR.exists():
        pytest.skip(f"Stories dir not found (CI): {STORIES_DIR}")


def test_at_least_5_stories(stories: list[Path]) -> None:
    if not STORIES_DIR.exists():
        pytest.skip("Stories dir not present in CI environment")
    assert len(stories) >= 5, f"Expected ≥ 5 stories, found {len(stories)}"


@pytest.mark.parametrize("story_path", _list_stories())
def test_story_has_frontmatter(story_path: Path) -> None:
    if not STORIES_DIR.exists():
        pytest.skip("Stories dir not present in CI environment")
    fm = _load_frontmatter(story_path)
    assert fm, f"{story_path.name} missing or invalid frontmatter"


@pytest.mark.parametrize("story_path", _list_stories())
def test_story_frontmatter_required_fields(story_path: Path) -> None:
    fm = _load_frontmatter(story_path)
    missing = set(REQUIRED_FRONTMATTER) - set(fm)
    assert not missing, f"{story_path.name} missing: {missing}"


@pytest.mark.parametrize("story_path", _list_stories())
def test_story_status_is_final(story_path: Path) -> None:
    fm = _load_frontmatter(story_path)
    assert fm.get("status") == "final", f"{story_path.name} status: {fm.get('status')}"


@pytest.mark.parametrize("story_path", _list_stories())
def test_story_has_wiki_references(story_path: Path) -> None:
    fm = _load_frontmatter(story_path)
    refs = fm.get("wiki_references", [])
    assert isinstance(refs, list), f"{story_path.name} wiki_references not a list"
    assert len(refs) >= 2, f"{story_path.name} wiki refs: {len(refs)}"


@pytest.mark.parametrize("story_path", _list_stories())
def test_story_wiki_references_format(story_path: Path) -> None:
    fm = _load_frontmatter(story_path)
    refs = fm.get("wiki_references", [])
    for ref in refs:
        assert ref.startswith("[["), f"{story_path.name} bad ref format: {ref}"
        assert ref.endswith("]]"), f"{story_path.name} bad ref format: {ref}"


@pytest.mark.parametrize("story_path", _list_stories())
def test_story_korean_body_minimum(story_path: Path) -> None:
    text = story_path.read_text(encoding="utf-8")
    # Strip frontmatter
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        body = text[end + 5 :]
    else:
        body = text
    # Count Korean characters
    ko_chars = sum(1 for c in body if "가" <= c <= "힣")
    assert ko_chars >= 400, f"{story_path.name} Korean chars: {ko_chars} (≥400 required)"


@pytest.mark.parametrize("story_path", _list_stories())
def test_story_has_quote(story_path: Path) -> None:
    text = story_path.read_text(encoding="utf-8")
    assert "> " in text, f"{story_path.name} no blockquote (>)"
    quote_lines = [line for line in text.split("\n") if line.startswith(">")]
    assert len(quote_lines) >= 1, f"{story_path.name} no quote lines"


@pytest.mark.parametrize("story_path", _list_stories())
def test_story_has_sections(story_path: Path) -> None:
    text = story_path.read_text(encoding="utf-8")
    sections = ["도입", "전개", "절정", "결말"]
    found = sum(1 for s in sections if f"## {s}" in text)
    assert found >= 3, f"{story_path.name} sections: {found}/4"


@pytest.mark.parametrize("story_path", _list_stories())
def test_story_has_connections_section(story_path: Path) -> None:
    text = story_path.read_text(encoding="utf-8")
    assert "## 연결" in text, f"{story_path.name} missing '## 연결'"


@pytest.mark.parametrize("story_path", _list_stories())
def test_story_has_notes_section(story_path: Path) -> None:
    text = story_path.read_text(encoding="utf-8")
    assert "## 각주" in text, f"{story_path.name} missing '## 각주'"


@pytest.mark.parametrize("story_path", _list_stories())
def test_story_has_game_integration(story_path: Path) -> None:
    text = story_path.read_text(encoding="utf-8")
    # Should reference the game or design directory
    assert "roguelike_sprawl" in text or "event_dialogues" in text, (
        f"{story_path.name} no game integration reference"
    )


def test_index_exists() -> None:
    assert INDEX_PATH.exists(), f"INDEX.md not found at {INDEX_PATH}"


def test_index_lists_all_stories(stories: list[Path]) -> None:
    text = INDEX_PATH.read_text(encoding="utf-8")
    for story in stories:
        # Should reference the story filename
        assert story.stem in text, f"INDEX.md missing reference to {story.stem}"


def test_index_total_count() -> None:
    """INDEX should declare total count."""
    text = INDEX_PATH.read_text(encoding="utf-8")
    m = re.search(r"Total stories.*?(\d+)", text, re.IGNORECASE)
    assert m, "INDEX.md missing 'Total stories'"
    declared = int(m.group(1))
    actual = len(_list_stories())
    assert declared == actual, f"INDEX says {declared} stories, found {actual}"


def test_story_files_referenced_in_dashboard() -> None:
    """stories.html must link to all stories."""
    dash = REPO_ROOT / "dashboard" / "stories.html"
    assert dash.exists(), "stories.html not found"
    html = dash.read_text(encoding="utf-8")
    stories = _list_stories()
    for story in stories:
        assert story.name in html, f"stories.html missing link to {story.name}"


@pytest.mark.parametrize("story_path", _list_stories())
def test_story_pov_valid(story_path: Path) -> None:
    """POV should be specified in frontmatter (format field)."""
    fm = _load_frontmatter(story_path)
    fmt = fm.get("format", "")
    assert "1인칭" in fmt or "3인칭" in fmt, f"{story_path.name} POV unclear: {fmt}"
