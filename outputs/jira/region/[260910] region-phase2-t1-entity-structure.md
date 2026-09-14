# P2-T1 — 지역 엔티티 구조 정합 (스팟형 canonical + translation)

**요약** — 지역(region)을 스팟과 같이 canonical 엔티티 + 언어별 번역 구조로 정합한다. 생성 시 한국어 기준 번역을 함께 생성하고, 이후 지역 상세에서 다른 언어 번역을 추가하며, 공개 상태는 언어별로 독립 관리한다. **선행: Phase 1 T2·T3**

## 배경

- 현재 Region은 운영상 각 언어별로 별도의 Region을 생성·관리하는 구조여서 동일한 지역 정보와 공개 상태를 언어마다 반복 관리해야 하는 불편 존재
- 하나의 Region에 여러 언어의 번역값을 연결하는 구조로 변경하여, 공통 정보는 Region 단위로 관리하고 이름·설명·공개 상태 등은 번역별로 관리 필요
- 생성 시 한국어 번역을 기본으로 만들고 상세에서 다른 언어 번역을 추가하는 스팟형 관리 방식 적용
- 기존 `/tips/region-guide`는 조회 수가 적고 신규 `/region` 허브와 역할이 중복되므로 제거 필요

## 구현

### 유저 플로우

- 운영자는 언어 선택 없이 지역을 생성하고, 생성 시 한국어 기준 번역을 함께 생성
- 운영자는 지역 생성 완료 후 해당 지역 상세로 이동
- 운영자는 지역 상세의 언어 탭에서 번역이 없는 언어를 추가하고, 기존 번역 복사 또는 AI 번역으로 콘텐츠 입력
- 운영자는 각 언어 번역의 공개·비공개 상태를 독립적으로 설정
- 공개된 번역은 신규 `/region` 허브, 스팟·쿠폰 리스트의 지역 필터, 지도 마커, 검색·선택 드롭다운 등 모든 Region 탐색 영역에 노출
- 유저는 요청 언어의 공개된 지역 번역만 목록·검색·상세에서 조회
- 요청 언어 번역이 없거나 비공개인 경우 다른 언어 번역으로 대체 노출하지 않으며, 직접 상세 URL 접근도 허용하지 않음

### 프론트엔드 동시 변경 범위 (구조 전환 필수)

- 지역 생성 모달에서 **언어 선택** 영역 제거
- 지역 생성 모달에서 **공개 여부** 영역 제거
- 지역 생성 모달에 **지역은 한국어로 생성됩니다. 한국어를 입력해주세요.** 안내 노출
- 기존 **지도 뷰 공개 여부** 토글을 선택 언어 번역의 **공개** 토글로 교체
- 공개 토글 변경 시 선택 언어의 `isPublish`만 변경하고 다른 언어의 공개 상태는 유지
- 기존 `isShownMap`을 사용하는 어드민·유저 프론트엔드의 조회 조건과 파라미터를 `isPublish`로 일괄 변경
- `/tips/region-guide` 페이지를 제거하고, 기존 내부 진입점은 신규 `/region` 허브로 교체
- 언어 탭과 공통/번역 필드의 상세 화면 구성은 P2-T2에서 정의

### 백엔드 요구사항

- **`region`(canonical)** — 언어와 무관한 지역 정보 및 관계를 보유
    - 필드: slug·`city_slug`(→ Phase 1의 `region.city` FK)·`legal_location_legal_codes`·히어로/리스트 이미지·priority
    - 관계: `region_has_subway`·`region_has_detail_location`·카테고리 순서·이동쌍
- **`region_translation`(언어별)** — 언어별 콘텐츠와 상태를 보유
    - 텍스트: name·한 줄 소개·description·태그(라벨)·seo·persona 라벨/설명·역 부가설명
    - 기준어: `is_default`, 한국어 번역에 `true` 적용
    - AI 번역 여부: `is_translated_by_ai`
    - 공개 상태: `is_publish`, 해당 번역의 목록·필터·지도·검색·상세 노출 제어
- **지역 생성** — 스팟과 동일하게 `region`과 한국어 `region_translation`을 하나의 생성 흐름으로 처리
    - 한국어 번역을 `is_default=true`, `is_translated_by_ai=false`, `is_publish=false`로 생성
    - 번역 생성 실패 시 `region` 생성도 함께 롤백
- **공개 인터페이스 전환** — Region 공개 필드를 DB·ORM의 `is_publish`, GraphQL의 `isPublish`로 통일
    - DB·ORM의 `is_shown_map` 필드는 데이터 이관 후 제거
    - GraphQL 조회·필터 파라미터를 `isShownMap`에서 `isPublish`로 변경
    - 변경된 `isPublish` 파라미터를 사용하는 모든 호출부에 동일한 공개 판정 적용
- **언어별 공개 판정** — 요청 언어의 `region_translation.is_publish=true` + canonical 필수값 충족 + 해당 번역의 name·태그·description 충족 + 부모 CITY 활성화를 목록·필터·지도·검색·상세의 공통 노출 조건으로 적용. 한 줄 소개는 선택 입력
- **비공개 처리** — 요청 언어의 번역이 없거나 `is_publish=false`이면 다른 언어로 대체 노출하지 않고 직접 상세 URL 접근도 차단
- **AI 번역 생성** — 새 번역을 `is_translated_by_ai=true`, `is_publish=false`로 생성하고 운영자 검수 후 공개 가능
- **리뷰 노출 설정** — `is_shown_review`를 제거하고 `region_review` 테이블과 적재는 유지

### 데이터 마이그레이션

- **공개 상태 이관** — 각 `region_translation` 행의 새 `is_publish` 값을 기존 `is_shown_map` 값으로 설정
- **기존 값 제거** — 기존 `is_publish` 값은 승계·병합하지 않고 제거하며, `is_shown_map` 컬럼은 이관 완료 후 제거
- **언어별 독립성 유지** — 공개 값을 지역 단위로 병합하지 않고 각 번역 행의 기존 `is_shown_map` 값을 그대로 승계
- **`is_default` 지정** — 기존 `region_translation`에서 한국어 행을 기준어로 마킹, 한국어 행이 없는 지역은 예외 처리 대상 목록화
- **`is_translated_by_ai` 초기화** — 기존 번역은 AI 번역 여부를 확인할 근거가 없으면 `false`로 설정
- **오노출·유실 검수** — 마이그레이션 전후 각 언어에서 기존 `is_shown_map=true`였던 지역과 새 `is_publish=true`인 지역이 일치하는지 비교하고, 필터·지도·검색·상세 및 legal_code 기반 스팟 매칭을 검수

### 사람이 수행할 작업

- 기존 `is_shown_map=true` 지역과 새 `is_publish=true` 지역의 언어별 목록 비교 검수
- `/tips/region-guide`를 가리키는 내부 링크·메뉴·리다이렉트 경로를 신규 `/region` 허브로 교체했는지 검수
- 한국어 기준 번역 행이 없는 지역 확인·보정
- 기존 `is_publish=true`, `is_shown_map=false`처럼 충돌하는 데이터가 있는 경우 제거 대상인 기존 `is_publish` 값이 새 공개 상태에 영향을 주지 않는지 검수

## 수용 조건

- 지역 생성 시 언어 선택 영역과 공개 여부 영역이 노출되지 않음
- 지역 생성 시 `region`과 `is_default=true`, `is_publish=false`인 한국어 `region_translation`이 함께 생성됨
- 각 `region_translation.is_publish`가 해당 언어의 실제 공개 상태를 제어
- 기존 `region_translation.is_shown_map` 값이 동일 언어 행의 새 `is_publish` 값으로 정확히 이관되고, 기존 `is_publish` 값은 승계되지 않음
- `is_shown_map` 컬럼·GraphQL 필드·조회 파라미터가 제거되고 `is_publish`로 대체됨
- 특정 언어의 공개 상태를 변경해도 다른 언어의 공개 상태가 변경되지 않음
- 공개 상태가 신규 `/region` 허브, 스팟·쿠폰 리스트 지역 필터, 지도 마커, 검색·선택 드롭다운, Region 상세 접근에 공통 적용됨
- 요청 언어 번역이 없거나 비공개인 경우 다른 언어 번역이 대신 노출되지 않고 직접 상세 URL 접근도 허용되지 않음
- `/tips/region-guide` 페이지가 제거되고 기존 내부 진입점이 신규 `/region` 허브를 가리킴
- `region_translation`에 기준어(`is_default`)·AI 번역 플래그(`is_translated_by_ai`)가 존재하고, 한국어 번역이 기준어로 지정
- AI로 생성한 번역은 기본 비공개 상태로 생성되고 운영자가 언어별로 공개 가능
- 마이그레이션 후 기존 `is_shown_map=true`였던 언어별 지역의 탐색 노출이 의도치 않게 바뀌지 않음
- 리뷰 노출(`is_shown_review`) 토글이 제거되고 `region_review` 테이블·적재는 유지
