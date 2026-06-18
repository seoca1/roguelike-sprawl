# raw/ - 원본 자료

이 디렉토리는 **읽기 전용**이다. AI 에이전트와 사용자는 절대 수정하지 않는다.

원본 자료의 무결성 유지가 LLM Wiki 패턴의 핵심이다.

## 디렉토리 구조 (예정)

```
raw/
├── README.md
├── sprawl_trilogy/         # 윌리엄 깁슨 스프롤 3부작
│   ├── neuromancer.txt
│   ├── count_zero.txt
│   └── mona_lisa_overdrive.txt
├── references/             # 다른 사이버펑크 레퍼런스 (선택적)
│   └── cyberpunk_1988_tonality_notes.md
└── assets/                 # 레퍼런스 이미지, 사운드 (선택적)
```

## 추가 규칙

- 텍스트 파일은 UTF-8, LF 줄바꿈
- 발췌 시 출처 명시 (예: `neuromancer_ch01.txt`)
- 라이선스 확인 (대부분 fair use 가능)
- 원본 그대로 유지 (주석, 마크다운 변환 X)
- 변형 / 발췌본은 `wiki/` 또는 `design/`에 작성

## 라이선스 / 저작권

- 깁슨 소설: fair use (교육, 분석 목적)
- 다른 자료: 각 자료의 라이선스 확인
- 의문 시 추가하지 말 것
