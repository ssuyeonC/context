---
name: write-doc
description: 템플릿 기반 문서 생성 - 지라 티켓(요구사항) 또는 제안서를 템플릿에 맞춰 작성하고 지정 경로에 저장
---

# Write Doc

템플릿을 기반으로 문서를 생성합니다.

## 문서 타입

| 타입 | 트리거 키워드 | 템플릿 | 저장 경로 | 파일명 패턴 |
|------|-------------|--------|----------|------------|
| 요구사항 (지라 티켓) | `지라`, `티켓`, `요구사항`, `requirements` | `.context/templates/requirements-template.md` | `.context/outputs/jira/` | `requirements_{slug}.md` |
| 제안서 | `제안`, `제안서`, `proposal` | `.context/templates/proposal-template.md` | `.context/outputs/proposals/` | `proposal_{slug}.md` |

## 실행 단계

### Step 1: 타입 판별

유저의 요청에서 문서 타입을 판별합니다.

- 키워드가 명확하면 바로 진행
- 모호하면 AskUserQuestion으로 타입을 확인:

```json
{
  "questions": [{
    "question": "어떤 문서를 작성할까요?",
    "options": ["요구사항 (지라 티켓)", "제안서"]
  }]
}
```

### Step 2: 템플릿 읽기

해당 타입의 템플릿 파일을 Read 도구로 읽습니다.

- 요구사항: `.context/templates/requirements-template.md`
- 제안서: `.context/templates/proposal-template.md`
  - **제안서일 때는 `.context/templates/planning-frame.md`도 반드시 함께 읽습니다.**
  - 이 프레임의 핵심 자문(Q1·Q2)은 제안서 필수 섹션이며, 빈 값으로 저장하지 않습니다.

템플릿의 **양식 섹션**(예시 위의 `---` 이전)을 문서 구조로 사용합니다.
템플릿의 **예시 섹션**(`---` 이후)은 작성 시 참고하되 출력물에 포함하지 않습니다.

### Step 3: 정보 수집

유저가 제공한 정보를 템플릿 섹션에 매핑합니다.

**제안서의 경우 필수**: Q1(수단의 필연성)·Q2(타깃 정합성)·Q3(베이스라인 증분)에 대한 답이 명시적으로 제공되지 않았으면, AskUserQuestion으로 **반드시** 물어서 수집합니다. Q3는 지표·자연 수준·증분 가설 세 필드를 모두 채워야 합니다. 유추해서 채우지 않습니다.

- 유저가 충분한 정보를 제공했으면 바로 문서 작성
- 정보가 부족하면 AskUserQuestion으로 핵심 정보를 수집:

```json
{
  "questions": [{
    "question": "다음 정보를 추가로 알려주세요: {부족한 섹션 목록}",
    "options": ["직접 입력할게", "있는 정보만으로 작성해줘"]
  }]
}
```

### Step 4: Slug 생성 및 문서 작성

1. **Slug 생성**: 문서 제목/주제에서 영문 kebab-case slug를 자동 생성
   - 예: "파트너 리뷰 답글" → `partner-review-reply`
   - 예: "럭키드로우 교차 탐색" → `lucky-draw-cross-exploration`
   - 한국어는 의미를 영어로 번역하여 slug 생성

2. **파일명 결정**: `{타입접두사}_{slug}.md`
   - 요구사항: `requirements_{slug}.md`
   - 제안서: `proposal_{slug}.md`

3. **문서 작성**: 템플릿 양식에 맞춰 내용을 채워 Write 도구로 저장
   - 요구사항 → `.context/outputs/jira/requirements_{slug}.md`
   - 제안서 → `.context/outputs/proposals/proposal_{slug}.md`

### Step 5: 완료 보고

생성된 파일 경로를 유저에게 알려줍니다.

```
문서가 생성되었습니다: .context/outputs/jira/requirements_{slug}.md
```

## 규칙

- 템플릿 양식을 벗어나는 섹션을 임의로 추가하지 않습니다.
- 예시 섹션의 톤과 깊이를 참고하여 실제 내용을 작성합니다.
- 유저가 제공하지 않은 정보는 `{미정}` 또는 `TBD`로 표시합니다.
- 기존 파일과 slug가 겹치면 유저에게 확인 후 덮어쓰거나 slug를 변경합니다.
