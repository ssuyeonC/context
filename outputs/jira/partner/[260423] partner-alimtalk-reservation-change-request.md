# 세부 기획안 요구사항 문서 양식

## 배경

### 문제 정의

현재 파트너 알림톡을 통한 예약 처리 플로우에서 **예약 승인은 action_token 기반으로 로그인 없이 처리**되지만, **예약 변경 요청은 그렇지 않다.**

알림톡의 "예약 변경 요청" 버튼을 클릭하면 action_token이 발급되어 `/travel-partner/reservations/redirect?type=Change`로 진입하지만, 실제로는 **어드민 예약 상세 페이지(`#reservation-date-change` 앵커)로 리다이렉트**만 된다. 파트너는 어드민 로그인 후 `DateChangeRequestMailTemplate` 폼에서 날짜 제안을 입력해야 변경 요청을 보낼 수 있다.

이로 인한 문제:

- **마찰 발생**: 파트너가 알림톡을 받고도 어드민에 로그인해야 변경 요청 가능 → 승인과 달리 추가 진입 장벽이 있어 처리 포기 또는 지연으로 이어짐
- **일관성 부재**: 승인/거절은 action_token으로, 변경은 로그인 기반으로 — 동일 알림톡 내에서 채널 경험이 분리됨
- **운영 병목으로 직결**: 파트너가 변경 요청을 못 보내면 운영팀이 중간에서 파트너-유저 간 조율을 대행하게 됨

또한 현재 어드민의 변경 요청 폼(`DateChangeRequestMailTemplate`)은 admin 전용 컨텍스트(role 체크, useMyInfo, SMS 옵션)가 박혀 있어 **다른 진입 경로에서 재사용이 불가능**하다. 향후 변경 요청 기능을 개선할 때마다 두 곳을 각각 수정해야 하는 유지보수 이슈가 예상된다.

### 가설적 임팩트

- 파트너가 알림톡 링크 클릭 1회로 변경 요청까지 완료 가능 → 승인 플로우 대비 누락되는 변경 요청 건 회수
- 어드민 로그인 필요성 제거로 Type D(미사용) 파트너의 첫 액션 허들 낮춤
- 변경 요청 비즈니스 로직을 단일 서비스 계층으로 통합 → 향후 룰 변경(예: 180일 한도 조정, 메일 템플릿 수정) 시 양쪽 플로우에 자동 반영되어 유지보수 비용 감소

## 구현

### 유저 플로우

1. 파트너는 예약 건의 알림톡을 수신하고 "예약 변경 요청" 버튼을 클릭한다.
2. 파트너는 로그인 절차 없이 예약 변경 요청 전용 페이지로 진입한다.
3. 파트너는 해당 페이지에서 제안 날짜(복수 가능), 메일 제목, 메일 본문을 입력한다.
4. 파트너가 "변경 요청 발송" 버튼을 클릭하면 유저에게 변경 요청 메일이 발송되고, 예약의 변경 요청 이력이 생성된다.
5. 파트너는 성공 화면을 확인하고, 기존 승인 플로우와 동일하게 "파트너 어드민에서 모든 예약 관리하기" CTA를 볼 수 있다.
6. 토큰이 만료되었거나 이미 사용된 경우, 에러 화면을 노출하고 어드민 로그인 경로를 안내한다.

### 프론트엔드 요구사항

**공용 폼 컴포넌트 추출**

- 기존 `frontend/apps/admin/src/components/reservation/DateChangeRequestMailTemplate.tsx`에서 auth-agnostic한 순수 폼 컴포넌트를 추출한다.
- 추출 대상:
  - 날짜 제안 피커 (`useReservationDateSuggestionsDatePicker` 훅 포함)
  - 메일 제목/본문 입력 필드 (Froala 에디터 포함)
  - 제출 버튼
- props로 주입받는 auth-specific 항목:
  - `onSubmit: (input) => Promise<void>` — 호출자가 mutation 주입
  - `canEditTemplate: boolean` — 템플릿 편집 가능 여부
  - `showSmsOption: boolean` — SMS 발송 옵션 노출 여부
  - `initialTemplates?: MailTemplate[]` — 초기 템플릿 목록
- `useMyInfo`, `useIsTravelPartner` 등 admin 전용 훅 의존성 제거

**Admin 페이지 마이그레이션**

- 기존 예약 상세 페이지의 `#reservation-date-change` 섹션을 신규 공용 폼 컴포넌트로 교체한다.
- `sendReservationDateChangeRequestByAdmin` mutation을 `onSubmit`으로 주입한다.
- SMS 옵션, 템플릿 편집 등 admin 전용 기능은 props로 활성화한다.

**토큰 기반 신규 페이지**

- `/travel-partner/reservations/redirect?type=Change` 진입 시 리다이렉트 대신 공용 폼 컴포넌트를 렌더링한다.
- `TravelPartnerReservationsRedirect/reducer.ts`의 상태 머신에 변경 요청 플로우 상태 추가:
  - `waitingChange` → `requestingChange` → `changeSuccess` / `changeError`
- `skipAuth: true` 컨텍스트로 신규 mutation `requestReservationDateChangeByPartnerToken` 호출
- props 설정:
  - `canEditTemplate: true` (파트너가 자신의 예약이므로)
  - `showSmsOption: false` (인증 컨텍스트 없음)
- 성공 시 `StatusView.tsx`의 success UI를 재사용하며, 기존 승인 플로우와 동일한 CTA 노출

**에러 처리**

- 토큰 만료, 재사용, 예약 상태 불일치 등 에러 케이스별 사용자 메시지 정의
- 재사용된 토큰은 기존 승인 플로우와 동일한 에러 메시지 패턴 사용

### 백엔드 요구사항

**공용 서비스 계층 유지 및 재사용**

현재 `reservation-date-change-request-history.service.ts` 내부의 auth-agnostic 로직을 그대로 신규 usecase에서 재사용한다.

- `validationService.checkBaseConditionForSendRequest()` — 예약 상태/날짜 검증
- `validationService.validateDateChangeLimit()` — 180일 범위 등 날짜 검증
- `reservationMailService.sendMailToRequestChangeReservationDate()` — 유저에게 변경 요청 메일 발송
- `ReservationDateChangeRequestHistory.createDomainForAdmin()` — 이력 도메인 생성
- 이메일 템플릿: `reservation-request-date-change-v2.builder.ts` 재사용

위 메서드들은 auth 정보 없이 동작하므로 신규 usecase에서 그대로 호출 가능하다. 향후 검증 룰/메일 내용/이력 스키마가 변경되면 양쪽 플로우에 자동 반영된다.

**신규 Mutation 추가**

- 이름: `requestReservationDateChangeByPartnerToken`
- 가드: `skipAuth: true` (기존 `approveReservationByPartnerToken`과 동일 패턴)
- Input:
  - `actionToken: string`
  - `reservationId: number`
  - `mailSubject?: string`
  - `mailContent: string`
  - `dateSuggestions: ReservationDateChangeRequestDateSuggestionInput[]` (start, isAllDay)
- 처리 순서:
  1. `ReservationPartnerActionTokenService`로 토큰 검증 (type === CHANGE, 미사용 상태, 24h 이내)
  2. 토큰의 reservationId와 input의 reservationId 일치 검증
  3. 예약 조회 및 관계 로드
  4. 공용 validationService 호출 (상태/날짜 검증)
  5. 공용 reservationMailService로 유저에게 변경 요청 메일 발송
  6. 이력 생성 — `writerCode`는 예약의 partnerId에서 추출
  7. 예약 상태 업데이트: `setDateChangeRequestStatus(ADMIN_REQUESTED)`
  8. 토큰 사용 처리 (`markAsUsed`)

**Usecase 구조**

```
send-by-admin.usecase.ts (기존, 리팩토링)
  → 공용 서비스 호출

send-by-partner-token.usecase.ts (신규)
  → 토큰 검증 + 공용 서비스 호출
```

기존 `reservation-date-change-request-history.service.ts`의 `sendReservationDateChangeRequestByAdmin` 메서드를 shared service 기반으로 분리하여, 양쪽 usecase가 동일한 내부 로직을 호출하도록 한다.

**이메일 템플릿**

- 기존 `reservation-request-date-change-v2.builder.ts` 그대로 사용
- 파라미터(`reservationCode`, `spotName`, `requestedDate`, user `name`) 변경 없음

**액션 토큰 인프라**

- 기존 `ReservationPartnerActionTokenService.generateToken()`이 이미 `ReservationPartnerActionType.CHANGE` 타입을 지원함 — 추가 작업 불필요
- 기존 토큰 발급 로직(`talk-template.reservation-confirm-required.service.ts`) 변경 없음

**로깅/이벤트**

- 기존 Admin 플로우의 이벤트 발행(`event emit for tracking`)과 동일한 이벤트를 토큰 플로우에서도 발행
- 토큰 기반 요청임을 구분할 수 있는 메타데이터(`source: 'partner-token'`) 추가 고려
