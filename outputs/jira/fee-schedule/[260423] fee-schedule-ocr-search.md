# 세부 기획안 요구사항 문서

## 배경

### 문제 정의

- 어드민의 스팟 상세 페이지에는 이미 수가표(시술 가격표) 이미지를 업로드하는 기능이 존재하며, 업로드된 이미지는 유저 페이지(`SpotDetailFeeScheduleSection`)에 그대로 노출되고 있다.
- 수가표 이미지는 `spot_trans_fee_schedule` 테이블에 **언어별로 분리** 저장된다(컬럼: `image_pathname`, `title`, `description`, `priority`). 즉 특정 스팟의 영어 페이지/대만어 페이지 등에 각각 다른 수가표가 올라갈 수 있으며, 일반적으로 한두 개 언어에만 존재한다.
- 수가표가 **이미지 형태**로만 저장되어 있어 이미지 내부의 시술명·카테고리·가격 텍스트가 OpenSearch 인덱스에 포함되지 않는다.
- 그 결과 유저가 시술 키워드(예: "Ultherapy", "Botox")로 검색해도 수가표에만 해당 정보가 있는 스팟은 검색 결과에 노출되지 않아 검색 커버리지에 사각지대가 발생한다.
- 기존 "K뷰티 시술 관리" 데이터는 스팟 자체에 귀속되며 생성 시 모든 언어 번역값이 입력되는 구조인 반면, 수가표는 스팟 번역(`spot_translation`)에 귀속되어 업로드된 언어에만 존재한다. 두 데이터는 언어 커버리지 특성이 다르다.

### 가설적 임팩트

- 수가표 텍스트를 검색 인덱스에 포함시키면, 기존에 "K뷰티 시술 관리" 값이 입력되지 않은 스팟도 시술 키워드 검색에 노출될 수 있다.
- 특히 "K뷰티 시술 관리"의 커버리지가 낮은 병·의원 스팟에서 검색 가능성 확대 효과가 크다.
- 유저 관점에서 "원하는 시술을 제공하는 스팟을 찾지 못해 이탈"하는 경로를 차단 → 상담/예약 전환 기회 확보.
- 수치화된 임팩트 추정: {미정 — 수가표 업로드된 스팟 수, 검색 미노출로 인한 이탈률 파악 필요}

## 구현

### 유저 플로우

**어드민 (스팟 담당자)**

1. 어드민의 특정 스팟 상세 페이지에서 수가표 이미지를 **언어별로** 업로드한다. (기존 기능 그대로 유지)
2. 업로드된 수가표 이미지에 대해 **"수가표 가격 반영(가제)"** 버튼이 노출된다.
3. 관리자가 "수가표 가격 반영" 버튼을 클릭하면, OCR 엔진이 해당 언어 수가표 이미지의 텍스트를 추출하고 위계에 맞게 구조화(트리 형태)한다.
4. 추출 결과가 **트리 검수 UI**로 표시된다. 관리자는 다음을 확인/수정할 수 있다.
   - 시술명·카테고리 라벨 텍스트가 정확한지
   - 위계(카테고리 > 패키지 > 세부 항목)가 올바른지
   - 가격이 올바른 숫자로 추출되었는지
5. 관리자가 "저장"을 클릭하면 해당 구조가 해당 언어의 `spot_trans_fee_schedule` 레코드에 저장되고, 검색 인덱스의 해당 언어 필드에 반영된다.
6. "재추출" 버튼으로 OCR을 다시 실행할 수 있다. (기존 저장 값은 재추출 시 덮어쓴다)
7. "수가표 OCR 값 제거" 액션으로 특정 언어의 추출 값을 삭제할 수 있다.

**유저 (일반 이용자)**

- 유저 페이지 노출은 **기존과 동일** — 수가표 이미지 원본이 그대로 노출된다. 추출된 텍스트는 유저 페이지에 직접 표시되지 않는다.
- 시술 키워드 검색 시 기존 검색 결과 모달 UI(`{시술명} products total {n} items` + 이름/가격 리스트)에 매칭된 시술 아이템이 노출된다. 소스는 언어별 우선순위 규칙에 따른다(아래 참조).

### 데이터 공존 및 언어별 노출 우선순위

- 한 스팟은 **K뷰티 시술 관리 데이터와 수가표 OCR 데이터를 동시에 보유할 수 있다.** 배타 제약 없음.
- 검색/모달 노출은 **언어 단위로 독립 판정**한다. 한 스팟이 언어마다 서로 다른 소스로 노출될 수 있다.
- 우선순위 규칙:

```
for each language L of 스팟 S:
  if (S의 spot_trans_fee_schedule[L].ocr_structure 존재) {
    L의 검색 매칭 / 모달 아이템 소스 = 해당 언어 OCR 데이터
  } else if (S에 SpotBeautyOption 존재) {
    L의 검색 매칭 / 모달 아이템 소스 = K뷰티 시술 관리 (L 번역값)
  } else {
    L에서 시술 검색에 미노출
  }
```

**예시 시나리오**

스팟 A가 다음을 모두 보유한 상태:
- K뷰티 시술 관리: `Rejuran - 1HB` / 100,000 KRW (모든 언어 번역값 존재)
- 영어 수가표 OCR: `Rejuran Premium` / 200,000 KRW
- 대만어 수가표 OCR: `Rejuran Premium` / 200,000 KRW
- 일본어 수가표 OCR: 없음

| 검색 언어 | 노출 소스 | 모달 아이템 |
|---|---|---|
| 영어 "Rejuran" | 영어 OCR | `Rejuran Premium` / 200,000 |
| 대만어 "Rejuran" | 대만어 OCR | `Rejuran Premium` / 200,000 |
| 일본어 "Rejuran" | K뷰티 시술 관리 | `Rejuran - 1HB` / 100,000 |

**이 설계가 의도하는 것**

- **수가표 = 해당 언어에서 병원이 제공한 가장 최신·공식 가격**이므로 OCR이 있는 언어에서는 OCR 우선.
- **K뷰티 시술 관리 = 글로벌 fallback** 역할. 수가표가 없는 언어의 검색 커버리지를 보장.
- 운영 관점에서 배타·중복 제거 로직 불필요 — 한 언어당 단일 소스가 자동 결정됨.

### 프론트엔드 요구사항

**어드민**

- 기존 `SpotFeeScheduleImageSection`(`frontend/apps/admin/src/components/spot/SpotBasicInfo/feeScheduleImage/`) 및 언어별 탭 `SpotFeeScheduleTab`에 **"수가표 가격 반영(가제)"** 액션 추가.
  - 이미지가 업로드되어 있을 때만 활성화
  - 클릭 시 OCR 실행 → 검수 모달 오픈
- "수가표 OCR 값 제거" 액션 추가 (언어별 삭제).
- **수가표 검수 모달** (신규)
  - 좌측: 업로드된 수가표 이미지 미리보기
  - 우측: 추출된 트리 구조 편집기
    - 노드 텍스트 인라인 수정
    - 노드 추가/삭제/드래그 이동 (위계 재배치)
    - 각 리프 노드의 `priceKrw` 단일 필드 편집 (할인가든 단일가든 최종 노출가 하나만 저장)
    - `rawText`(OCR 원문) 보조 뷰 토글
  - 하단: "재추출", "저장", "취소" 버튼
- **안내 문구** (어드민 수가표 영역)
  - "수가표 OCR 값을 저장한 언어에서는 해당 언어의 검색·모달 노출이 K뷰티 시술 관리 대신 수가표 기준으로 동작합니다. 주요 시술이 수가표에서 누락되지 않도록 검수 시 확인해주세요."

**유저 웹**

- 변경 없음. 수가표 섹션(`SpotDetailFeeScheduleSection`)은 원본 이미지 노출 방식 유지.
- 시술 키워드 검색 결과 모달 UI도 기존 구조 유지. OCR 데이터는 백엔드 인덱싱 병합으로 자동 반영된다.

### 백엔드 요구사항

**데이터베이스 스키마**

- `spot_trans_fee_schedule` 테이블에 컬럼 추가:
  - `ocr_structure jsonb NULL` — OCR로 추출·검수된 트리 구조
  - `ocr_extracted_at timestamp NULL` — 마지막 OCR 실행 시각
- 트리 구조 스키마 (재귀 트리, 가격 필드 단일화):

```json
{
  "nodes": [
    {
      "label": "Lifting",
      "children": [
        { "label": "Ultherapy Prime 300 shots", "priceKrw": 1700000 },
        {
          "label": "Lifting BASIC",
          "children": [
            {
              "label": "Titanium Encore 3D 40KJ + XERF 100 shots + Repair Light",
              "priceKrw": 850000
            }
          ]
        }
      ]
    }
  ],
  "rawText": "<OCR 원문 전체>"
}
```

- 모든 필드 optional. `children` 재귀 구조로 임의 depth 수용(수가표 양식 다양성 대응).
- **가격 필드는 `priceKrw` 하나만 저장**. 원가·할인가가 병기된 수가표에서는 **할인가(최종 노출가)**를 저장. 가격이 하나만 있는 수가표에서는 그 숫자를 그대로 `priceKrw`로 저장.
- `rawText`는 파싱 실패 시 검색 fallback 및 원본 보관.

**언어 종속성 (확정)**

| 데이터 | 종속 | 검색 매칭 범위 |
|---|---|---|
| 수가표 OCR | `spot_translation` 언어별 레코드 | 업로드·저장된 언어의 검색에서만 매칭 (의도된 동작) |
| K뷰티 시술 관리 | 스팟 자체(모든 언어 번역값) | OCR이 저장되지 않은 언어에서 fallback으로 매칭 |

- 대만어 수가표 OCR 값 → 영어 검색 미노출은 **정상 동작**. 대신 영어는 K뷰티 시술 관리로 매칭됨(존재 시).
- 같은 언어 내 부분 매칭(예: 영어 "Ulthera" → "Ultherapy")은 본 기능 범위 밖이며, 시술 검색 전반의 analyzer/동의어 정책에 위임한다.

**OCR 처리**

- OCR 엔진 호출 → 트리 파싱 → JSON 변환을 담당하는 usecase 신규 추가.
- OCR 응답 지연 대비 비동기 처리 또는 로딩 UI 필요.
- OCR 실패/부분 실패 시에도 `rawText`는 저장하여 검색 fallback을 보장한다.
- 재실행 시 기존 `ocr_structure` 덮어쓰기.

**검색 인덱싱 (언어별 독립 판정)**

- OpenSearch 스팟 인덱스는 **단일 인덱스 + 언어별 필드** 구조(`en.beautyProcedures`, `zh-TW.beautyProcedures`, `jp.beautyProcedures` …).
- 스팟 문서 빌드 시 각 언어 필드를 다음 규칙으로 채운다:

```
for each language L:
  if (spot_trans_fee_schedule[L].ocr_structure 존재) {
    {L}.beautyProcedures = [L의 OCR 리프 노드 라벨 전체]
  } else if (SpotBeautyOption 존재) {
    {L}.beautyProcedures = [K뷰티 시술 관리의 L 번역값]
  } else {
    {L}.beautyProcedures = []
  }
```

- 검색 쿼리 코드(`backend/apps/search/src/modules/opensearch-client/opensearch-client.service.ts`)는 수정 불필요 — 기존 `{language}.beautyProcedures` 필드를 그대로 재사용한다.
- **Reindex 트리거**
  - 특정 언어의 `ocr_structure` 추가/수정/제거 → 해당 언어 필드만 재빌드
  - `SpotBeautyOption` 추가/수정/제거 → OCR이 없는 모든 언어 필드 재빌드
- Analyzer/부분 매칭 품질은 기존 시술 검색 정책을 그대로 따른다.

**검색 응답 페이로드 (모달 아이템 구조)**

- 검색 결과 모달은 `{시술명 + 가격}` 리스트를 렌더링하므로, `SearchedSpot.items` (또는 동등한 필드)가 두 소스를 공통 스키마로 담을 수 있어야 한다.
  - K뷰티 시술 관리 기반: `SpotBeautyOption.priceKrw` 사용
  - OCR 기반: 해당 언어 `ocr_structure`의 리프 노드 `priceKrw` 사용
- 언어 우선순위 규칙에 따라 검색 응답 생성 시 소스를 하나만 선택해 아이템 리스트를 구성한다.
- 구체적인 필드 매핑은 현재 `SearchedSpot.items` 스키마 확인 후 정의한다. {현재 페이로드 구조 조사 필요}

**GraphQL API**

- Mutation: `extractFeeScheduleOcr(feeScheduleId)` — OCR 실행, 추출 결과 반환(저장 X, 검수용).
- Mutation: `saveFeeScheduleOcrStructure(feeScheduleId, structure)` — 관리자 검수 완료 후 저장.
- Mutation: `removeFeeScheduleOcrStructure(feeScheduleId)` — 특정 언어 OCR 값 제거.
- K뷰티 시술 관리 mutation에 **배타 검증 추가 없음** (공존 허용).
- Query: 어드민 스팟 상세 응답에 언어별 `ocrStructure`, 스팟 단위 `hasBeautyOption` 필드 포함.

**영향 범위**

- `spot.repo` / `spot-trans-fee-schedule.entity.ts` / `spot-trans-fee-schedule.resolver.ts`
- 스팟 문서 빌드/인덱싱 파이프라인 (외부 Lambda 등): 언어별 우선순위 로직 추가
- OpenSearch 검색 쿼리 코드: **변경 없음**
- 검색 응답(`SearchedSpot`) 페이로드 빌더: 언어별 소스 선택 및 아이템 리스트 구성
- 어드민 `SpotFeeScheduleImageSection` / `SpotFeeScheduleTab` / 신규 검수 모달 / 안내 문구
- 유저 웹: **변경 없음**
