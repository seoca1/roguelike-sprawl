"""소설 stem → 파일 경로 정규화 (R1).

`missions.json`의 `story.source` 필드는 소설 stem (예: `case_jackout-30sec`)이고,
실제 파일은 날짜 prefix를 가진 형태 (예: `2026-06-23_case_jackout-30sec.md`)입니다.
날짜 prefix는 v1 → v2 갱신 시 변경될 수 있으므로 코드에서 정규화합니다.

소설은 다음 디렉토리 중 하나에 저장됨 (test_novels.py 검증):
  - short-stories/  (단편,   derivative_type: short_story)
  - novelettes/     (중단편, derivative_type: novelette)
  - novellas/       (중편,   derivative_type: novella)

규칙:
- canonical 날짜 순으로 모든 소설 디렉토리 검색
- 없으면 다른 날짜 prefix 시도
- 한국어 번역 (`.ko.md`) 도 동일한 정규화
"""

from __future__ import annotations

from pathlib import Path

# 가장 최근 canonical 날짜 (v2.1). 새 버전 출시 시 갱신.
CANONICAL_DATES = (
    "2026-07-08",
    "2026-07-01",
    "2026-06-30",
    "2026-06-29",
    "2026-06-25",
    "2026-06-23",
    "2026-06-22",
    "2026-06-20",
    "2026-06-19",
)

# 소설 디렉토리 목록 (derivative_type 순) — 2026-07-10 구조 변경 반영
# en/ko 하위 디렉토리로 분리됨. resolver는 양쪽 구조 (legacy + new) 모두 지원.
NOVEL_DIR_NAMES: tuple[str, ...] = ("short-stories", "novelettes", "novellas")
LANG_SUBDIRS: tuple[str, ...] = ("en", "ko")


def _novel_dirs(repo_root: Path) -> list[Path]:
    """모든 소설 디렉토리 경로 반환 (존재하는 것만).

    Searches all three trilogies (Sprawl / Bridge / Blue Ant).
    Returns both legacy paths (e.g., short-stories/case_jackout.md)
    and new paths (e.g., short-stories/en/case_jackout.md).
    """
    derivative = repo_root / "Fiction" / "derivative"
    trilogies = ("sprawl-trilogy", "bridge-trilogy", "blue-ant")
    paths: list[Path] = []
    for trilogy in trilogies:
        for name in NOVEL_DIR_NAMES:
            base = derivative / trilogy / name
            if base.exists():
                paths.append(base)
                for lang in LANG_SUBDIRS:
                    sub = base / lang
                    if sub.exists():
                        paths.append(sub)
    return paths


def _short_stories_dir(repo_root: Path) -> Path:
    """단편 소설 디렉토리 경로. (legacy 호환용)"""
    return repo_root / "Fiction" / "derivative" / "sprawl-trilogy" / "short-stories"


def _search_in_dirs(stem: str, suffix: str, repo_root: Path) -> Path | None:
    """모든 소설 디렉토리에서 canonical 날짜 순으로 검색.

    2026-07-10 구조 변경: en/ko 하위 디렉토리도 검색.
    """
    for date in CANONICAL_DATES:
        for base in _novel_dirs(repo_root):
            candidate = base / f"{date}_{stem}{suffix}"
            if candidate.exists():
                return candidate
    # 어떤 날짜든 매칭
    for base in _novel_dirs(repo_root):
        matches = sorted(base.glob(f"*_{stem}{suffix}"), reverse=True)
        if matches:
            return matches[0]
    return None


def resolve_story_path(stem: str, repo_root: Path) -> Path | None:
    """소설 stem → 영어 본편 파일 경로.

    Args:
        stem: 미션의 source 필드 (예: "case_jackout-30sec")
        repo_root: 프로젝트 루트 (Projects/)

    Returns:
        찾은 파일 경로. 없으면 None.
    """
    return _search_in_dirs(stem, ".md", repo_root)


def resolve_ko_translation(stem: str, repo_root: Path) -> Path | None:
    """소설 stem → 한국어 번역 파일 경로.

    Args:
        stem: 미션의 source 필드
        repo_root: 프로젝트 루트

    Returns:
        한국어 번역 파일 경로. 없으면 None.
    """
    return _search_in_dirs(stem, ".ko.md", repo_root)


def list_available_stems(repo_root: Path) -> list[str]:
    """사용 가능한 소설 stem 목록 (모든 날짜/디렉토리 통합, 중복 제거)."""
    stems: set[str] = set()
    for base in _novel_dirs(repo_root):
        for f in base.glob("*.md"):
            if f.name.endswith(".ko.md"):
                continue
            # 2026-06-23_case_jackout-30sec → ['2026-06-23', 'case_jackout-30sec']
            # 최대 1번 split으로 [날짜, stem] 분리 (stem 내부에 하이픈 허용)
            parts = f.stem.split("_", 1)
            if len(parts) == 2 and parts[0].startswith("2026-"):
                stems.add(parts[1])
            else:
                stems.add(f.stem)
    return sorted(stems)


def validate_mission_sources(
    missions: dict[str, dict[str, object]], repo_root: Path
) -> list[dict[str, object]]:
    """missions.json의 모든 source 필드 검증.

    Returns:
        문제 보고서 리스트. 각 항목:
            - mission_id
            - source (stem)
            - en_path (or None)
            - ko_path (or None)
            - issues (list of issue strings)
    """
    report = []
    for mid, m in missions.items():
        story = m.get("story", {})
        if not isinstance(story, dict):
            continue
        source = story.get("source", "")
        if not source:
            report.append(
                {
                    "mission_id": mid,
                    "source": source,
                    "en_path": None,
                    "ko_path": None,
                    "issues": ["MISSING_SOURCE"],
                }
            )
            continue
        en = resolve_story_path(source, repo_root)
        ko = resolve_ko_translation(source, repo_root)
        issues = []
        if en is None:
            issues.append("EN_NOT_FOUND")
        if ko is None:
            issues.append("KO_NOT_FOUND")
        report.append(
            {
                "mission_id": mid,
                "source": source,
                "en_path": str(en) if en else None,
                "ko_path": str(ko) if ko else None,
                "issues": issues,
            }
        )
    return report
