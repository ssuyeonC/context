# 세부 기획안 요구사항 문서 양식

## 배경
### 문제 정의

랜딩페이지는 주로 행사나 이벤트를 진행하기 위해 만들어지고 있으나, 해당 스팟의 상세 페이지에서는 연결된 랜딩페이지(이벤트)의 존재를 유저가 인지할 수 없다.

스팟에 이벤트가 걸려 있더라도 유저가 이를 발견하지 못하면 이벤트 참여율이 낮아지고, 랜딩페이지의 노출 효과가 제한된다.

### 가설적 임팩트

스팟 상세 페이지에 연결된 랜딩페이지 진입점을 노출함으로써:

- 유저가 스팟에 걸린 이벤트/행사를 자연스럽게 인지하여 랜딩페이지 유입이 증가
- 이벤트 참여율 및 전환율 개선 기대
- 추가 광고/프로모션 노출 채널 확보

## 구현
### 유저 플로우

스팟 상세 페이지에 진입한 유저는, 해당 스팟에 연결된 랜딩페이지가 존재하고 다음 조건을 모두 만족할 경우 랜딩페이지 진입점을 볼 수 있다:
- 랜딩페이지의 **공개 여부**가 `true`
- 랜딩페이지의 **히든페이지** 설정이 `false`
- 유저가 보고 있는 스팟 상세 페이지의 **로케일**이 해당 랜딩페이지가 **생성된 언어**와 일치
- 해당 스팟에 대한 **비노출 설정**이 아님

하나의 스팟이 2개 이상의 랜딩페이지와 연결될 수 있으며, 이 경우 조건을 만족하는 모든 랜딩페이지 진입점이 노출된다.

랜딩페이지 설정 페이지에서 관리자는 랜딩페이지에 연결된 스팟 단위로 비노출 옵션을 설정할 수 있다. 비노출로 설정된 스팟에서는 해당 랜딩페이지 진입점이 노출되지 않는다.

### 프론트엔드 요구사항

**스팟 상세 페이지 (유저 앱)**

- 해당 스팟에 연결된 랜딩페이지 진입점 UI 노출
  - 노출 조건: 공개 여부 `true` + 히든페이지 `false` + 로케일 일치 + 비노출 설정 아님
  - 복수의 랜딩페이지가 조건을 만족하면 모두 노출
- 진입점 클릭 시 해당 랜딩페이지로 이동

- **노출 위치**: `SpotCommunityPostsLink` 바로 아래
- **UI 형태**: 텍스트 전용 카드 리스트 (아이콘/썸네일 없음)
  - 랜딩페이지에 별도 썸네일 필드가 없으므로 텍스트만으로 구성
  - 기존 `CommunityPostsLink`와 동일한 `bg-gray` + `rounded-lg` 스타일 유지
  - 카드 구성:
    - 1줄: `EVENT` 뱃지 + 기간 (`~ YYYY.MM.DD`, `isDisplayPeriod=true`일 때만 노출)
    - 2줄: 랜딩페이지 제목 (말줄임 처리)
    - 우측: 화살표(`›`) 아이콘
  - 복수 랜딩페이지는 카드를 수직으로 나열 (gap: 8px)
- **GA 이벤트**: Click / Impression
- **프로토타입**: `.context/outputs/prototypes/spot-landing-page-entry.html`

**랜딩페이지 설정 페이지 (어드민)**

- 연결된 스팟 리스트 컴포넌트 내부에 '비노출 스팟' 영역 추가
  - 기능 설명 텍스트 추가
  - '비노출 스팟' 영역에 추가할 수 있는 스팟은 해당 영역이 포함된 그룹에 포함된 스팟
- 스팟 단위로 비노출 옵션 토글 기능 추가
  - 비노출로 설정된 스팟의 상세 페이지에서는 해당 랜딩페이지 진입점이 노출되지 않음

### 백엔드 요구사항

**데이터 모델**

- `sub_landing_area_has_linked_domain` 테이블에 `is_hidden_on_spot_detail` 컬럼 추가
  - 타입: `BOOLEAN NOT NULL DEFAULT false`
  - 목적: 그룹-스팟 연결 단위로 스팟 상세페이지 내 해당 랜딩페이지 진입점 비노출 여부 관리
  - 별도 테이블 생성하지 않는 이유:
    - 비노출 여부는 "그룹-스팟 연결" 1건당 1개 값 → 기존 행의 속성
    - `priority`, `linked_domain_type` 등 연결 속성을 같은 테이블에 두는 기존 패턴과 일관
    - 조회 시 추가 JOIN 없이 WHERE 조건으로 필터링 가능
- `SubLandingAreaHasLinkedDomain` 엔티티에 `isHiddenOnSpotDetail: boolean` 필드 추가
- Sequelize 마이그레이션 생성: `pnpm migration:generate --name add-is-hidden-on-spot-detail-to-sub-landing-area-has-linked-domain`

**API — 유저향 (스팟 상세 조회)**

- 스팟 상세 조회 시 연결된 랜딩페이지 정보를 함께 반환하는 필드 추가
- 기존 `findAllByLinkedDomainIdAndType` 메서드를 활용하여 spotCode + `SPOT` 타입으로 역방향 조회
- 조건 필터링 (모두 AND):
  - `LandingArea.isPublish = true`
  - `LandingArea.isHidden = false`
  - `LandingArea.language` = 요청 로케일과 일치
  - `SubLandingAreaHasLinkedDomain.isHiddenOnSpotDetail = false`
- 반환 정보 (랜딩페이지당):
  - `id`: 랜딩페이지 ID
  - `title`: 랜딩페이지 제목
  - `periodTo`: 종료 기간
  - `isDisplayPeriod`: 기간 노출 여부
  - URL (기존 `LandingArea`의 라우팅 규칙에 따라 생성)

**API — 어드민향 (비노출 스팟 설정)**

- 비노출 설정 Mutation 추가:
  - `updateSpotDetailVisibilityForLinkedDomain(input: { subLandingAreaHasLinkedDomainId: ID!, isHiddenOnSpotDetail: Boolean! }): SubLandingAreaHasLinkedDomain`
  - 해당 그룹-스팟 연결 레코드의 `isHiddenOnSpotDetail` 값을 업데이트
  - 권한: `ADMIN`, `SUPER_ADMIN`
- 기존 `SubLandingArea` 조회 시 각 연결 도메인의 `isHiddenOnSpotDetail` 필드가 GraphQL 응답에 포함되도록 스키마 반영
- 비노출 설정 가능 범위: 해당 `SubLandingArea(그룹)`에 연결된 스팟만 대상 (다른 그룹의 스팟은 불가)
