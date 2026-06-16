# 지도(/map) 지역 뷰 보기 - 좌표 판정 버그 수정

## 배경

### 문제 정의

지도(/map) 도메인의 '지역 뷰 보기' 기능이 정상 동작하지 않음

- 현재 조회 중인 지역의 중심점이 지역 폴리곤 안에 있어도 '지역 뷰 보기' 버튼이 노출되지 않는 경우가 많음
- 완전히 안 뜨는 것은 아니고, 폴리곤 경계선 근처(~100m 이내)에서만 간헐적으로 노출됨
- 원인은 백엔드의 `ST_Contains` 공간 쿼리 인자 순서가 반전되어 있어 1순위 판정 로직이 완전히 무효화된 상태이고, fallback 로직은 경계선 ~100m만 탐지하는 구조

### 가설적 임팩트

- 지역 뷰 기능이 사실상 폴리곤 경계선 근처에서만 작동하므로, 대부분의 유저가 지역 뷰를 경험하지 못하고 있음
- 수정 시 폴리곤 내부 전체에서 지역 뷰가 정상 노출되어 지역 기반 탐색 경험이 개선됨

## 구현

### 유저 플로우

1. 유저가 지도(/map)에서 특정 지역을 조회함
2. 지도 중심점이 지역 데이터의 폴리곤 내부에 있으면 '지역 뷰 보기' 버튼이 노출됨
3. 유저가 버튼을 토글하면 해당 지역 정보를 담은 패널이 노출됨

현재는 2단계에서 폴리곤 내부 판정이 실패하여 버튼이 노출되지 않는 상태

### 프론트엔드 요구사항

없음 (프론트엔드 변경 불필요. 백엔드 `regionByLocation` resolver의 응답이 정상화되면 기존 프론트엔드 로직으로 정상 동작)

### 백엔드 요구사항

`ST_Contains` 공간 쿼리 인자 순서 수정

- 파일: `backend/apps/trip/src/modules/legal-location/repos/legal-location.repo.ts`
- 메서드: `findOneByBoundaryContainsPoint` (line 46)
- 현재: `ST_Contains(POINT, boundary)` → "점이 폴리곤을 포함하는가" (항상 false)
- 수정: `ST_Contains(boundary, POINT)` → "폴리곤이 점을 포함하는가"

```diff
- ST_Contains(ST_GeomFromText('POINT(${longitude} ${latitude})'), boundary)
+ ST_Contains(boundary, ST_GeomFromText('POINT(${longitude} ${latitude})'))
```

호출 흐름:

```
regionByLocation (GraphQL resolver)
  → RegionService.getRegionByLocation
    → LegalLocationRetrieverService.getMostNearOneByCoords
      → 1순위: findOneByBoundaryContainsPoint  ← 항상 null (버그)
      → 2순위: findOneByBoundaryIntersectsPoint ← 경계선 ~100m만 작동
    → RegionRepo.findOneByLegalCodeContained
```

영향 범위:

- `findOneByBoundaryContainsPoint` → `LegalLocationRetrieverService.getMostNearOneByCoords` → `RegionService.getRegionByLocation` → `regionByLocation` GraphQL resolver
- 프론트엔드 `/map` 페이지가 이 resolver를 사용하여 지역 뷰 노출 여부를 판단
