# CX 검색 예약 상세 URL 동기화

## 배경
### 문제 정의

현재 CX 검색(`/cx-search`) 페이지에서 예약내역을 조회하고 "자세히 보기"로 상세 모달을 열어도, URL이 변경되지 않아 해당 화면 상태를 다른 사람에게 공유할 수 없다.

CX 담당자 간 특정 예약 건에 대해 커뮤니케이션할 때, 해당 예약을 직접 검색해야 하는 불편함이 있다.

### 가설적 임팩트

예약 상세 모달이 열린 상태를 URL로 공유할 수 있으면, CX 담당자 간 특정 예약 건에 대한 커뮤니케이션 효율이 개선된다. URL을 클릭하면 cx-search 페이지에서 해당 예약 모달이 바로 열리므로, 별도의 검색 과정 없이 즉시 맥락을 공유할 수 있다.

## 구현
### 유저 플로우

**예약 상세 모달 열기 → URL 변경**
- CX 담당자가 `/cx-search`에서 예약을 검색한다.
- 조회 결과에서 "자세히 보기" 버튼을 클릭하면 예약 상세 모달이 열린다.
- 모달이 열리면 URL이 `/cx-search?reservationId={id}&domainType={type}`으로 변경된다.

**URL 공유 → 모달 자동 오픈**
- 다른 CX 담당자가 공유받은 URL(`/cx-search?reservationId=123&domainType=Reservation`)에 접속한다.
- cx-search 페이지가 로드된 후, URL의 `reservationId`와 `domainType` 파라미터를 읽어 해당 예약 상세 모달이 자동으로 열린다.

**모달 닫기 → URL 복원**
- 모달을 닫으면 URL에서 `reservationId`, `domainType` 파라미터가 제거되어 `/cx-search` 상태로 복귀한다.
- 기존 검색 파라미터(`domainIdSearch`, `userSearch` 등)가 있었다면 해당 파라미터는 유지된다.

### 프론트엔드 요구사항

**FR-1. 모달 오픈 시 URL 파라미터 추가**
- "자세히 보기" 버튼 클릭 시 `reservationId`와 `domainType`을 URL 쿼리 파라미터에 추가
- 기존 `cxSearchStore`의 `syncStoreWithURL()` 패턴 활용하여 `history.replaceState()`로 URL 갱신
- 지원 domainType: `Reservation`, `StayReservation`, `Insurance`, `LanguageCourse`

**FR-2. URL 파라미터 기반 모달 자동 오픈**
- 페이지 마운트 시 URL에 `reservationId`와 `domainType`이 있으면 해당 예약 상세 모달을 자동으로 오픈
- `CXReservationModal` 컴포넌트의 기존 domainType별 분기 로직을 그대로 활용
- 예약 데이터 조회가 필요하므로, `reservationId`로 해당 도메인의 쿼리를 실행하여 모달에 데이터 전달

**FR-3. 모달 닫기 시 URL 파라미터 제거**
- 모달 닫힘 시 URL에서 `reservationId`, `domainType` 파라미터 제거
- 기존 검색 관련 파라미터(`domainIdSearch`, `userSearch`, `page`, `limit`)는 유지

### 백엔드 요구사항

백엔드 변경사항 없음. 기존 예약 조회 쿼리를 그대로 활용한다.
