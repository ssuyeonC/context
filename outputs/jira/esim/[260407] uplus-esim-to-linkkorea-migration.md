# 유플러스 eSIM → 링크코리아 파트너십 전환

## 배경
### 문제 정의

크리에이트립 eSIM 상품은 현재 두 개의 파트너를 통해 공급받고 있음:
- **LG U+**: 직접 API 연동 (OAuth2 인증, spot code 12898, 9개 상품)
- **링크코리아**: SKT eSIM 중개 (spot code 13043, 15개 상품)

유플러스와의 파트너십이 종료 확정되었으며, 기존에 SKT eSIM만 공급하던 링크코리아에서 LG U+ eSIM도 추가 공급받을 계획임 (2026-04-04 창우님 구두 전달)

이에 따라 유플러스 직접 API 연동을 제거하고, 링크코리아를 단일 eSIM 공급 파트너로 일원화하는 작업이 필요함

**현재 구조:**
```
크리에이트립 eSIM
├── LG U+ (직접 API 연동)
└── 링크코리아 (SKT 중개)
```

**변경 후 구조:**
```
크리에이트립 eSIM
└── 링크코리아 (단일 파트너)
    ├── SKT eSIM (기존)
    └── LG U+ eSIM (신규)
```

### 영향 범위

U+ 관련 SIM 스팟은 약 4개 존재하나(2개는 임시 예약 off 상태), 코드상 U+ API에 연동된 스팟은 **spot 12898 (LG U+ eSIM) 1개뿐**임.

| Spot Code | 상품명 | U+ API 연동 | 이번 작업 대상 |
|-----------|--------|:-----------:|:-------------:|
| 12898 | LG U+ eSIM | O | O |
| 12890 | LG U+ Data SIM (공항 수령) | X (오프라인 수령) | X |
| 기타 2개 | TBD (임시 예약 off) | X (코드 연동 없음) | X |

공항 수령형 물리 SIM(12890 등)은 API 자동 발급이 아닌 오프라인 프로세스이므로 이번 파트너십 전환과 무관함.
따라서 **코드 조치 대상은 spot 12898만 해당**.

### 가설적 임팩트

- 파트너 관리 단일화로 운영 복잡도 감소 (API 연동 2개 → 1개)
- U+ 직접 연동 관련 인프라/환경변수/에러 핸들링 코드 제거로 유지보수 비용 절감
- 향후 eSIM 상품 추가/변경 시 링크코리아 API 하나만 대응하면 되므로 확장성 향상

## 구현
### 유저 플로우

고객 관점에서 플로우 변화 없음. 예약 확정(CONFIRM) 시 자동으로 eSIM이 발급되는 기존 흐름 유지.

- 고객이 eSIM 상품을 구매 → 예약 생성
- 예약 확정(CONFIRM) → 백엔드에서 링크코리아 API 호출하여 eSIM 발급
- PDF 바우처(QR 코드 포함) 생성 → 고객에게 전달

### 프론트엔드 요구사항

프론트엔드 변경 없음. eSIM 발급은 백엔드에서 예약 확정 시 자동 트리거되며 고객 대면 UI 변경 불필요.

단, 어드민에서 U+ 관련 상품 관리 UI가 있다면 확인 필요. (TBD)

### 백엔드 요구사항

**1. U+ 직접 연동 제거**
- `backend/apps/trip/src/infrastructure/uplus/` 디렉토리 전체 삭제
  - `uplus.module.ts`, `uplus-request.service.ts`, `uplus-request.interface.ts`, `uplus-request.error.ts`, `uplus-request.constants.ts`
- `backend/apps/trip/src/modules/reservation/reservation/handle-special-cases/uplus-esim/` 디렉토리 전체 삭제
  - `uplus-esim.service.ts`, `uplus-esim.constants.ts`
- `reservation.module.ts`에서 `UPlusModule` import 및 `UPlusESIMService` provider 제거
- `handle-special-cases.service.ts`에서 spot code 12898 분기 로직 제거
- `env.ts`에서 U+ 관련 환경변수 제거 (`UPLUS_BASE_URL`, `UPLUS_CLIENT_ID`, `UPLUS_CLIENT_SECRET`, `UPLUS_USER_ID`, `UPLUS_PARTNER_CODE`, `UPLUS_CLIENT_IP`)

**2. 링크코리아 LG U+ 상품 추가**
- `link-korea.esim.constants.ts`에 LG U+ 상품 코드 → 사용 기간 매핑 추가
  - 신규 spot code 및 spot item code는 링크코리아 측 확정 후 반영 (TBD)
- 기존 링크코리아 서비스 로직이 LG U+ 상품도 동일하게 처리할 수 있는지 확인
  - 바우처 템플릿 분리 필요 여부 확인 (기존 `skt_esim_voucher` vs 신규 LG용 템플릿)
  - 링크코리아 API 요청 파라미터 차이 확인 (TBD - 링크코리아 API 스펙 확인 필요)

**3. 기존 U+ 상품(spot code 12898) 처리**
- 기존 U+ 상품의 판매 중단 처리 방식 결정 필요 (TBD)
- 이미 발급된 U+ eSIM 바우처의 유효기간 내 고객 대응 방안 (TBD)

**4. 테스트**
- `reservation-handle-special-cases.spec.ts` 업데이트: U+ 관련 테스트 제거 및 링크코리아 LG 상품 테스트 추가

**5. 인프라/배포**
- 환경변수에서 U+ 관련 값 제거 (스테이징/프로덕션)
- 링크코리아 측 LG 상품 API 연동 테스트 (스테이징 환경)
