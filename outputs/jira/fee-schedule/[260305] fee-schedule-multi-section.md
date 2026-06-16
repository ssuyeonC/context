# 수가표 다중 섹션 구조 개선

## 배경

### 문제 정의

현재 수가표는 SpotTrans(스팟 번역)당 **단일 이미지 1장**만 저장할 수 있는 구조(`feeScheduleImagePathname`)로, 이벤트별/기간별로 구분된 수가표를 표현할 수 없다.

뷰티 스팟의 경우 시술 가격이 이벤트나 기간에 따라 달라지므로, 여러 개의 수가표를 제목/설명과 함께 제공해야 유저에게 명확한 가격 정보를 전달할 수 있다.

### 가설적 임팩트

- 수가표 정보의 구조화를 통해 유저의 가격 정보 파악이 용이해지고, 예약 전환율 개선 기대
- 운영팀이 이벤트별 수가표를 유연하게 관리할 수 있어 운영 효율 향상

## 구현

### 데이터 구조

**AS-IS (단일 이미지)**
```
SpotTrans
  └─ feeScheduleImagePathname (VARCHAR, nullable)
```

**TO-BE (다중 섹션)**
```
SpotTrans
  └─ FeeScheduleSection[] (1:N)
       ├─ title (필수) — 수가표 섹션 제목 (예: "March Event", "3-Month Event")
       ├─ description (선택) — 부가 설명 (예: "*VAT Included")
       ├─ imagePathname (필수) — 수가표 이미지 경로
       └─ priority (필수) — 노출 순서
```

### 유저 플로우

- 유저가 스팟 상세 페이지를 조회할 때, 해당 스팟에 등록된 수가표 섹션이 1개 이상이면 "수가표" 영역이 노출된다.
- 각 섹션은 제목 + (선택적) 설명 + 이미지로 구성되며, priority 순서대로 노출된다.
- 어드민에서 스팟 기본정보 편집 시, 수가표 섹션을 추가/수정/삭제/순서 변경할 수 있다.

### 프론트엔드 요구사항

**Web (유저 페이지)**

- 기존 `SpotDetailFeeScheduleSection` 컴포넌트를 다중 섹션 구조로 개선
- 각 섹션별로 제목, 설명(있는 경우), 이미지를 순서대로 렌더링
- 수가표 섹션이 0개이면 수가표 영역 자체를 숨김
- 수가표 영역 하단에 주의사항 Notice 박스 하드코딩 노출
  - 스타일: 회색 배경(`gray/2`), 테두리(`gray/10`, 1px), borderRadius 8px
  - ⚠️ 아이콘 + "주의사항" 타이틀 (Body_Bold/Body2_20)
  - 안내 문구: "해당 이미지는 참고용이며, 병원 내 이벤트, 시술 구성, 제품 수급 상황 등에 따라 실제 결제 금액은 달라질 수 있으며, 방문 시 안내되는 금액이 최종 적용됩니다."
  - 번역 키: `spot.detail.fee-schedule.caution`
- 피그마 (수가표 + 주의사항): https://www.figma.com/design/yalcxOrviDIvrcCV1ezZJ0/Sprint-107?node-id=2029-8647
- 피그마 (전체 스팟 상세): https://www.figma.com/design/yalcxOrviDIvrcCV1ezZJ0/Sprint-107?node-id=2029-13064

**Admin (어드민 페이지)**

- 기존 `SpotFeeScheduleImageSection` 컴포넌트를 다중 섹션 관리 UI로 개선
- 섹션 추가/삭제 기능
- 각 섹션별 제목(필수), 설명(선택), 이미지(필수) 입력
- 드래그앤드롭으로 섹션 간 순서 변경 (priority 자동 재계산)
- `upsertSpotBasicInfo` mutation에 수가표 섹션 데이터 포함

### 백엔드 요구사항

**데이터베이스**

- 새 테이블 생성: `spot_fee_schedule_section`
  - `id` (PK, auto increment)
  - `spot_trans_code` (FK → spot_translation.code)
  - `title` (VARCHAR, NOT NULL) — 섹션 제목
  - `description` (VARCHAR, NULL) — 부가 설명
  - `image_pathname` (VARCHAR, NOT NULL) — 이미지 경로
  - `priority` (INT, NOT NULL) — 노출 순서
  - `created_at`, `updated_at`
- 기존 `spot_translation.fee_schedule_image_pathname` 컬럼은 마이그레이션 후 제거

**GraphQL 스키마**

- 새 ObjectType: `SpotFeeScheduleSection`
  - `id: ID!`
  - `title: String!`
  - `description: String`
  - `imageUrl: URL!`
  - `priority: Int!`
- `SpotTrans`에 ResolveField 추가: `feeScheduleSections: [SpotFeeScheduleSection!]!`
- 기존 `feeScheduleImageUrl` 필드는 deprecated 처리 후 단계적 제거
- Mutation InputType: `UpsertSpotFeeScheduleSectionInput`
  - `title: String!`
  - `description: String`
  - `imageUrl: String!`
  - `priority: Int!`

**API 및 비즈니스 로직**

- `upsertSpotTrans` mutation에서 수가표 섹션 리스트를 받아 일괄 저장 (replace 방식)
- 이미지 URL → pathname 변환은 기존 패턴(`URLUtil.imageUrlToPathname`) 활용
- 조회 시 pathname → CloudFront URL 변환은 기존 패턴(`URLUtil.addCloudFrontHost`) 활용

**데이터 마이그레이션**

- 기존 `fee_schedule_image_pathname`에 값이 있는 레코드를 새 테이블로 이관
  - title: 기본값 설정 (예: "수가표")
  - description: null
  - imagePathname: 기존 값 그대로
  - priority: 0
