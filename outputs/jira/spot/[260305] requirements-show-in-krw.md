# Show in KRW 토글 기능 요구사항

## 배경

### 문제 정의

스팟 상세 페이지에서 옵션 가격이 외화(USD 등)로 표시되지만, 실제 현장 결제 금액은 한국 원(KRW)이다.
사용자가 실제로 현장에서 지불할 금액을 파악하기 어렵다는 불편이 있다.

### 가설적 임팩트

- KRW 가격 노출을 통해 사용자의 가격 이해도를 높여 전환율 개선 기대
- 현장 결제 금액에 대한 사전 인지로 CS 문의 감소 기대

## 구현

### 유저 플로우

1. 유저가 스팟 상세 페이지의 Options 섹션에 진입한다.
2. Options 헤더 우측에 "Show in KRW" 토글이 노출된다.
   - 단, 스팟 ID 14535, 11230에서는 토글이 노출되지 않는다 (하드코딩).
3. 유저가 토글을 ON으로 전환하면, 각 옵션의 판매가/혜택가 우측에 KRW 가격이 함께 노출된다.
   - 멤버십 적용 가격에는 KRW가 노출되지 않는다.
4. 유저가 토글을 OFF로 전환하면, 기존과 동일하게 외화 가격만 표시된다.
5. 토글 옆 정보 아이콘(ⓘ)을 클릭/호버하면 "The prices displayed may fluctuate slightly depending on the exchange rate." 툴팁이 노출된다 (번역 값 기저장).
6. 페이지 새로고침 시 토글 상태는 초기화된다 (OFF).

### 프론트엔드 요구사항

**토글 UI**

- Options 섹션 헤더("Options") 우측에 체크박스 토글 + "Show in KRW" 라벨 + ⓘ 아이콘 배치
- 기본 상태: OFF (체크 해제)
- 토글 상태는 컴포넌트 로컬 state로 관리 (페이지 이탈 시 초기화)

**토글 ON 시 가격 표시**

| 가격 항목 | KRW 노출 | 표시 예시 |
|-----------|---------|----------|
| 예약금 (Deposit) | O | `20.6 USD (KRW 30,000)` |
| 판매가 (Sale Price) | O | `199.14 USD (KRW 290,000)` |
| 원가 (Original Price, 취소선) | O | `~~274.68 USD~~ (KRW XX0,000)` |
| 멤버십 적용 가격 (Membership Price) | **X** | `12.36 USD` |

- KRW 금액은 천 단위 콤마 포맷 적용
- 외화 가격 우측에 괄호로 표시: `(KRW 30,000)`

**ⓘ 정보 아이콘**

- 툴팁 문구: "The prices displayed may fluctuate slightly depending on the exchange rate." (다국어 번역 값 기저장)

**제외 스팟 처리**

- 스팟 ID 14535, 11230은 토글 자체를 노출하지 않음 (프론트엔드 하드코딩)

### 백엔드 요구사항

**데이터 구조 (코드 확인 완료)**

- SpotItem 엔티티의 기본 가격 필드가 KRW 기준, SpotItemTrans의 `local~` 필드가 외화 기준
- `salePrice` (KRW 판매가): **필수** (>= 0, 기본값 0) → 항상 존재
- `originalPrice` (KRW 원가): **선택** (nullable) → 없을 수 있음
- 기존 API에서 KRW 가격 필드(`salePrice`, `originalPrice`)가 프론트엔드에 내려오는지 확인 필요
- 별도 백엔드 수정 없이 기존 필드를 활용할 수 있을 가능성 높음

**엣지 케이스**

- `originalPrice`가 null인 옵션: KRW 원가를 노출하지 않음 (판매가 KRW만 노출)
