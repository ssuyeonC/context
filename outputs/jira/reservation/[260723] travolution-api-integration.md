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

## 프로세스 변화 (현재 수동 → 연동 후)

이 연동의 목표는 **어드민이 손으로 공급사 시스템에 부킹·상태확인하던 과정을 API가 대신**하는 것이다. "자동화"의 정도는 상품 유형·상황에 따라 다르다.

### 유형별 처리 흐름 비교
| 단계 | 현재 (수동) | 연동 후 (자동) |
|---|---|---|
| 주문 접수 | 크리에이트립 주문 생성 | 동일 |
| **공급사 전달** | 어드민이 공급사 콘솔에 **수동 입력·부킹** | `POST /orders` **자동 전달** |
| **확정 (Ticket)** | 어드민 확인 후 바우처 수동 발급 | 응답 `voucherInfo`로 **즉시 자동 확정·발급** |
| **확정 (Booking)** | 공급사 승인 확인 → 크리에이트립에 **수동 반영** | 공급사 승인/거절을 **웹훅으로 자동 수신**해 상태 반영(PD→AC/RJ) |
| 사용/취소 반영 | 어드민이 수동 추적·반영 | `REDEEMED`/`CANCELED`/`PARTIAL_CANCELED` 웹훅 + `lookup` 대사로 자동 반영 |

### 자동화 범위·한계 (기대치 정렬)
- **Ticket(즉시발권)**: 거의 완전 자동. 주문=확정=바우처 발급이 실시간으로 일어나 사람 개입 사실상 불필요.
- **Booking(예약)**: "전달·상태동기화"는 자동화되나 **승인 자체는 공급사 몫**이다(자동 재고면 즉시, 아니면 공급사 담당자 처리). 우리가 손으로 옮겨 적던 일이 사라지는 것이지 승인 단계가 없어지는 것은 아니다.
- **사람이 계속 개입하는 구간**: 거절·실패·타임아웃 건의 어드민 확인 및 CS, 재고 부족/마감 안내, 취소·환불 정책 처리. → 정상 주문은 자동으로 흐르고 **예외만 사람이 본다.**
- **대상 제한**: 자동화는 **매핑된 상품에만** 적용된다. 미매핑 상품은 그대로 수동이며, 롤아웃도 단계적(티켓 우선 → 예약 확장)이라 전 상품이 한 번에 전환되지 않는다. 과도기엔 자동·수동 주문이 **공존**한다.

---

## 연동 대상

### 대상 상품 (개발환경 매핑 완료 · 2026-03-19 기준)
공급사가 dev 환경에 아래 상품을 매핑해 두었다. 각 상품은 **상품유형** 이 다르며, 이 유형에 따라 주문 흐름이 갈린다(아래 "상품 유형별 주문 흐름" 참고). 유형은 공급사 상품 조회 응답의 `type` 필드(**TK**=Ticket / **BK**=Booking / **PKG**=Package / **PAS**=Pass)로 확정된다. 아래 표의 유형은 기획 레벨 분류이며, 실제 `type`(특히 코레일패스는 PAS일 가능성)은 상품 조회로 확인한다.

| 상품 | product UID | 유형(기획) |
|---|---|---|
| [Seoul] NANTA Show Ticket (홍대/명동 극장) | 117 | Booking |
| [Jeju] Aqua Planet Discount Ticket | 2 | Ticket |
| [Seoul] COEX Aquarium (SEA LIFE) Ticket | 4 | Ticket |
| [Seoul] Hanboknam 경복궁점 Hanbok Rental | 18 | Ticket |
| [Seoul] Yeouido Han River E-land Ferry Cruise | 43 | Booking |
| [KORAIL PASS] KTX Unlimited Boarding Pass (2~5인 그룹) | 373 | Booking/Pass |
| [Busan] Centum Spa Land Discount Ticket | 1435 | Booking |

> 위 목록은 dev 테스트용 매핑이며, 실제 연동 상품 범위는 공급사와 확정 필요. NANTA(117)는 실적표에 없는 테스트 상품.

### 상품 식별 체계 (매핑 키)
공급사 상품은 **3단 UID 구조**로 식별된다. 크리에이트립 상품/옵션과 이 3키를 잇는 **매핑 테이블**이 연동의 핵심 데이터 작업이다.

- **product UID** → 상품 단위 (예: NANTA = 117), 상품 조회 응답에 `type`(TK/BK/PKG/PAS) 포함
- **option UID** → 옵션 단위 (예: 홍대극장 = 1035, 명동극장 = 1034)
- **unit UID** → 요금/좌석 단위 (예: 홍대극장 A석 = 1385, S석 = 1386, VIP석 = 1387)

예시(코레일패스, product 373): `4일 셀렉트 SAVER Pass` = option 1246 → `Person` = unit 1693.

---

## 시스템 연동 규격

### 인증 / 환경
- **인증**: 모든 요청에 `Authorization` 헤더로 API 액세스 토큰 전달 + `Content-Type: application/json`. (토큰 포맷 — `Bearer` 접두사 유무 — 만 확인 필요)
- **baseURL**: 개발 `https://dev.bankoftrip.com` / 운영 `https://www.bankoftrip.com` (HTTPS), 공통 경로 prefix **`/api/partner/v1.1`**
- **개발환경 어카운트**: `partner@creatrip.com` (콘솔 `dev.bankoftrip.com`)
- **API 가이드**: https://docs.bankoftrip.com (한국어 https://docs.bankoftrip.com/v1.1.4-korean), 최신 버전 v1.1.4
- **권한**: 승인된 파트너만 호출 가능.

### API 엔드포인트 (연동 순서)
실제 API는 `/api/partner/v1.1/` 하위 리소스 기반(RESTful) 구조다. 주문 생성은 상품유형별로 URL이 갈리지 않고 **단일 `POST /orders`** 이며, 유형은 상품 `type`으로 결정된다.

| 단계 | 기능 | 메서드·경로 | 비고 |
|---|---|---|---|
| 1 | 상품 조회 | `GET /api/partner/v1.1/products` (상세 `/{productUid}`) | 응답 `type`으로 유형 구분 |
| 2 | 옵션 조회 | `GET /api/partner/v1.1/products/{productUid}/options` | |
| 3 | 가격/단위 조회 | `GET .../options/{optionUid}/units` | |
| 4 | 스케줄·재고 조회 | `GET .../booking-schedules` | **Booking 전용** |
| 5 | 주문 필수 추가정보 조회 | `GET .../booking-additional-info/{additionalInfoUid}` | **Booking 전용**, BAC(공통)/TRV(여행자별) |
| 6 | 주문 생성 | `POST /api/partner/v1.1/orders` | **단일 엔드포인트**, 유형은 상품 `type`으로 분기 |
| 7 | 주문 조회 | `GET /api/partner/v1.1/orders/{orderNumber}` | referenceNumber로도 조회 |
| 8 | 주문 취소 | `DELETE /api/partner/v1.1/orders/{orderNumber}` | 주문 전체 단위 |

### 상품 유형별 주문 흐름
연동 설계의 핵심. 주문 생성은 단일 `POST /orders`이지만, 상품 `type`에 따라 사전 호출과 확정 시점이 다르다. 주문 생성 요청 body 공통 필드: `product`, `option`, `unitAmounts[{ unit, amount }]`, `referenceNumber`(선택, 최대 64자), `voucherSendType`(0~3), traveler 정보(name/email/number/nationality).

**① Ticket (TK · 즉시발권)** — 제주 아쿠아플라넷, COEX 아쿠아리움, 한복남
1. 상품(1) → 옵션(2) → 가격/단위(3) 조회
2. 주문 생성 `POST /orders`
3. **즉시 확정 → 응답의 `voucherInfo`로 실시간 바우처 발급/전달**

**② Booking (BK · 예약·재고관리)** — 크루즈, 센텀스파, 난타 (코레일패스는 유형 확인 필요)
1. 상품(1) → 옵션(2) → 가격/단위(3) 조회
2. **스케줄·재고 조회(4)** + **주문 필수 추가정보 조회(5)** ← 예약 상품만 필수
3. 주문 생성 `POST /orders` (`bookingDate`, `bookingTime`, `bookingAdditionalInfo` 포함)
4. **생성 직후 `bookingStatus=PD`(승인 대기)** → 웹훅으로 `BOOKING_ACCEPTED`(→ AC) / `BOOKING_REJECTED`(→ RJ) 수신 후 확정/거절 처리 (즉시 확정 아님)

**③ Pass & Package (PAS/PKG)**: `POST /orders` 사용, `option`은 `"PAS"`/`"PKG"`, product당 1 option·1 unit 제약. 코레일패스 등 패스류가 이 유형에 해당할 수 있음(상품 `type`으로 확정).

### 주문/예약 상태 값
- **주문 `status`**: `AV`(사용 가능) / `AP`(사용 완료) / `CR`(취소 요청) / `CL`(전체 취소) / `PC`(부분 취소) / `EP`(만료)
- **`bookingStatus`**(Booking 전용, nullable): `PD`(승인 대기) / `AC`(승인·확정) / `RJ`(거절)
- **바우처**: `voucherType`(1=주문당 1코드 / 2=unit당 1코드 / 3=파일/예약번호), `voucherInfo[{ product, option, unit, amount, codeType, voucherCode, voucherFile, voucherLink }]`, `validFrom` / `expiredAt` (상세는 아래 "바우처 발급 / 전달" 참고)

### 바우처 발급 / 전달
**바우처 발급도 API로 트리거된다.** 별도 발급 호출은 없고, 주문 생성 흐름에 실려 나온다.

- **상품별 바우처 구조는 상품 조회 응답에 박혀 있다.** `GET /products` (또는 `/products/{uid}`) 응답의 아래 필드로 상품마다 결정된다. `codeType`은 옵션 필드라 `?fields=codeType`로 요청해야 내려온다.
  - `type`(TK/BK/PKG/PAS) · `voucherType`(1/2/3) · `codeType`(PIN/1D/2D/File/ONVL) · `hasBookingAdditionalInfo`(Y/N) · `confirmDeadline`(예상 확정 리드타임: INSTANT / AFTER_ORDER+hours / BEFORE_TRAVEL_DATE-hours, **표시용 안내값·SLA 아님**)
  - 즉 **7개 dev 매핑 상품 각각의 실제 발급 구조는 dev API를 키로 조회해야 확정**된다(공개 문서엔 상품별 값이 없음).
- **발급 시점**
  - **Ticket(TK)**: `POST /orders` **응답에 `voucherInfo`가 즉시 포함** → 주문=확정=발급이 실시간.
  - **Booking(BK)**: 생성 직후 `bookingStatus=PD`(승인 대기) → **공급사 승인(AC) 후 바우처가 유효**해짐. 거절(RJ) 시 없음.
- **발송 방식 — `voucherSendType`(주문 생성 요청 파라미터)**: 공급사가 여행자에게 바우처를 직접 보낼지 여부를 지정
  - `0`: 발송 안 함(기본) → **파트너가 응답 `voucherInfo`를 받아 크리에이트립 채널로 자체 전달**
  - `1`: 이메일 발송 / `2`: 카카오 비즈메시징 발송 / `3`: 이메일+카카오
  - → 공급사 직발송 vs 크리에이트립 자체 발송 중 **정책적으로 선택 가능**(어느 쪽으로 갈지 내부 결정 필요).
- **바우처 형식 필드**
  - `codeType`: `PIN`(핀번호) / `1D`(바코드) / `2D`(QR) / `File`(파일) / `ONVL`(코드·파일 없는 수동 처리)
  - `voucherCode`(코드 문자열) / `voucherFile`(파일 링크) / `voucherLink`(Bank of Trip 생성 바우처 링크)
- **사용 통지**: 여행자가 바우처를 사용하면 `REDEEMED` 웹훅 수신 → 주문 `status` AP(사용 완료). 사용 취소·복구는 `RESTORED`.

### 웹훅 (파트너 구현 필수)
공급사 → 크리에이트립 서버로 **주문 상태 변경을 HTTPS POST(application/json)** 로 통지한다. 크리에이트립이 수신 엔드포인트를 구현하고 URL을 `dev@bankoftrip.com`에 등록·승인받아야 한다.

- **이벤트 종류**: `BOOKING_ACCEPTED`(예약 승인), `BOOKING_REJECTED`(예약 거절), `CANCELED`(전체 취소), `PARTIAL_CANCELED`(부분 취소), `REDEEMED`(사용 완료), `RESTORED`(사용 취소·복구)
- **페이로드**(JSON): `eventType`, `createdAt`(`YYYY-MM-DD HH:mm:ss`), `data { orderNumber(TV로 시작하는 공급사 주문번호), referenceNumber(크리에이트립 주문번호), dateAt }`
- **페이로드는 최소 정보만 담긴다** — 어느 unit·몇 개가 취소/사용됐는지 등 상세는 페이로드에 없으므로, 웹훅 수신 후 **`GET /orders/{orderNumber}` 재조회로 `unitAmounts`·`voucherInfo`·`status`를 대사**해 반영한다.
- **보안**: `Authorization` Bearer 토큰(옵션, 파트너 제공) + `x-nonce`(재전송·변조 방지용 일회성 난수, 필수)
- **수신 요구**: HTTPS 전용, JSON 처리 가능한 엔드포인트. 로컬 테스트는 ngrok 등 활용.
- **전송 이력**: 공급사 콘솔 웹훅 전송 이력 페이지에서 상태(In Progress / Success / Failure) 확인 가능.

---

## 구현 요구사항

### 데이터 / 매핑 (백엔드)
- 공급사 3단 UID(`product / option / unit`)와 **크리에이트립 상품·옵션·요금 단위를 잇는 매핑 테이블**을 설계·구축한다.
- 상품 `type`(TK/BK/PKG/PAS)은 상품 조회 응답으로 확인되므로, 주문 생성 경로를 매핑에 별도 저장할 필요는 없다(생성은 단일 `POST /orders`). 매핑엔 크리에이트립 ↔ 공급사 UID 대응만 보관한다.
- 매핑은 상품 추가/변경에 대비해 **데이터로 관리**(하드코딩 금지)한다. 공급사가 신규 어트랙션·체험 상품을 지속 확대 공급할 예정이므로 매핑 확장이 용이해야 한다.

### 주문 생성 플로우 (백엔드)
- 크리에이트립 주문 생성 시, 상품 `type`에 따라 다음을 수행한다.
  - **Ticket(TK)**: 가격/단위 확인 후 `POST /orders` 호출 → 즉시 확정 처리 → 응답 `voucherInfo`로 바우처 발급 트리거.
  - **Booking(BK)**: `booking-schedules`로 스케줄·재고 확인, `booking-additional-info`로 필수 추가정보 수집 → `POST /orders`(bookingDate 등) 호출 → **`bookingStatus=PD`(승인 대기)** 로 보류.
- 주문 생성 요청에 크리에이트립 주문번호를 `referenceNumber`(최대 64자)로 전달하여 웹훅·조회 매칭 키로 사용한다.
- 예약 상품의 **재고 부족·마감**은 주문 생성 시 `LOW_STOCK` / `LOW_STOCK_FOR_SCHEDULE` / `SCHEDULE_CLOSED` 에러로 수신되므로, 이 에러 기준으로 유저/어드민 처리 흐름을 정의한다.

### 주문 상태 동기화 / 웹훅 수신 (백엔드)
- 웹훅 수신 엔드포인트(HTTPS, JSON)를 구현하고 URL을 공급사에 등록한다.
- `x-nonce` 기반 **중복 수신 방지(멱등 처리)** 를 구현한다. (동일 이벤트 재전송 대비)
- 웹훅은 최소 페이로드이므로, 수신 즉시 **`GET /orders/{orderNumber}` 재조회로 상세 상태를 대사**한 뒤 크리에이트립 주문에 반영한다.
- 이벤트별 크리에이트립 주문 상태 매핑:
  - `BOOKING_ACCEPTED` → 예약 확정 (`bookingStatus` PD→AC)
  - `BOOKING_REJECTED` → 예약 거절/실패 처리 (PD→RJ, 환불·CS 연계)
  - `CANCELED` / `PARTIAL_CANCELED` → 전체/부분 취소 반영 (`status` CL/PC)
  - `REDEEMED` → 사용 완료 처리 (`status` AP)
  - `RESTORED` → 사용 완료 복구(미사용 상태로)
- 기존 **수동 부킹 상태 모델과의 정합**을 맞춘다(자동 연동 주문과 수동 주문이 공존하는 과도기 고려).

### 취소 / 환불
- 크리에이트립발 취소 시 `DELETE /orders/{orderNumber}` 호출로 공급사 취소를 연동한다(주문 전체 단위).
- 공급사발 취소(`CANCELED`/`PARTIAL_CANCELED`) 수신 시 `lookup` 대사 후 크리에이트립 취소·환불·CS 흐름과 연결한다.
- 취소 불가 조건은 `ORDER_EXPIRED` / `ORDER_ALREADY_USED` / `ORDER_ALREADY_CANCELLED` / `ORDER_CANNOT_BE_CANCELED` 에러로 내려오므로, 이 기준으로 취소 가능 시점을 처리한다. 예약 상품의 **취소·환불 정책(기한·수수료)** 문구는 공급사와 확정해 반영한다.

### 어드민 / 오퍼레이션
- 자동 연동으로 전환되는 상품은 **수동 부킹 단계를 제거/축소**하되, 예약 상품의 승인 대기·거절 건은 어드민에서 상태 확인·개입이 가능해야 한다.
- 연동 실패(호출 오류·타임아웃·거절) 시 **폴백(수동 처리) 경로**를 유지한다.

### 프론트엔드 (유저 노출)
- 즉시발권(Ticket) 상품은 주문 완료 후 **실시간 바우처 발급/전달**을 유저에게 노출한다.
- 예약(Booking) 상품은 **승인 대기(PD) → 확정(AC)** 상태를 유저에게 명확히 안내한다(기존 예약 상태 UI 정합).

---

## 확인 필요 사항 (공급사 문의 / TBD)

**공급사(트래볼루션)에 확인**
1. **rate limit 정책** — overview / responses / error 등 전 문서에 명시 없음. 호출 상한·재시도 설계 전제.
2. **웹훅 재시도 정책** — 문서상 자동 재전송을 별도로 운영하지 않는 것으로 보임(전송 이력에 Success/Failure/In-Progress 상태만 존재). 자동 재시도가 없다면 **파트너가 `GET /orders/{orderNumber}` 폴링으로 상태를 대사**해야 하므로, 이 전제가 맞는지 확정 필요.
3. **파트너발 부분취소 가능 여부** — 취소는 `DELETE /orders/{orderNumber}`로 **주문 전체 단위**다. `PARTIAL_CANCELED` 웹훅은 공급사발로 보이며, 파트너가 unit 단위 부분취소를 *요청*할 수 있는지는 취소 요청 body 스펙이 공개 문서에 없어 확인 필요(OpenAPI `partnerApi.json` 확인).

*(정책·기타)* 예약 상품 취소·환불 기한·수수료 문구, `Authorization` 토큰의 정확한 포맷(`Bearer` 접두사 유무).

**내부 결정 (TBD)**
- 매핑 테이블 스키마·관리 주체
- 자동 연동 주문 ↔ 기존 수동 주문 **상태 모델 통합 방식**
- 웹훅 수신 서버 구현 위치
- 롤아웃 단위/순서(예: 즉시발권 티켓 우선 → 예약 상품 확장)

---

## 참고 자료
- API 가이드: https://docs.bankoftrip.com/v1.1.4-korean (llms 색인 https://docs.bankoftrip.com/llms.txt)
- 주문 상태·웹훅 처리: https://docs.bankoftrip.com/api/order-status-and-webhook-handling.md
- 웹훅 연동: https://docs.bankoftrip.com/connecting-a-webhook.md
- OpenAPI 스펙: `partnerApi.json` (취소 body 등 공개 문서에 없는 스키마 확인용)
- 개발환경 콘솔: https://dev.bankoftrip.com (계정 `partner@creatrip.com`)
- 원본 메일: 트래볼루션 백향란(2026-03-24, 연동 규약·개발환경·매핑 상품 전달), 배인호 대표(2026-03-26, 전 상품 대상 연동 범위 제안)
- 첨부: `creatrip_products_api_list_20260319.xlsx` (dev 매핑 상품·UID 리스트)
- 공급사 개발 문의: dev@bankoftrip.com / +82-2-6264-1115
