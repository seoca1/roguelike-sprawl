"""Demo: 12 BGM 사운드 (MiniMax 트림) 모두 실제로 재생되는지 검증.

테스트 방법: 각 WAV 의 첫 5초만 afplay 로 재생 (소리 들으면서 검증).
사용법:
  uv run python scripts/demo_minimax_bgms.py           # 5초씩 (빠른 검증)
  uv run python scripts/demo_minimax_bgms.py --full   # 30초씩 전곡 (감상)
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

BGM_FILES: list[str] = [
    "theme_broadcast.wav",
    "theme_chiba.wav",
    "theme_cyberspace.wav",
    "theme_finn_office.wav",
    "theme_hammer_alert.wav",
    "theme_industrial.wav",
    "theme_loa_channel.wav",
    "theme_loa_drum.wav",
    "theme_loa_drum_fade.wav",
    "theme_manarase_drone.wav",
    "theme_matrix_rain.wav",
    "theme_sense_net.wav",
]

SNDS_DIR = Path(__file__).resolve().parent.parent / "data" / "sounds_test"


def main() -> int:
    parser = argparse.ArgumentParser(description="12 MiniMax BGM 트랙 데모")
    parser.add_argument("--full", action="store_true", help="30초 전곡 (기본: 5초씩)")
    parser.add_argument("--skip", type=int, default=0, help="이 인덱스부터 시작")
    parser.add_argument("--only", type=str, help="단일 트랙만 (예: theme_matrix_rain.wav)")
    parser.add_argument("--silent", action="store_true", help="파일 검증만 (재생 안 함)")
    args = parser.parse_args()

    duration = 30 if args.full else 5
    files = BGM_FILES
    if args.only:
        files = [args.only]

    if not SNDS_DIR.exists():
        print(f"[ERROR] {SNDS_DIR} not found")
        return 1

    print(f"=== 12 MiniMax BGM 검증 — {duration}초씩 ===\n")
    print(f"위치: {SNDS_DIR}\n")

    passed = failed = 0
    for idx, name in enumerate(files):
        if idx < args.skip:
            continue
        path = SNDS_DIR / name
        if not path.exists():
            print(f"  ❌ {idx+1:2}. {name:<32} (파일 없음)")
            failed += 1
            continue

        size_kb = path.stat().st_size // 1024
        print(f"  [{idx+1:2}/{len(files)}] ▶ {name:<32} ({size_kb:>5} KB)")

        if args.silent:
            print(f"      ✓ 파일 검증 OK")
            passed += 1
            continue

        if sys.platform == "darwin":
            cmd = ["afplay", "-t", str(duration), "-v", "0.6", str(path)]
            try:
                subprocess.run(cmd, check=True, capture_output=True, timeout=duration + 5)
                print(f"      ✓ 재생 완료 ({duration}초)")
                passed += 1
            except Exception as e:
                print(f"      ❌ 재생 실패: {e}")
                failed += 1
        else:
            print(f"      (afplay 없음, 검증만)")
            passed += 1

    print(f"\n=== 결과: {passed} OK / {failed} 실패 (전체 {len(files)}개) ===")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
