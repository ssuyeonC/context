---
name: sync-context
description: .context 폴더를 GitHub(ssuyeonC/context)에 커밋 & 푸시
---

# Sync Context

`.context` 폴더의 변경사항을 `https://github.com/ssuyeonC/context`에 반영합니다.

## 구조

개인 스킬과 문서는 `.context` 내부에서 관리하며, `.agents/skills/`에서 심링크로 연결합니다.

```
.context/                          ← ssuyeonC/context repo
├── agents/skills/                 ← 개인 스킬 (원본)
│   ├── write-doc/SKILL.md
│   └── sync-context/SKILL.md
├── templates/                     ← 문서 템플릿
├── outputs/                       ← 생성된 문서
└── work/                          ← 워크스페이스 상태

.agents/skills/
├── write-doc -> ../../.context/agents/skills/write-doc     ← 심링크
└── sync-context -> ../../.context/agents/skills/sync-context ← 심링크
```

## 트리거

다음 키워드가 포함된 요청 시 실행:
- `깃헙에 업데이트`, `깃헙 업데이트`, `context 푸시`, `context 업데이트`, `sync context`

## 실행 단계

### Step 1: 변경사항 확인

```bash
cd .context && git status
```

- 변경사항이 없으면 "변경사항이 없습니다"를 알리고 종료
- 변경사항이 있으면 Step 2로 진행

### Step 2: 변경 내역 요약 (파일 목록 + 세부 내용)

`git status`와 `git diff`를 분석하여 변경된 파일 목록을 유저에게 보여줍니다.

```
변경된 파일:
- (M) outputs/jira/requirements_xxx.md
- (A) outputs/proposals/proposal_yyy.md
- ...
```

**파일 목록만 보고 끝내지 않는다.** 각 수정(M) 파일에 대해 `git diff`로 라인 단위 내용 변경을 확인하고, 무엇이 어떻게 바뀌었는지(추가/삭제/수정된 핵심 내용)를 요약해 유저에게 함께 보여준다. 신규(A) 파일은 어떤 문서인지 한 줄 요약. 의도치 않은 변경(오타·실수 편집·`.DS_Store` 등)이 섞여 있으면 커밋 전에 짚어준다.

```bash
git diff --stat        # 파일별 변경 규모
git diff               # 라인 단위 내용 (핵심만 추려 요약)
```

### Step 3: 커밋 & 푸시 (현재 브랜치)

1. 모든 변경사항을 스테이징: `git add -A`
2. 변경 내용을 요약하여 커밋 메시지 작성
   - 형식: `docs: {변경 요약}`
   - 예: `docs: 파트너 리뷰 답글 요구사항 추가`
3. 커밋 실행: `git commit -m "{메시지}"`
4. 현재 브랜치로 푸시: `git push origin HEAD`

### Step 4: main 브랜치로 머지 & 푸시

현재 브랜치가 이미 `main`이면 Step 4를 건너뜁니다.

> **주의**: Conductor 워크스페이스 환경에서는 `main`이 다른 워크트리(예: `/Users/suyeon/conductor/repos/context`)에 체크아웃되어 있어 이 워크스페이스에서 `git checkout main`이 실패합니다. 따라서 로컬 체크아웃 없이 원격에 직접 fast-forward 푸시하는 방식으로 진행합니다.

1. 원격 main 최신 상태 가져오기: `git fetch origin main`
2. 분기 상태 확인: `git merge-base --is-ancestor origin/main HEAD`
   - **참(0)**: HEAD가 origin/main을 모두 포함 → Step 4로 바로 진행
   - **거짓(1)**: origin/main에 HEAD에 없는 커밋이 있음 (예: GitHub UI에서 이전 PR이 머지된 경우) → 현재 브랜치에 `git merge origin/main --no-edit`로 먼저 머지. 충돌 시 사용자에게 보고하고 자동 진행 중단.
3. 현재 브랜치 푸시 (분기 머지본 반영): `git push origin HEAD`
4. main으로 fast-forward 푸시: `git push origin HEAD:main`
   - 실패 시 (rejected non-FF) 사용자에게 상황을 보고. 임의로 force-push 하지 않습니다.

> 작업 브랜치(워크스페이스 브랜치)는 삭제하지 않습니다. Conductor 워크스페이스가 해당 브랜치에 묶여 있어 계속 사용해야 합니다.

### Step 5: 푸시 후 내용 검증 (세부 내용까지)

푸시·머지가 "성공"으로 떠도, 리모트에 로컬 내용이 글자 단위로 그대로 올라갔는지 확인한다. git은 내용 기반 해시라 아래 diff가 비어 있으면 리모트 == 로컬이 보장된다.

```bash
git fetch origin main
git diff --stat HEAD origin/main      # 비어 있어야 함 (= 본문까지 완전 동일)
```

- diff가 비어 있음 → 세부 내용까지 리모트에 정확히 반영됨. Step 6으로.
- diff가 남아 있음 → 푸시가 일부만 반영됐거나 머지 누락. 차이 파일을 유저에게 보여주고 원인 파악 후 진행. 임의로 force-push 하지 않는다.

### Step 6: 완료 보고

```
✓ .context가 GitHub에 반영되었습니다.
  커밋: {커밋 해시} - {커밋 메시지}
  머지: {원래 브랜치} → main (fast-forward)
  내용 검증: origin/main == 로컬 HEAD (diff 없음, 본문까지 일치)
```

## 규칙

- `.DS_Store` 파일은 커밋하지 않습니다. `.context/.gitignore`에 없으면 추가합니다.
- 푸시·머지 실패 시 에러 내용을 유저에게 보여주고, 강제 푸시·rebase는 유저 확인 없이 실행하지 않습니다.
- 커밋 메시지는 한국어로 작성합니다.
- 작업 브랜치(워크스페이스 브랜치)는 머지 후에도 삭제하지 않습니다.
