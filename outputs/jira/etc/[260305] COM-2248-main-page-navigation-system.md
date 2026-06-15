# COM-2248: 메인 페이지 내비게이션 관리 시스템 추가

> **선행 작업**: [COM-2253](https://creatrip.atlassian.net/browse/COM-2253) — 예약 대분류 카테고리 아이콘 관리 기능
> (기존 `mapIconPath`/`mapIconUrl` 활용, 하드코딩 아이콘 마이그레이션 및 전체 페이지 전환 포함)

## 배경

### 문제 정의

현재 메인 페이지(`/`)와 스팟 메인 페이지(`/spot`)의 카테고리 내비게이션은 다음과 같은 문제를 가짐:

- 카테고리 내비게이션에 **카테고리가 아닌 항목**(약국, 환전 등)도 하드코딩으로 삽입되어 운영 불가
- 어드민에서 홈에 노출되는 카테고리의 **선택/순서/개수를 관리할 수 없음** (백엔드에서 `MAIN_RESERVATION` 전체가 자동 노출)
- **언어별로 다른 내비게이션 구성**이 필요하나 코드 분기로만 처리 중 (대만: PHOTO 제외 + Stay 추가)

### 가설적 임팩트

- 운영 효율: 카테고리/프로모션 내비게이션을 개발 배포 없이 즉시 변경 가능
- 확장성: 신규 카테고리, 프로모션 랜딩 페이지 등을 내비게이션에 자유롭게 추가
- 언어별 최적화: 각 시장의 니즈에 맞는 내비게이션 구성 가능

---

## 구현

### 유저 플로우

**어드민 (내비게이션 관리)**

1. 어드민 사용자는 언어를 선택한 뒤, 해당 언어의 내비게이션 항목을 관리한다.
2. '내비게이션 항목 추가' 버튼을 클릭하면 입력 폼이 노출된다:
   - **타입 선택**: 카테고리 / URL 중 택일
   - **카테고리 선택 시**: 대분류 카테고리(MAIN_RESERVATION) 선택 → 이름과 아이콘이 카테고리로부터 자동 연결 (readonly)
   - **URL 선택 시**: 이름 직접 입력, 아이콘 직접 업로드, URL 직접 입력 (외부 URL 포함 자유 입력)
3. 드래그앤드롭으로 내비게이션 항목의 순서를 변경할 수 있다.
4. 최대 15개까지 추가 가능하며, 15개 미만도 허용된다.

**유저 페이지**

1. 메인 페이지(`/`)와 스팟 메인 페이지(`/spot`)에 동일한 내비게이션이 노출된다.
2. 등록된 항목만 표시되며, 빈 슬롯은 노출되지 않는다.
3. 카테고리 타입 항목 클릭 시: 기존과 동일하게 `/spot/list?page=1&category={id}&order=MOST_VIEWED_IN_A_MONTH`로 이동
4. URL 타입 항목 클릭 시:
   - URL에 `creatrip` 포함 → 내부 페이지 이동 (SPA 네비게이션)
   - URL에 `creatrip` 미포함 → 새 탭에서 열림

---

### 프론트엔드 요구사항

#### 1. 어드민 — 내비게이션 관리 페이지 신설

- 언어 선택 탭/드롭다운
- 내비게이션 항목 리스트 (드래그앤드롭 순서 변경)
- 항목 추가 폼:
  - 타입 선택 (카테고리 / URL)
  - 카테고리 타입: 대분류 카테고리 셀렉터 → 이름/아이콘 자동 표시 (readonly)
  - URL 타입: 이름 입력, 아이콘 업로드, URL 입력 (외부 URL 포함)
- 항목 삭제 기능
- 최대 15개 제한 (프론트 validation)
- 허용 아이콘 포맷: **PNG, GIF** (GIF는 Beauty 등 애니메이션 아이콘 대응)

#### 2. 유저 페이지 — 내비게이션 렌더링

**홈 페이지 (`/`)**
- `HomeTravelMenu.tsx`: 기존 `categories(type: MAIN_RESERVATION)` 쿼리 → 새 내비게이션 API로 교체
- `HomeMainCategoryNavList.tsx`: 내비게이션 항목 타입(카테고리/URL)에 따른 분기 렌더링
- 대만 특수 로직 (PHOTO 제외, Stay 추가) 제거 → 어드민에서 언어별 관리로 대체
- 그리드 레이아웃: 15개 이하 가변 개수에 대응하는 반응형 그리드

**스팟 메인 페이지 (`/spot`)**
- `SpotMain.tsx`: 동일한 내비게이션 API 사용, 홈과 동일 렌더링
- 기존 하드코딩 제거: `TravelMainPharmacyCategoryNavItem` (약국), `TravelMainCurrencyExchangeNavItem` (환전) → 어드민 내비게이션 항목으로 마이그레이션

**URL 타입 항목의 내부/외부 판별**
- URL에 `creatrip` 문자열 포함 여부로 판별
- 내부: Next.js `<Link>` 사용 (SPA 네비게이션)
- 외부: `<a target="_blank" rel="noopener noreferrer">` 사용

---

### 백엔드 요구사항

#### 1. HomeNavigation 엔티티 신설

```
home_navigation
├── id (PK)
├── language (VARCHAR, NOT NULL)  -- 언어 코드
├── type (ENUM: CATEGORY, URL)    -- 진입점 타입
├── category_code (FK → category.code, NULLABLE)  -- 카테고리 타입일 때
├── url (VARCHAR, NULLABLE)       -- URL 타입일 때
├── label (VARCHAR, NULLABLE)     -- URL 타입의 표시 이름
├── icon_path (VARCHAR, NULLABLE) -- URL 타입의 아이콘 경로
├── priority (INT, NOT NULL)      -- 노출 순서
├── created_at (DATETIME)
├── updated_at (DATETIME)
```

- `type = CATEGORY`일 때: `category_code` 필수, `url`/`label`/`icon_path` NULL (카테고리의 `translation.name`과 `mapIconUrl` 사용)
- `type = URL`일 때: `url`, `label`, `icon_path` 필수, `category_code` NULL

#### 2. GraphQL API

**Query**
```graphql
type HomeNavigation {
  id: ID!
  language: String!
  type: HomeNavigationType!  # CATEGORY | URL
  category: Category         # type=CATEGORY일 때, category.mapIconUrl 포함
  url: String                # type=URL일 때
  label: String!             # CATEGORY면 category.translation.name, URL이면 직접 입력값
  iconUrl: String!           # CATEGORY면 category.mapIconUrl, URL이면 직접 업로드 이미지
  priority: Int!
}

query homeNavigations(language: String!): [HomeNavigation!]!
```

**Mutation**
```graphql
mutation createHomeNavigation(input: CreateHomeNavigationArgs!): HomeNavigation!
mutation updateHomeNavigation(input: UpdateHomeNavigationArgs!): HomeNavigation!
mutation deleteHomeNavigation(id: Int!): Boolean!
mutation updateHomeNavigationPriority(input: UpdateHomeNavigationPriorityArgs!): [HomeNavigation!]!
```

- `createHomeNavigation`: 해당 언어의 내비게이션 항목 수가 15개 미만일 때만 허용
- 모든 mutation은 ADMIN, SUPER_ADMIN 권한 필요

#### 3. 기존 코드 영향

- 홈/스팟 메인 페이지의 카테고리 쿼리(`categories(type: MAIN_RESERVATION)`)가 `homeNavigations` 쿼리로 교체됨
- 카테고리 타입 내비게이션의 `label`과 `iconUrl`은 Category 엔티티의 `translation.name`과 `mapIconUrl`을 참조하므로, COM-2253(카테고리 아이콘 관리)이 선행 완료되어야 함
