# 세부 기획안: 무료 상품 환불 정책 적용

## 배경

### 문제 정의

- 가격이 0원인 무료 상품(isFreeOfCharge)에 환불 정책이 설정되어 있어도, 유저가 환불 불가 기간에 취소 신청이 가능함
- 원인: 취소 가능 여부 판단 로직(`reservation-cancelable-by-user.loader.ts`)에서 모든 예약 아이템이 무료(`isFreeOfCharge`)이면 환불 정책과 무관하게 취소를 허용하고 있음
- 무료 상품 중 일부는 수량 제한이 있는 행사/이벤트성 상품으로, 환불 불가 기간에 취소가 되면 운영상 문제가 발생할 수 있음

### 가설적 임팩트

- 무료 행사/이벤트 상품의 노쇼 방지 및 좌석/수량 관리 안정화
- 운영팀이 환불 정책을 통해 무료 상품의 취소를 제어할 수 있게 되어 운영 자율성 확보

## 구현

### 유저 플로우

- 어드민 유저는 가격이 0원인 아이템을 포함한 스팟의 환불 정책 설정 영역에서 '무료 상품 환불 정책 적용' 토글을 확인할 수 있다.
- 어드민 유저가 해당 토글을 ON으로 설정하면, 유저 페이지에서 환불 정책에 의해 환불이 불가한 기간에 무료 상품의 취소 신청이 차단된다.
- 해당 토글이 OFF이면 기존 동작과 동일하게 무료 상품은 환불 정책과 무관하게 취소가 가능하다.

### 프론트엔드 요구사항

#### [어드민 스팟 상세 - 결제 정보] 페이지

- 환불 정책 설정 영역 하단에 토글 추가
- **노출 조건**: 해당 스팟에 가격이 0원인 아이템(`isFreeOfCharge = true`)이 존재하고, 환불 정책이 1개 이상 설정된 경우에만 토글 노출
- **토글 라벨**: `무료 상품에도 환불 정책 적용` (보조 설명: "활성화하면 무료 상품도 환불 정책에 따라 취소가 제한됩니다")
- 기존 환불 정책 UI(`SpotPaymentInfo/RefundPolicy.tsx`) 하단에 배치

#### [유저 예약 상세] 페이지

- 기존 취소/환불 버튼 로직에 변경 없음 (백엔드에서 `isCancelableByUser` 값이 달라지므로 프론트는 기존 로직 그대로 동작)

### 백엔드 요구사항

#### 1. 데이터 저장

- `reservation_policy` 테이블에 컬럼 추가:
  - `enforce_refund_policy_on_free_items` (boolean, default: false): 무료 상품에 환불 정책 적용 여부

#### 2. API

- 기존 ReservationPolicy 관련 mutation에 `enforceRefundPolicyOnFreeItems` 필드 추가
- ReservationPolicy GraphQL 타입에 해당 필드 노출

#### 3. 취소 가능 여부 로직 수정

- `reservation-cancelable-by-user.loader.ts`의 `canCancelWithZeroRefund` 메서드 수정:
  - 현재: 모든 아이템이 무료이면 무조건 취소 허용 (`reservedItems.every((item) => item.isFreeOfCharge)`)
  - 변경: `enforceRefundPolicyOnFreeItems = true`인 경우, 무료 아이템이어도 환불 정책의 환불률이 0%이면 취소 차단
