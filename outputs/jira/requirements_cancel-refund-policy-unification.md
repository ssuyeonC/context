# 세부 기획안: 취소/환불 정책 통합

> **선행 작업:** COM-2343 (무료 상품 환불 정책 적용 토글) — 본 작업으로 옵트인 토글을 전사 룰로 승격
> **확인 완료:** 경영지원팀(하얀님), 사업개발팀, CX팀(가진님)
> **사전 논의록:** `.context/inputs/cancel-refund-policy-merger-discussion.md`

## 배경

### 문제 정의

크리에이트립은 현재 "환불 정책"만 존재하고 별도의 "취소 정책"이 없는 구조다. 이로 인해 다음 두 가지 운영상 허점이 발생하고 있다.

1. **무료 예약 상품의 무제한 취소 허점**
   - 무료 예약 상품은 환불할 금액이 0원이므로, 환불 정책상 "환불 불가 기간"에 진입한 후에도 사실상 언제든 자유롭게 취소가 가능하다.
   - 피부과 등 무료 예약이 일반적인 카테고리에서 노쇼/직전 취소가 발생할 경우 파트너의 시간/자원 손실이 발생한다.
   - COM-2343에서 `isRefundPolicyOnFreeItems` 토글로 어드민이 스팟별 옵트인 가능하도록 도입했으나, 토글이 OFF인 스팟은 여전히 허점이 유지되고 있다.

2. **환불 정책 미설정 상품의 통제 부재**
   - 환불 정책 자체가 입력되지 않은 스팟은 취소 가능 여부가 불명확한 상태로 운영되고 있다.

타 OTA(Klook, KKday, 트립닷컴, 마이리얼트립)는 모두 "취소 정책"과 "환불 정책"을 통합 운영하며, "미환불 취소"라는 별도 개념을 두지 않는다.

### 가설적 임팩트

- **무료 예약 노쇼/직전 취소 감소**: 피부과·뷰티 카테고리의 무료 예약 비중이 높은 만큼, "환불 불가 구간 = 취소 불가"가 강제되면 무성의한 직전 취소로 인한 파트너 손실이 감소한다.
- **CS 응대 부담 감소**: "취소가 되네/안 되네" 케이스별 분쟁이 정책 일원화로 줄어든다.
- **타 OTA 대비 정책 일관성 확보**: 사용자에게 익숙한 정책 모델로 정렬되어 신뢰도가 향상된다.

## 구현

### 유저 플로우

#### 사용자 (예약자)
1. 사용자가 예약 상세에서 취소 버튼을 누르면, 시스템은 **환불 정책 구간 소속 여부**를 기준으로 취소 가능 여부를 판단한다.
2. 100% / 부분(예: 50%) 환불 가능 구간 → 취소 가능. 실제 환불액이 0원인 무료 예약도 정책 구간 내라면 취소 가능.
3. 환불 불가 구간(0%) 또는 환불 정책 미설정 스팟 → 취소 버튼 비활성화 또는 클릭 시 "취소 불가" 안내.

**판단 기준 예시**
- 무료 예약 + "3일 전 100% 환불" 정책 → 예약일 4일 전 취소 요청: 취소 가능 / 2일 전 취소 요청: 취소 불가.
- "0일 전 100% 환불" 정책 → 예약 당일 취소 요청: 취소 가능.

#### 어드민 (스팟 등록/수정)
1. 어드민이 스팟 결제 정보 페이지에서 환불 정책을 설정한다. 페이지 라벨은 "환불 정책"에서 **"취소 및 환불 정책"**으로 변경된다.
2. 무료 예약 스팟(피부과 등)의 빠른 등록을 위해 **"당일 취소 가능" 토글**을 제공한다. 토글 클릭 시 `baseDate=0, percent=100` 정책이 자동 입력된다.
3. 정책 미설정 상태일 경우, 안내 카피로 "정책이 없으면 사용자는 취소 자체가 불가합니다. (CS 콘솔을 통한 수동 환불은 별도)"가 노출된다.
4. **기존 무료 상품 토글(`isRefundPolicyOnFreeItems`)은 어드민 UI에서 제거**된다. 어드민이 스팟별로 선택하는 단계가 사라지고, 모든 스팟이 동일하게 환불 정책 구간에 따라 동작한다.

#### CS 운영자 (변경 없음)
- CS 콘솔의 수동 환불 경로(`setRefundedAfterManualRefund`, `setRefundedWithoutRefund`)는 환불 정책 체크를 우회하므로 기존과 동일하게 동작한다.
- 분쟁/보상/외부 결제수단 환불 등의 케이스는 영향을 받지 않는다.

### 프론트엔드 요구사항

#### 어드민 (`frontend/apps/admin`)
- `SpotPaymentInfo/index.tsx` 외 관련 컴포넌트의 라벨을 "환불 정책" → "취소 및 환불 정책"으로 변경한다.
- `ToggleIsRefundPolicyOnFreeItemsSwitch.tsx` 컴포넌트를 제거한다. (마이그레이션 완료 후 `paymentInfo` fragment에서도 필드 제거)
- `CreateRefundPolicy.tsx`에 **"당일 취소 가능" 토글**을 신규로 추가한다.
  - 토글 ON: `baseDate=0, percent=100` 정책이 자동 생성 mutation으로 등록된다.
  - 이미 동일한 정책이 존재하면 토글이 ON 상태로 표시된다.
- 환불 정책 미설정 상태인 스팟에는 "사용자 취소 불가" 경고 카피를 노출한다.

#### 사용자 웹 (`frontend/apps/web`)
- `CancelOrRefundReservationButton.tsx` (common / member / nonMember 3종)에서 취소 버튼 활성화 조건을 변경한다.
  - 기존: `localizedRefundableAmount > 0` 또는 `isZeroRefundCancelableByUser`
  - 신규: 환불 정책 구간 소속 여부 (백엔드가 GraphQL로 응답한 단일 boolean 필드 기준)
- 무료 예약 상품에 대해 "환불액이 0원이지만 취소 가능합니다" 안내 카피를 추가한다 (정책 구간 내일 경우).
- 환불 불가 구간 또는 정책 미설정 케이스에는 disable + 비활성화 사유 툴팁을 노출한다.

#### i18n
- `cancel`, `refund` 관련 메시지 키를 "취소 및 환불"로 통합한 카피로 일괄 변경한다.

### 백엔드 요구사항

#### 적용 범위
- 핵심 코드 변경은 **Trip 서비스(`backend/apps/trip/`)** 에 집중된다.
- Language School(어학당), Stay(숙박)는 무료 예약이 존재하지 않거나 외부 공급사 정책을 그대로 사용하므로 코드 변경 범위 외이나, 정책 룰 자체는 전사 동일하게 적용된다는 점을 문서화한다.

#### 1) 취소 가능 여부 판정 로직 일원화
- 파일: `backend/apps/trip/src/modules/reservation/reservation/repos/loaders/reservation-cancelable-by-user.loader.ts` (`canCancelWithZeroRefund`)
- 파일: `backend/apps/trip/src/modules/reservation/reservation/reservation-cancel.service.ts` (`isZeroRefundCancelableByUser`)
- 기존 4분기 로직(`isRefundPolicyOnFreeItems` 토글 분기 포함)을 제거하고, 다음 단일 룰로 통합한다.
  1. 환불 정책 미설정 스팟 → 취소 불가
  2. 환불 정책의 `percent` 구간이 1 이상 (= 정책 구간 소속) → 취소 가능
  3. 환불 정책 구간 밖 (예약 시점 기준 `differenceOfDays < baseDate` 이거나 0% 구간) → 취소 불가
- 기존의 `isWithinRefundableWindow()` 유틸은 재사용 가능. dummy amount(1,000,000)로 환불액 > 0 여부를 확인하는 트릭을 그대로 활용한다.

#### 2) 환불 정책 미설정 처리 명시화
- 파일: `backend/apps/trip/src/modules/reservation-policy/reservation-policy/reservation-policy.entity.ts` (`calculateRefundAmountByReservation`)
- 정책이 0건일 때 현재는 `ZeroRefundableAmountError`를 던지고 있다. 사용자 취소 경로에서는 "취소 불가"로 명확히 처리되도록 호출부 분기를 보강한다. (CS 수동 환불은 영향 없음)

#### 3) GraphQL 스키마 변경
- `ReservationPolicy.isRefundPolicyOnFreeItems` 필드를 `@deprecated`로 마킹한다. (후속 PR에서 제거)
- `setIsRefundPolicyOnFreeItems` mutation을 `@deprecated`로 마킹한다.
- `Reservation.isZeroRefundCancelableByUser` 필드의 의미를 재정의하거나, 신규 단일 필드(예: `isCancelableByPolicy`)로 대체하는 안을 검토한다.
- 컨슈머 호환성 원칙(`backend/CLAUDE.md`)에 따라 nullable→non-null 전환은 동반 프론트엔드 PR로 처리한다.

#### 4) 적용 시점 (4-2 결정)
- **신규 예약부터 적용** (예약 생성일 기준).
- 기존 예약(배포 이전 생성)은 기존 정책으로 처리되도록 분기 추가. 예약 엔티티의 `createdAt`을 기준으로 분기한다.

#### 5) 데이터 마이그레이션 (운영팀 리스트 기반)
- 운영팀이 다음 컬럼의 CSV를 전달한다.
  - `spotId`
  - 정책 변경 종류: `(a) isRefundPolicyOnFreeItems 전환` / `(b) 환불 정책 신규 입력`
  - 신규 환불 정책 값 (`baseDate`, `percent` 배열) — (b) 케이스용
  - 적용 제외 여부 — "당분간 취소 불가가 맞다"는 스팟 표시
- 마이그레이션은 다음 2단계로 배포된다.
  1. 코드 배포 (신규 룰 활성화 + `isRefundPolicyOnFreeItems` deprecate)
  2. 운영팀 리스트 기반 마이그레이션 실행 (토글 값 정리 + 신규 정책 일괄 등록)
  3. 후속 PR에서 `is_refund_policy_on_free_items` 컬럼 drop
- 마이그레이션 입력 CSV는 롤백 대비를 위해 `.context`에 보관한다.

#### 6) CS 콘솔 수동 환불 (4-7 검증 결과)
- `setRefundedAfterManualRefund`, `setRefundedWithoutRefund` 경로는 `verifyCancelable()`만 호출하며 환불 정책에 의존하지 않는다.
- 어드민 강제 취소 경로의 `isCancellationOverrideAllowed: true` 옵션이 유지되므로 신규 정책 도입 후에도 CS는 정책 외 환불을 처리할 수 있다.
- 추가 코드 변경 없음.

#### 7) 부분환불 처리 (4-5 결정)
- 환불 정책의 `percent` 값(1~99)이 자연스럽게 부분환불을 발생시킨다. 별도 분기 추가 없이 기존 로직을 유지한다.

#### 8) GA/로그 (4-6 결정)
- 신규 GA 이벤트는 추가하지 않는다. 분석 요청 발생 시 후속 작업으로 처리.
