# ADR-0030: GitHub 활용 계획 (GitHub Utilization Plan)

> **상태**: Draft
> **날짜**: 2026-06-18
> **결정자**: 사용자
> **관련**: `../../../Fiction/`, `typing_language` (참고 프로젝트)

## 1. 컨텍스트

Roguelike Sprawl은 현재 Git 저장소가 아니다 (`.git/` 없음). 로컬 파일만 관리되어:
- 코드 이력 추적 불가
- CI/CD 파이프라인 없음
- 외부 협업 불가
- 대시보드 (`dashboard/`) 호스팅 불가

typing_language 프로젝트는 이미 다음을 구현해 참고할 수 있다:
- GitHub 저장소: `https://github.com/seoca1/typing-language.git`
- GitHub Actions CI (`.github/workflows/deploy.yml`)
- GitHub Pages 자동 배포 (Vite 빌드 → Pages)
- npm scripts: dev, build, test, lint, typecheck

## 2. 목표

Roguelike Sprawl에 다음 역량 추가:

| 목표 | 효과 |
|---|---|
| Git 버전 관리 | 모든 변경 이력 추적, 안전한 롤백 |
| GitHub Actions CI | PR마다 자동 test/lint/typecheck |
| GitHub Pages 호스팅 | 대시보드 5개 (index/story/stages + 상위 허브) 무료 호스팅 |
| Issue/Project 관리 | 작업 추적, 우선순위 |
| Releases/태그 | 버전 마일스톤 (Phase 1-6) |

## 3. 옵션 비교

### Option A: typing_language 미러 (단일 저장소)

| 항목 | 내용 |
|---|---|
| 저장소 | `seoca1/roguelike-sprawl` (1개) |
| CI | `.github/workflows/ci.yml` (test/lint/typecheck) + `deploy.yml` (Pages) |
| Pages | 대시보드 정적 호스팅 (Python 빌드 불필요, 그대로) |
| 장점 | 단순, typing_language과 동일한 패턴 |
| 단점 | 게임 코드 + 위키/디자인 단일 저장소 |

### Option B: 모노레포 (워크스페이스)

| 항목 | 내용 |
|---|---|
| 저장소 | `seoca1/roguelike-sprawl` + `seoca1/roguelike-sprawl-wiki` 등 분리 |
| 장점 | 게임 / 위키 / 디자인 명확히 분리 |
| 단점 | 저장소 여러 개 관리 부담. 위키는 이미 `wiki/` 디렉토리에 있음 |

### Option C: 외부 호스팅 + Git only

| 항목 | 내용 |
|---|---|
| 저장소 | GitHub but Pages 없음, 로컬에서만 대시보드 |
| 장점 | Git 이력만 확보 |
| 단점 | 대시보드 공유 불가, 협업자 dashboard 접근 불가 |

**추천**: **Option A** (typing_language과 동일 패턴, 단순, 효과적)

## 4. 권장안 (Option A) 상세

### 4.1 저장소 구조

```
seoca1/roguelike-sprawl/
├── prototype/             # Python 게임 코드
├── dashboard/             # 대시보드 (정적)
├── design/                # GDD, 결정, 시스템 스펙
├── wiki/                  # 위키
├── raw/                   # 원본 자료 (read-only)
├── testcases/             # 회귀 테스트 케이스
├── decisions/             # ADR
├── AGENTS.md              # AI 가이드
├── README.md              # 프로젝트 소개
├── ROADMAP.md             # 로드맵
├── index.md               # 인덱스
└── log.md                 # 작업 로그
```

### 4.2 GitHub Actions 워크플로우

#### A. CI 워크플로우 (`.github/workflows/ci.yml`)

PR / push마다 자동 실행:
1. `setup-python` v3.11
2. `pip install` 또는 `uv sync --all-extras`
3. `make format` (검증)
4. `make lint` (ruff)
5. `make typecheck` (mypy strict)
6. `make test` (pytest 578 tests)
7. 코드 커버리지 리포트 업로드

#### B. Pages 배포 워크플로우 (`.github/workflows/pages.yml`)

main/master push 시:
1. Checkout
2. Python 정적 검증 (선택)
3. Pages artifact 업로드 (`dashboard/` + JSON 데이터)
4. GitHub Pages 배포

대시보드는 정적 HTML + JSON fetch이므로 Python 빌드 불필요. HTML을 그대로 Pages로 호스팅.

#### C. Issue 자동 라벨링 (`.github/labeler.yml`)

PR/Issue 자동 분류:
- `phase-1` ... `phase-6`
- `prologue` / `event-dialogue` / `stage` / `dashboard`
- `bug` / `enhancement` / `docs`
- `python` / `html` / `json`

### 4.3 Branch 전략

```
main              # 안정. main에 머지 = 자동 Pages 배포
├── develop       # 개발 통합
├── feat/xxx      # 기능 단위
├── fix/xxx       # 버그 수정
└── docs/xxx      # 문서만
```

PR 규칙:
- main 직접 push 금지
- develop → main PR은 사용자 승인 필요
- feat/fix → develop PR은 CI 통과 필요
- Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

### 4.4 GitHub Projects (보드)

3개 보드:

| 보드 | 목적 | 카드 |
|---|---|---|
| **Phase 6+ 작업** | 새 기능 (엔딩 확장, 추가 미션) | 이슈 |
| **버그** | 발견된 결함 | 이슈 |
| **대시보드 작업** | 미구현 대시보드 (Sound, Combat, Cyberspace, Equipment) | 이슈 |

### 4.5 GitHub Releases

Phase 완료마다:
- `v0.1.0` - Phase 1 완료
- `v0.2.0` - Phase 2 완료
- ...
- `v1.0.0` - Phase 6 완료 (정식 출시)

### 4.6 GitHub Wiki

내부 위키는 이미 `wiki/` 디렉토리에 있음. **GitHub Wiki는 비활성화** 권장 (대신 MkDocs 또는 단순 md 호스팅).

## 5. 구현 단계 (Action Plan)

### Phase 0: Git 초기화 (즉시, 5분)

```bash
cd /Users/emilio/projects/Projects/Game/roguelike_sprawl
git init
git add .
git commit -m "feat: initial commit - Roguelike Sprawl Phase 1-5 complete

- 578 unit tests passing
- Story system: 3 protagonists, 2 endings, 14 dialogues
- Stage system: 6 stages, 3 missions, death flow
- 3-tier dashboard (hub/sub/sub-sub)
- Python 3.11+ tcod roguelike engine"
```

### Phase 1: GitHub 저장소 생성 (10분)

1. https://github.com/new 접속
2. Repository name: `roguelike-sprawl`
3. Description: "🌆 깁슨 스프롤 3부작 기반 로그라이크 · Python + tcod"
4. Public / Private 선택
5. **README, .gitignore, license 모두 추가 안 함** (이미 있음)
6. `git remote add origin https://github.com/seoca1/roguelike-sprawl.git`
7. `git push -u origin main`

### Phase 2: CI 워크플로우 (15분)

`.github/workflows/ci.yml` 작성:
- Python 3.11 matrix
- uv 설치
- `make all` (format + lint + typecheck + test)
- PR 코멘트로 결과 표시

### Phase 3: Pages 배포 (10분)

`.github/workflows/pages.yml` 작성:
- `actions/deploy-pages@v4`
- `dashboard/` + `design/**/​*.json` 아티팩트
- 환경: `github-pages`

Settings → Pages → Source: GitHub Actions

### Phase 4: Issue 템플릿 + 라벨 (5분)

`.github/ISSUE_TEMPLATE/`:
- `bug.md` - 버그 리포트
- `feature.md` - 새 기능 요청
- `dashboard.md` - 대시보드 추가 요청

라벨 12개 (자동 적용):
- phase-1..6, prologue/event/stage/dashboard, bug/enhancement/docs

### Phase 5: Projects 보드 (5분)

GitHub Projects 생성:
- 컬럼: Backlog / In Progress / Review / Done
- 이슈를 카드로 변환

### Phase 6: Releases (선택)

`v0.5.0` 태그 생성 (현재 상태):
```bash
git tag -a v0.5.0 -m "Phase 1-5 complete: prologue + 3-tier dashboard"
git push origin v0.5.0
```

GitHub → Releases → Draft new release

## 6. 결과 (Consequences)

### 긍정적
- ✅ 코드 이력 영구 보존
- ✅ PR마다 자동 CI (test/lint/typecheck 보장)
- ✅ 대시보드 무료 호스팅 (https://seoca1.github.io/roguelike-sprawl/)
- ✅ 외부 협업자/관찰자 접근 가능
- ✅ typing_language와 일관된 워크플로우

### 부정적
- ❌ GitHub 계정/저장소 관리 부담 (typing_language 동일)
- ❌ Public 시 코드 공개 (의도된 경우 OK)
- ❌ Pages는 정적만 (대화형 게임은 별도 호스팅 필요)

### 중립
- typing_language와 동일 패턴 → 학습 비용 0

## 7. 열린 질문 (Open Questions)

1. **저장소 이름**: `roguelike-sprawl` vs `roguelike_sprawl` vs `sprawl-jockey`?
2. **공개 범위**: Public (깁슨 톤 자키 커뮤니티 공개) vs Private (개인 작업)?
3. **라이선스**: MIT vs Apache 2.0 vs 비공개?
4. **대시보드 호스팅**: GitHub Pages vs Netlify vs Vercel?
5. **Wiki 도구**: GitHub Wiki vs MkDocs vs Obsidian Publish?

## 8. 열린 결정 사항

- [ ] 저장소 이름 확정
- [ ] 공개/비공개 결정
- [ ] 라이선스 결정
- [ ] GitHub 계정 상태 확인 (typing_language는 seoca1, 동일 계정 사용?)

## 9. 참고

- `typing_language/GITHUB_SETUP_GUIDE.md` - 14KB 상세 가이드
- `typing_language/.github/workflows/deploy.yml` - Pages 배포 참고
- GitHub 공식 문서: https://docs.github.com/

## 10. 다음 단계

사용자 결정 후:
1. 저장소 이름/공개 범위/라이선스 확정
2. `git init` + 첫 commit
3. GitHub 저장소 생성
4. CI/Pages 워크플로우 추가
5. 첫 release (v0.5.0)
