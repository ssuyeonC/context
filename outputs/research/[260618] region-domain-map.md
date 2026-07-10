# 크리에이트립 '지역(Region)' 도메인 정리

> 🔗 **허브**: `outputs/plans/[260701] region-domain-improvement-master.md` — 지역 도메인 개선 통합 기획서 (전체 문서 맵)

작성일: 2026-06-18
출처: datastream_creatrip DB 스키마/실데이터 + outputs/jira/map, outputs/jira/spot, outputs/reddit-koreatravel

> 크리에이트립에서 "지역"은 단일 개념이 아니라 **목적이 다른 4개의 평행 체계**가 겹쳐 있다. 같은 "명동"이라도 ① 행정구역 폴리곤(legal_location), ② 상품이 매달리는 운영 분류(category), ③ SEO·리뷰·지도용 콘텐츠 페이지(region), ④ 마케팅 랜딩(landing_area)으로 각각 따로 존재한다. 이 문서는 그 층위와 연결, 실데이터 규모, 유저 수요, 현재 한계를 한 장으로 정리한다.

---

## 0. 한눈에 보기 — 지역의 4개 층위

| 층위 | 테이블 | 정체성 | 규모 | 주 용도 |
|---|---|---|---|---|
| **① 행정구역(좌표 기준)** | `legal_location` | 정부 행정표준코드 + GeoJSON 폴리곤 | 5,332행 (시도17/시군구250/읍면동5,065) | 좌표→지역 판정, /map 지역뷰 |
| **② 운영 분류(상품 기준)** | `category` (type=CITY/DETAIL_LOCATION/SUBWAY) | 스팟이 실제로 매달리는 도시>상세지역>지하철 분류 | 도시 169·상세지역 158·지하철역 478 | 스팟 분류·검색·필터 |
| **③ 콘텐츠 페이지** | `region` (+ translation/review/has_*) | SEO·리뷰·지도 노출용 "지역 페이지" 엔티티 | 514행(서울 498) / 로케일당 발행 ~12개 | 지역 랜딩·지역 리뷰·지도 패널 |
| **④ 마케팅 랜딩** | `landing_area` | 캠페인성 지역 기획 페이지 | 2,606행 | "부산 일일투어" 류 프로모션 |

핵심: **②가 상품 운영의 실세, ③은 콘텐츠·SEO 자산, ①은 지도 백본, ④는 마케팅.** 서로 `region.legal_location_legal_codes`, `region_has_detail_location`로 느슨하게 연결된다.

---

## 1. 층위별 상세

### ① legal_location — 행정구역 / 지도 백본
- 컬럼: `legal_code`(행정표준코드, 예 11140=중구·11110=종로구), `level`(1 시도 / 2 시군구 / 3 읍면동), `name_kor`·`name_eng`, `boundary_geojson`(폴리곤), `category_code`.
- 규모: **level1 17개(강원특별자치도·경기도…), level2 250개(강남구·가평군…), level3 5,065개(법정동).**
- 역할: 좌표 한 점이 어느 지역 폴리곤 안에 있는지 판정 → `/map`의 '지역 뷰 보기' 노출 판단의 근거.
- 호출 흐름: `regionByLocation`(GraphQL) → `RegionService.getRegionByLocation` → `LegalLocationRetrieverService.getMostNearOneByCoords` → `RegionRepo.findOneByLegalCodeContained`.
- ⚠️ **알려진 버그**: `findOneByBoundaryContainsPoint`의 `ST_Contains` 인자 순서 반전(`POINT,boundary`)으로 폴리곤 내부 판정이 항상 false. fallback이 경계선 ~100m만 잡아, 사실상 대부분 유저가 지역뷰를 못 봄. 수정: `ST_Contains(boundary, POINT)`. (outputs/jira/map/[260305] map_region_view_bug.md)

### ② category (CITY / DETAIL_LOCATION / SUBWAY) — 상품 운영 분류
- `category` 테이블의 `type`으로 지리 분류를 구분. 지리 관련 타입 분포:
  - **CITY 169 / DETAIL_LOCATION 158 / MAIN_SUBWAY 11(노선) / MIDDLE_SUBWAY 478(역)**
- 계층: `parent_code`로 상세지역 → 도시 연결. `category_location`(627행)이 "이 카테고리는 지역형"임을 표시.
- **상세지역을 가진 도시(실사용):** 서울 33 · 부산 10 · 인천 6 · 대전 2 · 광주 1 · 울산 1 → 사실상 **서울 중심, 부산·인천이 보조.**
- **스팟↔상세지역 연결:** `spot_has_category`(category.type=DETAIL_LOCATION) 기준 **스팟 3,710개 / 링크 3,751개 / 스팟당 평균 1.01개.** → 거의 모든 스팟이 상세지역 **단 1개**에만 연결됨.
- 지하철(노선 11·역 478)도 별도의 지리 탐색축. `region_has_subway`로 지역과 연결.

### ③ region — 콘텐츠/SEO/리뷰/지도 페이지
- 컬럼: `slug`(myeongdong), `city_slug`(seoul), `legal_location_legal_codes`(["11140"] — ①과 연결), `seo_image_path`·`list_image_path`·`itinerary_option_image_path`, `like_count`, `flags`.
- 규모: **514행 중 498개가 서울.** 나머지 도시(부산·제주·강원·대구·광주·세종·대전·울산·인천)는 각 1개뿐 → region은 **사실상 서울 동네(명동·경복궁·홍대…) 카탈로그.**
- 발행 상태(`region_translation` 기준, 로케일당):
  - **발행(is_publish=1): ko 3 / en 13 / 그 외 12** → 완성된 SEO 지역 페이지는 **로케일당 ~12개뿐**, 대다수는 드래프트.
  - **지도 노출(is_shown_map=1): ~30개** / **리뷰 노출(is_shown_review=1): ~512개(거의 전부).**
  - → region의 실질 가치는 "발행 페이지"보다 **지역 단위 리뷰 집계**에 더 쏠려 있음.
- 다국어: `region_translation` 15개 언어(ko·en·zh-TW·zh-CN·zh-HK·jp·th·vi·id·de·ru·it·fr·es·mn), name/address/description/seo_title/seo_description/itinerary_option_description.
- 부속 관계:
  - `region_has_detail_location`(30행) — region ↔ ② 상세지역(category) 브리지(`detail_location_code`=category.code).
  - `region_has_place`(19) — region ↔ `place`(구글 POI 등).
  - `region_has_subway` — region ↔ 지하철역. `region_has_blog`/`region_has_user_blog` — 콘텐츠 연결.
  - `region_review`/`region_review_translation` — 지역 리뷰.
  - `region_spot_area`(6) + `region_spot_area_has_spot`(27) + `_trans` — 지역 내 **큐레이션 스팟 묶음**(priority 순). 소규모 실험적 기능.

### ④ landing_area — 마케팅 지역 랜딩
- 2,606행. `page_type`, `is_publish`, `period_from/to`, `language`, `title`, 콘텐츠/주의사항/접수폼(`has_required_info`, `is_accept_qna`).
- 예: "2025釜山一日遊精選商品…", "首爾美食推薦懶人包(서울맛집 총정리)" → **도시·테마 결합 캠페인 페이지.** GA4 `LandingAreaPV`로 트래픽 추적.

---

## 2. 연결 관계 요약

```
legal_location (행정구역·폴리곤)
   ▲ legal_code
   │  region.legal_location_legal_codes = ["11140"]
region (콘텐츠 페이지, slug/city_slug)
   ├─ region_translation        (15개 언어, 발행/지도/리뷰 노출 플래그)
   ├─ region_review             (지역 단위 리뷰)
   ├─ region_has_detail_location → category(DETAIL_LOCATION)  ← 스팟이 매달리는 곳
   ├─ region_has_place          → place (POI)
   ├─ region_has_subway         → category(SUBWAY)
   └─ region_spot_area_has_spot → spot (큐레이션 묶음)

category(CITY) ─parent─▶ category(DETAIL_LOCATION) ─spot_has_category─▶ spot (3,710개, 평균 1.01)
```

---

## 3. 유저 관점 — '지역'은 무엇을 의미하나 (r/koreatravel 5,554건 분석)

(outputs/reddit-koreatravel/[260612] REPORT_region_deepdive.md)

- 목적지 테마가 전체 게시물의 **55.5%** — 지역이 커뮤니티 담론의 핵심 축.
- **지역 = 주제가 아니라 '질문의 좌표계'.** 지역 글의 89%가 질문형이고, 내부 동반 주제는 볼거리(72.5%)>추천(53.3%)>교통(52.8%)>일정(45.6%). 즉 "서울"이라는 그릇에 명소·동선·이동·거점을 얹어 최적화하려는 수요.
- **27.4%가 다(多)도시 비교** — "서울 며칠 vs 부산 며칠" 식 시간 배분 문제(`seoul busan` 바이그램 1위).
- 도시별 니즈 지문: **서울=볼거리·큐레이션 / 부산=접근성(KTX) / 제주=렌터카·체험.**
- 시사: 지역 페이지는 정보 나열이 아니라 **다도시 시간배분 + 동선/이동/거점 의사결정 도구**여야 함. 서울 허브 + 근교(경주·전주·남이섬·DMZ) 당일치기 add-on 기회.

---

## 4. 현재 한계 · 진행 중 작업

| 이슈 | 상태 | 출처 |
|---|---|---|
| /map 지역뷰가 폴리곤 내부에서 안 뜸 (ST_Contains 인자 반전) | 백엔드 1줄 수정 필요 | jira/map/[260305] map_region_view_bug |
| 스팟의 상세지역이 1개로 제한 → 두 지역 경계 스팟이 한쪽 검색에서만 노출 | 세부기획 중(최대 2개+순서값+배열 색인) | jira/spot/[260617] spot-multiple-detail-locations |
| region 발행 페이지가 로케일당 ~12개뿐, 서울 외 도시 부재 | 콘텐츠 공백 (확장 여지) | DB 실측 |
| region(콘텐츠) ↔ category(운영) ↔ legal_location(행정) **3중 분류 미정합** | 구조적 부채 | DB 구조 |
| 경주 지역 페이지 신규 작업 흔적 | 진행 중 | outputs/region-gyeongju (list/seo html·이미지) |

---

## 5. 핵심 시사점

1. **'지역'은 4개 체계의 합성어.** 어떤 작업이든 "어느 지역을 말하는가"(행정 폴리곤 / 상품 분류 / 콘텐츠 페이지 / 마케팅 랜딩)부터 정의해야 혼선이 없다.
2. **운영의 실세는 category(상세지역)** — 스팟 3,710개가 여기 매달려 있고 현재 스팟당 1개 한계가 곧 풀린다(복수 상세지역). 검색 노출·발견율의 레버.
3. **region은 잠재 SEO 자산이나 미완성** — 514개 중 발행은 ~12개, 서울 일색. 리뷰 집계로만 주로 쓰이는 상태. 다도시 수요(27% 멀티시티)와 정면으로 어긋남.
4. **유저는 '목적지 선택'이 아니라 '다도시 일정 최적화'를 원함** — 지역 페이지/상품을 시간배분·동선·거점 계산기로 재정의할 때 시장 핏.
5. **지도 백본(legal_location)은 버그로 사실상 무력화** — 1줄 수정으로 지역 기반 탐색 경험을 즉시 복구 가능(저비용 고효율).

---

## 6. 어드민 관리 심층 — 5개 지역 개념은 어떻게 운영되나

> 어드민에서 보이는 5개(도시·상세지역·지역·법정지역·지하철)는 **3개의 서로 다른 관리 패러다임**으로 나뉜다. 이걸 모르면 "왜 어떤 건 발행 토글이 있고 어떤 건 없나"가 설명되지 않는다.

### 관리 패러다임 3분류

| 패러다임 | 대상 | 테이블 | 관리 주체 | 노출/발행 제어 |
|---|---|---|---|---|
| **A. 카테고리 관리(한 지붕)** | 도시·상세지역·지하철 | `category`(type으로 구분) + `category_translation` | 운영자(카테고리 관리 화면) | **없음**(구조적 데이터, type/priority/parent만) |
| **B. 지역 콘텐츠 관리(별도 어드민)** | 지역 | `region` + `region_translation` + `region_has_*` | 콘텐츠 작성자(writer_code 3명) | **있음**(언어별 is_publish/is_shown_map/is_shown_review) |
| **C. 외부 동기화(관리 대상 아님)** | 법정지역 | `legal_location` | 정부 데이터 적재 | 해당 없음(좌표 판정 백본) |

---

### ① 도시 (City) — 패러다임 A
- **테이블/타입:** `category` (type=`CITY`). **169개, 전국 시군구 단위**(강릉시·서귀포시·평양·타이페이까지 포함 — 한국 외/북한도 일부 존재).
- **관리 필드:** `priority`(노출 순서, 서울=1·인천=2·부산=3…), `parent_code`(전부 NULL — 도시는 최상위), `alias`, `map_icon_path`(`category_icon_management` 작업으로 어드민 업로드화 진행), `tag_code`.
- **번역:** `category_translation`(name/description) 15개 언어. **발행 플래그 없음.**
- **실사용:** 모든 스팟이 도시 1개에 연결됨 — **스팟 5,425개 / 링크 5,425개(정확히 1.0개/스팟).** 도시는 스팟의 **필수 단일 앵커.**
- **공백:** 169개 중 상세지역 자식을 가진 도시는 **6개뿐**(서울·부산·인천·대전·광주·울산). 나머지 163개 도시는 이름만 있고 하위 분류 없음.

### ② 상세지역 (Detail location) — 패러다임 A
- **테이블/타입:** `category` (type=`DETAIL_LOCATION`). **158개.** `parent_code`로 도시에 연결.
- **관리 필드:** 도시와 동일 구조(priority/parent_code/alias). 번역도 category_translation 공유, **발행 플래그 없음.**
- **실사용:** 스팟이 `spot_has_category`로 연결 — **스팟 3,710개 / 링크 3,751개(1.01개/스팟).** → 거의 모든 스팟이 상세지역 **단 1개**(이 1개 제한이 `[260617] spot-multiple-detail-locations`로 최대 2개로 확장 중).
- ⚠️ **정합성 부채(중요):**
  - **158개 중 105개(66%)가 parent_code 없음** — 도시에 안 매달린 고아 상세지역(서촌·창덕궁·인사동·성수동·을지로 등 유명 동네 다수가 여기).
  - **이름 중복:** `서면`×3(코드 87/109/112), `성수동`×2(98 고아 / 477 서울시).
  - **개념 혼재:** 관광지명(명동·홍대·경복궁)과 행정구(강남구·종로구·중구)가 한 바구니에 섞여 있음 → 분류 기준이 일관되지 않음.

### ③ 지역 (Region) — 패러다임 B (유일하게 '콘텐츠'로 관리)
- **테이블:** `region`(514개, 서울 498) + `region_translation`(15언어) + `region_has_*`. 도시/상세지역과 **완전히 별도 어드민.**
- **관리 필드:** `slug`(myeongdong)·`city_slug`(seoul)·이미지 3종(seo/list/itinerary)·`legal_location_legal_codes`(["11140"], ①과 연결)·`writer_code`(**작성자 3명**이 전부 생성).
- **노출 제어(이게 A와의 결정적 차이):** `region_translation`에 **언어별 3개 플래그** — `is_publish`(SEO 페이지 발행, 로케일당 ~12개만 ON), `is_shown_map`(지도 패널, ~30개), `is_shown_review`(지역 리뷰, ~512개=거의 전부). → region의 실질 가치는 발행 페이지가 아니라 **지역 단위 리뷰 집계.**
- **큐레이션 관계:** `region_has_detail_location`(→②), `region_has_place`(→POI), `region_has_subway`(→⑤, **836링크로 가장 많음**), `region_has_blog`/`region_spot_area`(지역 내 스팟 묶음). → 지역 페이지는 동네별 콘텐츠를 사람이 손으로 엮는 큐레이션 단위.

### ④ 법정지역 (Legal location) — 패러다임 C (어드민이 만들지 않음)
- **테이블:** `legal_location`(5,332개). **정부 행정표준코드 + GeoJSON 폴리곤**을 적재한 동기화 데이터.
- **구조:** `level`(1 시도17 / 2 시군구250 / 3 읍면동5,065), `legal_code`(11140=중구), `name_kor/name_eng`, `boundary_geojson`.
- **관리 성격:** `category_code`가 **전 행에 단일 상수값**(per-row 매핑 아님) → 운영자가 행별로 관리하는 대상이 아님. **좌표→지역 판정 백본**으로만 기능하며, region이 `legal_location_legal_codes` 문자열로 참조.
- ⚠️ `/map` 지역뷰가 `ST_Contains` 인자 반전 버그로 사실상 무력화(§1·§4 참조).

### ⑤ 지하철 (Subway) — 패러다임 A (2단계 노선→역)
- **테이블/타입:** `category` (type=`MAIN_SUBWAY` 노선 11 / `MIDDLE_SUBWAY` 역 478). `parent_code`로 역→노선 연결.
- **노선(11):** Line 1(65역)·수인분당(63)·7호선(53)·4호선(51)·5호선(46)·3호선(44)·2호선(43)·9호선(38)·6호선(37)·8호선(24)·공항철도(14). 전부 수도권. 번역명이 영문("Line 1") 중심.
- **실사용(특이):** 스팟이 인근 역에 **다중 태깅** — **역(MIDDLE_SUBWAY): 스팟 3,992개 / 링크 21,513개(평균 5.4개/스팟)**, **노선(MAIN_SUBWAY): 스팟 3,313개 / 10,180링크(3.1개/스팟).** → 도시·상세지역이 1개씩인 것과 달리, 지하철은 **'가까운 역 여러 개'로 교통 기반 발견을 위한 다대다 태깅.**
- region과의 연결도 836링크로 region_has_* 중 최다 → 지역 페이지의 핵심 탐색축.

---

### 종합 — 스팟이 지역에 묶이는 실제 모습 (태깅 밀도)

| 지역축 | 스팟당 평균 연결 | 의미 |
|---|---|---|
| 도시(City) | **1.0** | 필수 단일 앵커 |
| 상세지역(Detail loc) | **1.01** | 사실상 단일(→2개로 확장 중) |
| 지하철 노선 | 3.1 | 교통 기반 다중 태깅 |
| 지하철 역 | **5.4** | 인근 역 전부 태깅(발견 극대화) |

→ **운영 설계 의도:** 도시·상세지역은 "이 스팟은 어디에 있나"(귀속), 지하철은 "이 스팟에 어떻게 가나/근처에 뭐가 있나"(접근·발견). 두 성격이 명확히 갈린다.

### 어드민 관리상 핵심 시사점
1. **A 패러다임(도시·상세지역·지하철)은 발행/번역 노출 제어가 없다** — 카테고리는 만들면 곧 노출되는 구조라, 품질 관리가 입력 단계에 전적으로 의존한다. 상세지역의 66% parent 누락·중복이 그 방증.
2. **상세지역이 가장 약한 고리** — 개념 혼재(관광지/행정구) + parent 누락 + 중복. 스팟 검색·노출의 직접 레버인데 정합성이 가장 낮다. 복수 상세지역 작업 전에 **분류 기준·parent 정리·중복 제거**가 선행돼야 효과가 산다.
3. **region(지역)만이 '발행' 개념을 가진 콘텐츠 자산** — 그러나 514개 중 발행 ~12개로 잠재력 미실현. 카테고리(운영)와 region(콘텐츠)이 region_has_detail_location로만 느슨히 연결돼, 두 체계의 동기화가 수작업.
4. **법정지역은 관리가 아니라 정합성(버그)이 이슈** — 데이터는 정부 표준이라 견고하나, 이를 쓰는 좌표판정 로직이 깨져 있음.

---

## 7. 도시·상세지역의 어드민 CRUD 범위와 생성 경로 (코드 검증)

> §6은 "어떻게 관리되나"를 데이터로 봤고, 여기서는 product 모노레포(`creatrip/product`) 어드민/백엔드 **코드를 직접 읽어** 도시·상세지역이 어드민에서 무엇을 할 수 있고 없는지, 그리고 도시가 실제 어떤 경로로 생성됐는지를 확정한다. 인용은 `frontend/apps/admin`·`backend/apps/trip` 기준.

### 7-1. 어드민 Locations 화면의 실제 권한 (CRUD 게이팅)

어드민 지역 관리 화면은 라디오 탭 **도시 / 상세지역 / 법정지역**으로 나뉜다(`LocationFilters.tsx`). 그런데 생성·수정·삭제 UI 전체가 **`상세지역일 때만` 렌더되도록 막혀 있다.**

```tsx
// LocationTable.tsx
const isDetailLocation = type === CategoryType.DetailLocation;
...
{isDetailLocation && (   // ← 추가 버튼·생성·수정 모달이 전부 이 조건 안에만 존재
  <> <Button>추가</Button> <CreateLocationModal/> <UpdateLocationModal/> </>
)}
```

| 탭 | 추가 | 수정 | 삭제 | 순서(드래그) | 비고 |
|---|---|---|---|---|---|
| **도시(City)** | ❌ | ❌ | ❌ | ✅ | 조회 + priority 변경만 |
| **상세지역(DetailLocation)** | ✅ | ✅ | ✅ | ✅ | 유일하게 CRUD 가능 |
| **법정지역(LegalLocation)** | ❌ | ❌ | ❌ | ❌ | 완전 읽기전용 |

- **도시는 어드민에서 추가·수정·삭제 불가** — 순서만 바꿀 수 있는 사실상 읽기전용. → 도시는 어드민 밖에서 관리되는 마스터 데이터.
- **상세지역 생성/수정 모달은 `type`+언어별 이름만** 전송(`CreateLocationModal.tsx`/`UpdateLocationModal.tsx`). **상위 도시(parent)를 넣는 입력이 없다.** 표의 '상위 지역명'은 `location.parent`를 **읽어서 보여주기만** 함.
- **결론:** 어드민으로 상세지역을 만들면 **무조건 parent=NULL 고아로 태어난다.** §6에서 본 상세지역 105개(66%) 고아의 직접 원인.

### 7-2. 상세지역의 상위(도시) 연결은 어드민·생성/수정 API 어디에도 없다
- `CreateCategoryArgs`/`UpdateCategoryArgs`(`category.args.ts`)는 `type`·`translations`·`categoryIconPaths`만 받음 → **`parentCode`를 안 받음.**
- DB 엔티티엔 `parent_code` 컬럼이 있고 읽기 fragment엔 `parentCode`가 있어 **조회만 가능.**
- `linkChildCategoryToParent` 뮤테이션이 있지만 **대분류↔중분류(예약/리뷰 등) 전용**이고 Location에는 연결돼 있지 않음.
- → parent를 채우려면 **DB 직접 UPDATE / 스크립트**뿐. 어드민 기능 추가(생성·수정 모달에 상위 도시 선택 + 백엔드 `parentCode` 인자)가 선행돼야 정상화된다.

### 7-3. 생성 시점 타임라인 — 일괄 시딩이 아니라 점진 + 1회 벌크

| 분류 | 패턴 | 비고 |
|---|---|---|
| **도시(169)** | 2018 초기 10개 → 2020~2022 산발 1~3개 → **2022-10-04 93개 벌크** → 2024 1개 | 93개 벌크 = 전국 시군구 일괄 도입 추정 |
| **상세지역(158)** | 2018~2023 산발, **2019-05-03(24개)·2022-10-04(26개)** 묶음 | parent 채워진 53개의 73%가 이 두 배치 산물 |

→ parent가 채워진 상세지역은 **스크립트성 배치 때만** 생성됨. 평소 어드민으로 하나씩 추가된 것들은 parent를 넣을 자리가 없어 NULL.

### 7-4. 도시는 어떻게 생성됐나 — 자동 생성 아님 (마스터 데이터)

도시를 자동 생성할 수 있는 코드 `findOrCreateCityByKoName`(`category.repo.ts:49`, `category.service.ts:70`)이 **존재하지만 레포 전체에서 호출하는 곳이 0** — 죽은 코드다. 남은 TODO 주석(*"city category가 어드민에서 정리된다면 create가 아닌 단순 find로 바뀔 예정"*)은 과거 설계 의도의 흔적일 뿐 현재 동작 근거가 아니다.

실제로 도시명을 다루는 모든 지점은 **"찾기만 하고 없으면 에러"**:
- **스팟 등록:** 기존 CITY 목록에서 선택해 `spot_has_category` 연결(자유 입력 생성 아님).
- **숙소 동기화(ONDA/야놀자):** 주소의 한글 도시명으로 기존 CITY 조회, 못 찾으면 생성이 아니라 `UnableToFindCreatripCityFromOndaCity` **에러를 던짐**(`onda-content.service.ts:888-895`).

따라서 도시는 **"새 이름이 등장해 자동 생성된 것"이 아니라, 앱 바깥에서 주입된 마스터 목록**이다. 유력 경로:
- **`createCategory` 뮤테이션 직접 호출** — 서버가 `type=CITY`를 막지 않음(`category.service.ts`의 create에 type 검증 없음). UI엔 없지만 GraphQL 직접 호출이면 도시 생성 가능.
- **DB/시드 직접 INSERT** — 특히 2022-10-04의 93개 벌크.
- (참조 시 자동 생성 가설은 코드상 죽어 있어 **기각.** 과거 호출 여부는 git 히스토리로만 확정 가능.)

이것이 도시 목록에 평양·타이페이·대만·한국 같은 잡다한 값이 정제 없이 섞여 있는 이유 — 입력 검증/관리 UI 없이 백엔드로 쌓였기 때문이다.

### 7-5. 운영 개선 시사 (도시·상세지역)
1. **`createCategory`에 type 화이트리스트** 추가(예: DETAIL_LOCATION만 생성 허용)로 무분별한 CITY 직접 생성 차단.
2. **상세지역 생성/수정 모달에 상위 도시 선택 + 백엔드 `parentCode` 인자** 추가 — 고아 양산 구조의 근본 차단.
3. 그 후 **기존 105개 고아 상세지역 parent 일괄 보정** + 중복(서면×3·성수동×2)·개념 혼재(관광지/행정구) 정리.
4. 도시 마스터(169개)에서 비유효 값(평양·대만·한국 등) 정리 — 단, 어드민에 도시 수정/삭제 기능이 없어 이 또한 기능 추가가 선행돼야 함.
