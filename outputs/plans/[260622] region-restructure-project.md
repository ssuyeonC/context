# 지역(Region) 도메인 재구조화 프로젝트

> 🧭 **마스터 [260701] §6·§3의 상세 스포크** — 이 문서는 **작업분해(Phase/BE/FE/AD)·D1~D10** 정본. 개념·IA·B-2 등 상위 결정은 마스터가 소유(겹치면 마스터 우선).

작성일: 2026-06-22 · 최종 수정: 2026-06-25
상태: **기획 확정 단계** (모델·IA·어드민 설계 합의 / 착수 전, 와이어프레임 1차 나옴)
근거 문서:
- `outputs/research/[260618] region-domain-map.md` — 지역 4층위 도메인 정리
- `outputs/meetings/region/[260619] meeting-region-page-improvement-0619.md` — 회의록 + 추가논의 #1~#3
- `outputs/reddit-koreatravel/[260612] REPORT_region_deepdive.md` — 지역 수요 분석
- 와이어프레임: `https://wireframes-lkb.pages.dev/#region-domain-renewal` (2026-06-23)
- prod DB 실측 + product 모노레포 코드 검증 (2026-06-22~24 세션)

> ⚠️ **후속 결정으로 대체된 부분 (2026-07-06)** — 본 문서(Path 1)의 일부 모델은 이후 문서로 갱신됐다. 최신 확정은 `[260701] region-geo-model-decision.md` §0·§0-3 및 `[260701] region-domain-improvement-master.md`를 따른다: ① **CITY = 시도(L1)** · **DETAIL_LOCATION = 시군구(L2, LEGAL 참조)** (본 문서의 "CITY=시/군, DL=행정구59/관광지81/동18"·"DL:LEGAL 1:1" 서술 대체), ② REGION 스팟 해상도는 `spot_has_category`(구)가 아니라 **legal(법정동) 기반**(§T2 원복), ③ 정비는 **LEGAL 정합·비파괴**(없는 값만 생성·완전 무연결만 제거·관광지 DL 삭제는 REGION 트랙 후속). 아래 D1~D10·작업분해는 이 갱신 위에서 읽는다.

> **한 줄 요약** — REGION을 '행정 폴리곤에 매인 단일 동네'에서 **'여행객이 인지하는 큐레이션 구역'**(여러 행정구 DETAIL_LOCATION을 묶은 단위)으로 재정의한다. 스팟은 `region_has_detail_location → spot_has_category`로 가져오고, legal_location은 행정구 DETAIL_LOCATION에 1:1로 붙어 REGION 폴리곤으로 상속된다. 구조는 **CITY → REGION(평면)** 2단, 테마는 어드민 섹션 CMS로 편성한다.

---

## 1. 왜 하나 (배경)

세 가지가 동시에 가리킨다:

1. **수요 vs 트래픽 격차** — 외부 여행 담론(r/koreatravel)의 **55.5%가 '지역'**인데, 지역 페이지는 트래픽의 **3.8%**만 받고 평균 **11초**에 이탈(리스트 49초의 22%). 끝까지 본 5%는 스팟으로 전환 → **구조가 수요와 어긋남**.
2. **분류 축 불일치** — 같은 스팟 풀을 신선도/인기 렌즈로 16개 섹션에 반복. 유저가 원하는 **의도·다도시·지역간 이동** 축이 없다.
3. **도메인 4층위 혼재** — '지역'이 ①행정(legal_location) ②운영분류(category) ③콘텐츠(region) ④마케팅(landing_area)으로 평행 존재.

→ 답은 "섹션을 더 쌓는 것"이 아니라 **분류 축을 유저 인지(구역)·의도(테마)로 바꾸는 것.**

---

## 2. 핵심 결정사항 (요약)

| # | 결정 | 한 줄 |
|---|---|---|
| D1 | **REGION = 인지 구역** | 여러 **행정구** DETAIL_LOCATION을 손으로 묶는 '여행객 인지 구역' (강남=강남구+서초구) |
| D2 | **스팟 축 전환** | `legal prefix` → `region_has_detail_location → spot_has_category` |
| D3 | **legal = 행정구 detail_location에 1:1** | `category.legal_code` 단일컬럼, REGION은 union으로 상속 / 관광지(~81)는 legal 없이 잔존 |
| D4 | **2레이어 구조** | 기반 분류(category: CITY·DETAIL_LOCATION·SUBWAY) 위에 REGION 도메인(콘텐츠) 얹기 |
| D5 | **CITY → REGION 평면 (FK)** | REGION 중첩 없음. `region.city` → `category(CITY)` **FK**. CITY는 **카드 메타만 저장**, ~~상세는 자식 REGION 집계~~ → **상세 스팟 = B-2(CITY 스팟 ∩ 테마), 2026-07-14 확정** |
| D6 | **IA — 테마 leaf + 캐러셀** | `/region` → `/{city}` → `/{city}/{zone}`, theme은 depth 3·4에 leaf(`/{city}/{theme}`·`/{city}/{zone}/{theme}`). city×theme은 zone과 3번째 칸 공유 → **city별 슬러그 레지스트리**로 판정. 페이지 내 테마 섹션 = **monthly best 9 캐러셀 + 전체보기→leaf**, leaf는 **스팟 10개부터 생성**(가드레일) |
| D7 | **테마 = REGION 섹션(자유) + master_theme 사전** | REGION 섹션 = 이름+카테고리+순서(자유 편성), REGION 섹션 CMS에서 master_theme에 매핑. ~~CITY 편집 화면에서 관리자가 소속 REGION 테마들을 master_theme로 묶음 → CITY 집계~~ → **CITY 집계는 B-2**(CITY 스팟 ∩ master_theme), REGION 그룹핑 불필요 |
| D8 | **활성화 게이트** | CITY 활성화 = image·tags·desc (~~≥1 REGION~~ → B-2로 폐지, §3-7) / REGION 활성화 = ≥1 행정구 DETAIL_LOCATION |
| D9 | **비공개 REGION 500개 삭제** | 2025-02-14 벌크(id 25~531), 의존성 검증 후 |
| D10 | **스팟 구 재태깅으로 coverage 해결** | 관광지-only 스팟에 구 detail_location 추가 → REGION 구단위 묶음으로 누락 0 |

---

## 3. 타깃 구조

### 3-1. 2레이어 모델

```
[기반 분류 레이어 — 스팟에 직결, REGION 도메인과 무관하게 항상 존재]
category
  ├ CITY             ─ spot_has_category ─ spot     (도시 분류, 169)
  ├ DETAIL_LOCATION  ─ spot_has_category ─ spot     (상세지역 158 = 행정구형 59 + 관광지형 81 + 동 18)
  └ SUBWAY           ─ spot_has_category ─ spot     (지하철 노선11·역478 — '주요 역' 탭)

[REGION 도메인 레이어 — 콘텐츠/프레젠테이션, 위에 얹힘]
CITY(활성화)   ← slug·hero·tags·desc·도시간이동 / 활성화 게이트
  └ REGION (= 1개 이상의 '행정구' DETAIL_LOCATION 묶음, CITY 하위·평면)
        - 행정구 DETAIL_LOCATION.legal_code → legal_location(1:1) → REGION 폴리곤 = union
        - 테마 섹션(어드민 CMS) · subway · blog · persona 큐레이션
        - 스팟 = REGION의 detail_location들 ∩ (섹션 카테고리)  via spot_has_category
```

### 3-2. 엔티티 정의

| 엔티티 | 테이블 | 역할 | 비고 |
|---|---|---|---|
| **CITY** | `category(type=CITY)` + 카드메타 | 도시. 페이지 = `/region/{city}` = ~~자식 REGION을 theme로 집계~~ **CITY 스팟 ∩ theme (B-2)** | slug·카드메타·활성화·도시간이동만 신규(§3-7) |
| **DETAIL_LOCATION** | `category(type=DETAIL_LOCATION)` | 스팟 분류 + (행정구형은) REGION의 묶음 단위 | 행정구59=묶음키 / 관광지81=스팟태그로 잔존 |
| **REGION** | `region` + `region_has_detail_location` | 인지 구역. 페이지 = `/region/{city}/{zone}` | 행정구 detail_location 묶음, CITY 하위 평면 |
| **legal_location** | `legal_location` | 지도 폴리곤·좌표판정 (기하 전용) | 행정구 DETAIL_LOCATION에 1:1 연결 |
| **SUBWAY** | `category(type=*_SUBWAY)` | '주요 역' 탭, 역 주변 스팟 발견 | `region_has_subway` 기존 매칭 활용 |

### 3-3. REGION = 인지 구역 (큐레이션)

여행객은 '방이동'(법정동)이 아니라 '잠실/롯데월드'(인지 구역)로 목적지를 잡는다(§4-6 실측 검증). REGION을 그 인지 구역으로 재정의:

```
서울시(CITY)
  ├ 마포구 & 서대문구 (DETAIL_LOCATION) = 홍대 (REGION)
  ├ 용산구 (DETAIL_LOCATION)            = 이태원 (REGION)
  └ 강남구 & 서초구 (DETAIL_LOCATION)   = 강남 (REGION)
```

- 스팟 노출: `region_has_detail_location → spot_has_category` (그 REGION의 detail_location들에 태깅된 스팟)
- 관광지/행정구 혼재도 의도적으로 OK이나, **묶음 키는 행정구**(legal·구 재태깅 정합 때문). 관광지 detail_location은 스팟 태그로만 잔존.

### 3-4. legal_location 처리 (기하 전용, 행정구에 저장)

- legal_location은 **사라지지 않고 기하 전용으로 강등** — 스팟 필터 역할만 폐기.
- `category(행정구 DETAIL_LOCATION).legal_code`에 **1:1로 1번 저장**(강남구→11680). REGION은 자기 detail_location들의 legal **union**으로 폴리곤 상속. (REGION에 직접 박지 않음 — 재사용·정합 위해)
- 폴리곤 노출: `/region/{city}`(도시 경계) + 행정구 묶음 REGION(union). 관광지-only는 마커만.
- `ST_Contains` 인자 반전 버그는 **수정 완료**.

### 3-5. IA — 테마 leaf 페이지(SEO) + 캐러셀 섹션

```
① /region                              도시 인덱스 (지도 + 도시 선택 + 도시간 이동)
② /region/seoul                        CITY 상세 (REGION 그리드 + 도시간 이동 + 블로그 + 테마 캐러셀)
   └ /region/seoul/restaurants         CITY×테마 leaf   ← 'seoul restaurants' (월 1만~10만)   ★신설(A안)
③ /region/seoul/gangnam                REGION(zone) 상세 (섹션·subway·persona·구역 지도 + 테마 캐러셀)
   └ /region/seoul/gangnam/restaurants ZONE×테마 leaf  ← 'gangnam restaurants' (롱테일)
       └ 타이틀 "seoul (gangnam) restaurants" + (지역 detail_location ∩ master_theme 카테고리) 스팟 카드
```

- **theme은 depth 3·4 두 곳에 leaf로 존재** — city×theme(`/{city}/{theme}`) + zone×theme(`/{city}/{zone}/{theme}`). 둘 다 풀 그리드 SEO 랜딩.
- **3번째 칸 = zone/theme 공유 네임스페이스 (A안):** `/region/{city}/{X}`에서 X가 zone인지 theme인지를 **city별 슬러그 레지스트리**(`(city, slug) → {type: zone|theme, target_id}`, slug 유니크 PK)로 판정. 4번째 칸은 zone 확정 하의 theme이라 모호함 없음. zone=지명·theme=의도명사라 충돌 사실상 0, 어드민에서 zone↔master_theme 슬러그 충돌 생성 차단(가드).
- **페이지 내 테마 섹션 = 캐러셀** (city·zone 공통): '더보기→리스트' 폐기(→ 이전 'W3: 더보기→리스트 흡수' 결정 **갱신**). **monthly best 상위 9개**(기존 컴포넌트 가정, 디자인 시 조정) 캐러셀 + 스팟이 더 있으면 **"전체 보기" → 해당 leaf**.
  - **city×테마**(`/region/{city}/{theme}`): 'seoul restaurants' 등 **대형 키워드(월 1만~10만)** 포획. **CITY 스팟 전체 ∩ 테마(B-2)** 를 페이지화 — 완전집합이라 콘텐츠 항상 충분.
  - **zone×테마**(`/region/{city}/{zone}/{theme}`): 'gangnam restaurants' 등 **롱테일(100~1천)**. 콘텐츠 편차 커 임계 게이트(아래)로 조건부 생성.
  - 스팟 = ~~(해당 지역의 detail_location) ∩ (master_theme 카테고리)~~ → **city×테마 = CITY 스팟 ∩ 테마(B-2) / zone×테마 = REGION 선택 법정동 ∩ 테마**. **테마는 카테고리 2개 이상 묶을 수 있어 단일 필터 `/spot/list`로 표현 불가** → leaf 전용 쿼리. 데이터는 기존 그대로, **FE 페이지 템플릿 + 라우팅만 추가.**
- **leaf 생성 게이트 = 스팟 10개(= 캐러셀 9 + 1)부터:** ≤9면 캐러셀이 전부 노출 → "전체 보기"·leaf 없음. ≥10이면 캐러셀 9(monthly best 상위) + "전체 보기" → leaf. **"캐러셀에 다 못 담으면 leaf" 단순 규칙, 비노출 구간 0.**
- **SEO 가드레일 (필수 — 안 하면 thin/중복으로 역효과):**
  - **콘텐츠 임계 = 10**: 스팟 10개 미만 테마 leaf는 생성·색인하지 않음. (10~11짜리 leaf는 다소 thin할 수 있어 필요 시 개별 noindex)
  - **canonical**: 테마 leaf가 정본. `/spot/list?category=` 필터뷰는 noindex/canonical 양보(중복 경쟁 방지).
  - **slug = master_theme 안정 슬러그**(restaurants/tickets/shopping…) → URL·타이틀 일관.
  - **짧은 에디토리얼 인트로**(1~2줄, 자동/큐레이션)로 순수 카드 그리드 thin 방지.
- 기존 `/spot/region/{id}` 숫자 URL → 새 slug 구조 **301 리다이렉트**.

### 3-6. 테마 섹션 = 어드민 CMS (REGION 레벨)

> ⚠️ **스코프 (2026-07-14, 마스터 [260701] §5-2 확정):** 이 문서의 `master_theme`·"여러 카테고리 묶기" 서술은 **REGION(구역) 레벨 전용**이다. **CITY 레벨 테마축은 `home-navigation`(MAIN_RESERVATION 단일 카테고리)로 확정** — 문서 곳곳의 'CITY 집계 = CITY 스팟 ∩ master_theme' 식 표현은 모두 **home-nav MAIN_RESERVATION** 기준으로 읽는다(master_theme 다중묶음은 CITY에 적용 안 함, 마스터가 정본).

고정 택소노미가 아니라 운영자가 REGION별로 편성:
1. REGION 상세 → '섹션 생성'
2. 섹션명(예: 볼거리·체험) + 연결 카테고리(tickets&attractions, Day tour… 재량) + 저장
3. 섹션 간 순서 드래그

- 데이터 모델(신규): `region_section`(region_id·name(다국어, **자유**)·priority) + `region_section_has_category`(section↔category_code) + **`master_theme`(전역 사전: id·name 다국어·아이콘·**slug**)** + `region_section.master_theme_id`(**CITY 편집 화면에서 관리자가 그룹핑**, nullable). master_theme.slug는 테마 leaf 페이지(§3-5) URL·타이틀에 사용.
- ~~**마스터 테마 = CITY 집계용 그룹핑.** CITY가 REGION 섹션들을 합치려면 같은 master_theme로 묶여야 하고, 그 매핑을 CITY 편집 화면에서 관리자가 수동으로 함.~~ → **B-2 확정(2026-07-14)으로 CITY 집계는 REGION 섹션 그룹핑에 의존하지 않음**(CITY 스팟 ∩ master_theme). master_theme는 전역 테마 사전(테마↔카테고리)·테마 leaf 정의용으로 유지, REGION 섹션은 자유 편성(강남'쇼핑·패션', 홍대'쇼핑'). REGION 페이지 자체는 master_theme 안 씀.
- → category→intent 매핑 테이블 불필요. **"intent 척추 vs vibe" 분리는 시스템 강제 아님 → 권장 프리셋(§6 부록)으로 제공.**
- 가드레일: 카테고리 연결 시 `(지역 × 카테고리) 스팟 수`를 보여줘 빈 섹션 방지. **이 스팟 수가 10 미만이면 테마 leaf는 생성·색인하지 않음(§3-5 SEO 가드레일). 섹션 자체(캐러셀)는 9개 이하라도 노출.**

### 3-7. CITY tier (카드 메타만 저장, 스팟은 B-2로 뿌림)

CITY는 상세 콘텐츠를 **저장하지 않는다.** 스팟은 ~~자식 REGION에서 파생~~ **B-2 = 그 CITY에 `spot_has_category`로 연결된 스팟 전체 ∩ 테마**로 뿌린다(2026-07-14 확정):
- **CITY가 저장하는 것**: `slug`(라우팅) · **카드 메타**(대표 이미지·태그·설명 — `/region` 인덱스 카드용) · **도시간 이동**(도시쌍 테이블) · 폴리곤(시 경계). hero/긴 설명 같은 상세 에디토리얼은 저장 X.
- **CITY 상세 페이지 본문 = 파생**:
  - **스팟** = ~~연결된 REGION들(`region.city` FK)의 스팟을 지역 구분 없이 master_theme 기준으로 묶어 노출. master_theme = 관리자가 CITY 편집 화면에서 소속 REGION 섹션들을 묶어 만든 그룹~~ → **그 CITY에 `spot_has_category`로 연결된 스팟 전체를 master_theme(테마) 기준으로 묶어 노출(B-2)**. REGION 커버리지와 무관하게 완전집합이라 항상 충분.
  - **블로그** = theme와 **독립.** `블로그.detail_location → REGION → CITY` 경로로 집계해 **정렬 기준으로 별도 섹션** 노출(테마 묶음 아님).
- **활성화 게이트**: 카드 메타(image·tags·desc) 필수 (~~+ ≥1 REGION 연결~~ → **B-2 확정으로 REGION 없이 CITY 스팟만으로 페이지 성립** — 부산·제주 즉시 활성화 가능. REGION은 있으면 zone 그리드에 노출)
- **zone 그리드**(강남·홍대…)는 **네비게이션용 유지** — "지역구분 없이 theme"는 스팟 콘텐츠 묶음 방식이지 `/region/{city}/{zone}` 진입 제거가 아님

### 3-8. 어드민 `/region` 설계

- **탭 [CITY | REGION]**
- **CITY 탭**: `category(type=CITY)` 전체 테이블 → 활성화/비활성화(필수필드 게이트). **CITY 편집 화면 = 카드메타·slug·도시간이동 입력만.** ~~REGION 배선 + 소속 REGION 테마를 `master_theme`로 묶는 그룹핑 UI~~ → **폐기** (REGION→CITY 자동 도출 / CITY 집계는 B-2·home-nav — 마스터 §3-3①·§5-2). REGION↔master_theme 매핑은 REGION 섹션 CMS에서.
- **REGION 탭**: REGION 생성 + 행정구 detail_location 매핑 + 섹션 CMS + subway/blog/persona 큐레이션
- 부수: detail_location 생성/수정에 **상위 도시(parent) 입력** 추가(고아 양산 차단), `createCategory` type 화이트리스트

---

## 4. 결정 근거 · 검증 로그

### 4-1. 도메인 4층위
'지역'은 단일 개념이 아니라 ①legal_location ②category ③region ④landing_area의 합성어. 운영 실세는 ②, ③은 미완성 SEO 자산. (도메인 맵 §0)

### 4-2. REGION provenance — 자동생성·미관리
3개 독립 이벤트: **2025-01-13** 마이그레이션(컬럼 추가) → **2025-01-16** legal_location 5,332 정부 적재 → **2025-02-14** region 500개 자동 스크립트 생성(id 25~531). 공개 13개 외 미관리 → 삭제 근거.

### 4-3. 연결 메커니즘 — 프리픽스 LIKE (FK 아님)
`spot.legal_location_legal_code` ← `region.legal_location_legal_codes`(코드배열)을 `LIKE 'code%'`로 매칭. 강남=`["11650108","11680101"]` = 이미 멀티코드 union → 새 모델은 같은 묶음을 **detail_location 축으로** 이전.

### 4-4. 카디널리티 → 행정구만 1:1 → 단일 컬럼
detail_location 158 = 행정59/관광지81/동18. 행정구↔시군구 legal은 1:1. 관광지(홍대=마포구 6법정동, 1:N)는 REGION으로 빠지므로 legal 링크 제외 → 정션 불필요, 단일 컬럼.

### 4-5. spot↔region 직접 연결 = 없음
`spot` 테이블에 `region_id` FK 없음. 유일한 직접 연결은 `region_spot_area_has_spot`(6 area / 27 링크). → '스팟의 Region 연결 제거'는 이 27건 정리.

### 4-6. 전제 검증 — '인지 구역 vs 법정동' (Reddit 실측)
r/koreatravel 10,001건 원문 대조. 인지구역/POI가 같은 위치 행정·법정 단위를 1~2 오더 압도:

| 인지 구역 / POI | 언급 | 행정·법정 단위 | 언급 |
|---|---:|---|---:|
| Myeongdong | 1,030 | Jung-gu | 22 |
| Hongdae | 905 | Mapo-gu | 24 |
| Gangnam | 576 | Gangnam-gu | 8 |
| **Lotte World 223 + Jamsil 90** | **313** | Songpa-gu 3 / **Bangi-dong** | **0** |
| Seongsu | 181 | Samseong-dong·Jamsil-dong | **0** |

- 집계(`region_place_freq.csv`) sub-city 지명 35개 중 **법정동 0개**. → 전제 확정.
- 뉘앙스: `Gangnam`(576) ≫ `Gangnam-gu`(8) — 행정 접미사 없는 인지 라벨 선호(모델 지지). "지역=질문의 좌표계"는 별개 facet(`region_subtopic.csv` 근거).

---

## 5. 검증된 데이터 (prod, 2026-06-22~24)

| 항목 | 값 |
|---|---|
| region 총 / 공개(is_publish) | 514 / **13** (전부 legal_codes·marker 보유) |
| region 생성 | 2024 개별 14(id 4~22) + **2025-02-14 벌크 500(id 25~531)** |
| legal_location | 5,332 (시도17/시군구250/읍면동5,065), 2025-01-16 일괄 |
| detail_location | **158** = 행정구 59(구49·시2·군5·읍면3) / 관광지명 81 / 동 18 |
| └ parent(도시) | 있음 53 / **고아 105(66%)** |
| └ 연결 | 스팟 133 / region 30 / **무연결 25(삭제 후보, 12개 parent도 없음)** |
| └ 중복 | 서면×3(87/109/112), 성수동×2(98/477) |
| spot↔CITY / DETAIL_LOCATION | 5,425링크(1.0) / 3,751링크(1.01) |
| spot↔region 직접 | **없음**(region_id FK 부재) / region_spot_area_has_spot 6 area·27 링크 |
| detail_location↔legal | **없음** → 신설(행정구만, 단일 컬럼) |
| 인지구역 vs 법정동(Reddit) | 롯데월드223+잠실90 vs **Bangi-dong 0** / sub-city 35개 중 법정동 0 (§4-6) |

---

## 6. 작업 계획

> 의존성: **데이터(P1) → REGION/CITY 생성(P2) → 파라미터(P3) → UI(P4)**. P1의 재태깅은 외부 **multi-detail_location 기능**에 게이트됨.

### ⛔ 외부 선행 게이트
**스팟 multi-detail_location(1개→2개) 기능** — 별도 진행 중(`[260617] spot-multiple-detail-locations`). 이게 출시돼야 '관광지-only 스팟 구 재태깅'이 가능.

### Phase 1 — 데이터 정비 *(기획 독립, 일부는 게이트 대기)*
| ID | 작업 | 규모 |
|---|---|---|
| DL-3 | 행정구/관광지 분류 (게이트) — 동 18은 관광지로 흡수 | 행정 59 / 관광지 81+18 |
| DL-1 | 무연결 detail_location 제거 | 25개 |
| DL-2 | 중복 detail_location 통합 | 서면×3, 성수동×2 |
| LL | 행정구 59 → `category.legal_code` 1:1 연결 | 이름 자동매칭 + 수동 잔여 |
| RG-1 | region 벌크 500(id 25~531) 삭제 | ⚠️ 의존성 검증 선행 |
| RG-3 | region_spot_area_has_spot 27건 정리 | 스팟 직접 region 연결 해제 |
| DL-5 | **관광지-only 스팟 구 재태깅** | ⛔ multi-dl 게이트 / 대상 수 별도 산정 |

### Phase 2 — REGION/CITY 생성
- 행정구 묶음 REGION 생성 (강남=강남구+서초구 …) + 기존 공개 13개 `region_has_detail_location` 재배선
- CITY 콘텐츠 입력 + 활성화 (image·tags·desc / ~~≥1 REGION~~ B-2로 폐지)
- *관광지 REGION 승격은 구조 완성 후 수동(비긴급, 트래픽 낮음)*
- **생성 = 어드민** (스크립트 아님) → AD 도구가 Phase 2 선행. **유저 페이지(P4) 배포는 데이터 생성 완료 후 일정.**

### Phase 3 — 파라미터/백엔드 *(input: 와이어프레임)*
| ID | 작업 |
|---|---|
| BE-1 | 스팟 조회 축 전환 (legal prefix → region_has_detail_location → spot_has_category) |
| BE-2 | 폴리곤 resolve (city 경계 / 행정구 union / 관광지 마커) |
| BE-3 | slug 라우팅·리졸버 + **city별 슬러그 레지스트리**(`(city,slug)→{zone|theme}`, 유니크) — `/region/{city}/{zone\|theme}`(3번째 칸 공유 판정) + zone×theme leaf `/{city}/{zone}/{theme}` |
| BE-4 | **테마 leaf 쿼리**(지역 detail_location ∩ master_theme 카테고리, 멀티카테고리) + **테마 섹션 캐러셀 쿼리**(monthly best 상위 9) + **콘텐츠 임계 10·canonical**(`/spot/list?category=` 필터뷰 noindex 양보) |
| BE-5 | **`region_section`(자유명) + `region_section_has_category` + `master_theme`(전역) + section→master 매핑** (REGION 섹션 CMS + CITY 그룹핑) |
| BE-6 | **CITY 카드메타+slug+도시간이동 테이블** + **상세 스팟 쿼리**(~~자식 REGION theme 집계~~ **CITY 스팟 ∩ master_theme, B-2**) + `region.city` FK |
| BE-7 | subway('주요 역') · blog(detail_location 기준) · persona 큐레이션 영역 |
| BE-8 | **CITY 블로그 섹션** — `블로그.detail_location → REGION → CITY` 집계, 정렬 기준 노출 (theme 독립) |

### Phase 4 — UI
| ID | 작업 |
|---|---|
| FE-1 | 라우팅 (도시·구역·**테마 leaf** / 3번째 칸 zone\|theme 분기) |
| FE-2 | 기존 `/spot/region/{id}` → 301 |
| FE-3 | CITY 페이지(zone 그리드+이동+**theme 집계=CITY 스팟∩테마 B-2**) / REGION 페이지(섹션+subway+persona+지도) |
| FE-4 | 테마 섹션 **캐러셀**(monthly best 9) + 전체보기 → **테마 leaf**(풀 그리드 + 에디토리얼 인트로) / 폴리곤 렌더 |

> **유저 페이지 배포 = Phase 2 데이터 생성 완료 후 일정** (D #3). 어드민으로 데이터부터 채우고, FE 공개는 그 다음.

### 어드민 (횡단)
AD-1 `/region` 탭[CITY|REGION] · AD-2 CITY 활성화 게이트 · AD-3 REGION↔detail_location 매핑 · AD-4 섹션 CMS(생성/카테고리연결/순서) · AD-5 detail_location parent 입력 + createCategory type 화이트리스트 · AD-6 **슬러그 레지스트리 유니크 가드**(zone↔master_theme 슬러그 충돌 생성 차단)

### 검증
CV-1 재태깅 대상 스팟 수 산정 · CV-2 성공지표(참여 11초→·유입·구역필터 사용률 / 스팟이동 5% 가드레일)

### 부록 — 도시별 권장 섹션 프리셋 (어드민 출발점, 강제 아님)
- **서울**: 볼거리·체험 / 미식 / 쇼핑 / K-뷰티 / K-pop / 근교 (볼거리 톱)
- **부산**: 이동·접근 / 볼거리 / 해변·야경 / 미식 (교통 톱)
- **제주**: 거점·숙소 / 렌터카·드라이브 / 자연·체험 / 미식 (숙소·이동 톱)
- 근거: 도메인맵 도시 지문 + 레딧 인텐트(볼거리72.5·교통52.8·일정45.6·음식33·숙소28.1). 과소대표된 **일정/동선·숙소**는 블로그/숙소 섹션으로 보강.

---

## 7. 열린 결정 / 리스크

**닫힌 결정 (2026-06-24)**
- ✅ CITY 콘텐츠 저장소 → **카드 메타만 저장**(별도 콘텐츠 테이블 없음). ~~상세는 자식 REGION을 theme로 집계~~ → **2026-07-14 B-2로 갱신: 상세 스팟 = CITY 스팟 전체 ∩ theme**
- ✅ REGION→CITY 연결 → **FK** (`region.city` → `category(CITY)`)
- ✅ Phase 2 생성 방식 → **어드민**. 유저 페이지 배포는 데이터 생성 후 일정
- ✅ 동 18개 분류 → **관광지 버킷 흡수**(구 단위 아님). 부암동·평창동·송월동=무연결 삭제, 성수동×2=중복 통합과 겹침
- ✅ **마스터 테마** → REGION 섹션은 자유 편성, REGION 섹션 CMS에서 master_theme에 매핑. ~~CITY 편집 화면에서 관리자가 소속 REGION 테마를 master_theme로 그룹핑~~ → **B-2 확정(2026-07-14)으로 CITY 집계는 CITY 스팟 ∩ master_theme, REGION 그룹핑 불필요.** 블로그는 theme 독립(detail_location 경로 정렬 섹션)
- ✅ **테마 노출 = 캐러셀 + leaf (2026-06-25)** — city·zone 테마 섹션을 'monthly best 상위 9 캐러셀 + 전체보기→테마 leaf'로. 더보기→`/spot/list` 폐기(테마는 멀티카테고리라 단일필터 리스트 불가)
- ✅ **city×테마 살림(A안) (2026-06-25)** — `/region/{city}/{theme}` 신설해 head 키워드(seoul restaurants 월 1만~10만) 포획. zone과 3번째 칸 공유는 **city별 슬러그 레지스트리 + 어드민 유니크 가드**로 판정(zone=지명·theme=의도명사라 충돌 0)
- ✅ **leaf 임계값 10 (2026-06-25)** — 스팟 10개(= 캐러셀 9+1)부터 테마 leaf 생성·색인. "캐러셀에 다 못 담으면 leaf" 단순 규칙, 비노출 구간 0. 정렬은 monthly best

**남은 디테일 (구현 시)**
1. `master_theme` **전역 사전 vs CITY별** — *추천: 전역(쇼핑·미식 재사용, 도시간 일관)*
2. CITY에서 **미매핑 REGION 섹션 처리** — 노출 제외 vs 'etc' 묶음

**리스크**
- RG-1 삭제 안전성 — 의존성 검증 미실행
- DL-5 재태깅 — 외부 multi-dl 게이트에 종속 (일정 불확실)
- 임팩트 천장 — 3.8% 베이스. 활성화 개선만으론 작음 → 유입(리스트→/region 동선) 병행 필요 (회의록 합의 6·7)

---

## 8. 참고 문서
- 도메인 맵: `outputs/research/[260618] region-domain-map.md`
- 회의록(논의 전문): `outputs/meetings/region/[260619] meeting-region-page-improvement-0619.md`
- 수요 분석: `outputs/reddit-koreatravel/[260612] REPORT_region_deepdive.md`
- 와이어프레임: `https://wireframes-lkb.pages.dev/#region-domain-renewal`
