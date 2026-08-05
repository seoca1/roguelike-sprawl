# Session Summary — 2026-07-11 (Dashboard Audio Debugging + Audio Tools)

**Scope**: 사용자가 "대시보드에서 사운드 안 들림" 보고로 시작한 세션. 본 세션 동안 `Game/roguelike_sprawl/dashboard/sound.html` 의 사운드 재생 코드 수정 + 터미널 오디오 검증 도구 작성 + 시스템 오디오 라우팅 진단까지 진행.

**핵심 결정 — 정착된 도구/관행**:

> **"Terminal afplay 만으로는 검증 가능 → 브라우저 (Chrome/Safari) audio 라우팅은 macOS 시스템 레벨 → 재부팅 전까지 정상화 어려움"** (사용자 판단, 2026-07-11)
>
> 브라우저 측 사운드 재생 검증은 `audio-doctor.py switch` + `afplay` 조합으로 터미널에서 즉시 가능.
> 향후 동일 증상 발생 시 `verify_sounds.py` + `audio-doctor.py` 활용 패턴을 첫 진단 단계로 정착.

## 액션 요약 (12개)

| # | 액션 | 산출 | 파일 |
|---|------|------|------|
| 1 | sound.html UI 명확화 | 재생 버튼 ▶ 아이콘 + Reference 카드 opacity/cursor/dashed border | `dashboard/sound.html` |
| 2 | Reference 섹션 헤더 추가 | "📋 Reference — read-only..." 명시 | `dashboard/sound.html` |
| 3 | catch handler 진단 개선 | NotAllowedError/NotSupportedError/code 4 분기화 | `dashboard/sound.html` `playTheme()` |
| 4 | "Empty src attribute" 오진단 수정 | `_bgmCleared` 플래그 + src 검증 가드 | `dashboard/sound.html` `playTheme/stopAll` |
| 5 | DOM audio element 부착 | `ensureBgmAudio()` + `document.body.appendChild` | `dashboard/sound.html` |
| 6 | Playwright 검증 | 12/12 정상 재생, currentTime 진행 확인 | (인메모리) |
| 7 | 로그 4개 항목 append | UI 명확화 / catch 개선 / Empty src 수정 / DOM audio | `Game/roguelike_sprawl/log.md` |
| 8 | WAV 검증 스크립트 | 12개 audible/RMS/silent 감지 + 재생 옵션 | `scripts/verify_sounds.py` (신규) |
| 9 | 오디오 진단 CLI | 상태/전환/순회/테스트 + doctor 종합 진단 | `scripts/audio-doctor.py` (신규) |
| 10 | switchaudio-osx 설치 | macOS 오디오 디바이스 CLI 전환 도구 | `brew install switchaudio-osx` |
| 11 | Chrome audio helper 재시작 | `kill -TERM <pid>` → SIGTERM → auto respawn | (인메모리) |
| 12 | coreaudiod 재시작 가이드 | `sudo killall coreaudiod` 사용자 직접 실행 | (사용자 액션) |

## 누적 지표

| 지표 | 시작 | 현재 |
|---|---|---|
| `sound.html` 본 BGM 재생 코드 라인 (effectively) | broken | ✅ 12/12 헤드리스 검증 |
| `sound.html` `_bgmCleared`/`ensureBgmAudio` 등 안전 패턴 | 0 | 4개 패턴 적용 |
| `sound.html` 404/Empty src 오진 메시지 가능 여부 | 있음 | ✅ 가드 + 진짜 메시지 분기 |
| `scripts/` 오디오 진단 도구 | 0 | 2개 (`verify_sounds.py`, `audio-doctor.py`) |
| Brew CLI 오디오 전환 도구 | 없음 | `switchaudio-osx 1.2.2` |
| `log.md` 일자 항목 수 (07-11) | 0 | 4 |
| macOS 출력 디바이스 (HDMI 정상) | NV156 | NV156 (변동 없음) |
| **macOS 브라우저 오디오 라우팅** | ❓ | **⏳ 미해결 (재부팅 시 해결 전망)** |

## 적용된 수정 패턴 (`sound.html`)

| 패턴 | 효과 |
|------|------|
| `▶ <label>` 버튼 라벨 | 클릭 가능 vs Reference 카드 시각 구분 |
| `opacity: 0.55` + `border-style: dashed` on Reference | 비활성 카드 분명히 |
| `catch (e)` 의 `e.name === 'NotAllowedError' / 'NotSupportedError'` 분기 | 사용자 vs 진짜 에러 메시지 구분 |
| `a._bgmCleared` 플래그 | `src = ""` 시 발생하는 오진 메시지 방지 |
| `if (a.error.code === 4 && a.networkState === 3 && a.src.length > 0)` | 진짜 404 만 "파일 없음 (404)" 표시 |
| `new Audio()` + 명시적 `a.src = ...` | cross-browser 안정성 |
| `ensureBgmAudio()` + `document.body.appendChild` | Safari/모바일 detached element 자동재생 보장 |

## 도구 사용법 (재현 가능)

```bash
# 12개 WAV 일괄 검증 (RMS/silent 감지)
python3 /Users/emilio/projects/Projects/scripts/verify_sounds.py

# 특정 인덱스만 재생 (0~11)
python3 /Users/emilio/projects/Projects/scripts/verify_sounds.py --play 0

# 전체 순차 재생 (각 3초)
python3 /Users/emilio/projects/Projects/scripts/verify_sounds.py --play-all

# 출력 디바이스 상태/전체
python3 /Users/emilio/projects/Projects/scripts/audio-doctor.py status

# 출력 디바이스 전환 (부분 일치 매칭)
python3 /Users/emilio/projects/Projects/scripts/audio-doctor.py switch "Mac mini"

# 1초 테스트 사운드 (현재 디바이스로)
python3 /Users/emilio/projects/Projects/scripts/audio-doctor.py test 1

# 모든 디바이스 순회 (어디서든 들리는지 격리)
python3 /Users/emilio/projects/Projects/scripts/audio-doctor.py cycle

# 종합 진단 + 권장 다음 액션
python3 /Users/emilio/projects/Projects/scripts/audio-doctor.py doctor

# 별칭 (선택) — ~/.zshrc 에 추가
alias audio-doc="python3 /Users/emilio/projects/Projects/scripts/audio-doctor.py"
alias verify-sounds="python3 /Users/emilio/projects/Projects/scripts/verify_sounds.py"
```

## 알려진 잔여 / 미해결

| 위치 / 증상 | 상태 | 다음 액션 |
|---|---|---|
| macOS 브라우저 (Chrome + Safari) 오디오 라우팅 | ⏳ 사용자 재부팅 보류 | 재부팅 후 재테스트 |
| macOS 26.5.2 의 per-app audio device 매핑 | (단순한 OS 버그 추정) | 재부팅 외 해결책 없음 |
| `docs/notion-reflects/PROGRESS_REPORT_*_NOTION_READY.md` 누적 | 이전 노션 보고서 형식 따름 | 사용자 Notion 업로드 |

## 작성/수정 파일

- `/Users/emilio/projects/Projects/Game/roguelike_sprawl/dashboard/sound.html` (4단계 수정)
- `/Users/emilio/projects/Projects/Game/roguelike_sprawl/log.md` (07-11 4개 항목)
- `/Users/emilio/projects/Projects/scripts/verify_sounds.py` (신규)
- `/Users/emilio/projects/Projects/scripts/audio-doctor.py` (신규)
- `/Users/emilio/projects/Projects/docs/notion-reflects/PROGRESS_REPORT_2026-07-11_NOTION_READY.md` (신규)
- 이 문서: `/Users/emilio/projects/Projects/Game/roguelike_sprawl/SESSION_SUMMARY_2026-07-11.md`
- macOS: `switchaudio-osx 1.2.2` (homebrew)
- ~/.config/opencode/ : 미수정 (세션 시작 시 구성 그대로)

## 다음 단계 (사용자 판단 보류)

- 🔵 macOS 재부팅 후 브라우저 오디오 사운드 페이지가 정상 작동하는지 확인
- 🔵 재부팅 후에도 안 들리면 → Chrome `chrome://settings/content/sound` 에서 localhost 출력 디바이스 검토
- 🟢 `verify_sounds.py` / `audio-doctor.py` 를 다른 게임/미디어 검증에도 활용 (재사용 가능 도구)

---

# Part 2 — 2026-07-11 (BGM v3: MiniMax 외부 생성 + 갤러리 + prototype 통합)

**Scope**: 사용자가 "음량이 작아서 안 들리는 트랙이 있다, 게임 BGM 같은 느낌으로 보강하고 싶다, 길이도 늘려다" 라고 시작한 후속 세션. 본 세션 동안 **12 트랙 모두 미니맥스 Music 2.6 무료 베타 웹 UI 로 재생성 → 게임 배포용 30초 WAV + 대시보드 감상용 풀 mp3 + (f)/(m) variants → 12개 갤러리 슬롯 모두 active → prototype Python 사운드 모듈 통합 검증** 까지 완료.

**핵심 결정 — 정착된 도구/관행**:

> **"BGM 외부 생성 = API 결제가 아니라 **미니맥스 웹 UI 무료 베타** + **import_minimax_track.sh 자동화** + **갤러리 = 풀 mp3, 게임 = 30초 WAV** 패턴"** (2026-07-11)
>
> wav → mp3 변환 시 75~85 % 디스크 절약. 미니맥스 quota 일 500회이므로 12 트랙 모두 사용자 부담 $0.

## 액션 요약 (BGM v3, 18개)

| # | 액션 | 산출 |
|---|------|------|
| 1 | 미니맥스 웹 UI 생성 (1 트랙당 4-10 회 재생성) | 12 트랙 × (원본 + (f) 또는 (m)) = 24 mp3 |
| 2 | `import_minimax_track.sh` 작성 | BGM 30초 trim + 정규화 + 풀 보관 자동화 |
| 3 | `ffmpeg loudnorm -16 LUFS` 정규화 | 12 BGM -16~18 dBFS |
| 4 | fade in/out + 30초 구간 trim | 게임 배포용 BGM |
| 5 | 풀 mp3 그대로 보관 | 대시보드 갤러리 감상용 |
| 6 | (f)/(m) variants 별도 보관 | 갤러리 한 트랙에 2 variants |
| 7 | `dashboard/sounds/` 폴더 정리 | 옛 `.wav.removed`, 짧은이름 mp3, 중복 정리 |
| 8 | `dashboard/sound.html` 갤러리 갱신 | 12 active 마스터 행 + 12 variant 행 |
| 9 | 갤러리 audio src wav→mp3 일괄 치환 | 24 src 검증 OK |
| 10 | `dashboard/scripts/import_minimax_track.sh` 보관 | 다음 세션 재사용 |
| 11 | `~/Downloads/*.mp3` 24개 삭제 | 154 MB 절약 |
| 12 | `prototype/data/sounds_test/` 에 12 symlink | ThemePlayer 자동 인식 |
| 13 | `prototype/scripts/demo_minimax_bgms.py` 신규 | 12 BGM 검증 CLI |
| 14 | `headless_sound_demo.py` 4 단계 실제 재생 | Prologue → Briefing → Matrix → Combat |
| 15 | `ThemePlayer` 단위 테스트 (afplay) | matrix_rain 3초 재생 성공 |
| 16 | `THEMES` dict 12 키 검증 | 모두 새 BGM 파일 매칭 |
| 17 | Notion 발행 (BGM External Guide) | 12개 프롬프트 가이드 |
| 18 | log.md 6 개 항목 append | 본 세션 작업 전체 기록 |

## 누적 지표 (BGM v3)

| 지표 | 시작 | 최종 | 변화 |
|---|---|---|---|
| `dashboard/sounds/` WAV BGM | 12 (v1 3초, -43~-47 dBFS) | 12 (30초, -16~-18 dBFS) | 길이 +10x, 음량 +25~28 dB |
| `dashboard/sounds/full/` 풀 트랙 | 0 | 24 mp3 | 신규 (12×2 variants) |
| `sound.html` 갤러리 audio controls | 0 | 24 (12 base + 12 variants) | 신규 |
| 미니맥스 생성 트랙 | 0 | 12 (BGM v3 완성) | 신규 |
| `verify_sounds.py` 도구 | ✅ | ✅ | 활용 |
| `audio-doctor.py` 도구 | ✅ | ✅ | 활용 |
| `import_minimax_track.sh` 자동화 | — | ✅ | 신규 |
| `demo_minimax_bgms.py` 검증 | — | ✅ | 신규 |
| 사용 비용 (BGM 12 트랙) | (조건부) | $0 (free beta) | — |

## 파일 형식 표준화

| 용도 | 형식 | 이유 |
|------|------|------|
| 게임 배포 (BGM) | WAV 16-bit 44.1 kHz, 30초 loop, -16 LUFS | uncompressed quality + decode 가능 |
| 대시보드 감상 (풀 트랙) | MP3 256kbps | 디스크 절약 75% (WAV 33-45 MB → MP3 5-8 MB) |
| 갤러리 audio src | `.mp3` 직접 | 브라우저는 두 포맷 모두 지원 |

## 디렉토리 구조

```
dashboard/sounds/                       ← 단일 진실 공급원 (single source of truth)
├── theme_*.wav (12)                    ← 게임 배포용 BGM (WAV)
└── full/                               ← 감상용 풀 mp3 24 (12 base + 12 variants)
    ├── theme_<name>.mp3 (12)           ← 풀 트랙 base
    └── theme_<name>_full_<f|m>.mp3 (12) ← 변형 (fade-out 또는 minor 톤)

prototype/data/sounds_test/             ← symlink (자동 동기화)
└── theme_*.wav (12 symlinks)           ← ThemePlayer 가 자동 인식
```

## 작성/수정 파일 (BGM v3)

- `dashboard/sounds/theme_*.wav` × 12 (3초 v1 → 30초 BGM 교체)
- `dashboard/sounds/full/*.mp3` × 24 (신규 풀 트랙)
- `dashboard/sound.html` (갤러리 12 active 행 + 24 audio)
- `dashboard/scripts/import_minimax_track.sh` (신규 — 다음 세션 재사용)
- `prototype/data/sounds_test/theme_*.wav` × 12 (symlink)
- `prototype/scripts/demo_minimax_bgms.py` (신규)
- `Game/roguelike_sprawl/log.md` (BGM v3 6 개 항목)
- `Game/roguelike_sprawl/SESSION_SUMMARY_2026-07-11.md` (본 문서)
- `docs/notion-reflects/BGM_EXTERNAL_GENERATION_GUIDE_2026-07-11_NOTION_READY.md` (Notion-ready)
- `~/Downloads/*.mp3` × 24 삭제 (154 MB 절약)
- macOS: `switchaudio-osx 1.2.2` (이전 Part 1 에서 설치)

## 검증

| 검증 | 결과 |
|------|------|
| 12 BGM 실제 재생 (afplay) | ✅ matrix_rain 등 |
| 갤러리 24 audio src 모두 파일 존재 | ✅ |
| `headless_sound_demo.py` 4 단계 실제 재생 | ✅ (Prologue → Combat) |
| `THEMES` dict 12 키 매칭 | ✅ |
| Demo verification (silent / 5s / 30s 모드) | ✅ |
| Downloads mp3 모두 제거 | ✅ 154 MB |

## 다음 단계 (BGM v3 완료 후)

- 🟢 Notion 발행: `🎵 BGM v3 Final` 진행 보고서 (이 SESSION_SUMMARY 기반)
- 🟢 외부 생성 가이드 (`bgm-external-generation-guide.md`) 의 "1. 서비스 선택" 섹션에 미니맥스 웹 UI 경로 추가
- 🟢 게임 플레이 세션 (`scripts/play.py`) 로 미니맥스 BGM 12 트랙 실제 게임플레이 검증
- 🟢 다른 게임 (typing_language 등) 의 사운드 자산 검증에 `verify_sounds.py` 활용
- 🔵 macOS 재부팅 후 브라우저 dashboard 사운드 페이지 (Part 1 의 미해결 작업)

