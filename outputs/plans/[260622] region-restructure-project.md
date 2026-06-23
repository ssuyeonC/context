# 지역(Region) 도메인 재구조화 프로젝트

작성일: 2026-06-22
상태: **기획 확정 · 착수 전** (Phase 1 데이터 정비부터)
출처/근거:
- `outputs/research/[260618] region-domain-map.md` (지역 4층위 도메인 정리)
- `outputs/meetings/region/[260619] meeting-region-page-improvement-0619.md` (회의록 + 추가논의 #1~#3)
- `outputs/reddit-koreatravel/[260612] REPORT_region_deepdive.md` (지역 수요 분석)
- prod DB 실측 (2026-06-22 세션) + product 모노레포 코드 검증

> **한 줄 요약** — REGION을 '행정 폴리곤에 매인 단일 동네'에서 **'여행객이 인지하는 큐레이션 구역'**으로 재정의한다. 스팟은 `legal_location` 프리픽스가 아니라 `region_has_detail_location → spot_has_category`로 가져오고, legal_location은 지도 기하 전용으로 강등한다. 데이터 정비 → REGION 생성 → 파라미터 → UI의 4단계 긴 호흡 프로젝트.

---

## 1. 왜 하나 (배경)

세 가지가 동시에 가리킨다:

1. **수요 vs 트래픽 격차** — 외부 여행 담론(r/koreatravel)의 **55.5%가 '지역'** 주제인데, 우리 지역 페이지는 전체 트래픽의 **3.8%**만 받고, 들어온 사람도 **평균 11초**에 이탈(스팟 리스트 49초의 22%). 단, 끝까지 본 5%는 스팟으로 전환 → 콘텐츠 가치가 0은 아니고 **구조가 수요와 어긋남**.
2. **분류 축 불일치** — 현재 지역 페이지는 같은 스팟 풀을 신선도/인기 렌즈로 16개 섹션에 반복 노출. 유저가 원하는 **의도(볼거리·교통·투어)·다도시·지역간 이동** 축이 없다.
3. **도메인 4층위 혼재** — '지역'이 ①행정(legal_location) ②운영분류(category) ③콘텐츠(region) ④마케팅(landing_area)으로 평행 존재. REGION(③)은 514개 중 발행 13개·서울 일색으로 잠재 SEO 자산이나 미완성.

→ 답은 "섹션을 더 쌓는 것"이 아니라 **분류 축을 유저 인지(구역)·의도(테마)로 바꾸는 것.**

---

## 2. 핵심 결정사항 (요약)

| # | 결정 | 한 줄 |
|---|---|---|
| D1 | **REGION = 큐레이션 구역** | 여러 DETAIL_LOCATION을 손으로 묶는 '여행객 인지 구역' (강남=강남구+서초구) |
| D2 | **스팟 축 전환** | `legal prefix` → `region_has_detail_location → spot_has_category` |
| D3 | **legal 연결은 행정구 detail_location만** | 행정구(~59)에 `category.legal_code` 1:1 단일컬럼 / 관광지(~81)는 REGION으로 |
| D4 | **관광지 detail_location 유지(삭제 안 함)** | 스팟 태깅돼 있음 → REGION으로 승격하되 비긴급(수동·후행) |
| D5 | **legal_location 기하 전용 강등** | 스팟 필터 역할 폐기, 폴리곤·좌표판정만 유지 |
| D6 | **4단 IA** | `/region` → `/{city}` → `/{zone}` → `/{category}` |
| D7 | **비공개 REGION 500개 삭제** | 2025-02-14 벌크(id 25~531), 의존성 검증 후 |

---

## 3. 모델 재정의 상세

### 3-1. REGION = 여행객이 인지하는 구역

여행객은 '방이동'(법정동)이 아니라 '잠실/롯데월드'(인지 구역)로 목적지를 잡는다. REGION을 그 **인지 구역**으로 재정의하고, 여러 DETAIL_LOCATION을 사람이 큐레이션해 묶는다. *(이 전제는 Reddit corpus로 실측 검증 — §4-6)*

- `강남` REGION → DETAIL_LOCATION `강남구` + `서초구`
- `광화문` REGION → `을지로` + `종로구` + `광화문` (관광지+행정구 혼재도 의도적으로 OK)
- `/region/seoul/gwanghwamun` 페이지 = 이 구역에 묶인 detail_location들에 태깅된 스팟 노출

### 3-2. 두 갈래 포크 (체인 아님)

```
            ┌─ region_has_detail_location ─ detail_location ─ spot_has_category ─ spot   ← 콘텐츠/스팟 축 (새로 사용)
region ─────┤   (관리자 큐레이션 junction)     (=category.code)    (스팟 실제 태깅)
            │
            └─ legal_location_legal_codes ─ legal_location                              ← 지도 기하 축 (강등·유지)
               (또는 detail_location.legal_code 경유)   (폴리곤·좌표판정)
```

핵심: **detail_location과 legal_location은 직접 안 닿는다**(category에 legal_code 컬럼 없음). 스팟은 detail_location 통해, 기하는 legal_location 통해 — 두 축은 region에서 갈라진다.

### 3-3. detail_location ↔ legal_location — 행정구만 1:1

- **행정구역 단위(구·시·군·읍면, ~59개)에만** `category.legal_code`를 1:1로 신설(강남구→11680, 종로구→11110). 이름 기준 자동매칭 가능.
- **관광지명(~81개, 홍대·경복궁·명동)은 legal 연결 안 함** → REGION으로 관리. 단 스팟 태깅돼 있어 **삭제하지 않음**.
- 1:1이라 **정션 불필요, 단일 컬럼으로 충분**(다대다였던 홍대=마포구 6법정동 케이스는 홍대가 REGION이 되며 빠짐).

### 3-4. legal_location 역할 분리

| legal_location의 일 | 새 모델 |
|---|---|
| 스팟 필터(region.legalLocationLegalCodes 프리픽스) | ❌ 폐기 → detail_location |
| 지도 폴리곤(경계 그리기) | ✅ 유지 |
| 좌표→지역 판정 | ✅ 유지 (`ST_Contains` 버그 수정 완료) |

**폴리곤 소싱**: `/region/seoul`급 = CITY가 자기 legal(11) 직접 보유 / 행정구 묶음 REGION = detail_location들의 legal **union** / 관광지 REGION = **마커만**(폴리곤 없음). 폴리곤은 /region/seoul급에서 필요.

### 3-5. 4단 IA

```
① /region                              도시 (서울·부산·제주·경주)  + 도시간 이동
② /region/seoul                        도시 상세 (구역 리스트 + 도시간 이동)
③ /region/seoul/gwanghwamun            구역(REGION) 상세 = 연결된 detail_location 스팟
④ /region/seoul/gwanghwamun/tickets    구역 × 테마(category)
```
- ④ 스팟 쿼리 = (구역 detail_location들) ∩ (category=tickets). URL=상품 카테고리, 큐레이션 정렬=Reddit 의도.
- 기존 `/spot/region/{id}`(숫자 id) → 새 slug 구조로 **301 리다이렉트**.

### 3-6. 비공개 REGION 500개 삭제

- 514개 = 공개 13 + 비공개 501. 비공개 대부분은 2025-02-14 자동 스크립트 일괄 생성·미관리.
- **삭제 기준 = id 25~531 (2025-02-14 벌크)**, `is_publish=0` 아님(초기 수동 비공개 1개 보호).
- 선행: region_review·하드코딩 regionId(4·5·15)·region_has_* 의존성 검증.

---

## 4. 결정에 이른 논의·근거 (검증 로그)

### 4-1. 도메인 4층위 (출발점)

"지역"은 단일 개념이 아니라 ①legal_location(행정 폴리곤) ②category CITY/DETAIL_LOCATION/SUBWAY(운영 분류) ③region(콘텐츠 페이지) ④landing_area(마케팅)의 합성어. 운영 실세는 ②(스팟 3,710개가 매달림), ③은 미완성 SEO 자산. (도메인 맵 §0)

### 4-2. REGION provenance — 자동생성·미관리 확인

DB 타이밍 + 마이그레이션 코드로 확인한 3개 독립 이벤트:
- **2025-01-13** 마이그레이션 `add-legal-location-relationships` — region에 `legal_location_legal_codes`·`marker_position` 컬럼 추가
- **2025-01-16** legal_location 5,332행 정부 데이터 일괄 적재
- **2025-02-14** region 500개 자동 스크립트 일괄 생성(id 25~531, 코드·마커 채워서)

→ "legal_location 생길 때 일괄 추가"가 아니라 **별도 자동화 산물**. 공개 13개를 뺀 나머지는 미관리 → 삭제 근거 확보.

### 4-3. 연결 메커니즘 — 프리픽스 LIKE (FK 아님)

- `spot.legal_location_legal_code`(좌표로 계산된 법정동 풀코드) ← `region.legal_location_legal_codes`(코드 접두사 배열)을 **`LIKE 'code%'`**로 매칭. (`update-region-flags.consumer.ts`, `region-review.repo.ts`, `region.repo.ts`)
- 명동=`["11140"]`(중구) → 중구 아래 모든 법정동 스팟. 부산=`["26"]`(시도) → 부산 전체.
- **강남=`["11650108","11680101"]`** = 서초구·강남구 각 1개 법정동. → 현재도 이미 **멀티코드 union**을 하고 있고, 새 모델은 같은 묶음을 legal_code 축에서 **detail_location 축으로** 옮기는 것.

### 4-4. 카디널리티 → 행정구만 1:1 → 단일 컬럼

- detail_location 158개 이름 분류: 구49/시2/군5/읍면3=**행정 59**, 기타(관광지명)=**81**, 동=**18**.
- 행정구↔시군구 legal은 **1:1**(강남구↔강남구). 관광지(홍대=마포구 6법정동)는 1:N이지만 **REGION으로 빠지므로** 링크 안 함.
- 결과: legal 링크 대상이 1:1만 남아 **정션 → `category.legal_code` 단일 컬럼**으로 단순화.

### 4-5. 커버리지 갭

스팟이 detail_location 경로로만 노출 → **detail_location 미태깅 스팟 ~1,700개**(CITY 5,425 − DETAIL_LOCATION 3,710)가 새 경로에서 누락 가능. 구역이 큐레이션이라 허용될 수 있으나 인지 필요.

### 4-6. 전제 검증 — '인지 구역 vs 법정동' (Reddit 실측, 2026-06-22)

§3-1 전제("여행객은 법정동이 아니라 인지 구역으로 목적지를 파악")를 크롤링 corpus(r/koreatravel 10,001건)로 직접 대조. 인지 구역/POI 언급이 **같은 위치의 행정·법정 단위를 1~2 오더 압도**(원문 occurrence):

| 인지 구역 / POI | 언급 | 같은 곳 행정·법정 단위 | 언급 |
|---|---:|---|---:|
| Myeongdong | 1,030 | Jung-gu | 22 |
| Hongdae | 905 | Mapo-gu | 24 |
| Gangnam | 576 | Gangnam-gu | 8 |
| **Lotte World 223 + Jamsil 90** | **313** | Songpa-gu 3 / **Bangi-dong** | **0** |
| Insadong 251 · Bukchon 208 | | Jongno-gu | 18 |
| Seongsu | 181 | Samseong-dong·Jamsil-dong·Yeoksam | **0** |

- 집계(`region_place_freq.csv`)의 sub-city 지명 **35개 중 법정동 0개** — 전부 인지구역·랜드마크·도시.
- 네 예시 그대로 **롯데월드(223)+잠실(90) vs 방이동(0)** → 전제 확정.
- 뉘앙스: ① `Gangnam`(576) ≫ `Gangnam-gu`(8) — 인지구역·행정구 명칭이 겹쳐도 **행정 접미사 없는 라벨을 선호**(모델 지지: 강남구+서초구를 묶되 '강남'으로 노출). ② 행정구(-gu)도 8~24회 등장(숙소/물류 맥락) — 빈도만 1~2 오더 낮음 → **행정=백엔드 빌딩블록, 노출=인지구역** 모델과 정합. ③ "지역=질문의 좌표계"는 **별개 facet**(근거: `region_subtopic.csv` 볼거리72.5·교통52.8·일정45.6) — 네이밍 증거와 분리해야 정확.
- 방법론 주의: raw occurrence(부분문자열·과집계 노이즈) — 1~2 오더 격차라 결론 견고, 클린 per-post 집계도 동일 그림.

---

## 5. 검증된 데이터 (prod, 2026-06-22)

| 항목 | 값 |
|---|---|
| region 총 / 공개(is_publish) | 514 / **13** (전부 legal_codes·marker_position 보유) |
| region 생성 | 2024년 개별 14개(id 4~22) + **2025-02-14 벌크 500(id 25~531)** |
| legal_location | 5,332행 (시도17/시군구250/읍면동5,065), 2025-01-16 일괄 |
| detail_location(category type) | **158** |
| └ 분류(이름) | 구49·시2·군5·읍면3=**행정59** / 관광지명=**81** / 동=**18** |
| └ parent(도시) | 있음 53 / **고아 105 (66%)** |
| └ 연결 | 스팟 133 / region 30 / **무연결 25(삭제 후보, 12개는 parent도 없음)** |
| └ 중복 | 서면×3(87/109/112), 성수동×2(98/477) |
| spot↔CITY / DETAIL_LOCATION | 5,425링크(1.0) / 3,751링크(1.01) |
| 미태깅 갭 | detail_location 없는 스팟 ~1,700 |
| 인지구역 vs 법정동 (Reddit) | 롯데월드223+잠실90 vs **Bangi-dong 0** / sub-city 지명 35개 중 법정동 0 (§4-6) |
| region↔legal | `legal_location_legal_codes`(JSON) + 프리픽스 LIKE, FK 없음 |
| detail_location↔legal | **연결 없음** (신설 대상) |

---

## 6. 작업 계획 (4단계)

### Phase 1 — 데이터 정비 *(지금 가능, 기획 독립)*
| ID | 작업 | 규모/근거 |
|---|---|---|
| DL-3 | **행정구/관광지/동 분류** (게이트) | 59 / 81 / 18 |
| DL-1 | 무연결 detail_location 제거 | 25개 |
| DL-2 | 중복 detail_location 통합 | 서면×3, 성수동×2 |
| LL | 행정구59 + 노출 CITY → `category.legal_code` 연결 | 1:1 자동매칭 + 수동 잔여 |
| RG-1 | region 벌크 500개(id 25~531) 삭제 | ⚠️ 의존성 검증 선행 |
| DL-4 | detail_location parent 보정 | 후순위(어드민 피커용) |

### Phase 2 — REGION 생성
- 행정구 묶음 zone REGION 생성 (강남=강남구+서초구 등)
- **기존 공개 13개 `region_has_detail_location` 재배선** (현재 legal prefix → detail_location)
- *관광지 승격(RG-2)은 구조 완성 후 수동* — 트래픽 적어 비긴급
- ⚠️ 결정: 생성을 **스크립트 vs 어드민 손작업** — AD 도구 타이밍이 여기 달림

### Phase 3 — 필요한 파라미터 추가 *(input: 와이어프레임/개선계획)*
| ID | 작업 |
|---|---|
| BE-1 | 스팟 조회 축 전환 (legal prefix → region_has_detail_location → spot_has_category) — **지역 페이지뿐 아니라 스팟 리스트 `region=` 필터 + 프론트 변환·서울 도시 분기까지 포함** (↓ 주1) |
| BE-2 | 폴리곤 resolve (city=자기 legal / 행정구 zone=legal union / 관광지=마커만) |
| BE-3 | `/region/{city}/{zone}/{category}` slug 쿼리·리졸버 |
| BE-+ | 개선계획 신규 필드 (intent 탭·도시간 이동 카드 등) |

> **주1 — 스팟 리스트 `region=` 필터가 BE-1 범위인 이유 (코드 확인, 2026-06-23)**
> 구역 페이지의 "테마 더보기"는 기존 스팟 리스트(`/spot/list`)로 핸드오프하는데, 거기서 축이 어긋나면 *같은 구역인데 다른 스팟*이 나온다. 실측 결과:
> - **리스트 `region=`은 현재 legacy 축(legal prefix LIKE).** 프론트(`apps/web/.../pages/spot/list/index.tsx:327–348`)가 `region` 파라미터로 해당 region의 `legalLocationLegalCodes`를 꺼내 인자로 전달 → 백엔드(`spot.repo.ts:2297` `addLegalLocationLegalCodesFilter`)가 `legal_location_legal_code LIKE 'code%'`로 필터. `region_has_detail_location → spot_has_category`(신축) 아님.
> - **theme(`category`/`middleCategory`)는 이미 `spot_has_category` 경유 → 신축과 호환.** 핸드오프 시 그대로 재사용 가능.
> - **서울 도시는 별도 분기.** 프론트가 `SEOUL_REGION_CITY_SLUG`를 명시적으로 제외(L328–330)하고 legal_codes를 비움 → 서울은 다른 경로로 필터됨. 신축 통합 시 별도 처리 필요.
> - **결론:** BE-1은 ① 백엔드 `region=` 리졸버를 신축으로 교체(구역 페이지와 **공용 리졸버**) + ② 프론트의 legal_codes 직접 변환 제거(region id 그대로 전달) + ③ 서울 도시 분기 신축 통합 — 까지 덮어야 더보기 핸드오프가 일관됨.

### Phase 4 — region 페이지 UI 개선
| ID | 작업 |
|---|---|
| FE-1 | 4단 라우팅 |
| FE-2 | 기존 `/spot/region/{id}` 498 → 새 slug 301 |
| FE-3 | 스팟 섹션 detail_location 재편 + intent 탭 + 이동 카드 + above-the-fold |
| FE-4 | `/region/seoul`급 폴리곤 렌더 |

### 횡단 트랙
- **어드민(AD)**: detail_location parent 입력 / detail_location↔legal 매핑 UI / region↔detail 연결 UI / createCategory type 화이트리스트 — 생성·매핑 방식에 따라 Phase 2~3 배치
- **검증(CV)**: 미태깅 스팟 ~1,700 방침 / 성공지표(참여 11초→목표·유입·구역필터 사용률, 스팟이동 5% 가드레일)

### 의존성
데이터(P1) = REGION(P2)의 재료 → REGION = 파라미터(P3)의 테스트 대상 → 파라미터 = UI(P4)의 공급원. LL은 폴리곤(FE-4)이 필요해지는 P2(서울)와 함께.

---

## 7. 열린 결정 / 리스크

1. **Phase 2 생성 방식** — 스크립트 vs 어드민(AD 도구 선후 결정).
2. **동 18개 분류** — 행정/구역 판정 필요.
3. **DL-4 parent 보정 우선순위** — region.city_slug가 도시묶음을 대신하므로 후순위 가능.
4. **미태깅 스팟 ~1,700개** — 누락 허용 vs detail_location 보강.
5. **RG-1 삭제 안전성** — 의존성 검증 미실행(다음 액션).
6. **임팩트 천장** — 3.8% 베이스. 활성화(페이지 개선)만으론 전사 임팩트 작음 → 유입(리스트→/region 동선)이 병행돼야 의미. (회의록 합의 6·7)

---

## 8. 참고 문서
- 도메인 맵: `outputs/research/[260618] region-domain-map.md`
- 회의록(논의 전문): `outputs/meetings/region/[260619] meeting-region-page-improvement-0619.md` (추가논의 #1 퍼포먼스 / #2 3단 IA / #3 REGION 재정의)
- 수요 분석: `outputs/reddit-koreatravel/[260612] REPORT_region_deepdive.md`
