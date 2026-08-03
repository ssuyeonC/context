# 예약 거절 요청 · 일정 변경 플로우 코드 조사 — 세션 요약

작성일: 2026-08-03
성격: 코드 조사 세션 요약 (기획 단계 아님 / 요구사항·제안서 아님)
대상 코드베이스: `creatrip/product` 모노레포 (backend `apps/trip`, frontend `apps/admin`)

> 목적: 파트너·관리자의 예약 거절/일정 변경 플로우가 코드상 실제로 어떻게 동작하는지, 그리고 어드민 예약 리스트의 변경요청 탭 개편이 기술적으로 얼마나 복잡한지를 코드 근거로 확인한 기록. 향후 기획 시 근거 자료로 사용.

---

## 1. 파트너의 예약 '거절 요청' 가능 상태값

**질문:** 파트너가 생성된 예약 건에 대해 '거절 요청'을 할 수 있는 상태값은?

### 예약 상태 enum
`backend/apps/trip/src/modules/reservation/reservation/reservation.constants.ts:33-40`
```
PAYMENT_REQUIRED = 1
CONFIRM_REQUIRED  = 2
COMPLETE          = 3
CANCEL            = 4
PARTIAL_REFUND    = 5
USED              = 6
```

### 거절 요청 가능 상태 = 3가지
`reservation.entity.ts:1337-1347` `validateForPartnerRejection()` — 아래 3개가 아니면 `PartnerInvalidReservationStatusError`로 차단.

| 상태 | 값 | 의미 |
|------|-----|------|
| CONFIRM_REQUIRED | 2 | 파트너 확정 대기 |
| COMPLETE | 3 | 확정 완료 |
| PARTIAL_REFUND | 5 | 부분 환불 |

**불가:** PAYMENT_REQUIRED(1, 결제 전) · CANCEL(4, 종료) · USED(6, 종료)

- 유스케이스: `request-reservation-rejection-by-partner.usecase.ts` (권한 체크 → 락 조회 → 기존 거절건 확인 → 상태 검증 → `PARTNER_REJECTION_REQUESTED` 이벤트)
- UI 게이트도 동일: `partner-admin-reservation-detail-state.types.ts:144-162` `buildPartnerRequestAction()`이 취소요청·변경요청과 같은 3개 상태 세트 사용.

---

## 2. 일정 변경 플로우 & 크로스-액터 가능 여부

### 플로우
```
1. 관리자/파트너의 예약 변경 요청
2. 유저의 승낙
3. 관리자/파트너의 확인(최종 승인)
4. 예약 변경 완료 (예약일 변경 + 메일 + 타임슬롯 이동)
```

### 변경요청 상태 enum
`reservation-date-change-request-history.types.ts:27-33`
```
ADMIN_REQUESTED      (요청 생성, 유저 응답 대기)
USER_REQUESTED       (유저 응답 완료, 최종 승인 대기)
CLOSED               (변경 확정 완료)
REJECTED / REJECTED_SILENTLY
```
※ 이 상태는 **예약(reservation) 테이블의 단일 컬럼** `dateChangeRequestStatus`에 비정규화되어 저장됨.

### 핵심 질문: "관리자가 요청 → 유저 승낙 → 파트너가 확정" 이 크로스-액터 플로우가 성립하나?
**→ 성립함.** 액터 매칭 제약 없음.

- 최종 확정 엔드포인트 `applyReservationDateChangeRequest`
  - 권한(`resolver.ts:148-166`): ADMIN, SUPER_ADMIN, **TRAVEL_PARTNER**, TRAVEL_PARTNER_SUPERIOR
  - 확정 대상(`service.ts:502-507`): **writerType=USER 히스토리**만 찾아 확정
- 유저가 승낙하면(`service.ts:462-472`) `createDomainForUser`로 **writerType=USER 히스토리가 새로 생성**되고 상태가 USER_REQUESTED로 전환 → 이후 파트너가 이 USER 히스토리로 apply 가능.
- 즉 확정 로직은 "최초 요청자(ADMIN)"를 보지 않고 **유저의 승낙 기록(USER)만** 본다. → 요청자=관리자, 확정자=파트너 조합을 막는 가드가 없음.

> ⚠️ 조사 중 발견한 오독 주의점: 유저 승낙 시 발생하는 `APPLIED` 이벤트 핸들러(`handler.ts:97-104`)가 관리자 초기화 건이면 early-return 하는데, 이건 **파트너 알림톡 발송 여부만 스킵**하는 것이지 확정을 막는 게 아님. 실제 확정은 항상 별도 수동 `apply` 호출로만 발생. (초기 서브에이전트 조사가 이걸 "차단"으로 오독 → 직접 코드 확인으로 정정함)

---

## 3. 최종 승인 시 어드민 vs 파트너의 슬롯 처리 차이

`applyReservationDateChangeRequest` 내부(`service.ts:531`):
```
const allowAutoCreateWhenUnavailable = Authorizer.isAdmin(member);
```
- `Authorizer.isAdmin` = **ADMIN / SUPER_ADMIN만** true (`authorizer.ts:52-55`). `TRAVEL_PARTNER_SUPERIOR`(파트너 상위)도 false.

이 플래그가 가용성 검증·슬롯 이동에 전달됨 (`time-slot/.../move-reserved.service.ts`):

| 승인 주체 | 유저가 고른 날짜에 가용 슬롯이 없을 때 |
|-----------|------------------------------------|
| **어드민**(ADMIN/SUPER_ADMIN) | 재고부족·마감·비공개·미생성 **전부** 판매 비노출 예외 슬롯 자동 생성 → **통과** (line 32-33, 193-195) |
| **파트너**(TRAVEL_PARTNER) | 가용 슬롯 없으면 **즉시 `NotFoundTimeSlotAtThatTimeError` → 실패** (line 134-135, 189-190) |

**결론:** "어드민 승인 = 슬롯 여부 무관 강제 확정 가능 / 파트너 = 실제 예약 가능한 슬롯 필요" — 맞음. 단 승인 주체 기준이며 요청 시작자와 무관.

**뉘앙스 3가지:**
1. 파트너 상위(TRAVEL_PARTNER_SUPERIOR)도 어드민 아님 → 슬롯 필요. "어드민 예외"는 ADMIN/SUPER_ADMIN 한정.
2. 날짜 변경 제한 검증(`validateDateChangeLimit`, `service.ts:511`)은 어드민 포함 전원 적용.
3. 어드민도 100% 무조건은 아님 — 다중 아이템이 같은 부모 풀 공유 + 풀이 거의 가득 찬 희귀 엣지에서 `run()`이 `NotEnoughTimeSlotVacancyError`로 실패·롤백 가능(`move-reserved.service.ts:76-81`). 일반 마감/미생성은 전부 통과.

---

## 4. 어드민 예약 리스트 변경요청 탭 개편 — 구현 가능성 & 복잡도

### 개편 아이디어 (아직 기획 전)
- 현재: `dateChangeRequestStatus` 단일 컬럼 기준으로 '관리자 예약 변경 요청'/'유저 예약 변경 요청'/'예약 변경 완료' 탭 분류. 유저 응답 후 ADMIN_REQUESTED→USER_REQUESTED로 바뀌면 탭이 이동해버림.
- 원하는 것: (신규 예정) **'파트너 예약 변경 요청'** 탭 하위에 '유저 응답 대기 중' / '유저 응답 완료' / '전체' 서브탭. '관리자 예약 요청'도 동일하게 하고 싶으나 다른 팀이 현행 선호.

### 전제 정정 — "최초 요청자 기록이 안 된다"는 절반만 맞음
- 맞음: **예약 테이블 단일 컬럼**에는 최초 요청자 정보가 없음.
- 틀림: **히스토리 테이블에는 남아 있음.** `reservation_date_change_request_history`에 `writer_code`(→member.level), `writer_type`(ADMIN/USER), `responded_at`, 파트너 발 요청엔 `partner_action_request_id`까지 기록(`entity.ts:22-40`). `createDomainForAdmin`은 `writerCode` **필수** → ADMIN-type 히스토리엔 작성자 항상 존재(토큰 요청 포함).
- **이미 이 데이터를 쓰는 필터 존재:** `dateChangeRequestWriterRoles`(`args.ts:128-138`). 백엔드가 히스토리 JOIN으로 분리(`reservation.repo.ts:1870-1881`):
  ```sql
  WHERE history.writer_type = 'ADMIN'
    AND history.responded_at IS NULL       -- 사실상 "유저 응답 대기 중"
    AND writer.level IN (파트너/운영팀 롤)
  ```
  → "파트너가 요청 + 유저 응답 대기 중" 서브탭은 사실상 이미 구현되어 있는 셈.

### 3개 서브탭 매핑 (모두 같은 JOIN, `responded_at` 조건만 변경)
'파트너 예약 변경 요청' = `writer_type='ADMIN' AND writer.level IN (파트너 롤)` (또는 `partner_action_request_id IS NOT NULL` — 더 견고)

| 서브탭 | 추가 조건 | 대응 상태 | 현황 |
|--------|-----------|-----------|------|
| 유저 응답 대기 중 | `responded_at IS NULL` | ADMIN_REQUESTED | **이미 됨** |
| 유저 응답 완료 | `responded_at IS NOT NULL` | USER_REQUESTED | 조건만 뒤집으면 됨 |
| 전체 | (조건 제거) | - | 조건 제거 |

### 복잡도 평가: 전체 LOW ~ MEDIUM
- **DB 마이그레이션 불필요** ★ — 필요한 컬럼(writer, responded_at, partner_action_request_id)이 이미 존재.
- **백엔드 LOW~MEDIUM** — `buildDateChangeRequestWriterRoleFilter`의 하드코딩된 `responded_at IS NULL`을 파라미터(대기/완료/전체)로 열고 필터 인자 추가. JOIN 인프라 재사용.
- **프론트 LOW** — 상단 '파트너 예약 변경 요청' 탭(→ `dateChangeRequestWriterRoles=[파트너 롤]`) + 하위 3버튼. 기존 `DateChangeRequestStatusFilter.tsx` 패턴 확장.
- **관리자 탭도 동일 메커니즘**(롤만 ADMIN/SUPER_ADMIN)이라 대칭. **파트너만 먼저 하고 관리자는 현행 유지해도 기술 부채 없음.**

### 유일하게 신경 쓸 함정 (MEDIUM을 만드는 부분)
- **다중 변경 사이클 오분류:** 한 예약에 과거 종료된 파트너 사이클 + 현재 유저발 사이클이 겹치면, `responded_at IS NOT NULL` 서브쿼리가 과거 파트너 히스토리를 잡아 현재 유저발 건을 "파트너 요청·유저 응답 완료"로 오분류할 수 있음.
  - 해결: 현재 활성 사이클(예약의 현재 `dateChangeRequestStatus`, 또는 최신 미종료 히스토리 그룹) 기준으로 서브쿼리 스코핑. 이 정확도 처리가 유일하게 손이 가는 지점.
- **product 결정 필요:** '전체' 탭에 최종 승인 완료(CLOSED)까지 포함할지. apply 되면 CLOSED로 빠지므로 범위 정의 필요.

---

## 참조 파일 (traceability)
- `backend/apps/trip/src/modules/reservation/reservation/reservation.constants.ts` — 예약 상태 enum
- `.../reservation/reservation.entity.ts` — `validateForPartnerRejection`, `approveByPartner`
- `.../reservation/partner-admin-reservation-detail-state.types.ts` — 파트너 액션 UI 게이트
- `.../reservation-date-change-request-history/` — types / entity / service / handler / resolver / repo
- `.../reservation/repos/reservation.repo.ts` — 어드민 리스트 필터(`buildDateChangeRequestWriterRoleFilter`)
- `.../reservation/reservation.args.ts` — `dateChangeRequestStatus`, `dateChangeRequestWriterRoles` 필터
- `backend/libs/auth/src/core/authorizer.ts` — `isAdmin`
- `.../time-slot/services/update/move-reserved/move-reserved.service.ts` — 슬롯 이동·자동 생성
- `frontend/apps/admin/src/components/reservation/DateChangeRequestStatusFilter.tsx` — 탭 UI
