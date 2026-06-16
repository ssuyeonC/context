# 0원 예약 결제 리마인더 메일 이슈

> 작성: 2026-05-29 / 다음 세션에서 이어서 진행 예정

## 배경

Trip(예약) 도메인의 "결제가 필요합니다" 안내 메일이 **자동확정이 아니면서 판매가가 0원인 예약**에도 발송되고 있는 것으로 보인다. 0원이라 결제할 금액이 없는데도 유저에게 결제 독촉 메일이 가는 UX 이슈.

## 현재 동작 정리

### 메일 발송 파이프라인

- **Consumer**: `backend/apps/trip/src/modules/reservation/schedule/bull/send-payment-reminder-mail.consumer.ts:44-54`
- **Producer**: `backend/apps/trip/src/modules/reservation/schedule/bull/send-payment-reminder-mail.producer.ts:31-40`
- **쿼리**: `backend/apps/trip/src/modules/reservation/reservation/repos/reservation.repo.ts` → `findAllToSendPaymentReminderMail()` (라인 734-783)
- **템플릿**: OneSignal (`ONESIGNAL_PAYMENT_REMINDER_TEMPLATE_ID`)

### 발송 조건

- Cron `0 * * * *` (매시간 정각, KST)
- `status = PAYMENT_REQUIRED`
- `paymentStatus = UNPAID`
- `paymentExpiresAt`이 now+24h ~ now+26h 사이
- `paymentReminderMailSentAt is null` (1회만)
- 12~24h 내 다른 결제 예정 예약이 있는 회원은 제외 (빈도 제어)
- `isPackaged = true`(배달 패키지) 제외

### 0원 예약이 이 조건에 그대로 걸리는 이유

1. **상태 결정에 가격 분기가 없음**
   `reservation.entity.ts:920-933` `setStatusAndFinishCreatingReservation()`
   - 오직 `reservationPolicy.isPaymentRequired` 플래그만 본다
   - 가격이 0원이어도 정책상 `isPaymentRequired=true`이면 → `PAYMENT_REQUIRED` / `UNPAID` 로 진입
   - 동시에 `paymentExpiresAt`도 `getPaymentDueDate()`로 세팅됨

2. **승인 단계에도 0원 분기 없음**
   `reservation.entity.ts:1248-1254` `approveByPartner()` → `verifyPaymentStatusForConfirm()` (1616-1623)
   - `CANCELLED`, `PARTIAL_REFUNDED`만 거부, 0원 여부는 안 본다

3. **리마인더 쿼리에도 가격 필터 없음**
   `findAllToSendPaymentReminderMail()`에는 `expectedPaidPrice > 0` 같은 조건이 없다

### 트리거되는 시나리오 (스크린샷 케이스)

`.context/attachments/mdwdZ6/image.png` — "RESERVATION INFORMATION" 화면, TOTAL 0 USD, "PROCEED PAYMENT (0 USD)" 버튼

- 유저가 이 화면에 도달한 순간 백엔드에는 이미 예약이 `PAYMENT_REQUIRED/UNPAID` + `paymentExpiresAt` 세팅된 상태로 저장돼 있음
- 유저가 PROCEED를 안 누르고 이탈하면 → 24~26h 시점에 cron이 픽업 → "결제가 필요합니다" 메일 발송
- 자동확정 상품의 0원 예약은 PROCEED 누르는 즉시 0원 결제 처리 → `COMPLETE/PAID`로 넘어가므로 메일 미해당
- **문제 케이스: 자동확정 아님 + 0원 + 결제 확정 버튼 미클릭 이탈**

## 다음에 확인/논의할 것

- [ ] `reservationPolicy.isPaymentRequired`가 0원 상품/프로모션에서 정책적으로 `false`로 세팅되는 케이스가 있는지 확인
  - 어떤 상품 타입/프로모션이 `isPaymentRequired=false`를 사용하는지
  - 0원이면 항상 `false`로 가야 하는 정책인지 vs 가격과 무관한지
- [ ] 수정 방향 후보
  - (A) 쿼리에 `expectedPaidPrice > 0` 필터 추가 (가장 가벼움)
  - (B) 0원 예약은 생성 단계에서 `PAYMENT_REQUIRED` 대신 다른 상태로 분기 (구조적이지만 영향 범위 큼)
  - (C) `isPaymentRequired` 정책 자체를 0원일 때 false로 바꾸기 (가격 기반 정책 결정)
- [ ] 0원 예약이 실제로 얼마나 발생하는지 데이터 확인 (BigQuery)
- [ ] 같은 패턴이 Language School의 3종 결제 메일에도 있는지 점검

## 참고 파일

- `backend/apps/trip/src/modules/reservation/reservation/reservation.entity.ts`
- `backend/apps/trip/src/modules/reservation/reservation/repos/reservation.repo.ts`
- `backend/apps/trip/src/modules/reservation/schedule/bull/send-payment-reminder-mail.{consumer,producer}.ts`
- `backend/apps/trip/src/modules/reservation/reservation/usecases/approve-reservation-by-partner.usecase.ts`
