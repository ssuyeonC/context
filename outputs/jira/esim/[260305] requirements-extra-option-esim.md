# ESIM 끼워팔기 (Spot Extra Option 확장) 요구사항

## 배경

### 문제 정의

특정 스팟(투어, 숙소 등) 예약 시, 관련 부가 상품(ESIM 등)을 함께 할인 가격에 제안하여 판매할 수 있는 끼워팔기(번들) 기능이 필요하다.

현재 extraOption 도메인은 안심케어(CARE_BASIC) 전용으로만 운영되고 있으나, 설계 자체는 범용 부가 옵션 레이어로 확장 가능하도록 되어 있다.

### 가설적 임팩트

- 예약 시점에 할인된 ESIM을 함께 제안하여 객단가 상승 기대
- 여행에 필수적인 ESIM을 번들로 제공함으로써 예약 전환율 개선 기대
- extraOption 도메인의 범용 활용 첫 사례로, 향후 다양한 부가 상품 판매 확장 가능성 검증

## 구현

### 적용 범위

| 항목 | 값 |
|------|-----|
| 대상 스팟 | 13043 (ESIM) |
| 대상 아이템 | 27774, 27775 |
| 판매 가격 | 각 아이템 `salePrice`의 70% (`price_rate = 0.7`) |
| 확장 가능성 | 낮음 (현재는 위 스팟/아이템에만 적용) |
| 제외 카테고리 | 중카테고리가 '유심', '이심', '배달서비스'인 스팟에는 ESIM extraOption 비노출 |

### 유저 플로우

1. 유저가 특정 스팟의 결제 페이지에 진입한다.
2. 스팟의 중카테고리가 '유심', '이심', '배달서비스'가 **아닌** 경우 결제 페이지에 ESIM 추가 구매 섹션이 노출된다.
3. 유저가 ESIM 옵션(27774 또는 27775)을 선택하면, 해당 아이템의 판매가 × 70% 가격이 결제 금액에 추가된다.
4. 유저가 결제를 완료하면, 메인 예약의 `reserved_extra_option`에 기록됨과 동시에 **ESIM 스팟(13043)에 대한 별도 예약(reservation)도 생성**된다.

### 프론트엔드 요구사항

- 결제 페이지에서 ESIM 부가 옵션 선택 UI 필요 (기존 안심케어 섹션과 유사한 형태)
- 아이템 27774, 27775 **둘 다 노출**, 라디오 버튼 형태로 **하나만 선택 가능**
- 수량은 **1개 고정** (수량 선택 UI 불필요)
- 구체적인 UI/UX는 추가 기획 필요

### 백엔드 요구사항

**extraOption 도메인 + reservation 도메인을 조합하여 구현한다.**

- **extraOption 도메인**: 끼워팔기 옵션 정의, 스팟별 활성화, 가격 계산, 옵션 선택/해제
- **reservation 도메인**: ESIM 별도 예약 생성, 바우처 자동 발급, 환불 처리

> ESIM은 바우처 발급이 필요한 상품이므로 `reserved_extra_option`만으로는 처리할 수 없다.
> 바우처 발급 플로우가 `Reservation` 엔티티를 필수로 요구하기 때문에 별도 예약 생성이 반드시 필요하다.

**1. DB 마이그레이션**

`spot_extra_option` 테이블에 컬럼 추가:

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `reference_spot_item_code` | INT, NULLABLE | 가격 참조할 스팟 아이템 코드. 값이 있으면 해당 아이템의 `salePrice`를 base amount로 사용 |

**2. 데이터 설정 (DB 직접 구성, 어드민 UI 불필요)**

`spot_extra_option` 레코드 추가:

| 필드 | 아이템 27774용 | 아이템 27775용 |
|------|--------------|--------------|
| type | `ESIM_27774` | `ESIM_27775` |
| price_rate | 0.7 | 0.7 |
| refund_rate | 스팟 13043의 환불 정책을 따름 | 스팟 13043의 환불 정책을 따름 |
| is_active | true | true |
| reference_spot_item_code | 27774 | 27775 |

**ESIM 노출 조건:**

- 모든 스팟에 기본 노출 (스팟별 `spot_has_extra_option` 매핑 불필요)
- 중카테고리가 '유심', '이심', '배달서비스'인 스팟만 제외

**3. 가격 계산 로직 변경**

`ApplyCareOptionUsecase` (또는 일반화된 usecase)에서 분기 추가:

```
if (spotExtraOption.referenceSpotItemCode 존재)
  baseAmountKrw = SpotItem(referenceSpotItemCode).salePrice  ← DB 조회
else
  baseAmountKrw = mainReservation.baseAmountKrw  ← 기존 로직 (안심케어)

finalPrice = baseAmountKrw × price_rate
```

- 기존 안심케어 로직에는 영향 없음 (`referenceSpotItemCode`가 null이면 기존 동작 유지)
- ESIM 상품 가격이 변동되면 자동 반영됨

**4. 예약 생성 및 바우처 발급 (reservation 도메인)**

끼워팔기로 판매된 ESIM은 별도 예약(reservation)으로 생성하여 기존 바우처 발급 플로우를 활용한다.

**메인 예약 결제 완료 시 처리 순서:**

```
1. 메인 예약 결제 완료 (PAID)
2. reserved_extra_option 기록 생성
3. ESIM 스팟(13043)에 대한 별도 reservation 자동 생성
   - 선택된 아이템(27774 또는 27775)을 reserved_item으로 포함
   - 가격: extraOption에서 계산된 할인가 적용
4. ESIM 예약 상태 → CONFIRM_REQUIRED / COMPLETE
5. 기존 바우처 자동 발급 플로우 동작 (SpotItem.isVoucherAutoIssued → VoucherTemplate)
```

**메인 예약 ↔ ESIM 예약 연결:**

- `reserved_extra_option`에 `extra_reservation_id` 컬럼 추가 (INT, NULLABLE)
- 안심케어는 이 값이 null (별도 예약 없음)
- ESIM은 이 값으로 생성된 ESIM 예약을 참조

**환불 정책:**

- ESIM 스팟(13043)의 환불 정책을 따름
- 메인 예약 환불 시 연결된 ESIM 예약도 함께 환불 처리 필요

**5. 멤버십 할인**

- ESIM 부가 옵션에도 **멤버십 할인 적용**
- 안심케어의 할인율(50%)이 아닌, **일반 상품 구매에 적용되는 멤버십 할인율**을 사용

**6. 기존 로직 영향 범위**

| 기존 기능 | 영향 |
|-----------|------|
| 안심케어 (CARE_BASIC) | 없음 (`referenceSpotItemCode = null`, `extra_reservation_id = null`) |
| `isCareOption()` 분기 | 없음 (ESIM type은 `CARE_` prefix 아님) |
| 클레임/환불 플로우 | ESIM에는 미적용 (claim 필드는 null 유지) |
| 멤버십 할인 | 적용 (기존 50% 할인 로직 재사용) |
| 바우처 발급 | ESIM 별도 예약에서 기존 자동 발급 플로우 그대로 동작 |

**7. DB 마이그레이션 요약**

| 테이블 | 추가 컬럼 | 타입 | 설명 |
|--------|----------|------|------|
| `spot_extra_option` | `reference_spot_item_code` | INT, NULLABLE | 가격 참조할 스팟 아이템 코드 |
| `reserved_extra_option` | `extra_reservation_id` | INT, NULLABLE | 끼워팔기로 생성된 별도 예약 ID |
