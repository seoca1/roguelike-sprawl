"""단편 소설 stem → 파일 경로 정규화 (R1).

`missions.json`의 `story.source` 필드는 단편 stem (예: `case_jackout-30sec`)이고,
실제 파일은 날짜 prefix를 가진 형태 (예: `2026-06-23_case_jackout-30sec.md`)입니다.
날짜 prefix는 v1 → v2 갱신 시 변경될 수 있으므로 코드에서 정규화합니다.

규칙:
- `2026-06-23_<stem>.md` (가장 최신 canonical) 우선
- 없으면 다른 날짜 prefix 시도
- 한국어 번역 (`.ko.md`) 도 동일한 정규화
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional


# 가장 최근 canonical 날짜 (v2.0 최종). 새 버전 출시 시 갱신.
CANONICAL_DATES = ("2026-06-29", "2026-06-23", "2026-06-22", "2026-06-20", "2026-06-19")


def _short_stories_dir(repo_root: Path) -> Path:
    """단편 소설 디렉토리 경로. repo_root 기준."""
    return repo_root / "Fiction" / "derivative" / "sprawl-trilogy" / "short-stories"


def resolve_story_path(stem: str, repo_root: Path) -> Optional[Path]:
    """단편 stem → 영어 본편 파일 경로.

    Args:
        stem: 미션의 source 필드 (예: "case_jackout-30sec")
        repo_root: 프로젝트 루트 (Projects/)

    Returns:
        찾은 파일 경로. 없으면 None.
    """
    base = _short_stories_dir(repo_root)
    if not base.exists():
        return None
    # canonical 날짜 순으로 검색
    for date in CANONICAL_DATES:
        candidate = base / f"{date}_{stem}.md"
        if candidate.exists():
            return candidate
    # 어떤 날짜든 매칭
    matches = sorted(base.glob(f"*_{stem}.md"), reverse=True)
    return matches[0] if matches else None


def resolve_ko_translation(stem: str, repo_root: Path) -> Optional[Path]:
    """단편 stem → 한국어 번역 파일 경로.

    Args:
        stem: 미션의 source 필드
        repo_root: 프로젝트 루트

    Returns:
        한국어 번역 파일 경로. 없으면 None.
    """
    base = _short_stories_dir(repo_root)
    if not base.exists():
        return None
    for date in CANONICAL_DATES:
        candidate = base / f"{date}_{stem}.ko.md"
        if candidate.exists():
            return candidate
    matches = sorted(base.glob(f"*_{stem}.ko.md"), reverse=True)
    return matches[0] if matches else None


def list_available_stems(repo_root: Path) -> list[str]:
    """사용 가능한 단편 stem 목록 (모든 날짜 통합, 중복 제거)."""
    base = _short_stories_dir(repo_root)
    if not base.exists():
        return []
    stems = set()
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


def validate_mission_sources(missions: dict, repo_root: Path) -> list[dict]:
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
