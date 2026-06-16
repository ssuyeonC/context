# 세부 기획안: 어드민 스팟 '영업중' 자동 ON/OFF

## 배경

### 문제 정의

- 현재 어드민에는 '스팟 자동 공개/비공개' 기능(DatePicker + 토글)이 있지만, **'영업중' 상태**는 수동 토글로만 제어 가능
- 국가유산진흥원 등 상하반기 시즌 행사의 경우, 스팟 공개는 유지하면서 '영업중' 토글만 껐다 켜는 방식으로 운영 중
- 특정 시점(예: 3/16 14:00)에 여러 행사(5개 이상)를 동시에 오픈해야 하는 상황이 발생하며, 현재는 담당자가 각 행사 페이지를 띄워두고 정각에 수동으로 영업중 토글을 ON 처리
- 빈도가 높지는 않지만, 시즌에 몰리면 대응 실패 시 크리티컬한 이슈로 이어질 수 있음

### 가설적 임팩트

- 운영 리스크 제거: 수동 대응 실패로 인한 행사 미오픈 사고 방지
- 운영 효율 개선: 시즌별 다수 행사의 영업 시작/종료를 사전 예약하여 자동 처리

---

## 구현

### 유저 플로우

- 어드민 유저는 스팟 기본정보 페이지에서 '영업중 자동 시작' 날짜/시간을 설정하고 토글을 활성화하면, 해당 시점에 자동으로 `isInBusiness = true`가 된다.
- 어드민 유저는 스팟 기본정보 페이지에서 '영업중 자동 종료' 날짜/시간을 설정하고 토글을 활성화하면, 해당 시점에 자동으로 `isInBusiness = false`가 된다.
- 자동 영업 시작/종료는 독립적으로 설정 가능하며, 기존 '자동 공개/비공개' 기능과 동일한 UX를 따른다.

### 프론트엔드 요구사항

#### [어드민 스팟 상세 - 기본정보] 페이지

**자동 영업 시작 (Auto Open) 섹션**

- DatePicker + 토글 스위치 구성 (기존 '자동 공개' 섹션과 동일한 UI)
- 토글 ON 시 설정된 날짜/시간에 자동으로 영업중 상태 활성화
- 미래 날짜만 선택 가능 (과거/당일 validation)
- 토글 활성화 후 DatePicker 비활성화

**자동 영업 종료 (Auto Close) 섹션**

- DatePicker + 토글 스위치 구성 (기존 '자동 비공개' 섹션과 동일한 UI)
- 토글 ON 시 설정된 날짜/시간에 자동으로 영업중 상태 비활성화
- 미래 날짜만 선택 가능 (과거/당일 validation)
- 토글 활성화 후 DatePicker 비활성화

**UI 위치**: 기존 '영업중' 토글 근처 또는 자동 공개/비공개 영역 하단

**참고 구현**: 기존 `ToggleSpotAutoPublishedStatusSwitch`, `ToggleSpotAutoUnPublishedStatusSwitch` 패턴을 따라 구현

### 백엔드 요구사항

#### 1. 데이터 저장 — 필드 추가

- `spot` 테이블에 자동 영업 시작/종료 관련 컬럼 추가:
  - `is_auto_open` (boolean): 자동 영업 시작 활성화 여부
  - `auto_open_date` (datetime): 자동 영업 시작 예정 일시
  - `is_auto_close` (boolean): 자동 영업 종료 활성화 여부
  - `auto_close_date` (datetime): 자동 영업 종료 예정 일시
- DB 마이그레이션 작성

#### 2. GraphQL API

- mutation 추가:
  - `setSpotAutoOpenStatus(input: SetSpotAutoOpenStatusInput!): Spot!`
    - input: `spotCode`, `isAutoOpen`, `autoOpenDate`
  - `setSpotAutoCloseStatus(input: SetSpotAutoCloseStatusInput!): Spot!`
    - input: `spotCode`, `isAutoClose`, `autoCloseDate`
- 기존 `setSpotAutoPublishedStatus` / `setSpotAutoUnPublishedStatus` 패턴과 동일하게 구현
- 권한: 어드민/슈퍼어드민만 가능

#### 3. 스케줄러/배치 작업

- 예약된 날짜/시간 도래 시 `isInBusiness` 상태 자동 변경 로직 추가
- 기존 자동 공개/비공개 스케줄러 인프라 활용
- **시간 단위 정밀도 필요**: 기존 자동 공개/비공개가 날짜 단위(`YYYY-MM-DDT00:00:00`)라면, 이 기능은 시간 단위(예: 14:00 오픈)가 필요할 수 있으므로 스케줄러 주기 확인 필요

#### 참고: 기존 구현 위치
- 프론트: `frontend/apps/admin/src/components/spot/SpotBasicInfo/SpotBasicInfo.tsx`
- 백엔드 엔티티: `backend/apps/trip/src/modules/spot/spot/models/spot.entity.ts`
- 백엔드 서비스: `backend/apps/trip/src/modules/spot/spot/spot.service.ts`
- 백엔드 리졸버: `backend/apps/trip/src/modules/spot/spot/spot.resolver.ts`
