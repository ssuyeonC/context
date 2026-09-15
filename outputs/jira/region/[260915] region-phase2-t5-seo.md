# P2T5 — /region 유저페이지 SEO (canonical·색인 임계·에디토리얼 인트로·301 승계·GSC 측정)

**요약** — P2T4에서 노출하는 `/region` 5개 경로에 canonical·색인 판정·에디토리얼 인트로·구조화 데이터를 얹어 대형 지역 키워드를 중복 없이 색인·수취하고, 기존 숫자형 REGION URL의 링크 equity를 신규 정본 경로로 승계하며, 타깃 키워드셋을 GSC로 측정한다. **선행: P2T4**

## 배경

- P2T4에서 CITY 인덱스·CITY/REGION 상세·테마 leaf 5개 경로가 노출되지만 canonical·색인 판정·구조화 데이터·측정이 없어 대형 지역 키워드를 색인·수취할 수 없음
- 타깃 키워드 '도시×테마'(seoul restaurants 월 1만~10만)·'도시×구역'(seoul gangnam) 합산 추정 검색량 월 ~50만인데 이를 받을 색인 페이지 부재
- 콘텐츠 임계 없이 테마 leaf를 전부 색인하면 스팟이 적은 leaf가 thin·중복으로 색인 품질을 떨어뜨려 역효과
- 기존 `/spot/region/{id}`와 `/spot/list?category=` 필터뷰가 신규 경로와 중복 색인되면 정본이 분산돼 링크 equity 유실
- Q3 OKR KR1(서울 REGION 10개 × 테마 = 색인 테마 leaf 30개)·KR2(GSC 타깃 키워드 노출·평균순위) 측정 기반 필요

## 구현

### 유저 플로우

- 검색 유저는 '도시×테마'·'도시×구역' 키워드로 유입해도 중복 없는 단일 정본 경로로 도달
- 크롤러는 색인 대상인 CITY 인덱스·CITY/REGION 상세·임계 충족 테마 leaf만 색인하고 임계 미달 leaf와 카테고리 필터뷰는 색인 제외
- 기존 숫자형 REGION URL로 접근한 유저·크롤러는 신규 정본 경로로 301 승계돼 링크 평가가 이어짐
- 운영자는 GSC에서 타깃 키워드 노출·평균순위와 색인 테마 leaf 수를 측정

### 프론트엔드 요구사항

**와이어프레임 (참고)**

https://wireframes-lkb.pages.dev/#region-domain-renewal

**공통 메타·canonical**

- 각 페이지가 자기 경로를 절대 URL canonical로 선언하고 요청 언어 경로를 기준으로 함
- 공개된 언어별 번역 경로를 hreflang alternate로 상호 참조하고 비공개 언어는 alternate에서 제외
- CITY 인덱스·CITY 상세·REGION 상세·임계 충족 테마 leaf는 index,follow로 색인 허용
- 임계 미달 테마 leaf·비공개 CITY/REGION·유효하지 않은 경로는 색인 대상 아님(비생성·Not Found 또는 noindex)
- 기존 `/spot/list?category=` 카테고리 필터뷰는 noindex 처리하고 canonical을 대응 테마 leaf로 양보

**테마 leaf 색인 임계**

- 테마 leaf는 P2T3 집계 기준 전체 스팟이 10개 이상일 때만 생성·색인하고, 10개 미만은 더보기 미노출로 진입 불가·비생성이며 직접 URL 접근 시 기존 Not Found 처리
- CITY·REGION 상세의 스팟은 완전집합이라 항상 충분해 임계 판정 대상 아님

**에디토리얼 인트로**

- 테마 leaf 상단에 부모 지역 설명 기반 짧은 소개문을 노출해 thin 콘텐츠 방지
  - CITY×테마 leaf는 부모 CITY 설명, REGION×테마 leaf는 부모 REGION 설명을 재사용
- 소개문이 비어 있으면 인트로 영역 미노출하되 색인 임계 판정은 스팟 수 기준 유지

**구조화 데이터**

- 전 경로에 현재 CITY·REGION·테마 계층을 BreadcrumbList 구조화 데이터로 노출하고 화면 breadcrumb와 일치
- 테마 leaf·상세의 스팟 그룹을 ItemList 구조화 데이터로 노출(세부 필드 TBD)
- 페이지 `<title>`·`meta description`을 지역명·테마명 기반으로 생성하고 언어별 번역 사용

**타이틀·안정 slug**

- CITY/REGION/테마 계층과 지역명·테마명을 조합한 타이틀·메타 설명을 언어별로 생성
- 안정 slug로 URL 불변 — 지역명 slug와 예약 카테고리 slug 매핑 사전을 고정해 이름 불변 시 URL·canonical·색인이 흔들리지 않음

### 백엔드 요구사항

- 색인 판정 — 테마 leaf 스팟 수 10 임계·CITY/REGION 존재·요청 언어 공개 여부로 index/noindex/비생성 값을 페이지에 제공
- canonical 계산 — 요청 언어·경로 기준 절대 canonical과 공개 언어 hreflang alternate 목록 제공
- 필터뷰 매핑 — `/spot/list?category=` 필터뷰의 대응 테마 leaf canonical 타깃 계산
- 301 승계 — 기존 `/spot/region/{id}`와 498 동네 URL을 신규 정본 경로로 영구 리다이렉트(응답 구현은 P2T3·P2T4)하고, 쿼리 유지·매핑 없거나 대상 비공개면 Not Found로 정본 분산 방지
- sitemap — 색인 대상(CITY 인덱스·CITY/REGION 상세·임계 충족 테마 leaf)만 언어별 sitemap에 등록하고 비색인·비공개·임계 미달 경로는 제외
- 측정 — GSC 타깃 키워드셋(도시×테마·도시×구역) 노출·평균순위·색인 테마 leaf 수 측정 셋업, 권한 확보 후 진행

## 수용 조건

- 색인 대상 경로가 자기 경로 canonical(절대 URL)과 공개 언어 hreflang alternate를 선언함
- 스팟 10개 미만 테마 leaf가 비생성·비색인되고 직접 접근 시 Not Found 처리됨
- `/spot/list?category=` 카테고리 필터뷰가 noindex이고 canonical을 대응 테마 leaf로 양보함
- 테마 leaf 상단에 부모 지역 설명 기반 에디토리얼 인트로가 노출되고 빈 값이면 미노출됨
- 전 경로에 화면 breadcrumb와 일치하는 BreadcrumbList 구조화 데이터와 지역·테마 기반 타이틀·메타 설명이 노출됨
- 기존 `/spot/region/{id}`·동네 URL이 신규 정본 경로로 301 승계되고 매핑 없거나 비공개면 Not Found 처리됨
- 색인 대상만 언어별 sitemap에 등록되고 안정 slug로 지역명·카테고리 불변 시 URL·canonical이 불변임
- GSC 타깃 키워드셋(도시×테마·도시×구역) 노출·평균순위와 색인 테마 leaf 수(서울 KR1 30개)가 측정됨
