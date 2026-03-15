# Context Repo Conventions

## GitHub 참조 규칙

이 워크스페이스에서 "깃헙", "GitHub", "리모트" 등을 언급하면 `ssuyeonC/context` 레포(`.context/` 디렉토리)를 의미합니다. product 모노레포(`creatrip/product`)와는 별개입니다.

## 스킬 우선 적용 규칙

`.context/agents/skills/` 디렉토리에 정의된 스킬이 유저 요청의 키워드와 매칭되면, **반드시 해당 스킬의 SKILL.md를 먼저 읽고 그 절차를 따라야 합니다.**

| 트리거 키워드 | 스킬 | 설명 |
|-------------|------|------|
| `지라`, `티켓`, `요구사항`, `requirements`, `제안`, `제안서`, `proposal` | `write-doc` | 템플릿 기반 문서(요구사항/제안서) 생성. Jira API 직접 호출 금지, md 파일로 저장 |
| `깃헙에서 가져와`, `context 풀`, `pull context`, `context 동기화` | `pull-context` | GitHub(ssuyeonC/context)에서 최신 .context를 pull하고 심링크 복구 |
| `깃헙에 업데이트`, `깃헙 업데이트`, `context 푸시`, `sync context` | `sync-context` | .context 변경사항을 GitHub(ssuyeonC/context)에 커밋 & 푸시 |
| `/followup` (슬래시 커맨드) | `followup` | 회의록 파일에 추가 논의 내용을 append |
