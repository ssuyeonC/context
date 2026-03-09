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

### Step 2: 변경 내역 요약

`git status`와 `git diff`를 분석하여 변경된 파일 목록을 유저에게 보여줍니다.

```
변경된 파일:
- (M) outputs/jira/requirements_xxx.md
- (A) outputs/proposals/proposal_yyy.md
- ...
```

### Step 3: 커밋 & 푸시

1. 모든 변경사항을 스테이징: `git add -A`
2. 변경 내용을 요약하여 커밋 메시지 작성
   - 형식: `docs: {변경 요약}`
   - 예: `docs: 파트너 리뷰 답글 요구사항 추가`
3. 커밋 실행: `git commit -m "{메시지}"`
4. 푸시 실행: `git push origin main`

### Step 4: 완료 보고

```
✓ .context가 GitHub에 반영되었습니다.
  커밋: {커밋 해시} - {커밋 메시지}
```

## 규칙

- `.DS_Store` 파일은 커밋하지 않습니다. `.context/.gitignore`에 없으면 추가합니다.
- 푸시 실패 시 에러 내용을 유저에게 보여주고, 강제 푸시는 유저 확인 없이 실행하지 않습니다.
- 커밋 메시지는 한국어로 작성합니다.
