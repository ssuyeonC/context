# 공용화장실 POI 지도 노출

## 배경

### 문제 정의

위치기반 지도 페이지(`/map`)에서 제공하는 POI가 크리에이트립 상품(스팟, 숙소)과 편의시설(올리브영, 다이소 등)에 한정되어 있어, 여행자에게 실질적으로 필요한 생활 인프라 정보가 부족함.

특히 공용화장실은 한국 여행 중 빈번하게 필요하지만 위치를 찾기 어려운 정보로, 이를 지도에 제공하여 서비스의 실용성을 높이고자 함.

[공중화장실 정보 Open API](https://www.data.go.kr/data/15155058/openapi.do#/API%20%EB%AA%A9%EB%A1%9D/info)를 통해 전국 공용화장실 데이터(약 50,000건)를 확보하여, 기존 Place 테이블에 통합 관리함.

### 가설적 임팩트

- 지도 페이지의 실용성 향상으로 사용 빈도 증가
- 여행 중 지도 페이지 재방문율 개선

---

## 구현

### 유저 플로우

**필터 미선택 상태 (모든 POI 노출)**

- 줌 >= 최소 줌 레벨: 화장실 POI가 다른 POI와 함께 노출
- 줌 < 최소 줌 레벨: 화장실 POI 비노출 (다른 POI는 정상 노출)

**화장실 POI가 노출되지 않는 줌 레벨에서 '화장실' 필터 선택 시**

- 줌을 화장실 최소 줌 레벨로 자동 설정 후 화장실 POI 노출

**화장실 POI가 노출되는 줌 레벨에서 '화장실' 필터 선택 시**

- 화장실 POI 바로 노출

**화장실 필터 미선택 상태에서 줌 아웃 시**

- 줌 < 최소 줌 레벨이 되면 화장실 POI 자연스럽게 비노출

**화장실 필터 선택 상태에서 줌 아웃 시**

- 줌 < 최소 줌 레벨이 되면 화장실 필터 자동 해제
- 다른 필터가 함께 선택되어 있는 경우, 화장실 필터만 해제 (다른 필터는 유지)

### 프론트엔드 요구사항

**필터 추가**

- URL 필터명: `publicrestroom`
- `URL_FILTERS` 배열에 추가
- `URL_FILTER_TO_PLACE_TYPE`에 `publicrestroom → PlaceType.PublicRestroom` 매핑 추가
- 필터 라벨 i18n 추가
- 마커 아이콘 추가

**줌 레벨 기반 노출 제어**

- 최소 줌 레벨(`PUBLIC_RESTROOM_MIN_ZOOM`): 이 줌 레벨 이상일 때 화장실 POI가 노출됨
  - 구체적인 값은 실제 데이터를 지도에 올린 뒤 여러 줌 레벨에서 반복 테스트하며 결정
  - 뷰포트에 과도한 수의 화장실 POI가 노출되지 않는 적정 수준으로 설정
  - 상수로 분리하여 조정이 용이하도록 관리
- 줌 < 최소 줌 레벨일 때 화장실 쿼리 skip 처리
- 화장실 필터 선택 시 줌 자동 조정 로직 추가
- 줌 아웃 시 화장실 필터 자동 해제 로직 추가

**기존 인프라 활용**

- `useNearbyPlaces` 훅의 기존 타입 필터링 로직 활용
- 기존 클러스터링 로직(`clustering.ts`) 그대로 적용
- 뷰포트 기반 페칭 방식 유지

### 백엔드 요구사항

**PlaceType 확장**

- `PlaceType` enum에 `PUBLIC_RESTROOM` 추가
- `findNearbyFacilities`의 허용 타입에 `PUBLIC_RESTROOM` 추가

**데이터 임포트**

- 데이터 소스: [공중화장실 정보 Open API](https://www.data.go.kr/data/15155058/openapi.do#/API%20%EB%AA%A9%EB%A1%9D/info)
- Open API 데이터를 place 테이블에 임포트하는 마이그레이션 작성 (기존 `20251106_import_facility_places.ts` 패턴 참고)
- 필터 조건: `SE_NM`이 "공중화장실" 또는 "개방화장실"인 데이터만 대상

**필드 매핑**

| Open API 필드 | 설명 | Place 매핑 |
|---|---|---|
| `RESTRM_NM` | 화장실 이름 | `koreanTitle` |
| `WGS84_LAT` | 위도 | `latitude`, `location` (PostGIS POINT), `geohash` |
| `WGS84_LOT` | 경도 | `longitude`, `location` (PostGIS POINT), `geohash` |
| `SE_NM` | 구분 | 필터 조건으로만 사용 |
| `OPN_HR_DTL` | 운영시간 | `place_trans.openTimeInfo` |
| `MALE_TOILT_CNT` | 남자화장실 수 | `originalSourceJsonString` (JSON) |
| `FEMALE_TOILT_CNT` | 여자화장실 수 | `originalSourceJsonString` (JSON) |

**성능 고려사항**

- 50,000건 추가 시에도 기존 geohash 인덱스 + 타입 필터로 쿼리 성능 영향 미미
- 현재 `findNearbyFacilities`의 limit 상한(100)이 초밀집 지역에서 부족할 경우 상한 조정 검토
