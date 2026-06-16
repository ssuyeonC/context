# Google TTD 모수 확보 종합 정리

- **작성일**: 2026-06-01
- **기준 자료**: `work/kiev/ttd-pool-expansion-context.md` (5/28 모수 확장 검토) + `#product-core` 슬랙 (5/30 다중 POI 에러 대응)
- **역할 분담** (5/27 확정): 강병준 — 기술 대응(코드/데이터/POI) / 정수연 — 모수 확장 검토
- **목적**: TTD 활성 모수를 89개 → ~500개로 확장하기 위한 현황·제약·조치·액션 플랜 통합 정리. 5/30 다중 POI 조치 포함.

---

## 0. 한 문장 요약

> **Google TTD 피드에 노출되는 활성 모수(현재 89개) 중 절반 이상이 무효이거나 노출 효율이 낮다. 이를 (A) 내부 정상화 + (B) 다중 POI 에러 대응 + (C) 신규 메타데이터 입력으로 단계적으로 풀어 ~520개까지 확장한다. 5/30 다중 POI 처리로 패키지성 투어 25개가 노출 자격을 회복했고(6/1 확인), 잔여 무효 모수는 한글 POI 미매칭·빈 POI·계절·부적격 카테고리 등 원인별로 분리해 후속 처리한다(§5.8 / Action 0-A~F).**

---

## 1. 배경 & 목적

Google Actions Center의 **Things To Do (TTD)** 피드에 Creatrip 스팟을 내보내 입장권·투어·체험 상품을 광고/무료 노출하는 채널. 활성화된 스팟은 매일 TTD 피드로 업로드된다.

- 모수 = 노출 채널의 크기 → 모수 확장이 곧 무료/광고 노출 기회의 확장
- 5/27 슬랙(`#product-core`)에서 역할 분담: 강병준(기술 대응) / 정수연(모수 확장 검토)

---

## 2. 현재 연동 현황

### 2.1 DB 기준 (production)

- **활성 TTD 스팟 (`is_ttd = 1`)**: **89개**
- `spot_google_ttd` 메타데이터 행: **402개** (비활성화 이력 포함)
- relation_type 분포:
  - `RELATION_TYPE_ADMISSION_TICKET` (입장권): **49개**
  - `RELATION_TYPE_RELATED_NO_ADMISSION` (투어/체험): **40개**

### 2.2 Google Actions Center 기준 (report.tsv)

- 등록 모수: **87개**
- **유효 노출 효율 낮음**: 28일 Search Referrals 0건이 약 60개 (절반 이상)
- 상위 유입: 롯데월드(41), 전쟁기념관(6), 부산 해변열차(5), 블루라인파크 등
- 3개 채널(Ads/Admission/Experience) 전부 Not Approved인 **무효 모수: 약 16개**

### 2.3 report.tsv 컬럼 정의 (참고)

| 컬럼 | 의미 |
|---|---|
| Product Id | Creatrip 스팟 코드 (`spot.code`) |
| Title | 상품 제목. 150바이트(UTF-8) 제한 |
| Locations | 연결된 POI(관광지) 이름. 빈값이면 `Missing related POI` |
| Languages | 피드 포함 번역 언어 (표준 14개) |
| Ads / Admission / Experience / Tour Operator Status | 채널별 노출 자격 |
| Maps / Search Referrals (28d) | Google Maps·Search 유입 클릭 수 |

- **Status 값**: `Eligible`(노출) / `Not Approved`(거부)
- **정상 상태 정의**: Admission ↔ Experience 중 1개 이상 Eligible + Tour Operator는 Not Approved (중개사는 정상)

---

## 3. TTD 연동 정책

### 3.1 계정·브랜드
- **단일 계정 = 단일 트랙 원칙**: Appointments Redirect + Reservations(Dining) 동시 운영 불가
- Creatrip은 **TTD 전용 별도 계정** 운영
- 식당은 Appointments 계정에서 분리 → 별도 처리

### 3.2 4개 노출 채널

| 채널 | 비용 | 분류 | 자격 |
|---|---|---|---|
| Ads | 유료 | 모든 종류 | Google Ads allowlist |
| Admission Free Listing | 무료 | 입장권 | `ADMISSION_TICKET` + POI eligible |
| Experience Free Listing | 무료 | 투어/체험 | `RELATED_NO_ADMISSION` + POI eligible |
| Tour Operator | 무료 | 사업자 직접 | GBP 직접 보유 (중개사 제외) |

→ 스팟 단위로 보면 Admission ↔ Experience는 상호배타적. **단, 다중 POI 도입 후 POI 단위로는 공존 가능** (§5 참조).

### 3.3 relation_type (`TtdRelationType` 3종)

| 값 | 정의 | 노출 채널 |
|---|---|---|
| `ADMISSION_TICKET` | 상품 = POI 입장권 자체 | Admission Free Listing |
| `RELATED_NO_ADMISSION` | POI 근처/관련 활동·투어 (입장권 미포함) | Experience Free Listing |
| `SUPPLEMENTARY_ADDON` | POI 방문 보조 (셔틀/오디오가이드/픽업) | 보조 슬롯 (Eligible 카운트 미포함이 정상) |

오분류(투어인데 ADMISSION_TICKET) → `Overtagged admission` 에러 → 전체 거부

### 3.4 POI 요구사항
- 모든 상품은 최소 1개 POI 연결 필수
- POI는 TTD 프로그램 자격 보유 + Google Place ID 정확 매칭
- `google_place_id`를 리뷰 수집/TTD 공용으로 쓰던 것을 **TTD 전용 `related_google_place_id`로 분리** (5/12)

### 3.5 가격 정책
- 표준 성인 가격 명시 필수 / 30일 내 예약 가능 가격 1개 이상 / 계절·이벤트 종료 시 즉시 제거
- 노출 금액 = 옵션 중 최고가 (5/12 람다 수정)

### 3.6 데이터 품질
- title·option title 150바이트(UTF-8) 제한 / option 번역 빈 문자열 금지(모든 언어 채움)

### 3.7 카테고리 정책
- **TTD 미지원(영구 제외)**: 식당·헤어·카페 → Appointments/Dining 트랙
- **TTD 지원 (어드민 필터 기준 14개, 5/12)**: 명소&입장권·Concert·프라이빗투어·서울근교투어·자연명소투어·도시투어·전통체험투어·K-POP클래스·푸드클래스·원데이클래스·놀이공원·액티비티&레저·스키투어·한복&스냅
- **추가 4개 (애매하나 실적 있어 추가)**: 투어·체험·K-뷰티·전문헤어

### 3.8 운영 진입 조건 (`is_ttd = 1` 유지 게이트, 5/12 확정)
- 영업 중 + 예약 가능 + 예약 가능 시간대 존재 + 어권(다국어) 공개 + TTD 메타데이터·Option Categories 설정 완료
- 5/12에 위반 스팟 **90+개 `is_ttd=0` 일괄 회수**

---

## 4. 모수 확장을 가로막는 5대 제약

| # | 제약 | 현황 | 대응 |
|---|---|---|---|
| 5.1 | **카테고리 미커버** | 미지원(식당·헤어·카페) 7개 회수 | 5/12 카테고리 4개 추가로 일부 회복 |
| 5.2 | **relation_type 오분류** | 투어인데 ADMISSION → Not Approved. 5/12 18개 정정 | 단일 정정으로 부족한 패키지성 스팟은 **다중 POI로 재구성** (§5) |
| 5.3 | **Google Place ID 매칭 실패** | 23개 스팟 매칭 실패 | TTD 전용 필드 분리(5/11) + 다중 POI에서 올바른 POI 연결로 동시 해소 |
| 5.4 | **데이터 품질** | 번역 누락 19·title 초과 48·가격 위반 | 람다 패치 완료 |
| 5.5 | **운영 부적격** | 시간대/어권/예약가능성 미충족 | 5/12 90+개 일괄 회수 |

**관련 스팟 명단**
- §5.2 5/12 정정 18개: `2, 10941, 11519, 11522, 11583, 12850, 12872, 12957, 12986, 12998, 13000, 13064, 13115, 13167, 13468, 13879, 14491, 14542`
- §5.3 매칭 실패 23개: `11370, 12873, 12984, 13039, 13133, 13135, 13168, 13173, 13176, 13177, 13207, 13471, 13472, 13490, 13566, 13630, 13631, 13728, 13730, 13755, 13760, 13765, 14581`

---

## 5. 무효 모수 + 5/30 다중 POI 에러 대응 ★

5대 제약 중 §5.2·§5.3이 만들어낸 **무효 모수(채널 전부 Not Approved)**가 모수 효율의 가장 큰 누수다. 5/30 강병준 기술 대응으로 이 핵심을 다중 POI 처리로 풀고 있다.

### 5.1 직접 대상 에러 2종 (Actions Center 리포트, 5/30)

| 에러 | 건수 | 비중 | Google 권고 |
|---|---:|---:|---|
| **None of the related POIs is eligible for the program** | 45 | 51.72% | 자격 있는 관련 POI 추가. 'Find Location Matches'로 자격 확인 |
| **Missing related POI with an admission** | 39 | 44.83% | 관련 POI 중 하나를 입장권 보유로 표시 |

→ 두 에러가 전체의 ~96%. **상품 데이터가 아니라 POI 구성 자체의 문제.**

### 5.2 구조적 원인

기존에는 한 스팟에 **단일 POI + 단일 relation_type(fallback)** 만 연결 가능했다. 그러나 Creatrip 상품 다수는 **여러 관광지를 묶은 패키지**(예: "설악산+낙산사 일일투어", "남이섬+쁘띠프랑스+이탈리아마을").

- 단일 POI만 걸면 → 나머지 관광지 누락 → "자격 있는 POI 없음" / "입장권 POI 없음"
- 패키지 안에 입장권성(낙산사)과 비입장권 활동(설악산 트레킹)이 섞이는데 단일 relation_type으로 표현 불가

### 5.3 조치 — 다중 POI (Multiple Related POIs)

한 스팟에 **여러 Related POI를 연결하고, 각 POI마다 개별 relation_type을 부여**.

**적용 예시 — 스팟 2 (설악산+낙산사 일일투어)**, 어드민 `Google Actions → Things To Do → 상세 Drawer → Related POIs (2)`:

| # | POI | Google Place ID | relation_type |
|---|---|---|---|
| 1 | Seoraksan National Park | `ChIJ01rMH2ij2F8RftWPpRMs3kc` | `RELATED_NO_ADMISSION` |
| 2 | Naksansa Temple | `ChIJzcljWJOv2F8RhIkfptRT3sg` | `ADMISSION_TICKET` |

→ 입장권 POI(낙산사)를 명시해 **"Missing admission" 해소**, 자격 POI 2개 연결로 **"None eligible" 해소**.

**메타데이터 구조**
- `Relation Type (fallback)`: Related POIs가 비었을 때 스팟 기본 Place ID에 적용 (fallback 역할로 격하)
- `Related POIs`: POI별 Place ID + relation_type 개별 지정 (핵심 필드)

### 5.4 1차 대상 — 38개 스팟 (5/30 지정)

```
2, 10941, 11370, 11519, 11522, 12850, 12872, 12873, 12957, 12984,
12986, 12998, 13000, 13039, 13064, 13115, 13135, 13167, 13168, 13173,
13177, 13207, 13468, 13471, 13472, 13490, 13566, 13630, 13631, 13728,
13730, 13755, 13760, 13765, 13879, 14491, 14542, 14581
```

**기존 제약 명단과의 교차** — 38개는 §5.2(오분류) + §5.3(Place ID 실패)을 다중 POI 한 방식으로 동시 해소하는 묶음:

| 출처 | 겹침 | 해석 |
|---|---|---|
| §5.2 오분류 정정 18개 | 17개 겹침 | 단일 정정으로 부족 → 다중 POI 재구성 |
| §5.3 매칭 실패 23개 | 21개 겹침 | 올바른 POI 다중 연결로 동시 해소 |
| 무효 모수 16개 | 8개 (`12850, 12984, 12986, 13064, 13135, 13566, 13730, 13760`) | 절반이 이번 배치로 직접 해소 |

### 5.5 이번 배치 밖 — 별도 조사 필요 (무효 모수 잔여 8개)

| Spot ID | 제목 | 추정 원인 |
|---|---|---|
| 13455 | 부산 블루라인파크 스카이캡슐 일일투어 | relation_type / place_id |
| 14254 | 남이섬 입장권 + 셔틀버스 | Locations 빈값 |
| 12925 | 서울 나이트투어 북악~낙산 | 조사 필요 |
| 13414 | 강원여행 (제이드/남이/쁘띠) | 언어 누락 (th 없음) |
| 11239 | N서울타워 전망대 | 조사 필요 (입장권인데 거부) |
| 11240 | 남이섬+쁘띠+이탈리아+아침고요 | 조사 필요 |
| 11561 | 양평 패러글라이딩 | 조사 필요 |
| 11934 | 대구 컴뱃 태권도 | 조사 필요 |

→ 다중 POI만으로 안 풀릴 가능성(언어 누락·Locations 빈값·입장권 단독 거부). 개별 진단 후 별도 조치.

### 5.6 다중 POI가 바꾸는 정책 맥락

| 항목 | 기존 (5/28) | 다중 POI 후 |
|---|---|---|
| 스팟당 POI | 1개 (+ relation_type fallback) | N개, 각 POI별 relation_type |
| relation_type 오분류 | 단일 값 정정 | POI별 분리 지정으로 근본 해소 |
| 패키지 상품(다관광지) | 표현 불가 → 무효 | POI별 자연 매핑 |
| Admission ↔ Experience | 스팟 단위 택일 (§3.2) | **POI 단위 공존 가능** |

### 5.7 조치 후 현황 (2026-06-01 report.tsv 기준)

> ⚠️ 이전 시점 report.tsv 원본이 없어, 문서 기록된 과거 상태 + 현재 TSV의 다중 POI 흔적으로 추정한 비교.

**다중 POI 반영 확인** — `Locations` 컬럼에 복수 POI가 연결된 흔적이 38개 대상 다수에서 관측됨. 예: 스팟 2 = `Naksansa Temple` + `Seoraksan National Park` (5/30 스크린샷 일치), 13039 DMZ = POI 7개, 13631 제주 = POI 5개.

**38개 대상 결과: ~25개 유효화 / 13개 여전히 무효**

- **✓ 노출 자격 획득 (25개)**: `2, 10941, 11370, 11522, 12872, 12957, 12998, 13000, 13039, 13168, 13173, 13177, 13207, 13468, 13471, 13472, 13490, 13630, 13631, 13728, 13755, 13765, 13879, 14542, 14581`
  → DMZ·제주·남이섬·근교 다관광지 투어가 대거 통과. 조치의 핵심 성과.
- **✗ 여전히 무효 (13개)**: `11519, 12850, 12873, 12984, 12986, 13064, 13115, 13135, 13167, 13566, 13730, 13760, 14491` — 원인이 다중 POI가 아님(§5.8).

**기존 무효 모수 16개는 거의 그대로 무효** — `13455, 12986, 13730, 14254, 12925, 13135, 12850, 13414, 13064, 11239, 12984, 13760, 13566, 11240, 11561, 11934` 전부 현재도 무효. 이 중 8개는 38배치에 포함돼 다중 POI를 받았으나 다른 원인(한글 POI·계절·재승인 대기)으로 여전히 거부.

### 5.8 처리 필요 스팟 — 원인별 테이블

현재 무료 노출(Admission·Experience 둘 다 Not Approved)을 못 받는 스팟을 원인별로 분류.

**A. 한글 POI명 → Google Place 미매칭** (`related_google_place_id` 백필)

| Spot | 상품 | POI(현재) |
|---|---|---|
| 12850 | SCENT M.O.M.O 향수 만들기 | 센트모모 본점 |
| 11519 | 단양 패러글라이딩 | 단양패러글라이딩 |
| 11561 | 양평 패러글라이딩 | 패러러브 양평 캠프 |
| 11934 | 대구 컴뱃 태권도 | 아이캔늘품태권도장 |
| 14243 | The Cave 반 고흐 전시 | 더 케이브 서울 |
| 12879 | 런닝맨 강릉 | 런닝맨 강릉점 |

**B. Locations 빈값 (POI 미연결)**

| Spot | 상품 | 조치 |
|---|---|---|
| 13167 | 전통민화 클래스 | POI 신규 연결 (인사동 등) |
| 14254 | 남이섬 입장권+셔틀버스 | 남이섬=ADMISSION + 셔틀=SUPPLEMENTARY_ADDON 다중 구성 |

**C. 다중 POI 적용했으나 재승인 대기 / 일부 POI 미자격**

| Spot | 상품 | POI 수 |
|---|---|---|
| 12984 | 평화곤돌라+감악산 DMZ | 5 (한글 일부) |
| 12986 | 대구 템플스테이 1박2일 | 6 (한글 섞임) |
| 13566 | 서울 시즌 핫스팟 | 4 |
| 13760 | 춘천 레고랜드 프라이빗 | 4 |

**D. 계절상품** (시즌 재개 시 재활성화 — Action 6 자동 토글 대상)

| Spot | 상품 |
|---|---|
| 13064 | 청양 알프스마을 얼음분수축제 |
| 13730 | 딸기체험+비발디+어비얼음계곡 |

**E. TTD 부적격 카테고리 (헤어/마사지/공연)** — `is_ttd=0` 회수 검토

| Spot | 상품 | 분류 |
|---|---|---|
| 13054 | mood'e Hair 용산 | 헤어 (영구 제외) |
| 12763 | Blue Arirang 명동 | 마사지 (영구 제외) |
| 11263 | NANTA 명동 | 공연 — Concert 카테고리 자격 재검토 |
| 12895 | NANTA 제주 | 공연 — 동일 |

**F. 단일 POI 자격 미달 — 개별 진단 필요**

| Spot | 상품 | 비고 |
|---|---|---|
| 13113 | Sejong Bear Tree Park | **Search 유입 33 최상위인데 전부 NA — 최우선 진단** |
| 11239 | N서울타워 전망대 | 입장권인데 거부 |
| 13455 | 부산 블루라인파크 스카이캡슐 | POI명 truncated |
| 12925 | 서울 나이트투어 북악~낙산 | 단일 POI(Bugak Palgakjeong) |
| 13135 | 부산 퍼블릭 요트 투어 | 단일 POI(The Yacht) |
| 12916 | 파주 벽초지+프로방스+헤이리 | 단일 POI |
| 12873 | 여의도 E-Land 크루즈 | 동일상품 12872는 통과 — 비교 진단 |
| 14491 | Deep Station 프리다이빙 | 단일 POI |
| 11240 | 남이섬+쁘띠+이탈리아+아침고요 | 38배치 누락 → 다중 POI 추가 |
| 13414 | 강원여행(제이드/남이/쁘띠) | 38배치 누락 + th 언어 누락 |

---

## 6. TTD 전용 Place ID — 진행 상황

### 6.1 완료 (development 머지됨)

| 커밋 | 내용 |
|---|---|
| `4c9974b6694` | DB migration: `spot_google_ttd.related_google_place_id VARCHAR(255) NULL` |
| `e943bd39503` | 어드민 편집 폼 추가 |
| `09ec5465fec` | TTD Drawer Google Map 링크 변경 |
| `592ecc3580a` | Fallback: NULL이면 `spot.google_place_id` 사용 |
| `d65504c457f` 외 4건 | 편집 UI 안내·검증·일관성 보완 |

### 6.2 미완료
- **데이터 백필 0건**: 402개 행 전부 `related_google_place_id IS NULL`
- **람다 레포(`google-ttd`) fallback PR 머지/배포 여부 미확인** (별도 레포)

---

## 7. 후보 풀 추출 결과 (2026-05-29 production)

§3.8 운영 진입 조건 + POI 매칭 기준 SQL 추출:

| 구분 | 수 | 정의 | 필요 작업 |
|---|---:|---|---|
| Tier 1 | **32** | `spot_google_ttd` 메타 보유, `is_ttd=0` | 어드민 토글만 (relation_type 검수 후) |
| Tier 2 (보수) | **175** | 공식 지원 12개 카테고리, 메타 없음 | 메타데이터 신규 입력 |
| Tier 2 (애매) | **314** | 5/12 추가 4개 카테고리 | 단계적 진행 (헤어 제외) |
| **합계** | **521** | 즉시~단기 활성화 후보 | |

추출 조건: `is_ttd=0` AND `is_in_business=1` AND `is_reservable=1` + `google_place_id` 보유 + 지원 카테고리 + 표준 14언어 중 ≥12개 공개 + 30일 내 예약 가능 슬롯 존재

---

## 8. 모수 확보 액션 플랜 (임팩트순)

> 전제: (A) 내부 정상화(DB 상품 켜기) + (B) 신규 입점. (A)부터. POI(Google Maps 카테고리) ≠ Tour Operator GBP(파트너 직접 노출) 혼동 금지.

| Action | 내용 | 임팩트 | 소요/선행 |
|---|---|---:|---|
| **0. 다중 POI 에러 대응** (5/30 완료, 일부 재승인 대기) | §5 — 38개 다중 POI 재구성 → **25개 유효화** | 패키지성 투어 25개 노출 자격 회복 | 람다 Place ID fallback 배포 확인 |
| **0-A. 한글 POI 백필** | §5.8-A 6개 `related_google_place_id` 정정 | +6 | 올바른 Google Place ID 확보 |
| **0-B. 빈 POI 연결** | §5.8-B 2개 POI 신규 연결 (14254 다중 구성) | +2 | — |
| **0-C. 재승인 모니터링 + POI 정정** | §5.8-C 4개 'Find Location Matches'로 POI 자격 재확인 | +0~4 | Google 재승인 주기 |
| **0-D. 38배치 누락분 다중 POI** | §5.8-F 중 11240·13414 다중 POI 추가(+13414 th 보강) | +2 | — |
| **0-E. 단일 POI 개별 진단** | §5.8-F 8개 (13113 최우선) relation_type/POI 재지정 | +3~6 | 건별 조사 |
| **0-F. 부적격 카테고리 회수** | §5.8-E 헤어·마사지 2개 `is_ttd=0`, 공연 2개 자격 재검토 | 모수 정합성 | 카테고리 정책 |
| **1. Tier 1 토글** | 32개 relation_type 검수 후 `is_ttd=1` | +25~30 | 운영 1~2h, 어드민 폼(완료) |
| **2. Tier 2 보수 입력** | 175개 메타데이터 일괄 입력 | +150 | 운영 1~2일, 신규 row 생성 UI 확인 |
| **3. Place ID 백필** | 매칭 실패 23개 (틀린 ID 교체 / 카테고리 정정 / 신규 등록) | +15~20 | 람다 `google-ttd` 배포 선행 |
| **4. Tier 2 애매 단계 적용** | 투어26→체험148→K-뷰티160(시범30)→전문헤어180(보류) | +200~250 | 1~2주, Google 승인 모니터링 |
| **5. 자동 추천 + 부정합 가드** | 카테고리↔relation_type 매핑 정책화, 어드민 저장 시 경고 | 모수 유지 | 매핑 정책 합의 |
| **6. `is_ttd` 자동 토글 룰** | 진입 조건 위반 시 자동 회수/회복, 시즌 상품 자동 처리 | 운영 정착 | 매핑 정책 합의 |

### 누적 임팩트

| 단계 | 누적 활성 모수 | 비고 |
|---|---:|---|
| 현재 (6/1) | 89 | 다중 POI 25개 유효화 반영 |
| + Action 0-A~F | ~105 | 무효 모수 잔여 분 처리 (한글 POI·빈 POI·재승인·개별 진단) |
| + Action 1 | ~130 | 운영 1~2h |
| + Action 2 | ~280 | 운영 1~2일 |
| + Action 3 | ~300 | 람다 배포 선행 |
| + Action 4 | **~520** | 1~2주 단계적 |

---

## 9. relation_type / 다중 POI 분류 가이드 (어드민 정정용)

**결정 트리** (POI별로 적용)
```
구매하면 POI 게이트 통과? YES → ADMISSION_TICKET
                       NO ↓
주체적 활동(투어/체험/클래스)? YES → RELATED_NO_ADMISSION
                            NO  → SUPPLEMENTARY_ADDON
```

**상품 유형별 매핑**

| 유형 | 값 |
|---|---|
| 입장권/패스/티켓 단독 | `ADMISSION_TICKET` |
| 투어/택시투어/프라이빗투어/워킹투어/명상투어 | `RELATED_NO_ADMISSION` |
| 원데이클래스/체험/한복&스냅 | `RELATED_NO_ADMISSION` |
| 셔틀버스/픽업/오디오가이드 단독 | `SUPPLEMENTARY_ADDON` |
| 리조트 패키지/렌트카/헤어샵 | TTD 부적격 — 켜지 말 것 |

**다중 POI 적용 원칙**: 패키지 상품은 구성 관광지마다 POI를 분리하고, 각 POI에 위 결정 트리를 개별 적용. (예: 입장권 포함 관광지 = ADMISSION_TICKET, 단순 경유/트레킹 = RELATED_NO_ADMISSION)

---

## 10. 후속 액션

**즉시 — 무효 모수 잔여 처리 (Action 0-A~F)**
- [ ] **13113 Sejong Bear Tree Park 최우선 진단** — Search 유입 33 최상위인데 전부 Not Approved (원인 불명, 손실 가장 큼)
- [ ] 한글 POI 6개 `related_google_place_id` 백필 (§5.8-A: 12850·11519·11561·11934·14243·12879)
- [ ] 빈 POI 2개 연결 (§5.8-B: 13167·14254 — 14254는 셔틀 SUPPLEMENTARY_ADDON 다중 구성)
- [ ] 38배치 누락 2개 다중 POI 추가 (§5.8-F: 11240·13414, 13414는 th 언어 보강)
- [ ] 다중 POI 재승인 대기 4개 'Find Location Matches' 재확인 (§5.8-C: 12984·12986·13566·13760)
- [ ] 부적격 카테고리 회수 검토 (§5.8-E: 헤어 13054·마사지 12763 → `is_ttd=0`, 공연 11263·12895 자격 재검토)
- [ ] 단일 POI 자격 미달 개별 진단 (§5.8-F 잔여: 11239·13455·12925·13135·12916·12873·14491)

**단기 — 모수 확장 (Action 1~4)**
- [ ] Action 1 Tier 1 32개 토글 (relation_type 검수 후)
- [ ] Action 2 신규 row 생성 UI 진입점 존재 여부 확인 → 175개 입력
- [ ] 람다 `google-ttd` Place ID fallback PR 배포 상태 확인 (Action 0-A·3 선행)
- [ ] Action 4 Tier 2 애매 314개 단계 적용 (투어→체험→K-뷰티 시범, 헤어 보류)

**운영 정착**
- [ ] 다중 POI 입력 운영팀 가이드 정리 (§9 결정 트리 활용)
- [ ] Action 5·6 relation_type 부정합 가드 + `is_ttd` 자동 토글(계절상품 13064·13730 등)
- [ ] `general_click_event` 기반 모수별 노출/유입 효율 베이스라인

---

## 11. 참고 슬랙 스레드 (`#product-core`, `C05999AP2UU`)

- 2026-04-16: [Google TTD 이슈 요약](https://creatrip.slack.com/archives/C05999AP2UU/p1776333986340309) — 에러 카탈로그 5종
- 2026-04-28: [Google Actions TTD 메인](https://creatrip.slack.com/archives/C05999AP2UU/p1777353716535709) — 모수/카테고리/relation_type 논의
- 2026-05-27: [Google TTD 역할 분담](https://creatrip.slack.com/archives/C05999AP2UU/p1779852887682179)
- 2026-05-30: [google ttd 에러 대응 (다중 POI)](https://creatrip.slack.com/archives/C05999AP2UU/p1780078210705699)

> 상세 모수 분석 원본: `work/kiev/ttd-pool-expansion-context.md`
