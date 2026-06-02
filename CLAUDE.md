# Context Repo Conventions

## GitHub 참조 규칙

이 워크스페이스에서 "깃헙", "GitHub", "리모트" 등을 언급하면 `ssuyeonC/context` 레포(`.context/` 디렉토리)를 의미합니다. product 모노레포(`creatrip/product`)와는 별개입니다.

## 스킬 우선 적용 규칙

`.context/agents/skills/` 디렉토리에 정의된 스킬이 유저 요청의 키워드와 매칭되면, **반드시 해당 스킬의 SKILL.md를 먼저 읽고 그 절차를 따라야 합니다.**

| 트리거 키워드 | 스킬 | 설명 |
|-------------|------|------|
| `지라`, `티켓`, `요구사항`, `requirements`, `제안`, `제안서`, `proposal` | `write-doc` | 템플릿 기반 문서(요구사항/제안서) 생성. Jira API 직접 호출 금지, md 파일로 저장. **제안서일 경우 `.context/templates/planning-frame.md`의 Q1·Q2 자문을 반드시 포함.** |
| `깃헙에서 가져와`, `context 풀`, `pull context`, `context 동기화` | `pull-context` | GitHub(ssuyeonC/context)에서 최신 .context를 pull하고 심링크 복구 |
| `깃헙에 업데이트`, `깃헙 업데이트`, `context 푸시`, `sync context` | `sync-context` | .context 변경사항을 GitHub(ssuyeonC/context)에 커밋 & 푸시 |
| `/followup` (슬래시 커맨드) | `followup` | 회의록 파일에 추가 논의 내용을 append |

## Avatar 볼트 연동 (요약본 떨구기)

업무 산출물(outputs/)을 개인 Avatar 볼트로 넘길 때, **요약·정리는 이 세션(회사 계정)에서 수행**하고 결과물만 볼트에 쓴다. (개인 계정 토큰 절약 — 무거운 읽기는 여기서 끝낸다.)

### 대상 경로
- Avatar 볼트 루트: `/Users/suyeon/Library/Mobile Documents/iCloud~md~obsidian/Documents/Avatar`
- 출력 위치: `{볼트}/raw/career/` (크리에이트립 업무 자료 전용)

### 트리거
사용자가 "이거 Avatar에 정리해줘" / "raw로 떨궈줘"라고 특정 산출물(프로젝트·주제 단위)을 지정할 때.

### 동작
1. 지정된 outputs/ 자료(jira·meetings·proposals·reports·research 등)를 **이 세션에서 읽고** 핵심만 추린다.
2. 볼트에 요약본 1개 생성:
   - 파일명: `{YYYY-MM-DD}_{slug}.md` (날짜 = 수집일, slug = 영문 kebab 주제)
   - 형식 (기존 raw/career 문서와 통일):
     ```
     # {프로젝트/주제} — 원본 자료

     수집일: {YYYY-MM-DD}
     출처: outputs/{원본 경로들}

     ---

     ## 1. 배경·문제
     ## 2. 기획/스펙 핵심
     ## 3. 데이터·임팩트 (수치는 구체값으로)
     ## 4. 의사결정·후속
     ```
   - 길이: 원본을 다 옮기지 말고 **의사결정·수치·임팩트 중심으로 압축.** 표·핵심 지표는 보존.

### 경계 (중요)
- **`raw/career/`에만 쓴다.** `wiki/`, `index.md`, `log.md`는 **건드리지 않는다** — 그건 Avatar(개인) 세션이 볼트 전체 맥락을 보며 ingest·cross-link·index 갱신을 담당한다.
- 볼트의 다른 기존 파일을 수정·삭제하지 않는다. 신규 요약본 생성 또는 같은 슬러그의 기존 요약본에 append만 허용.
- **같은 슬러그의 기존 요약본이 있을 때**: 덮어쓰지 말고 해당 파일 하단에 `## {YYYY-MM-DD} 추가 — {원본 경로}` 섹션을 append한다. 단, 동일 원본이 이미 출처 라인에 명시되어 있으면 스킵하고 사용자에게 알린다. **파일명 날짜는 최초 생성일 그대로 유지.**
- 슬러그 기준으로 매칭한다(파일명 `{YYYY-MM-DD}_{slug}.md` 중 `{slug}` 부분). 같은 슬러그 파일이 여러 날짜로 존재하면 가장 최신 파일에 append.
