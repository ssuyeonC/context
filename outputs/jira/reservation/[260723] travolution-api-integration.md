# 세부 기획안 요구사항 문서 — 트래볼루션(Bank of Trip) API 연동

## 배경

### 문제 정의
- 트래볼루션(공급사, API 브랜드명 **Bank of Trip** / `bankoftrip.com`)이 크리에이트립에 B2B로 공급하는 티켓·예약 상품은 현재 **어드민에서 수동으로 주문을 확정·부킹**하고 있다.
- 이 수동 처리 때문에 **크리에이트립 주문 생성 시점 → 트래볼루션 시스템 반영까지 6시간~+1일 이상** 지연이 발생한다(공급사 실측 기준).
- 지연으로 인해 (1) 즉시발권 가능한 티켓 상품도 실시간 바우처를 못 주고, (2) 예약 상품은 인벤토리·마감 관리가 수동이라 오퍼레이션 부담이 크다.

### 연동 목적 (확정 사항)
- 공급사와의 **API 연동으로 주문 전달·확정·상태 동기화를 자동화**한다. (연동 진행은 확정됨)
- 즉시발권(티켓) 상품: 주문 즉시 확정 → **실시간 바우처 발송**으로 리드타임 단축.
- 예약 상품: 스케줄·재고 조회 및 공급사 승인/거절 결과를 자동 수신 → **어드민 수동 부킹 공수 절감**.
- 대상 범위: 인스턴트 티켓뿐 아니라 **예약·재고관리가 필요한 상품 전체**를 지향(공급사 제안). 실제 롤아웃 단위·순서는 구현 요구사항에서 정의.

---

## 연동 대상

### 대상 상품 (개발환경 매핑 완료 · 2026-03-19 기준)
공급사가 dev 환경에 아래 상품을 매핑해 두었다. 각 상품은 **상품유형(Ticket/Booking)** 이 다르며, 이 유형에 따라 주문 흐름이 갈린다(아래 "상품 유형별 주문 흐름" 참고).

| 상품 | product UID | 유형 |
|---|---|---|
| [Seoul] NANTA Show Ticket (홍대/명동 극장) | 117 | Booking |
| [Jeju] Aqua Planet Discount Ticket | 2 | Ticket |
| [Seoul] COEX Aquarium (SEA LIFE) Ticket | 4 | Ticket |
| [Seoul] Hanboknam 경복궁점 Hanbok Rental | 18 | Ticket |
| [Seoul] Yeouido Han River E-land Ferry Cruise | 43 | Booking |
| [KORAIL PASS] KTX Unlimited Boarding Pass (2~5인 그룹) | 373 | Booking |
| [Busan] Centum Spa Land Discount Ticket | 1435 | Booking |

> 위 목록은 dev 테스트용 매핑이며, 실제 연동 상품 범위는 공급사와 확정 필요. NANTA(117)는 실적표에 없는 테스트 상품.

### 상품 식별 체계 (매핑 키)
공급사 상품은 **3단 UID 구조**로 식별된다. 크리에이트립 상품/옵션과 이 3키를 잇는 **매핑 테이블**이 연동의 핵심 데이터 작업이다.

- **product UID** → 상품 단위 (예: NANTA = 117)
- **option UID** → 옵션 단위 (예: 홍대극장 = 1035, 명동극장 = 1034)
- **unit UID** → 요금/좌석 단위 (예: 홍대극장 A석 = 1385, S석 = 1386, VIP석 = 1387)

예시(코레일패스, product 373): `4일 셀렉트 SAVER Pass` = option 1246 → `Person` = unit 1693.

---

## 시스템 연동 규격

### 인증 / 환경
- **인증**: API Key 방식. (개발환경 Key는 공급사 전달 완료 / 문서에 헤더 이름·전달 포맷 미명시 → 확인 필요 항목 참고)
- **baseURL**: 개발 `https://dev.bankoftrip.com` / 운영 `https://www.bankoftrip.com` (HTTPS)
- **개발환경 어카운트**: `partner@creatrip.com` (콘솔 `dev.bankoftrip.com`)
- **API 가이드**: https://docs.bankoftrip.com (한국어 https://docs.bankoftrip.com/v1.1.4-korean), 최신 버전 v1.1.4
- **권한**: 승인된 파트너만 호출 가능.

### API 엔드포인트 (연동 순서)
| 단계 | 기능 | 경로 | 비고 |
|---|---|---|---|
| 1 | 상품 조회 | `/api/lookup/products` | |
| 2 | 옵션 조회 | `/api/lookup/options` | |
| 3 | 가격/단위 조회 | `/api/lookup/units` | |
| 4 | 스케줄·재고 조회 | `/api/lookup/booking-schedules` | **예약(Booking) 상품 전용** |
| 5 | 주문 필수 추가정보 조회 | `/api/lookup/booking-additional-info` | **예약(Booking) 상품 전용** |
| 6 | 주문 생성 | `/api/orders/create` | 유형별 분기: `/ticket`, `/booking`, `/pass-and-package` |
| 7 | 주문 조회 | `/api/orders/lookup` | |
| 8 | 주문 취소 | `/api/orders/cancel` | |

> HTTP 메서드·요청/응답 스키마·rate limit·에러코드는 각 버전 엔드포인트 상세 페이지에서 확정 필요.

### 상품 유형별 주문 흐름
연동 설계의 핵심. 유형에 따라 주문 확정 시점과 필요한 사전 호출이 다르다.

**① Ticket (즉시발권)** — 제주 아쿠아플라넷, COEX 아쿠아리움, 한복남
1. 상품(1) → 옵션(2) → 가격/단위(3) 조회
2. 주문 생성 `/api/orders/create/ticket`
3. **즉시 확정 → 실시간 바우처 발급/전달**

**② Booking (예약·재고관리)** — 크루즈, 코레일패스, 센텀스파, 난타
1. 상품(1) → 옵션(2) → 가격/단위(3) 조회
2. **스케줄·재고 조회(4)** + **주문 필수 추가정보 조회(5)** ← 예약 상품만 필수
3. 주문 생성 `/api/orders/create/booking`
4. **공급사 승인 대기** → 웹훅으로 `BOOKING_ACCEPTED` / `BOOKING_REJECTED` 수신 후 확정/거절 처리 (즉시 확정 아님)

**③ Pass & Package**: `/api/orders/create/pass-and-package` (코레일패스 등 패스류 별도 생성 경로 존재 — 대상 상품별 어느 create 경로를 쓰는지 매핑 시 확정)

### 웹훅 (파트너 구현 필수)
공급사 → 크리에이트립 서버로 **주문 상태 변경을 HTTPS POST**로 통지한다. 크리에이트립이 수신 엔드포인트를 구현하고 URL을 `dev@bankoftrip.com`에 등록·승인받아야 한다.

- **이벤트 종류**: `BOOKING_ACCEPTED`(예약 승인), `BOOKING_REJECTED`(예약 거절), `CANCELED`(전체 취소), `PARTIAL_CANCELED`(부분 취소), `REDEEMED`(사용 완료), `RESTORED`(사용 취소·복구)
- **페이로드**(JSON): `eventType`, `createdAt`(ISO 8601), `data { orderNumber(TV로 시작하는 공급사 주문번호), referenceNumber(크리에이트립 주문번호), dateAt }`
- **보안**: `Authorization` Bearer 토큰(옵션, 파트너 제공) + `x-nonce`(재전송·변조 방지용 일회성 난수)
- **수신 요구**: HTTPS 전용, JSON 처리 가능한 엔드포인트. 로컬 테스트는 ngrok 등 활용.
- **재시도 정책**: 문서 미기재 → 확인 필요. 전송 이력은 공급사 콘솔의 웹훅 전송 이력 페이지에서 확인 가능.

---

## 구현 요구사항

### 데이터 / 매핑 (백엔드)
- 공급사 3단 UID(`product / option / unit`)와 **크리에이트립 상품·옵션·요금 단위를 잇는 매핑 테이블**을 설계·구축한다.
- 상품별로 **어느 주문 생성 경로(`ticket` / `booking` / `pass-and-package`)를 사용하는지**를 매핑 데이터에 함께 보관한다.
- 매핑은 상품 추가/변경에 대비해 **데이터로 관리**(하드코딩 금지)한다. 공급사가 신규 어트랙션·체험 상품을 지속 확대 공급할 예정이므로 매핑 확장이 용이해야 한다.

### 주문 생성 플로우 (백엔드)
- 크리에이트립 주문 생성 시, 대상 상품의 매핑·유형에 따라 다음을 수행한다.
  - **Ticket**: 가격/단위 확인 후 `/orders/create/ticket` 호출 → 즉시 확정 처리 → 바우처 발급 트리거.
  - **Booking**: `/lookup/booking-schedules`로 스케줄·재고 확인, `/lookup/booking-additional-info`로 필수 추가정보 수집 → `/orders/create/booking` 호출 → **"승인 대기" 상태로 보류**.
- 주문 생성 요청에 크리에이트립 주문번호를 `referenceNumber`로 전달하여 웹훅 매칭 키로 사용한다.
- 예약 상품의 **재고 부족·마감** 응답에 대한 유저/어드민 처리 흐름을 정의한다.

### 주문 상태 동기화 / 웹훅 수신 (백엔드)
- 웹훅 수신 엔드포인트(HTTPS, JSON)를 구현하고 URL을 공급사에 등록한다.
- `x-nonce` 기반 **중복 수신 방지(멱등 처리)** 를 구현한다. (동일 이벤트 재전송 대비)
- 이벤트별 크리에이트립 주문 상태 매핑:
  - `BOOKING_ACCEPTED` → 예약 확정
  - `BOOKING_REJECTED` → 예약 거절/실패 처리(환불·CS 연계)
  - `CANCELED` / `PARTIAL_CANCELED` → 전체/부분 취소 반영
  - `REDEEMED` → 사용 완료 처리
  - `RESTORED` → 사용 완료 복구(미사용 상태로)
- 기존 **수동 부킹 상태 모델과의 정합**을 맞춘다(자동 연동 주문과 수동 주문이 공존하는 과도기 고려).

### 취소 / 환불
- 크리에이트립발 취소 시 `/api/orders/cancel` 호출로 공급사 취소를 연동한다.
- 공급사발 취소(`CANCELED`/`PARTIAL_CANCELED`) 수신 시 크리에이트립 취소·환불·CS 흐름과 연결한다.
- 예약 상품의 **취소·환불 정책(기한·수수료)** 을 공급사와 확정해 반영한다.

### 어드민 / 오퍼레이션
- 자동 연동으로 전환되는 상품은 **수동 부킹 단계를 제거/축소**하되, 예약 상품의 승인 대기·거절 건은 어드민에서 상태 확인·개입이 가능해야 한다.
- 연동 실패(호출 오류·타임아웃·거절) 시 **폴백(수동 처리) 경로**를 유지한다.

### 프론트엔드 (유저 노출)
- 즉시발권(Ticket) 상품은 주문 완료 후 **실시간 바우처 발급/전달**을 유저에게 노출한다.
- 예약(Booking) 상품은 **승인 대기 → 확정** 상태를 유저에게 명확히 안내한다(기존 예약 상태 UI 정합).

---

## 확인 필요 사항 (공급사 문의 / TBD)

**공급사(트래볼루션)에 확인**
- API Key **전달 헤더 이름·포맷**, 공통 요청/응답 스키마, rate limit, 에러코드 체계
- 웹훅 **재시도 정책 / 멱등성 처리 책임 범위**(nonce 기반 중복 제거의 우리 구현 범위)
- 예약 상품 **취소·환불 정책**(기한·수수료)과 CS 흐름 매핑
- 상품별 **주문 생성 경로**(ticket / booking / pass-and-package) 확정
- 실제 **연동 대상 상품 범위**와 운영 전환(cutover) 계획

**내부 결정 (TBD)**
- 매핑 테이블 스키마·관리 주체
- 자동 연동 주문 ↔ 기존 수동 주문 **상태 모델 통합 방식**
- 웹훅 수신 서버 구현 위치
- 롤아웃 단위/순서(예: 즉시발권 티켓 우선 → 예약 상품 확장)

---

## 참고 자료
- API 가이드: https://docs.bankoftrip.com/v1.1.4-korean (llms 색인 https://docs.bankoftrip.com/llms.txt)
- 웹훅 연동: https://docs.bankoftrip.com/connecting-a-webhook.md
- 개발환경 콘솔: https://dev.bankoftrip.com (계정 `partner@creatrip.com`)
- 원본 메일: 트래볼루션 백향란(2026-03-24, 연동 규약·개발환경·매핑 상품 전달), 배인호 대표(2026-03-26, 전 상품 대상 연동 범위 제안)
- 첨부: `creatrip_products_api_list_20260319.xlsx` (dev 매핑 상품·UID 리스트)
- 공급사 개발 문의: dev@bankoftrip.com / +82-2-6264-1115
