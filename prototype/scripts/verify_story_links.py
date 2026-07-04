"""Story link validator (R2).

`missions.json`의 `story.source` 필드가 실제 단편 파일과 매핑되는지 검증.
CI / pre-commit 훅 통합 가능.

사용법:
    python verify_story_links.py                 # vault 루트에서 실행
    python verify_story_links.py --json          # JSON 출력
    python verify_story_links.py --missing-only  # 누락된 항목만
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# 프로젝트 루트: 이 스크립트는 prototype/scripts/ 아래에 있으므로 4단계 상위
ROOT = Path(__file__).resolve().parents[3]  # scripts -> prototype -> roguelike_sprawl -> Game
ROOT = ROOT.parent  # Game의 부모 = Projects/

sys.path.insert(0, str(ROOT / "Game" / "roguelike_sprawl" / "prototype" / "src"))

from roguelike_sprawl.data.story_resolver import (  # type: ignore[import-not-found]  # noqa: E402
    list_available_stems,
    validate_mission_sources,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate mission→story source links")
    parser.add_argument(
        "--missions",
        type=Path,
        default=ROOT
        / "Game"
        / "roguelike_sprawl"
        / "prototype"
        / "data"
        / "missions"
        / "missions.json",
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--missing-only", action="store_true", help="Only show issues")
    args = parser.parse_args()

    if not args.missions.exists():
        print(f"ERROR: missions.json not found at {args.missions}", file=sys.stderr)
        return 2

    with args.missions.open(encoding="utf-8") as f:
        missions = json.load(f)

    report = validate_mission_sources(missions, ROOT)
    available = list_available_stems(ROOT)

    if args.json:
        print(
            json.dumps(
                {
                    "missions_total": len(missions),
                    "stories_available": len(available),
                    "report": report,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(f"Missions: {len(missions)}")
        print(f"Available stories: {len(available)}")
        print()
        print(f"{'미션':<22} {'source':<28} {'EN':<8} {'KO':<8} {'issues'}")
        print("-" * 80)
        for r in report:
            en = "✓" if r["en_path"] else "✗"
            ko = "✓" if r["ko_path"] else "✗"
            issues = ",".join(r["issues"]) if r["issues"] else "OK"
            if args.missing_only and not r["issues"]:
                continue
            print(f"  {r['mission_id']:<20} {r['source']:<28} {en:<8} {ko:<8} {issues}")
        print()
        issues_count = sum(1 for r in report if r["issues"])
        if issues_count > 0:
            print(f"⚠️  {issues_count} missions have issues")
            return 1
        print("✓ All mission sources resolve correctly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
