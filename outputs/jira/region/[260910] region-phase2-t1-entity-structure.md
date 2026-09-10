# P2-T1 — 지역 엔티티 구조 정합 (스팟형 canonical + translation)

**요약** — 지역(region)을 스팟처럼 canonical 엔티티 + 언어별 번역 구조로 정합한다. 언어마다 독립 관리되던 공개·노출을 지역 단위 하나로 묶는 작업. **선행: Phase 1 T2·T3**

## 배경

- 스팟은 `spot`(canonical 엔티티: `is_publish` 마스터 공개·좌표·이미지 등) + `spot_translation`(언어별: `is_default` 기준어·`is_publish`·`is_translated_by_ai`) 구조 — 한 스팟이 한 실체이고 번역은 그 위에 얹힘
- 지역은 `region`(canonical: slug·city_slug·`legal_location_legal_codes`·이미지·priority)이 있으나 **공개·노출 제어가 전부 `region_translation`에만** 존재:
    - `region_translation.is_publish` / `is_shown_map` / `is_shown_review` — 전부 언어별
    - `region`에 마스터 공개 플래그 없음 · `region_translation`에 기준어(`is_default`) 없음 · AI번역 플래그 없음
- 결과: 한 지역을 하나로 관리하지 못하고 언어마다 따로 켜고 따로 채워야 함 → 언어 간 콘텐츠 드리프트, 신규 지역을 15개 언어로 올리는 비용 큼
- Phase 2 유저페이지·어드민 설계는 이미 스팟형 canonical 구조를 전제(slug·히어로 이미지·주변역·카테고리 순서·이동쌍은 언어 무관, 어드민은 언어 탭 + 자동번역, 초기 백필 AI) → 이 구조를 명시적으로 정합해야 나머지 P2 태스크가 성립
- 지도 폴리곤은 선택 법정동(`legal_location_legal_codes`) union에서 자동 도출 = 언어 무관인데 `is_shown_map`이 언어별인 것은 모델 불일치

## 구현

### 유저 플로우

- 운영자는 한 지역을 **하나의 단위로 공개/비공개** — 언어별로 따로 켜지 않음
- 운영자는 **기준 언어(한국어)로 콘텐츠를 채우면** 나머지 언어는 자동번역으로 채워져 함께 노출
- 운영자는 지도 노출을 지역 단위 토글 하나로 제어(언어별 아님)
- 유저는 자신의 언어로 지역 페이지를 보되, 미완성 언어는 자동번역본으로 노출(빈 페이지 없음)

### 백엔드 요구사항

- **`region`(canonical)으로 승격** — 언어 무관 값을 `region`에 둔다:
    - **마스터 공개** `is_publish`(신규) — 엔티티 단위 공개. 지역 노출의 최상위 게이트
    - **지도 노출** `is_shown_map` — `region_translation` → `region`으로 이동(폴리곤이 legal_code union에서 자동 도출이라 언어 무관)
    - 이미 canonical인 값 유지: slug·`city_slug`(→ Phase 1의 `region.city` FK)·`legal_location_legal_codes`·히어로/리스트 이미지·priority
    - 언어 무관 관계 테이블(`region_has_subway`·`region_has_detail_location`·카테고리 순서·이동쌍)은 region 단위로 유지
- **`region_translation`(언어별)은 텍스트 + 언어 상태만** 보유:
    - 텍스트: name·한 줄 소개·description·태그(라벨)·seo·persona 라벨/설명·역 부가설명
    - **기준어** `is_default`(신규) — 스팟 `spot_translation.is_default`와 동형. 기준어 = 한국어
    - **AI번역 플래그** `is_translated_by_ai`(신규) — 자동번역본 식별
    - 언어별 `is_publish`는 **완성도 표시**로 격하(엔티티 공개의 하위) — 미완성 언어는 자동번역 라이딩
    - `is_shown_review`는 제거(Phase 2에서 리뷰 토글 폐기, 테이블·적재는 유지)
- **활성화·공개 판정 재정의** — 엔티티 공개(`region.is_publish`) = 히어로 이미지(canonical) + 기준어 name·태그·설명 충족 AND 부모 CITY 활성화. 기준어 충족 시 엔티티 활성화, 나머지 언어는 자동번역으로 채워 노출
- **기준어 폴백** — 유저 언어 번역이 없거나 미완성이면 자동번역본 → 없으면 기준어(한국어)로 폴백. 빈 페이지 미노출

### 데이터 마이그레이션

- **언어별 독립 공개 → 엔티티 공개로 접기** — 규칙 확정 필요: 기준어(한국어) `is_publish=1`이면 `region.is_publish=1`로 승격 + 나머지 언어 자동번역 백필. 기준어 미공개인데 타 언어만 공개된 케이스는 검수 대상
- **`is_shown_map` 병합** — 언어별로 값이 갈리는 지역은 대표값 선택(기준어 값 우선, 또는 OR)해 `region`으로 이관
- **`is_default` 지정** — 기존 `region_translation`에서 한국어 행을 기준어로 마킹. 한국어 행이 없는 지역은 예외 처리(대상 목록화)
- **오노출·유실 검수** — 마이그레이션이 현행 라이브 노출(공개 13개 등)을 바꾸는지 사전 검수. 노출 로직(legal_code 기반 스팟 매칭)은 불변

### 사람이 수행할 작업

- 언어별 공개 상태가 엇갈리는 지역 목록 검수 + 엔티티 공개 승격 규칙 예외 처리
- 기준어(한국어) 번역 행이 없는 지역 확인·보정

## 수용 조건

- `region`에 마스터 공개(`is_publish`)와 지도노출(`is_shown_map`)이 존재하고, `region_translation`에서 지도노출이 제거됨
- `region_translation`에 기준어(`is_default`)·AI번역 플래그(`is_translated_by_ai`)가 존재하고, 기준어 = 한국어로 지정됨
- 한 지역이 엔티티 단위로 공개/비공개되며, 기준어 충족 시 나머지 언어가 자동번역본으로 함께 노출됨(언어별 독립 공개 아님)
- 유저 언어 번역이 없으면 자동번역본 → 기준어 순으로 폴백해 빈 페이지가 노출되지 않음
- 마이그레이션 후 현행 공개 지역의 라이브 노출이 의도치 않게 바뀌지 않음(사전 검수 완료)
- 리뷰 노출(`is_shown_review`) 토글이 제거되고 `region_review` 테이블·적재는 유지됨
