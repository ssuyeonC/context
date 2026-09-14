# Google Actions Center — Offers Feed 스키마 ↔ Creatrip 데이터 매핑표

작성일: 2026-09-14
관련: [260819] google-actions-coupon-landing-page-correspondence.md
대상: 예약타입=쿠폰(`spot_reserve.type=3`) + 카테고리(면세점·맛집할인·핫한카페·쇼핑) + 공개·예약가능·영업중, `(폐업)` 제외 = **194개 스팟** (`[260914] google-actions-offer-feed-candidates.txt`)
피드 스키마 출처: https://developers.google.com/actions-center/verticals/reservations/offers/reference/feeds/offers-feed

---

## 0. 대상 데이터의 실측 특성 (194 스팟)

- 오퍼 연결: 194개 중 **191개**가 `spot_has_coupon → coupon`으로 연결. (3개는 쿠폰 미연결 → 확인 필요)
- 모든 쿠폰: **`use_type=ONSITE`(현장형), `discount_type=NONE`** → 할인율/할인액이 구조화 컬럼에 안 들어감. 실제 혜택은 `coupon.discount_description` free-text("10% OFF", "Free tea or Coffee")로만 존재.
- `spot_reserve.min_order_amount` = **전부 0/null** → 최소주문금액이 구조화 필드에 없음. "orders over 20,000 won" 류는 설명/유의사항 텍스트에만.
- `spot_reserve.reserve_hours`(요일·시간): 215건 중 **207건이 빈 값** → 요일/시간 제한 있는 오퍼는 소수(~8건).
- `coupon.issue_cycle`: 1~365(일). = 동일 쿠폰 재사용 쿨다운(≠ 총 사용횟수 한도).

> **핵심 시사점**: 구글 피드가 **구조화 필드**로 요구하는 조건(`min_spend_value`·`discount_percent/value`·`offer_restrictions`·`special_conditions`)이 우리 쪽엔 대부분 **비구조화 텍스트**로만 존재. → 랜딩페이지 조건 노출 이슈와 **동일한 근본 원인**. 피드 매핑 = 랜딩 조건영역 스펙 겸용.

---

## 1. Offers Feed 필드 매핑

범례: ✅ 그대로 매핑 / ⚠ 변환·규칙 필요 / 🔴 데이터 없음(신규 구조화 필요)

| # | Feed 필드 | Req | Creatrip 소스 | 상태 | 비고 |
|---|-----------|-----|---------------|------|------|
| 1 | `offer_id` | R | `coupon.code` | ✅ | 쿠폰 단위 고유 ID |
| 2 | `entity_ids` | O* | `spot.code`(엔티티 피드 merchant id) | ✅ | 엔티티 매핑, entity feed 스킵 여부는 Momo 확인중 |
| 3 | `offer_source` | R | 상수 = merchant(직접) | ✅ | 고정값 |
| 4 | `action_type` | R | 카테고리→버티컬 규칙 | ⚠ | 맛집할인·핫한카페→`ACTION_TYPE_DINING`, 쇼핑·면세점→shopping 계열. **로컬쇼핑 비-기프트카드 표현은 Momo 확인중(#16)** |
| 5 | `offer_modes` | R | 현장형(ONSITE) → walk-in 계열 | ⚠ | 예약형 아님. 정확한 mode enum Momo 확인 필요 |
| 6 | `offer_category` | R | 쿠폰 → coupon 계열 상수 | ⚠ | BASE vs coupon add-on 분류 확정 필요 |
| 7 | `offer_details` | R | `coupon.discount_type`/`discount_value`/`discount_description` | ⚠ | discount_type=NONE이라 텍스트 기반. 재구조화 권장 |
| 8 | `offer_display_text` | R | `coupon.discount_description` | ✅ | "10% OFF" 등 검색결과 노출 텍스트 |
| 9 | `discount_percent` | C | `coupon.discount_value`(RATIO일 때) | 🔴 | 현재 discount_type 전부 NONE → **할인율 구조화 필요** |
| 10 | `discount_value` | C | `coupon.discount_value`(FIXED일 때) | 🔴 | 동일. 정액 할인 구조화 필요 |
| 11 | `min_spend_value` | O | ❌ (`spot_reserve.min_order_amount`=0) | 🔴 | **최소주문 구조화 전무** → 텍스트에서 추출·신규 입력. 랜딩 이슈와 동일 |
| 12 | `max_discount_value` | O | ❌ | 🔴 | 대부분 불필요 추정 |
| 13 | `offer_restrictions` | R | ❌ 구조화 없음 | 🔴 | 유의사항 텍스트만 → 신규 구조화 |
| 14 | `combinable_with_other_offers` | R | 상수(정책상 false 추정) | ⚠ | 중복사용 정책 확정 필요 |
| 15 | `max_redemption_count` | O | `spot.reservation_limit_count_per_user` | ⚠ | **`issue_cycle`(재사용 쿨다운)와 혼동 금지** — 별개 개념 |
| 16 | `special_conditions` | O | `spot_translation.precautions`(free-text) | ⚠ | 텍스트 파싱/항목화 필요 |
| 17 | `validity_periods.valid_period` | R | `coupon.expired_at`(종료), `offline_coupon_benefit.start_date/end_date` | ✅ | 시작·종료 시점 확보 |
| 18 | `time_of_day`/`day_of_week` | O | `spot_reserve.reserve_hours`(요일·시간 JSON) | ⚠ | ~8건만 제한 존재, 나머지 전일 적용 |
| 19 | `terms.terms_and_conditions` | R/O | `spot_translation.precautions`/`more_information` | ✅ | T&C 텍스트 |
| 20 | `terms.url` / `offer_url` | O/R* | `https://creatrip.com/{lang}/spot/{spot.code}` | ✅ | 랜딩 URL |
| 21 | `coupon.code` | C | ❌(현장 확인형, 코드 미발급 추정) | ⚠ | 코드형 여부 확인 필요 |
| 22 | `banner_image_url` | O | `coupon.image_pathname` / `spot.main_image_pathname` | ✅ | 이미지 URL |
| 23 | `source_assigned_priority` | O | (선택) `spot.score`/`is_recommend` | ✅ | 우선순위 |

\* BASE_OFFER 카테고리에서만 required

---

## 2. Entity Feed (참고)

- Momo 힌트: 기존 GAC(예약) merchant feed가 이미 있으면 entity feed **스킵 가능성** → #16에서 확정 요청, 회신 대기.
- 스킵 불가 시: `spot.code`(엔티티 id), `spot_translation.spot_name`, `spot.address`/`latitude`/`longitude`, `telephone`, `google_place_id` 등으로 구성 가능.

---

## 3. 조치 필요 항목 (우선순위)

1. 🔴 **할인 구조화**(#9·#10): `discount_type=NONE` 일괄 → 실제 % / 정액 / 무료증정을 구조화 필드로 재입력하는 방안. free-text만으로 피드 통과 여부 확인 필요.
2. 🔴 **최소주문·이용조건 구조화**(#11·#13·#16): 최소주문금액·조건을 별도 필드로. **랜딩페이지 "Coupon conditions" 전용 영역과 동일 데이터셋** → 한 번에 설계.
3. ⚠ **버티컬/모드 매핑 규칙**(#4·#5·#6): 카테고리→action_type, 온사이트→offer_mode, 로컬쇼핑 비-기프트카드 표현 = Momo 회신(#16) 확정 후 고정.
4. ⚠ **max_redemption vs issue_cycle 구분**(#15): 재사용 쿨다운과 총 사용한도를 각각 어느 필드로 보낼지 정의.
5. 쿠폰 미연결 3개 스팟 점검.
