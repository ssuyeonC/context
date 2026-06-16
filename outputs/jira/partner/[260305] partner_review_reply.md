# 세부 기획안: 파트너 스팟 리뷰 답글 작성 기능

## 배경

### 문제 정의

- 현재 스팟 리뷰에 대한 답글 작성은 어드민(ADMIN/SUPER_ADMIN) 권한을 가진 내부 직원만 가능
- 슈피리어 파트너(TRAVEL_PARTNER_SUPERIOR)가 자신의 스팟에 달린 리뷰를 직접 확인하고 답글을 작성할 수 있는 방법이 없음
- 파트너가 리뷰에 직접 응대할 수 없어 고객 커뮤니케이션 속도와 품질에 한계가 존재

### 가설적 임팩트

- 파트너가 리뷰에 직접 답글을 작성함으로써 고객과의 소통 속도 개선
- 파트너의 적극적인 리뷰 응대를 통해 고객 만족도 및 리뷰 신뢰도 향상
- 리뷰 답글의 자동 번역 기능으로 다국어 리뷰에 대한 응대 장벽 해소

---

## 구현

### 유저 플로우

**어드민 계정 (내부 직원)**

1. 어드민이 회원 관리에서 `TRAVEL_PARTNER_SUPERIOR` 등급 회원의 상세 모달을 연다.
2. '파트너 권한 관리' 영역에서 '리뷰 답글 작성 권한' 토글을 활성화한다.
3. 해당 파트너에게 리뷰 답글 작성 권한이 부여된다.

**파트너 계정 (TRAVEL_PARTNER / TRAVEL_PARTNER_SUPERIOR)**

1. 파트너 계정으로 어드민 페이지에 로그인한다.
2. 좌측 메뉴에서 '스팟 리뷰 관리' 메뉴를 클릭한다.
3. 자신의 거래처에 연결된 스팟의 리뷰 목록이 노출된다.
4. 리뷰 row를 클릭하면 [스팟 리뷰 답글 작성] 모달이 열린다.
5. (리뷰 답글 작성 권한이 있는 TRAVEL_PARTNER_SUPERIOR만) 답글 작성 영역에서 답글을 입력한다.
6. 필요시 '자동 번역' 버튼을 클릭하여 입력한 답글을 리뷰 언어로 번역한다.
7. 답글을 저장한다.

---

### 프론트엔드 요구사항

#### 어드민

##### 1. 파트너 권한 관리 토글 추가

**대상 파일**: `MemberDetailModal.tsx`, `PartnerPermissionToggle.tsx`

- 회원 등급이 `TRAVEL_PARTNER_SUPERIOR`인 회원의 [회원정보 상세] 모달 내 '파트너 권한 관리' 영역에 **'리뷰 답글 작성 권한'** 토글 추가
  - 기존 토글 항목 (예약 변경 권한, 예약 거절 요청 권한, 예약 시간 관리 권한)과 동일한 UI/UX
  - `PartnerPermissionType`에 새로운 권한 타입 추가 필요 (예: `REVIEW_REPLY`)
  - `PERMISSION_FIELD_MAP`에 새로운 매핑 추가 (예: `hasReviewReply`)

##### 2. 사이드바 메뉴 - '스팟 리뷰 관리' 메뉴 추가

**대상 파일**: `Nav.tsx`

- 현재 '스팟 리뷰 관리' 메뉴의 `authLevels`가 `ADMIN_AND_SUPER_ADMIN`으로 설정되어 있음
- 파트너 계정(`TRAVEL_PARTNER`, `TRAVEL_PARTNER_SUPERIOR`)으로 로그인 시에도 좌측 메뉴에 '스팟 리뷰 관리' 메뉴가 노출되도록 변경
  - `authLevels`를 `TRAVEL_WITH_ADMIN` 등으로 변경하거나, 파트너 전용 메뉴 섹션에 별도 항목 추가

##### 3. 스팟 리뷰 목록 - 파트너 전용 필터링

**대상 파일**: `SpotReviews` 페이지 관련 컴포넌트

- 파트너 계정으로 접근 시, **거래처(Partnership)가 해당 파트너로 연결된 스팟의 리뷰만** 목록에 노출
  - 기존 어드민용 테이블 구성(컬럼, 정렬 등)은 동일하게 유지
  - row 클릭 시 동작(리뷰 상세 모달 오픈)도 동일하게 유지
- Partnership → Contract → ContractHasSpot → Spot 관계를 통해 파트너 소유 스팟 필터링

##### 4. 스팟 리뷰 상세 모달 - 답글 작성 영역 조건부 노출

**대상 파일**: `SpotReviewDetailModal.tsx`

- [스팟 리뷰 답글 작성] 모달 내 '답글 작성' 영역의 노출 조건:
  - 회원 등급이 `TRAVEL_PARTNER_SUPERIOR`이면서 **'리뷰 답글 작성 권한'이 True**인 경우에만 노출
  - `TRAVEL_PARTNER` 등급 또는 권한이 없는 `TRAVEL_PARTNER_SUPERIOR`의 경우 답글 작성 영역 숨김 처리 (리뷰 조회만 가능)
  - 어드민 계정(`ADMIN`, `SUPER_ADMIN`)은 기존과 동일하게 답글 작성 가능

##### 5. 스팟 리뷰 상세 모달 - 자동 번역 버튼 추가

**대상 파일**: `SpotReviewDetailModal.tsx`

- 답글 작성 영역에 **'자동 번역' 버튼** 추가
  - 버튼 클릭 시 입력된 답글 텍스트를 해당 리뷰의 `language` 값(리뷰 작성 언어)으로 자동 번역
  - 번역 결과를 답글 입력 필드에 반영
  - 번역 중 로딩 상태 표시
  - 답글이 비어있는 경우 버튼 비활성화 처리

#### 유저페이지

##### 6. 리뷰 답글 제목 작성자 유형별 분기

**대상 파일**: `SpotReviewAdminReply.tsx`, 다국어 번역 파일 (`locales/*/common.json`)

- 현재 리뷰 답글은 작성자와 무관하게 `spot.review-reply-admin` ("Admin Reply") 제목으로 표시됨
- 답글 작성자의 역할에 따라 제목을 분기 처리:
  - **어드민 작성 답글**: 기존 `spot.review-reply-admin` 유지 (예: "Admin Reply")
  - **파트너 작성 답글**: 신규 번역 키 `spot.review-reply-partner` 적용 (예: "Partner Reply")
- 답글의 `writer` 정보에서 작성자 역할(level)을 조회하여 분기
  - `SpotReviewAdminReply` GraphQL fragment에 작성자 역할 정보 추가 필요

---

### 백엔드 요구사항

#### 1. 파트너 권한 타입 추가

**대상 파일**: `partner-permission` 모듈

- `PartnerPermissionType` enum에 리뷰 답글 작성 권한 추가
  - 예: `REVIEW_REPLY = 'REVIEW_REPLY'`
- `partner_permission` 테이블에서 새로운 권한 타입 저장/조회 지원
- 기존 `setPartnerPermission` mutation에서 새로운 권한 타입 처리

#### 2. 파트너용 스팟 리뷰 조회 API

- 파트너 계정으로 리뷰 목록 조회 시, 해당 파트너의 거래처에 연결된 스팟의 리뷰만 반환하도록 필터링 로직 추가
  - Partnership → Contract → ContractHasSpot → Spot → SpotReview 경로로 필터링
- 기존 어드민용 리뷰 조회 API를 확장하거나 파트너 전용 쿼리 추가

#### 3. 파트너의 리뷰 답글 작성 권한 검증

- 리뷰 답글 생성/수정 API 호출 시, 파트너 계정인 경우:
  - `TRAVEL_PARTNER_SUPERIOR` 등급 검증
  - `REVIEW_REPLY` 권한 보유 여부 검증
  - 해당 리뷰가 파트너 소유 스팟에 속하는지 검증

#### 4. 답글 자동 번역 API

- 답글 텍스트와 대상 언어를 입력받아 번역 결과를 반환하는 API
  - 기존 번역 인프라(번역 서비스)가 있다면 이를 활용
  - 입력: 원문 텍스트, 대상 언어 코드
  - 출력: 번역된 텍스트

#### 5. 리뷰 답글 작성자 역할 정보 제공

- 리뷰 답글(children) 조회 시, 작성자(writer)의 역할(level) 정보를 함께 반환
  - 유저페이지에서 답글 제목을 "Admin Reply" / "Partner Reply"로 분기하기 위해 필요
  - 기존 `spotReview` 쿼리의 `children.writer` 필드에 `level` 추가

---

## 참고

### 현재 파트너 권한 관리 구조

| 권한 타입 | 필드명 | 설명 |
|-----------|--------|------|
| `RESERVATION_DATE_CHANGE_REQUEST` | `hasReservationDateChangeRequest` | 예약 변경 권한 |
| `RESERVATION_REJECT_REQUEST` | `hasReservationRejectRequest` | 예약 거절 요청 권한 |
| `PRODUCT_DEADLINE_MANAGEMENT` | `hasProductDeadlineManagement` | 예약 시간 관리 권한 |
| **`REVIEW_REPLY` (신규)** | **`hasReviewReply`** | **리뷰 답글 작성 권한** |

### 관련 회원 등급

| 등급 | 코드 | 리뷰 메뉴 접근 | 답글 작성 |
|------|------|----------------|-----------|
| `TRAVEL_PARTNER` | 56 | O (조회만) | X |
| `TRAVEL_PARTNER_SUPERIOR` | 57 | O | 권한 토글 True인 경우만 |
| `ADMIN` | 90 | O | O |
| `SUPER_ADMIN` | 99 | O | O |

### 유저페이지 답글 제목 분기

| 답글 작성자 역할 | 번역 키 | 표시 (EN) |
|-----------------|---------|-----------|
| `ADMIN` / `SUPER_ADMIN` | `spot.review-reply-admin` | Admin Reply |
| `TRAVEL_PARTNER_SUPERIOR` | `spot.review-reply-partner` (신규) | Partner Reply |

### 거래처-스팟 관계 구조

```
Partnership (거래처)
    └─ Contract (계약)
        └─ ContractHasSpot (계약-스팟 매핑)
            └─ Spot (스팟)
                └─ SpotReview (스팟 리뷰)
```
