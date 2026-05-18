# 취소/환불 정책 통합 — 논의 정리 (Pre-Requirement)

> **상태:** Frame 단계 — 다음 세션에서 이어 논의 후 requirements 문서 작성 예정
> **세션 일자:** 2026-05-15
> **원본 노션:** https://www.notion.so/creatrip/35fd62c69561801299dbf64e59796f8f
> **관련 선행 작업:** COM-2343 / PR #1455, #1473 (2026-03)

---

## 1. 요구사항 원문

### 배경
- 현재 정책은 "환불 정책"만 존재하고, "취소 정책"이 별도로 없음. 이로 인해 무료 예약 상품의 경우 환불할 금액이 0원이라 사실상 언제든 자유롭게 취소가 가능한 허점이 발생
- 타 OTA 조사 결과: Klook, KKday, 트립닷컴, 마이리얼트립 모두 "취소 정책"과 "환불 정책"을 통합 운영. "미환불 취소" 개념을 별도로 운영하는 플랫폼은 없음

### 개선 사항
- "환불 정책" → "취소 및 환불 정책"으로 통합. 환불 가능 여부 = 취소 가능 여부로 일원화
- 무료 예약 / 예약금 있는 상품 모두 동일 정책을 따름

### 적용 로직

| 환불 정책 설정 | 환불 금액 | 취소 가능 여부 |
| --- | --- | --- |
| 100% 환불 가능 구간 | 100% 환불 | 취소 가능 (전액 환불) |
| 부분 환불 구간 | 일부 환불 (예: 50%) | 취소 가능 (부분 환불) |
| 환불 불가 구간 | 0원 | 취소 불가 |
| 환불 정책 미설정 상품 | — | 취소 불가 |

**핵심 원칙**
- 환불 정책상 환불 가능 구간 내 → 취소 가능 (무료 예약이라 실제 환불액이 0원이어도 취소 가능)
- 환불 정책상 환불 불가 구간 → 취소 불가
- 환불 정책 미설정 → 취소 자체가 불가능

즉, "실제 환불 금액"이 아니라 "환불 정책상 어느 구간에 속하는지"가 취소 가능 여부의 기준.

**예시**
- Case 1. 무료 예약 + "3일 전 100% 환불": 4일 전 취소 요청 → 취소 가능 / 2일 전 → 취소 불가
- Case 2. "0일 전 100% 환불": 당일 취소 → 가능

### UI 개선 추가 요청
현재 환불 정책 설정 UI는 "예약일 N일 전까지 N% 환불" 형태로 직접 입력해야 함. 피부과 등 무료 예약 스팟은 대부분 "당일 취소도 무료 허용" 케이스가 많을 것으로 예상되는데, 매번 "0일 전 100% 환불"을 수기 입력하는 건 번거로움.
→ "당일 취소 가능" 토글/버튼을 별도로 추가해서 한 번 클릭으로 0일 전 100% 환불이 세팅되면 좋겠음.

### 확인 완료
- 하얀님(경영지원팀)
- 사업개발팀
- 가진님(CX팀)

---

## 2. 현재 코드베이스 구현 현황

### 2-1. COM-2343 선행 작업 (2026-03 머지)

**PR:** #1455 (2026-03-12, development) / #1473 (2026-03-13, production cherry-pick)
**작성자:** @SpaceTime52 (BohyeonKim)
**제목:** `feat: 무료 상품 환불 정책 적용 토글 (COM-2343)`

PR 요약 발췌:
> 무료 상품(`isFreeOfCharge`)이 환불 차단 기간에도 취소 가능한 버그 수정.
> `isRefundPolicyOnFreeItems` 토글 추가 → ON이면 무료 상품도 유료 상품과 동일한 환불 정책 적용.

→ **이번 요구사항이 지적하는 버그와 동일한 문제를 토글 옵트인 방식으로 해결.** 이번 작업은 토글을 없애고 "전사 룰"로 승격하는 셈.

### 2-2. 데이터 모델

**Trip 서비스 (`backend/apps/trip/`)**
- `PercentRefundPolicy` (`reservation-policy/refund/refund-policy.entity.ts:1-14`) — `baseDate`, `percent`
- `ReservationPolicy` (`reservation-policy/reservation-policy/reservation-policy.entity.ts`)
  - `refundPolicyListString` (line 258-261) — JSON 배열로 저장
  - `isRefundPolicyOnFreeItems` (line 497-499) — COM-2343에서 추가
- 마이그레이션: `backend/apps/trip/migrations/20260312120000-add-is-refund-policy-on-free-items.js`

**Stay 서비스 (숙박):** 별도 모델, 외부 공급사(Yanolja/Onda) 정책 사용 — **이번 범위 외로 추정**
**Language School:** 환불 정책 개념 없음, 단순 환불만 처리

### 2-3. 취소 가능 판정 로직 (`reservation-cancelable-by-user.loader.ts:81-111`)

```
1) 환불액 > 0                      → 취소 가능
2) 모두 무료 & 토글 ON             → 환불 가능 윈도우 내에서만 취소 가능
3) 토글 ON (부분 무료 포함)        → 취소 불가
4) 토글 OFF & 모두 무료            → 항상 취소 가능   ← 이번 요구사항이 막으려는 허점
   토글 OFF & 부분 무료            → 취소 불가
```

재사용 가능 자산: `isWithinRefundableWindow()` (line 113-120) — dummy 1,000,000원 넣어 환불액 > 0인지 보는 트릭. 신규 요구사항의 "환불 정책 구간 소속 여부" 판단에 그대로 활용 가능.

### 2-4. 어드민 UI
- `frontend/apps/admin/src/components/spot/SpotPaymentInfo/index.tsx`
- `RefundPolicy.tsx`, `CreateRefundPolicy.tsx`, `DeleteRefundPolicy.tsx`
- `ToggleIsRefundPolicyOnFreeItemsSwitch.tsx` — COM-2343 산출물

### 2-5. 사용자 웹 UI
- `frontend/apps/web/domain/travel/subdomain/reservation/common/CancelOrRefundReservationButton.tsx`
- member/nonMember 변종 2개

### 2-6. GraphQL 스키마 (`frontend/schema.graphql`)
- `PercentRefundPolicy` (line 17278-17283)
- `Reservation.isZeroRefundCancelableByUser` (line 18748)
- `ReservationPolicy.isRefundPolicyOnFreeItems` (line 19779)
- `ReservationPolicy.refundPolicies` (line 19842)
- Mutations: `setIsRefundPolicyOnFreeItems`, `addPercentRefundPolicy`, `updatePercentRefundPolicy`, `removePercentRefundPolicy`

---

## 3. 변경 필요 영역 & GAP

| 영역 | 파일 | 변경 포인트 |
|---|---|---|
| 백엔드 취소 판정 | `reservation-cancelable-by-user.loader.ts:81-111` | 토글 분기 제거, "환불 정책 구간 소속 여부" 단일화 |
| 백엔드 환불 실행 | `reservation-cancel.service.ts:774-803` | 위와 동일 |
| 백엔드 정책 미설정 처리 | `reservation-policy.entity.ts:776-820` | 정책 0건일 때 "취소 불가" 명시 |
| 어드민 라벨 | `SpotPaymentInfo/*` | "환불 정책" → "취소 및 환불 정책" |
| 어드민 토글 제거 | `ToggleIsRefundPolicyOnFreeItemsSwitch.tsx` | 컴포넌트 제거 |
| 어드민 신규 토글 | `CreateRefundPolicy.tsx` | "당일 취소 가능" 토글(baseDate=0, percent=100 자동) |
| 사용자 웹 취소 UI | `CancelOrRefundReservationButton.tsx` 3종 | 환불 정책 구간 기준 disable/문구 |
| i18n | cancel/refund 관련 키 | 통합 카피 |
| GraphQL | `isRefundPolicyOnFreeItems`, `setIsRefundPolicyOnFreeItems` | deprecate → 후속 PR에서 제거 |

---

## 4. 의사결정 포인트

### 4-1. `isRefundPolicyOnFreeItems` 처리 방침
- (A) 완전 제거 + 데이터 마이그레이션
- (B) deprecate만 하고 항상 true로 강제
- (C) 유지하되 기본값/UI에서 감춤
- **방향:** 2단계 배포 (코드 배포 → 마이그레이션 → 후속 PR에서 컬럼 drop) 권장

### 4-2. 기존 예약 처리
- 이미 예약된 건들도 새 정책 적용? 신규 예약부터?

### 4-3. 무료 예약 상품의 기본 정책
- 무료 상품 등록 시 자동으로 "당일 100% 환불" 강제?
- 어드민이 명시적으로 설정?

### 4-4. 적용 범위
- Trip(TTD/액티비티/피부과)만? Language School/Stay도?
- 피부과(아카데미)가 Trip 도메인 안에서 어떤 식별자로 구분되는지 확인 필요

### 4-5. 부분 무료(혼합 상품) 처리
- 통합 후 동작 정의 필요

### 4-6. GA/로그
- 취소 가능 여부 판정 추적 이벤트 정의 확인 필요

### 4-7. CS 운영자 수동 환불
- `setRefundedWithoutRefund()` 등 콘솔 수동 환불 케이스가 새 정책과 충돌하지 않는지

---

## 5. 확정된 결정 사항

### 5-1. 회귀 리스크 1·2 대응 방향 (2026-05-15 확정)

**리스크 1) `isRefundPolicyOnFreeItems = false`인 기존 스팟의 동작 변경**
**리스크 2) 환불 정책이 없는 무료 상품 스팟 (통합 후 "취소 불가"로 전환)**

→ **운영팀이 영향 받는 스팟 리스트를 전달 → 신규 기능 배포 시점에 토글 값/정책 일괄 마이그레이션으로 처리**

### 5-2. 운영팀 요청 리스트 스펙 (초안)

| 항목 | 필요 사유 |
|---|---|
| `spotId` | 마이그레이션 키 |
| 정책 변경 종류 | (a) `isRefundPolicyOnFreeItems` 전환 / (b) 환불 정책 신규 입력 구분 |
| 신규 환불 정책 값 (`baseDate`, `percent` 배열) | 정책 없는 스팟에 대한 운영팀 결정 사항 반영 |
| 적용 제외 여부 | "이 스팟은 당분간 취소 불가가 맞다"는 케이스 표시 |

### 5-3. 마이그레이션 설계 원칙
1. 리스트에 없는 스팟의 기본 동작 정의 필수 (화이트리스트 vs 전체 변환)
2. 2단계 배포: (a) 코드 배포 → (b) 마이그레이션으로 값 정리 → (c) 후속 PR에서 컬럼 drop
3. 롤백을 위해 마이그레이션 입력 CSV를 `.context`에 보관

### 5-4. 의사결정 포인트 4-2 ~ 4-7 (2026-05-15 확정)

| # | 결정 | 비고 |
|---|---|---|
| **4-2** | **신규 예약부터 적용** (예약 생성일 기준) | 기존 예약은 기존 정책 유지. 사용자 영향 최소화 |
| **4-3** | 무료 상품도 어드민이 명시 설정 | 자동 강제 X. "당일 취소 가능" 토글이 핵심 UX 장치 |
| **4-4** | Trip / Language School / Stay 모두 동일 룰 | LS·Stay는 무료 예약이 없어 영향 없음 → 일관성 확보. 코드 변경은 사실상 Trip만 |
| **4-5** | 부분환불은 기존 '부분환불' 상태값으로 관리 | 환불 정책 `percent` 값이 부분환불 발생/금액을 자연스럽게 결정. 별도 분기 추가 없음 |
| **4-6** | GA 이벤트 추가 안 함 | 분석 요청 들어오면 그때 추가 |
| **4-7** | CS 수동 환불 경로는 신규 정책과 무관 | `verifyCancelable()`이 환불 정책에 의존하지 않고, `isCancellationOverrideAllowed` 옵션으로 CS 경로 분리됨. 어드민 UX에 "정책 미설정 시 사용자 취소 불가" 안내 카피만 부수 추가 |

---

## 6. 남은 To-do

- [ ] PR #1455/#1473 작성자(@SpaceTime52)에게 COM-2343 도입 컨텍스트 재확인 (선택)
- [ ] DB 조회로 영향 범위 산정
  - `is_refund_policy_on_free_items = false`인 스팟 수
  - 환불 정책 없는 무료 상품 보유 스팟 수
- [ ] 운영팀 리스트 스펙 최종 합의 및 리스트 수령
- [ ] CS/사업개발팀 공지 & 어드민 정책 입력 가이드 준비
- [x] requirements 문서 작성 → `.context/outputs/jira/requirements_cancel-refund-policy-unification.md`

---

## 7. 권장 진행 순서

1. GAP 확정 회의 (의사결정 포인트 4-2~4-7)
2. 백엔드 통합 로직 PR (loader + service 일원화, 정책 미설정 처리)
3. GraphQL 스키마 변경 PR (필드 deprecate)
4. 어드민 UI PR (라벨 변경 + 당일 취소 토글 + 무료 토글 제거)
5. 웹 사용자 UI PR (카피/노출 조건 정리)
6. 마이그레이션 PR (운영팀 리스트 기반)
7. i18n 동기화 + QA
8. 후속: `isRefundPolicyOnFreeItems` 컬럼 drop PR
