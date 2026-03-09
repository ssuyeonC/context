---
name: pull-context
description: GitHub(ssuyeonC/context)에서 최신 .context를 가져오고 심링크 복구
---

# Pull Context

`https://github.com/ssuyeonC/context`에서 최신 내용을 가져와 로컬 `.context`에 반영합니다.

## 트리거

다음 키워드가 포함된 요청 시 실행:
- `깃헙에서 가져와`, `깃헙 가져와`, `context 풀`, `pull context`, `context 동기화`

## 실행 단계

### Step 1: Pull

```bash
cd .context && git pull origin main
```

- 충돌이 없으면 Step 2로 진행
- 충돌이 있으면 충돌 파일 목록을 유저에게 보여주고, 해결 방법을 확인받은 후 진행

### Step 2: 심링크 복구

`.context/agents/skills/` 내의 모든 스킬 디렉토리에 대해, `.agents/skills/`에 심링크가 없으면 생성합니다.

```bash
for skill_dir in .context/agents/skills/*/; do
  skill_name=$(basename "$skill_dir")
  if [ ! -L ".agents/skills/$skill_name" ]; then
    ln -s "../../.context/agents/skills/$skill_name" ".agents/skills/$skill_name"
  fi
done
```

새로 생성된 심링크가 있으면 `.gitignore`에도 추가합니다.

```
# Personal skill symlinks (source in .context/agents/skills/)
.agents/skills/{skill_name}
```

### Step 3: 변경 내역 요약

pull로 가져온 변경사항을 유저에게 보여줍니다.

```
가져온 변경사항:
- (A) agents/skills/new-skill/SKILL.md
- (M) outputs/jira/requirements_xxx.md
- ...

복구된 심링크:
- .agents/skills/new-skill → .context/agents/skills/new-skill
```

변경사항이 없으면 "이미 최신 상태입니다"를 알리고 종료합니다.

### Step 4: 완료 보고

```
✓ .context가 최신 상태로 동기화되었습니다.
```

## 규칙

- 로컬에 커밋되지 않은 변경사항이 있으면 pull 전에 유저에게 알리고 처리 방법을 확인합니다.
- 충돌 시 자동 해결하지 않고, 유저에게 확인 후 진행합니다.
- 심링크 복구 시 기존 심링크가 이미 있으면 덮어쓰지 않습니다.
