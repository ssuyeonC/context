# 세부 기획안 요구사항 문서 양식

## 배경
### 문제 정의

현재 파트너 권한 시스템에서 '리뷰 답글 권한(REVIEW_REPLY)'과 '예약 시간 관리 권한(PRODUCT_DEADLINE_MANAGEMENT)'은 계정 등급이 `TRAVEL_PARTNER_SUPERIOR`(57)인 파트너만 사용할 수 있으며, 관리자가 어드민에서 토글로 개별 허용해야 활성화된다.

이로 인해 `TRAVEL_PARTNER`(56) 등급의 파트너는 해당 기능을 사용할 수 없고, `TRAVEL_PARTNER_SUPERIOR` 등급이더라도 관리자가 별도로 권한을 부여해야만 사용 가능하다.

두 권한 모두 모든 파트너가 기본적으로 사용할 수 있어야 하는 기능으로 판단되어, 등급 및 개별 권한 설정 없이 모든 파트너에게 개방하도록 변경이 필요하다.

### 가설적 임팩트

- 파트너 온보딩 프로세스 간소화: 관리자가 개별 권한을 설정하는 단계가 제거됨
- 파트너 기능 접근성 향상: `TRAVEL_PARTNER` 등급 파트너도 리뷰 답글 작성 및 예약 시간 관리가 가능해짐
- 운영 부담 감소: 관리자가 파트너별로 권한 토글을 관리할 필요 없음

## 구현
### 유저 플로우

**변경 전:**
1. 관리자가 어드민에서 `TRAVEL_PARTNER_SUPERIOR` 등급 파트너의 상세 모달을 열고, '리뷰 답글 권한' / '예약 시간 관리 권한' 토글을 켜야 해당 파트너가 기능 사용 가능
2. `TRAVEL_PARTNER` 등급 파트너는 해당 기능 사용 불가

**변경 후:**
1. 모든 파트너(`TRAVEL_PARTNER`, `TRAVEL_PARTNER_SUPERIOR`)가 별도 권한 설정 없이 리뷰 답글 작성 및 예약 시간 관리 기능 사용 가능
2. 어드민 파트너 상세 모달에서 '리뷰 답글 권한' / '예약 시간 관리 권한' 토글 UI 제거

### 프론트엔드 요구사항

**어드민 - 파트너 권한 토글 UI 변경**

- 파일: `frontend/apps/admin/src/components/member/partner/PartnerPermissionToggle/PartnerPermissionToggle.tsx`
- 파일: `frontend/apps/admin/src/components/member/partner/PartnerPermissionToggle/constants.ts`
- 파일: `frontend/apps/admin/src/components/member/MemberDetailModal.tsx`

| 항목 | 변경 내용 |
|------|----------|
| 리뷰 답글 권한 토글 | 어드민 파트너 상세 모달에서 제거 |
| 예약 시간 관리 권한 토글 | 어드민 파트너 상세 모달에서 제거 |
| 나머지 토글(예약 변경 요청, 예약 거절 요청) | 기존 유지 |

> 참고: 권한 토글이 2개만 남게 되므로, `PARTNER_PERMISSION_TOGGLE_LIST`(constants.ts)에서 `REVIEW_REPLY`, `PRODUCT_DEADLINE_MANAGEMENT` 항목을 제거

### 백엔드 요구사항

**1. 권한 체크 로직 변경**

- 파일: `backend/apps/trip/src/modules/partner-permission/service/partner-permission-checker.service.ts`

| 메서드 | 현재 로직 | 변경 후 |
|--------|----------|---------|
| `canReplyReview()` | `TRAVEL_PARTNER_SUPERIOR`만 허용 + DB 권한 레코드 확인 | 모든 파트너(`isPartner`) 허용, DB 확인 불필요 |
| `canManageProductDeadline()` | `TRAVEL_PARTNER_SUPERIOR`만 허용 + DB 권한 레코드 확인 | 모든 파트너(`isPartner`) 허용, DB 확인 불필요 |

**2. 리뷰 답글 권한 적용 위치**

- 파일: `backend/apps/trip/src/modules/spot/spot-review/spot-review.service.ts`
- 메서드: `verifyPartnerReplyPermission()` — `canReplyReview()` 호출부이므로 checker 변경 시 자동 반영

**3. 예약 시간 관리 권한 적용 위치**

- 파일: `backend/apps/trip/src/modules/time-slot/graphql/time-slot.resolver.ts`
- `updateTimeSlot` 뮤테이션의 `@Roles` 데코레이터에 `TRAVEL_PARTNER` 추가 필요
- `canManageProductDeadline()` 호출부이므로 checker 변경 시 권한 체크는 자동 반영

**4. GraphQL 권한 설정 뮤테이션**

- 파일: `backend/apps/trip/src/modules/partner-permission/graphql/partner-permission.resolver.ts`
- `setPartnerPermission` 뮤테이션: `REVIEW_REPLY`, `PRODUCT_DEADLINE_MANAGEMENT` 타입에 대한 설정 요청 시 무시하거나, 해당 타입을 설정 불가로 처리 (나머지 2개 권한은 기존대로 유지)

**5. 기존 DB 데이터 처리**

- `partner_permission` 테이블에 기존에 부여된 `REVIEW_REPLY`, `PRODUCT_DEADLINE_MANAGEMENT` 레코드는 더 이상 참조되지 않음
- 데이터 정리 마이그레이션(선택): 기존 레코드 삭제 여부는 운영 판단에 따름
