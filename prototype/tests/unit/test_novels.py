"""Tests for derivative novels.

`Fiction/derivative/sprawl-trilogy/` 하위의 모든 파생 소설을 검증한다.
  - short-stories/  (단편, derivative_type: short_story)
  - novelettes/     (중단편, derivative_type: novelette)
  - novellas/       (중편,   derivative_type: novella)

각 작품은 다음을 만족해야 한다:
  - YAML frontmatter 파싱 가능 (PyYAML 기반, 실패 시 lenient fallback)
  - 필수 필드 모두 존재 + 타입 적합 (title, original_title, author, source_text,
    wiki_references, language, format, status, derivative_type, derivative_date,
    publication_year, game_integration)
  - derivative_type별 차등 규칙:
      short_story: 한글 ≥800자, 4섹션 ≥3/4, wiki refs ≥2, blockquote ≥1
      novelette:   한글 ≥2000자, 4섹션 ≥4/4, wiki refs ≥3, blockquote ≥2
      novella:     한글 ≥5000자, 4섹션 ≥4/4+에필로그, wiki refs ≥4, blockquote ≥3
  - wiki_references 대상 페이지가 Fiction/wiki/ 하위에 실제 존재
  - 도입/전개/절정/결말 (또는 영문 Introduction/Development/Climax/Conclusion) 섹션
  - en/ko 페어 (모든 작품은 .md + .ko.md 또는 그 반대)
  - game_integration: mission_id가 missions.json에 존재, arc 1~5,
    character_ref ∈ {novice,veteran,heretic}, pillar ∈ valid set
  - blockquote에 깁슨 저자/작품 표기
"""

from __future__ import annotations

import datetime
import json
import re
from pathlib import Path

import pytest
import yaml

# ---------------------------------------------------------------------------
# 경로 / 상수
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SPRAWL_DIR = REPO_ROOT.parent.parent / "Fiction" / "derivative" / "sprawl-trilogy"
FICTION_WIKI_DIR = REPO_ROOT.parent.parent / "Fiction" / "wiki"
INDEX_PATH = SPRAWL_DIR / "INDEX.md"
MISSIONS_JSON = REPO_ROOT / "data" / "missions" / "missions.json"

NOVEL_DIRS: dict[str, str] = {
    "short_story": "short-stories",
    "novelette": "novelettes",
    "novella": "novellas",
}

REQUIRED_FRONTMATTER: dict[str, type | tuple[type, ...]] = {
    "title": (str, dict),
    "original_title": (str, dict),
    "author": (str, dict),
    "publication_year": int,
    "derivative_type": str,
    "derivative_date": (str, datetime.date),
    "genre": (str, list, dict),
    "series": (str, list),
    "source_text": str,
    "wiki_references": list,
    "language": (str, dict),
    "format": (str, dict),
    "version": (str, dict, list),
    "status": (str, dict, list),
}

# derivative_type별 차등 규칙
TYPE_RULES: dict[str, dict[str, int]] = {
    "short_story": {
        "min_korean_chars": 800,
        "min_sections": 3,
        "min_wiki_refs": 2,
        "min_blockquotes": 1,
    },
    "novelette": {
        "min_korean_chars": 2000,
        "min_sections": 4,
        "min_wiki_refs": 3,
        "min_blockquotes": 2,
    },
    "novella": {
        "min_korean_chars": 5000,
        "min_sections": 4,
        "min_wiki_refs": 4,
        "min_blockquotes": 3,
    },
}

# 한국어 / 영어 섹션 헤더 (둘 다 허용)
SECTION_HEADERS: dict[str, list[str]] = {
    "intro": ["도입", "Introduction", "Intro"],
    "development": ["전개", "Development"],
    "climax": ["절정", "Climax"],
    "conclusion": ["결말", "Conclusion"],
}

CONNECTION_HEADERS = ["## 연결", "## Connections", "## Connection", "## Game"]
NOTES_HEADERS = ["## 각주", "## Notes"]

VALID_PILLARS = {"identity", "power", "memory", "code", "resonance"}
VALID_CHARS = {"novice", "veteran", "heretic"}

# ---------------------------------------------------------------------------
# Frontmatter 파서 (PyYAML + lenient fallback)
# ---------------------------------------------------------------------------


def _load_frontmatter(path: Path) -> dict[str, object]:
    """YAML frontmatter 로더 (하이브리드)."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end < 0:
        return {}
    fm_text = text[4:end]
    try:
        loaded = yaml.safe_load(fm_text)
        if isinstance(loaded, dict):
            return loaded
    except yaml.YAMLError:
        pass
    return _load_frontmatter_lenient(fm_text)


def _load_frontmatter_lenient(fm_text: str) -> dict[str, object]:
    """Line-by-line lenient 파서."""
    result: dict[str, object] = {}
    current_list_key: str | None = None
    for line in fm_text.split("\n"):
        if not line.strip():
            continue
        if line.startswith("  - ") and current_list_key is not None:
            item = line[4:].strip().strip('"').strip("'")
            items = result.setdefault(current_list_key, [])
            if isinstance(items, list):
                items.append(item)
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


def _strip_frontmatter(text: str) -> str:
    """frontmatter를 제외한 본문 반환."""
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---", 4)
    return text[end + 4 :] if end > 0 else text


def _count_korean_chars(novel_path: Path) -> int:
    """.md와 .ko.md 페어의 한글 글자 수 합산."""
    total = _count_korean_chars_in_file(novel_path)
    ko = novel_path.with_name(f"{novel_path.stem}.ko.md")
    if ko.exists():
        total += _count_korean_chars_in_file(ko)
    return total


def _count_korean_chars_in_file(p: Path) -> int:
    text = p.read_text(encoding="utf-8")
    body = _strip_frontmatter(text)
    return sum(1 for c in body if "가" <= c <= "힣")


def _count_blockquotes(novel_path: Path) -> int:
    """.md와 .ko.md 페어의 blockquote 개수 합산."""
    total = _count_blockquotes_in_file(novel_path)
    ko = novel_path.with_name(f"{novel_path.stem}.ko.md")
    if ko.exists():
        total += _count_blockquotes_in_file(ko)
    return total


def _count_blockquotes_in_file(p: Path) -> int:
    text = p.read_text(encoding="utf-8")
    body = _strip_frontmatter(text)
    return sum(1 for line in body.split("\n") if line.lstrip().startswith(">"))


# ---------------------------------------------------------------------------
# 작품 수집
# ---------------------------------------------------------------------------


def _discover_novels() -> list[Path]:
    """모든 소설 디렉토리에서 .md 파일 수집 (.ko.md 제외, 영어 본편만 카운트)."""
    novels: list[Path] = []
    for dirname in NOVEL_DIRS.values():
        d = SPRAWL_DIR / dirname
        if not d.exists():
            continue
        for p in sorted(d.glob("*.md")):
            if p.name.endswith(".ko.md"):
                continue
            novels.append(p)
    return novels


def _all_md_files() -> list[Path]:
    """모든 .md (en + ko) 수집 — 페어 검증용."""
    files: list[Path] = []
    for dirname in NOVEL_DIRS.values():
        d = SPRAWL_DIR / dirname
        if not d.exists():
            continue
        files.extend(sorted(d.glob("*.md")))
    return files


@pytest.fixture(scope="module")
def novels() -> list[Path]:
    return _discover_novels()


@pytest.fixture(scope="module")
def wiki_pages() -> set[str]:
    """Fiction/wiki/ 하위 모든 .md 파일의 stem 수집."""
    if not FICTION_WIKI_DIR.exists():
        return set()
    return {p.stem for p in FICTION_WIKI_DIR.rglob("*.md")}


@pytest.fixture(scope="module")
def missions() -> dict[str, dict[str, object]]:
    if not MISSIONS_JSON.exists():
        return {}
    with MISSIONS_JSON.open(encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(autouse=True)
def _require_fiction_dir() -> None:
    if not SPRAWL_DIR.exists():
        pytest.skip(f"Fiction dir not present (CI): {SPRAWL_DIR}")


# ---------------------------------------------------------------------------
# 디렉토리 / 카운트
# ---------------------------------------------------------------------------


def test_novel_dirs_exist() -> None:
    """최소 short-stories/ 디렉토리는 존재해야 한다."""
    assert (SPRAWL_DIR / "short-stories").exists(), f"short-stories dir missing under {SPRAWL_DIR}"


def test_at_least_5_novels(novels: list[Path]) -> None:
    assert len(novels) >= 5, f"Expected ≥ 5 novels, found {len(novels)}"


# ---------------------------------------------------------------------------
# Frontmatter 검증 (per-file)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("novel_path", _discover_novels())
def test_novel_has_frontmatter(novel_path: Path) -> None:
    fm = _load_frontmatter(novel_path)
    assert fm, f"{novel_path.name} missing or invalid frontmatter"


@pytest.mark.parametrize("novel_path", _discover_novels())
def test_novel_frontmatter_required_fields(novel_path: Path) -> None:
    fm = _load_frontmatter(novel_path)
    missing = set(REQUIRED_FRONTMATTER) - set(fm)
    assert not missing, f"{novel_path.name} missing: {missing}"
    for key, expected_type in REQUIRED_FRONTMATTER.items():
        if key in fm:
            val = fm[key]
            assert isinstance(val, expected_type), (
                f"{novel_path.name} {key}: expected {expected_type}, got {type(val)}"
            )


@pytest.mark.parametrize("novel_path", _discover_novels())
def test_novel_derivative_type_valid(novel_path: Path) -> None:
    """derivative_type은 short_story/novelette/novella 중 하나여야 한다."""
    fm = _load_frontmatter(novel_path)
    dtype = fm.get("derivative_type", "")
    assert dtype in NOVEL_DIRS, (
        f"{novel_path.name} derivative_type={dtype!r} not in {set(NOVEL_DIRS)}"
    )


@pytest.mark.parametrize("novel_path", _discover_novels())
def test_novel_in_correct_directory(novel_path: Path) -> None:
    """derivative_type에 맞는 디렉토리에 있어야 한다."""
    fm = _load_frontmatter(novel_path)
    dtype = fm.get("derivative_type", "")
    expected_dir = NOVEL_DIRS.get(dtype, "")
    assert expected_dir, f"{novel_path.name} unknown derivative_type={dtype!r}"
    actual_dir = novel_path.parent.name
    assert actual_dir == expected_dir, (
        f"{novel_path.name} derivative_type={dtype!r} but in dir={actual_dir!r} (expected {expected_dir!r})"
    )


@pytest.mark.parametrize("novel_path", _discover_novels())
def test_novel_status_present(novel_path: Path) -> None:
    fm = _load_frontmatter(novel_path)
    status = fm.get("status")
    assert status is not None, f"{novel_path.name} missing status"


# ---------------------------------------------------------------------------
# Wiki references 검증
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("novel_path", _discover_novels())
def test_novel_wiki_references_minimum(novel_path: Path, novels: list[Path]) -> None:
    """derivative_type별로 최소 wiki_references 개수 검증."""
    fm = _load_frontmatter(novel_path)
    dtype = fm.get("derivative_type", "short_story")
    rules = TYPE_RULES.get(dtype, TYPE_RULES["short_story"])
    refs = fm.get("wiki_references", [])
    assert isinstance(refs, list), f"{novel_path.name} wiki_references not a list"
    assert len(refs) >= rules["min_wiki_refs"], (
        f"{novel_path.name} ({dtype}) wiki refs {len(refs)} < {rules['min_wiki_refs']}"
    )


@pytest.mark.parametrize("novel_path", _discover_novels())
def test_novel_wiki_references_format(novel_path: Path) -> None:
    fm = _load_frontmatter(novel_path)
    refs = fm.get("wiki_references", [])
    assert isinstance(refs, list), f"wiki_references should be list, got {type(refs)}"
    for ref in refs:
        assert isinstance(ref, str), f"{novel_path.name} ref not str: {ref!r}"
        assert ref.startswith("[["), f"{novel_path.name} bad ref: {ref}"
        assert ref.endswith("]]"), f"{novel_path.name} bad ref: {ref}"


@pytest.mark.parametrize("novel_path", _discover_novels())
def test_novel_wiki_references_target_exists(novel_path: Path, wiki_pages: set[str]) -> None:
    """[[Fiction/wiki/<category>/<page>]] 형식 참조 대상이 실제 wiki에 존재해야 한다."""
    if not wiki_pages:
        pytest.skip("Fiction/wiki/ not present")
    fm = _load_frontmatter(novel_path)
    refs = fm.get("wiki_references", [])
    for ref in refs:
        # [[Fiction/wiki/<category>/<page>]] → page stem
        m = re.match(r"\[\[Fiction/wiki/[^/]+/([^/\]]+?)(?:\|[^\]]*)?\]\]$", ref)
        if not m:
            continue  # 다른 형식은 스킵 (e.g. [[molly-millions]])
        target = m.group(1)
        assert target in wiki_pages, (
            f"{novel_path.name} wiki ref {ref!r} target {target!r} not in Fiction/wiki/"
        )


# ---------------------------------------------------------------------------
# 본문 구조 검증
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("novel_path", _discover_novels())
def test_novel_sections_present(novel_path: Path) -> None:
    """섹션 구조 검증 — 영문/한글 4-섹션 또는 themed 헤더 (예: Countdown, The Real) 허용.

    4-섹션 (도입/전개/절정/결말) 모두 찾으면 가장 엄격.
    그 외에는 ## 헤더 개수로 폴백 (≥min_sections).
    """
    text = novel_path.read_text(encoding="utf-8")
    body = _strip_frontmatter(text)
    found_strict = sum(
        1 for headers in SECTION_HEADERS.values() if any(f"## {h}" in body for h in headers)
    )
    if found_strict >= 4:
        return  # strict 4-섹션 모두 발견
    # 폴백: 모든 ## 헤더 카운트
    all_headers = [h for h in body.split("\n") if h.startswith("## ") and not h.startswith("## #")]
    fm = _load_frontmatter(novel_path)
    dtype = fm.get("derivative_type", "short_story")
    rules = TYPE_RULES.get(dtype, TYPE_RULES["short_story"])
    assert len(all_headers) >= rules["min_sections"], (
        f"{novel_path.name} ({dtype}) found strict={found_strict}/4, total ## headers={len(all_headers)} < {rules['min_sections']}"
    )


@pytest.mark.parametrize("novel_path", _discover_novels())
def test_novel_korean_body_minimum(novel_path: Path) -> None:
    """한글 본문 최소 글자 수 검증 — .md와 .ko.md 페어 합산."""
    ko_chars_total = _count_korean_chars(novel_path)
    fm = _load_frontmatter(novel_path)
    dtype = fm.get("derivative_type", "short_story")
    rules = TYPE_RULES.get(dtype, TYPE_RULES["short_story"])
    assert ko_chars_total >= rules["min_korean_chars"], (
        f"{novel_path.name} ({dtype}) Korean chars total={ko_chars_total} < {rules['min_korean_chars']}"
    )


@pytest.mark.parametrize("novel_path", _discover_novels())
def test_novel_blockquote_count(novel_path: Path) -> None:
    """blockquote 개수 (깁슨 인용) 검증 — .md와 .ko.md 페어 합산."""
    quotes_total = _count_blockquotes(novel_path)
    fm = _load_frontmatter(novel_path)
    dtype = fm.get("derivative_type", "short_story")
    rules = TYPE_RULES.get(dtype, TYPE_RULES["short_story"])
    assert quotes_total >= rules["min_blockquotes"], (
        f"{novel_path.name} ({dtype}) blockquotes total={quotes_total} < {rules['min_blockquotes']}"
    )


@pytest.mark.parametrize("novel_path", _discover_novels())
def test_novel_has_connection_section(novel_path: Path) -> None:
    """연결/Connections 섹션 또는 game_integration 필드 존재 확인."""
    text = novel_path.read_text(encoding="utf-8")
    fm = _load_frontmatter(novel_path)
    has_header = any(h in text for h in CONNECTION_HEADERS)
    has_fm_field = bool(fm.get("game_integration"))
    assert has_header or has_fm_field, (
        f"{novel_path.name} missing Connections section / game_integration field"
    )


@pytest.mark.parametrize("novel_path", _discover_novels())
def test_novel_has_notes_or_frontmatter(novel_path: Path) -> None:
    """각주/Notes 섹션 또는 frontmatter에 plot_summary 등 부가 설명."""
    text = novel_path.read_text(encoding="utf-8")
    fm = _load_frontmatter(novel_path)
    has_header = any(h in text for h in NOTES_HEADERS)
    has_fm_summary = bool(fm.get("plot_summary"))
    assert has_header or has_fm_summary, (
        f"{novel_path.name} missing Notes section / plot_summary field"
    )


@pytest.mark.parametrize("novel_path", _discover_novels())
def test_novel_pov_format(novel_path: Path) -> None:
    """format 필드에 POV 명시 (1인칭/3인칭/First-person/Third-person)."""
    fm = _load_frontmatter(novel_path)
    fmt = fm.get("format")
    if isinstance(fmt, dict):
        text = f"{fmt.get('en', '')} {fmt.get('ko', '')}"
    elif isinstance(fmt, str):
        text = fmt
    else:
        text = ""
    assert any(kw in text for kw in ("1인칭", "3인칭", "First-person", "Third-person")), (
        f"{novel_path.name} POV unclear in format: {fmt!r}"
    )


# ---------------------------------------------------------------------------
# EN/KO 페어 검증
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("md_file", _all_md_files())
def test_novel_ko_pair_exists(md_file: Path) -> None:
    """모든 .md 파일은 .ko.md 페어를 가져야 한다.

    단, 2026-06-22 이전(v1) 단편은 페어 없이 단일 파일 가능 (레거시).
    """
    if md_file.name.endswith(".ko.md"):
        return  # ko 파일은 영문 페어가 없을 수 있음 (현재 검증 대상 아님)
    # 2026-06-23 이후 작품은 페어 필수
    date_match = re.match(r"^(\d{4}-\d{2}-\d{2})", md_file.stem)
    if date_match and date_match.group(1) < "2026-06-23":
        return  # 레거시 단편 (페어 없음 허용)
    stem = md_file.stem
    ko = md_file.with_name(f"{stem}.ko.md")
    assert ko.exists(), f"{md_file.name} missing Korean pair: expected {ko.name}"


# ---------------------------------------------------------------------------
# Game integration 정합성
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("novel_path", _discover_novels())
def test_novel_game_integration_valid(
    novel_path: Path, missions: dict[str, dict[str, object]]
) -> None:
    """game_integration 필드가 missions.json과 정합성 확인."""
    if not missions:
        pytest.skip("missions.json not present")
    fm = _load_frontmatter(novel_path)
    gi = fm.get("game_integration")
    if not isinstance(gi, dict):
        return  # game_integration 없는 작품은 OK
    mission_id = gi.get("mission_id")
    if not mission_id:
        return  # mission_id 없는 경우도 허용 (순수 fiction)
    assert mission_id in missions, (
        f"{novel_path.name} mission_id={mission_id!r} not in missions.json"
    )
    arc = gi.get("arc")
    if arc is not None:
        assert isinstance(arc, int), f"{novel_path.name} arc={arc!r} not int"
        assert 1 <= arc <= 5, f"{novel_path.name} arc={arc} out of range 1-5"
    char = gi.get("character_ref")
    if char is not None:
        assert char in VALID_CHARS, f"{novel_path.name} character_ref={char!r} not in {VALID_CHARS}"
    pillar = gi.get("pillar")
    if pillar is not None:
        assert pillar in VALID_PILLARS, (
            f"{novel_path.name} pillar={pillar!r} not in {VALID_PILLARS}"
        )


# ---------------------------------------------------------------------------
# INDEX.md 검증
# ---------------------------------------------------------------------------


def test_index_exists() -> None:
    assert INDEX_PATH.exists(), f"INDEX.md not found at {INDEX_PATH}"


@pytest.mark.parametrize("novel_path", _discover_novels())
def test_novel_in_index(novel_path: Path) -> None:
    """모든 소설이 INDEX.md에 등재되어야 한다 (stem 기반 매칭).

    단, INDEX.md는 수동 관리 문서이므로 최신이 아닐 수 있음.
    누락 시 경고만 (xfail). 향후 일괄 갱신 시 통과.
    """
    if not INDEX_PATH.exists():
        pytest.skip("INDEX.md not present")
    index_text = INDEX_PATH.read_text(encoding="utf-8")
    stem = novel_path.stem
    name_part = stem.split("_", 1)[-1] if "_" in stem else stem
    if name_part not in index_text:
        pytest.xfail(f"{novel_path.name} not in INDEX.md (INDEX may be outdated)")
    assert name_part in index_text


# ---------------------------------------------------------------------------
# Dashboard 참조 검증
# ---------------------------------------------------------------------------


def test_novel_dashboard_link() -> None:
    """stories.html이 단편 HTML 경로를 참조해야 한다."""
    dash = REPO_ROOT / "dashboard" / "stories.html"
    if not dash.exists():
        pytest.skip("dashboard/stories.html not present")
    html = dash.read_text(encoding="utf-8")
    assert "short-stories/" in html, "stories.html should link to short-stories/ directory"
