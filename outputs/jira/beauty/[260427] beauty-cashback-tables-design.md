# 뷰티캐시백 캠페인 - 백엔드 테이블 설계

> COM-2421 ([프로모션 캠페인 단위 뷰티 캐시백 가이드 관리 기능]) 의 **백엔드 테이블 설계 보강**.
> 본 문서는 테이블/스키마 범위만 다룬다. 어드민 UI·웹 노출·Slack 알림은 원티켓을 따른다.

## 설계 원칙

- **단일 도메인 테이블 + 번역 분리 + 매핑 분리**의 3-테이블 구조
- "기본 캠페인"과 "프로모션 캠페인"을 별도 테이블로 분리하지 않고, **`is_default` 플래그**로 동일 테이블 안에서 구분
- 스팟과의 관계는 spot 테이블 스키마를 건드리지 않는 **junction 테이블**로 분리 (한 스팟 = 한 캠페인 보장)
- 기간 기반 자동 전환은 본 스코프 제외 (필드는 미리 둠 → 후속 작업에서 활용 가능)

## 테이블

### 1. `beauty_cashback` (메인)

캠페인의 메타와 기본 언어(ko) 본문을 보관한다.

| 컬럼 | 타입 | NULL | 기본값 | 설명 |
|------|------|------|--------|------|
| `id` | INT AUTO_INCREMENT | NO | | PK |
| `title` | VARCHAR(100) | NO | | 어드민 내부 식별용 캠페인명. 유저 노출 X, 번역 X |
| `body` | TEXT | NO | | 기본 언어(ko) 본문 마크다운. 다른 언어는 번역 테이블에서 조회 |
| `refund_rate` | DECIMAL(5,2) | NO | | 일반 캐시백 환급률(%). UI/Slack 표시 전용 (실제 환급은 운영팀 수동 처리) |
| `membership_refund_rate` | DECIMAL(5,2) | YES | NULL | 멤버십 추가 환급률(%). 미설정 시 일반 환급률만 노출 |
| `is_default` | TINYINT(1) | NO | 0 | 기본 가이드 여부. 전체에 1건만 존재 |
| `period_start` | DATE | YES | NULL | 캠페인 시작일. 기본 가이드는 NULL |
| `period_end` | DATE | YES | NULL | 캠페인 종료일. 기본 가이드는 NULL |
| `created_at` | DATETIME | NO | now() | |
| `updated_at` | DATETIME | NO | now() | |

**제약 / 인덱스**

- `UNIQUE` (생성 컬럼 트릭 또는 app-level): `is_default = 1`인 row는 전역 1건만 존재
  - MySQL은 partial unique index 미지원 → `default_flag AS (CASE WHEN is_default = 1 THEN 1 END) STORED` + `UNIQUE(default_flag)` 또는 usecase에서 강제
- 비즈니스 룰 (app-level)
  - `is_default = 1` ⇒ `period_start`, `period_end` 모두 NULL
  - `is_default = 0` ⇒ `period_start`, `period_end` 모두 NOT NULL
  - 기본 가이드는 **삭제 불가**, **`title` 변경 불가** (`refund_rate` / `body` / 번역은 편집 가능)
  - `refund_rate >= 0`, `membership_refund_rate >= 0`

---

### 2. `beauty_cashback_translation` (본문 번역)

기본 언어(ko)를 제외한 나머지 언어의 본문을 보관한다.

| 컬럼 | 타입 | NULL | 기본값 | 설명 |
|------|------|------|--------|------|
| `id` | INT AUTO_INCREMENT | NO | | PK |
| `beauty_cashback_id` | INT | NO | | FK → `beauty_cashback.id`, ON DELETE CASCADE |
| `language` | VARCHAR(10) | NO | | `LanguageType` enum (ko, en, ja, zh_CN, zh_TW, id, vi, th, ms 등) |
| `body` | TEXT | NO | | 해당 언어 본문 마크다운 |
| `created_at` | DATETIME | NO | now() | |
| `updated_at` | DATETIME | NO | now() | |

**제약 / 인덱스**

- `UNIQUE(beauty_cashback_id, language)` — 한 캠페인은 같은 언어를 중복 보유 불가
- `ON DELETE CASCADE` — 메인 캠페인 삭제 시 번역도 함께 삭제

**조회 룰**

- 특정 언어 요청 시: `beauty_cashback_translation.body WHERE language = X` 우선 → 없으면 `beauty_cashback.body`(ko fallback)
- 자동번역으로 채우는 결과도 동일 테이블에 upsert

---

### 3. `beauty_cashback_spot` (캠페인-스팟 매핑)

스팟이 어떤 캠페인의 적용을 받는지를 매핑한다. 매핑이 없는 스팟 = 기본 캠페인 적용.

| 컬럼 | 타입 | NULL | 기본값 | 설명 |
|------|------|------|--------|------|
| `id` | INT AUTO_INCREMENT | NO | | PK |
| `beauty_cashback_id` | INT | NO | | FK → `beauty_cashback.id`, ON DELETE CASCADE |
| `spot_id` | INT | NO | | FK → `spot.id` (트립 서비스 내 동일 DB), ON DELETE CASCADE |
| `created_at` | DATETIME | NO | now() | |
| `updated_at` | DATETIME | NO | now() | |

**제약 / 인덱스**

- `UNIQUE(spot_id)` — 한 스팟에 동시에 두 캠페인 매핑 금지 (1 spot ↔ 1 campaign 보장)
- `INDEX(beauty_cashback_id)` — 캠페인별 매핑 스팟 리스트 조회용
- 매핑 row가 존재하는 캠페인은 어드민에서 **삭제 시 차단** 또는 **연결 일괄 해제 후 삭제** 두 단계로 강제

**조회 룰**

- `spot_id`로 매핑 row 조회 → 있으면 해당 캠페인 사용
- 매핑 row 없으면 `beauty_cashback WHERE is_default = 1` 사용
- 매핑은 있으나 캠페인 `period_end < today`인 경우 → **본 스코프에서는 자동 해제하지 않음.** 어드민 UI에 "만료" 표시만, 운영자가 수동 해제

---

## 마이그레이션 (기존 → 신규)

기존 `beauty_receipt_notice` 테이블은 언어별 row 1건씩 = 단일 가이드의 다국어 본문을 들고 있다. 이를 신규 구조의 "기본 캠페인" 1건으로 흡수한다.

1. 신규 테이블 3개 생성 (`beauty_cashback`, `beauty_cashback_translation`, `beauty_cashback_spot`)
2. 기본 캠페인 1 row 시드
   - `title = '기본 가이드'`
   - `refund_rate = 10.00` (현행 하드코딩 값)
   - `membership_refund_rate = 15.00` (현행 멤버십 추가율 — 확정값 운영 확인 필요)
   - `is_default = 1`
   - `period_start = NULL`, `period_end = NULL`
   - `body` = 기존 `beauty_receipt_notice` 의 `language = 'ko'` row의 `notice` 값
3. 번역 백필
   - 기존 `beauty_receipt_notice` 의 `language != 'ko'` 인 모든 row를 신규 `beauty_cashback_translation` 에 그대로 매핑
     - `beauty_cashback_id` = 시드된 기본 캠페인 id
     - `language` / `body` = 기존 `language` / `notice`
4. `beauty_cashback_spot`은 빈 상태로 시작 — 기존에 뷰티캐시백 토글 ON 상태였던 모든 스팟은 자동으로 "기본 캠페인 적용" 상태가 된다
5. 기존 `beauty_receipt_notice` 테이블은 본 마이그레이션에서는 **drop하지 않음**. 코드 의존성 제거 + 1회 이상 안정화 검증 후 후속 마이그레이션에서 drop (롤백 안전성 확보)

## 영향도 / 주의사항

- **트립 서비스 단독 변경**: 신규 테이블 3개는 모두 트립 서비스 내. spot 테이블 스키마 변경 없음 → 다른 도메인(예약/결제)에 영향 없음
- **CS Slack 알림** (원티켓 5번 요구): 결제/예약 시점에 `spot_id → beauty_cashback` 단일 조회로 캠페인명·환급률 가져와서 표시. 본 테이블 구조로 충분히 지원
- **자동번역**: 본 문서 범위 외. `beauty_cashback_translation` 에 row를 채우는 주체(자동번역 usecase vs 운영자 수동 입력)는 어드민 모달 스펙에서 결정
- **삭제 시 매핑 처리**: ON DELETE CASCADE 가 걸려 있어도, 어드민에서는 "매핑된 스팟이 있는 캠페인의 직접 삭제"를 차단하고 사용자에게 일괄 해제를 명시적으로 요구하는 것이 안전 (UI에서 의도 확인)

## 보완 옵션 (검토 필요)

- **기본 언어(ko) 본문도 번역 테이블에 두기**: 현 설계는 메인 테이블에 ko body, 번역 테이블에 그 외 언어. 모든 언어를 번역 테이블에 두면 fallback 로직이 단순해지고 메인 테이블이 메타 전용이 되어 더 깔끔하나, row 수가 늘고 운영팀의 "ko 입력 → 다른 언어 자동번역" 흐름과의 매핑이 한 단계 더 추가됨
- **`beauty_cashback_spot` 에 매핑 이력 컬럼 추가**: `applied_at`, `released_at` 또는 매핑별 활성 기간을 두면 만료된 캠페인의 자동 해제 + 이력 추적이 가능. 본 스코프는 단순 매핑(현재 활성 매핑만)이며, 향후 기간 기반 자동 전환 도입 시 함께 검토
- **`title` 다국어화**: 현 설계는 어드민 내부 식별용으로 단일 텍스트. 만약 캠페인 이름을 유저(웹/Slack 외 채널)에게 노출할 필요가 생기면 `beauty_cashback_translation` 에 `title` 컬럼을 추가하거나 별도 번역 테이블 분리
