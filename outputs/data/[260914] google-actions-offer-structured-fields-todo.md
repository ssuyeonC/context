# Offers Feed용 — 구조화 필요 정보 리스트

작성일: 2026-09-14
관련: [260914] google-actions-offer-feed-mapping.md / [260819] google-actions-coupon-landing-page-correspondence.md
정의: 구글 Offers feed가 **구조화 필드**로 요구하지만, 현재 우리 데이터엔 **비구조화 텍스트로만 있거나 아예 없는** 정보. (= 랜딩페이지 "Coupon conditions" 영역과 동일 데이터셋)

---

1. **할인 유형·값** (`discount_percent` / `discount_value`)
   - 현재: 쿠폰 194개 전부 `coupon.discount_type=NONE`, 값은 `discount_description` 텍스트("10% OFF")에만.
   - 필요: 할인율(%) / 정액할인(₩) / 무료증정 여부를 구조화 값으로.

2. **혜택 종류 구분 (할인 vs 무료증정)**
   - 현재: "Free tea or Coffee", "Discount Coupon" 같이 텍스트로 섞여 있음.
   - 필요: 할인형 / 증정형 등 타입 분류.

3. **최소 주문금액** (`min_spend_value`)
   - 현재: `spot_reserve.min_order_amount` 전부 0/null → 구조화 전무. "orders over 20,000 won"은 설명/유의사항 텍스트에만.
   - 필요: 최소주문금액 숫자 필드. ← **구글이 랜딩에서 지적한 핵심 항목**

4. **이용제한/조건** (`offer_restrictions` / `special_conditions`)
   - 현재: `spot_translation.precautions` 등 자유텍스트만.
   - 필요: 결제수단·유저세그먼트·코스/메뉴 제한 등을 항목화된 조건으로.

5. **사용횟수 한도** (`max_redemption_count`)
   - 현재: `coupon.issue_cycle`(재사용 쿨다운, 일수)만 존재 — 총 사용횟수 한도와는 **다른 개념**.
   - 필요: 인당 총 사용횟수 한도 필드 정의(현재 `spot.reservation_limit_count_per_user` 활용 가능 여부 확인).

6. **유효 요일·시간** (`time_of_day` / `day_of_week`)
   - 현재: `spot_reserve.reserve_hours`에 있으나 215건 중 207건이 빈 값(대부분 미설정).
   - 필요: 요일/시간 제한 있는 오퍼는 구조화, 없으면 "전일 적용" 명시.

7. **버티컬·모드 분류** (`action_type` / `offer_modes` / `offer_category`)
   - 현재: 우리 카테고리(맛집할인·핫한카페·쇼핑·면세점)만 있음.
   - 필요: 카테고리→구글 버티컬(Dining/Shopping) 매핑 규칙 + 온사이트 쿠폰의 offer_mode 확정. ← Momo 회신(#16) 대기

---

**우선순위**: 3(최소주문) · 4(이용제한) · 1(할인값)이 랜딩페이지 조건 노출 이슈와 직결 → 최우선. 7은 Momo 회신 후 확정.
