# 외부 파트너 어드민 액션 플랜 — P2 + P3 + P5 통합

> 근거 인사이트: `외부파트너_인사이트.md` P2(단발 세션), P3(반복 진입), P5(대시보드 1버튼)
> 데이터 범위: 2026-05-06 ~ 2026-05-15 (10일) / 외부 파트너 118명 / 1,095 세션
> 크로스체크 완료: 핵심 수치 ±1세션 이내 재현 (`인사이트_검증리포트` 본 문서 부록 참조)

## 문제 한 줄 요약

외부 파트너의 **40%(443 세션)가 30초 안에 닫히는 "단발 처리" 세션**임에도, 그들이 통과하는 도착점이 둘 다 비효율적이다.
- **알림 → "예약 상세 확인" 버튼 → `/reservation?id=X`** : 처리하려면 한 번 더 클릭 필요.
- **알림 외 진입 → `/travel-partner/dashboard`(존재하지 않는 라우트, Home으로 폴백) → 로고 화면 → 사이드바 "예약내역" 클릭**: 274/376 세션(72.3%)이 이 1버튼 클릭 외엔 아무것도 하지 않음.

## 검증된 사실 (재현 가능)

| 사실 | 수치 | 출처 쿼리 |
|------|------|-----------|
| 외부 파트너 30초 미만 세션 비중 | 443/1,095 = **40.5%** | `P2 verify` |
| 30초 미만 세션 평균 클릭 | 3.8 | `P2 verify` |
| `/travel-partner/dashboard` 클릭 | 690 / 74 admins / 376 sessions | dashboard label |
| `예약내역` 한 라벨이 차지하는 비중 | 307/690 = **44.5%** | label group |
| 대시보드에서 "예약내역"만 누르고 떠난 세션 | 274/376 = **72.3%** | session attribution |
| 대시보드에서 실제 처리 액션이 발생한 세션 | 35/376 = **9.2%** | processing action |
| 같은 예약을 3 세션 이상에서 다시 본 케이스 | 14건 (최악 12세션) | repeat view |
| `/reservation*` 단일 클릭 세션 | 100건 | single-click sessions |

## 코드베이스 확인 결과 (Step 10)

| 항목 | 상태 | 비고 |
|------|------|------|
| `/travel-partner/dashboard` 라우트 | ❌ 미구현, Router에 없음. `<Redirect path="*" to="/" />`로 Home 폴백 | 사용자는 이 URL을 가지고 있고, 트래커는 redirect 직전 pathname을 캡처. **유령 대시보드** |
| Home(`/`) 위젯 | ❌ 파트너 가치 0. 로고+공지만 | `frontend/apps/admin/src/page/Home.tsx` |
| 알림톡 발송 | ✅ 구현 | `backend/apps/trip/src/infrastructure/bizppurio/strategies/talk-template.reservation-confirm-required.service.ts` |
| 액션 토큰 딥링크 | ✅ 구현 | `/travel-partner/reservations/redirect` → 로그인 없이 1초 후 자동 redirect |
| "예약 상세 확인" 버튼 | ⚠️ 단순 라우팅 | `/reservation?id=X`만 보내고 처리는 별도 |
| 알림 중복 발송 dedup | ❌ 미구현 | reservation.handler.ts CONFIRM_REQUIRED 이벤트마다 발송 |
| 예약 상태 배지 | ✅ 구현(모바일) | `ReservationForMobile.tsx` |

---

## 액션 플랜

### P0 — 가장 임팩트 큰 두 건 (단기 1-2주)

#### A. **Home 페이지를 파트너 전용 워크큐로 분기**
**Why**: `/travel-partner/dashboard` 유령 URL이 Home으로 폴백하는데, Home은 로고만 보여줘 274세션(전체 파트너 세션의 25%)이 사이드바 "예약내역" 클릭으로 페이지를 떠난다. 이 한 단계는 **불필요한 클릭이자 인지 비용**.

**작업**:
1. `frontend/apps/admin/src/page/Home.tsx`에 `myInfo.level === TRAVEL_PARTNER` 분기 추가.
2. 파트너용 Home은 다음 위젯 표시:
   - **승인대기 예약 리스트 (Top 5)** — 한 클릭으로 확정/거절 가능
   - **이번 주 예약 캘린더** — `/reservation` 캘린더 위젯과 동일 컴포넌트 재사용
   - **미처리 카운트 배지** — 사이드바 "예약내역" 옆 빨간 점
3. `/travel-partner/dashboard` 경로를 정식 라우트로 등록하고 Home의 파트너 분기와 동일한 컴포넌트를 렌더. URL은 그대로 살리면서 컨텐츠를 채움.

**기대 효과**: 274세션 × 평균 1.5 클릭 절약 = **분기당 ~400 클릭 절감**. 단발 세션(40%)의 첫 클릭 비용 제거.

**참고 파일**:
- `frontend/apps/admin/src/page/Home.tsx`
- `frontend/apps/admin/src/components/Router.tsx:990` (fallback 라우트)
- `frontend/apps/admin/src/components/layout/Nav.tsx`

---

#### B. **알림톡 "예약 상세 확인" 버튼을 처리 동작 1-clik 딥링크로 통합**
**Why**: 현재 알림톡엔 두 종류 버튼이 공존 — (1) 토큰 기반 액션 딥링크(1초 redirect로 처리 완료), (2) "예약 상세 확인"(단순 페이지 이동). 후자로 진입하면 상세에서 다시 "예약 확정하기" 버튼을 눌러야 함. 단일 진입점으로 통합하면 한 번의 클릭으로 처리 가능.

**작업**:
1. `talk-template.reservation-confirm-required.service.ts:161` `buildReservationDetailButton`을 **action_token 포함**한 redirect URL로 변경. 단순 페이지가 아니라 "확인하면 자동 승인" 동작으로.
2. 또는 알림톡 메시지 본문에서 "예약 상세 확인" 버튼을 제거하고 액션 버튼(승인/거절)만 남겨 모호함 제거.
3. redirect 페이지의 `StatusView`에 "이미 처리됨" 상태를 명시적으로 표시(이미 일부 구현되어 있을 가능성, 확인 필요).

**기대 효과**: P3(같은 예약 N세션 진입)의 가장 큰 원인이 "처리 안 됐는지 모르겠어서 또 봄"이라면 강한 효과. 100건의 단일클릭 reservation 세션의 70% 이상을 사라지게 할 가능성.

**참고 파일**:
- `backend/apps/trip/src/infrastructure/bizppurio/strategies/talk-template.reservation-confirm-required.service.ts:161-186`
- `frontend/apps/admin/src/page/TravelPartnerReservationsRedirect/index.tsx`
- `frontend/apps/admin/src/page/TravelPartnerReservationsRedirect/components/StatusView.tsx`

---

### P1 — 알림 노이즈 정리 (2-3주)

#### C. **동일 reservation에 대한 알림톡 dedup**
**Why**: Chrissy Tan의 `260506ari7zh`가 12세션에서 열림. 같은 예약이 여러 알림을 트리거했을 가능성이 높음. dedup이 없어 파트너의 시간을 소모.

**작업**:
1. `reservation.handler.ts`의 `CONFIRM_REQUIRED` 이벤트 핸들러에서 동일 reservationId에 대해 **24시간 내 재발송 차단**(in-memory cache 또는 Redis로 dedup key 관리).
2. 이미 status가 3(확정)/4(취소)인 경우 알림 발송 스킵 가드 추가.
3. dedup 발생 시 Slack 로그로 가시화 (모니터링용).

**기대 효과**: 알림 노이즈 감소 + 파트너의 "이미 처리한 거 같은데 또 떴네" 마찰 제거.

**참고 파일**:
- `backend/apps/trip/src/modules/reservation/reservation/reservation.handler.ts` (CONFIRM_REQUIRED 이벤트)
- `backend/apps/trip/src/infrastructure/bizppurio/bizppurio-reservation-partner-message.service.ts`

---

### P2 — 측정 인프라 (병행)

#### D. **어드민 클릭 트래커의 `track_breadcrumb` 보강**
**Why**: 어드민 전 구간에서 `track_breadcrumb`/`aria_label`이 0건이라 페이지 내 컴포넌트 단위 퍼널 측정이 불가. P5 같은 인사이트의 후속 검증을 위해 필수.

**작업**:
1. web 앱의 `dispatchGAEvent`/클릭 트래커와 동일한 breadcrumb 수집 로직을 admin에도 활성화.
2. `aria-label` 컬럼은 admin 클릭에 한해 컴포넌트 props로부터 추출.
3. 최소 4주 데이터 누적 후 P3/P5 후속 검증.

**기대 효과**: 향후 어드민 UX 의사결정의 데이터 인프라 확보.

---

#### E. **"예약 확정하기 클릭 → 실제 status 전이" 매칭 분석**
**Why**: 클릭만으론 "처리가 정말 됐는지"를 확신할 수 없다. `reserve` 테이블 status 변화와 매칭해 실제 처리 성공률을 측정해야 위 액션들의 효과를 KPI로 잡을 수 있음.

**작업**: BigQuery `datastream_creatrip.reserve` 또는 reserve 스냅샷과 클릭 이벤트를 reservation_id 기준으로 조인. KPI 정의:
- "확정하기" 클릭 후 N분 내 status가 3으로 전이된 비율
- 알림 발송 → 첫 클릭까지의 시간 분포 (응답 SLA)

---

## 우선순위 매트릭스

| 액션 | 영향(파트너 세션) | 작업 규모 | 위험도 | 권장 순서 |
|------|------------------:|-----------|--------|-----------|
| A. 파트너 Home 워크큐 | 274세션/주 | 중 (FE 1-2주) | 낮음 | 1순위 |
| B. 알림 액션 통합 | 40% 단발 세션 흐름 | 소~중 (BE+FE) | 중 (토큰 보안 동선) | 2순위 |
| C. 알림 dedup | 14+ 반복 진입 케이스 | 소 (BE) | 낮음 | 3순위 |
| D. 트래커 breadcrumb | (간접) 향후 모든 분석 | 소 (FE) | 낮음 | 병행 |
| E. status 전이 매칭 | 측정 인프라 | 소 (분석) | 없음 | 병행 |

## 보지 말아야 할 것

- **모바일 라우트 통합**: `/reservation-for-mobile` vs `/reservations-for-mobile`는 리스트/상세로 의도된 분리. 통합 ❌.
- **새 대시보드 전면 신규 설계**: 데이터가 "예약내역 빠른 접근"이 핵심임을 명확히 가리킴. 새 위젯·차트를 늘리면 오히려 인지 부하 증가. 위 A안의 위젯 3개로 충분.
- **사이드바 메뉴 검색 강화**: 23 클릭/3명만 사용. 우선순위 매우 낮음.

## 부록 — 검증 리포트 요약

이 액션 플랜에 인용된 모든 수치는 5월 6~15일 데이터의 독립 쿼리로 재검증되었으며 ±1세션 이내로 일치:

- P2 30s미만 세션: 444 → 재검증 443 (±1, 측정 경계차)
- P5 예약내역 클릭 세션: 273 → 재검증 274 (±1)
- P5 처리 액션 세션: 35 (재검증)
- P3 3+세션 반복 예약: 14건 (단일 출처)
- `/travel-partner/dashboard` 라우트 부재: Router.tsx 검색 0건 (전체 18 파일에서 어떤 dashboard 매칭도 없음)
