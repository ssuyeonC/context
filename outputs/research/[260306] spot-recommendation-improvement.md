# 스팟 상세 페이지 추천 영역 개선 — 전체 논의 정리

## 1. 배경 및 목표

### 핵심 지표
- D1 Retention (New User → D1 Return User)

### 타겟 페이지
- 스팟 상세 페이지 (New User 트래픽이 압도적으로 집중)

### 제약 조건
- 앱 유저가 웹 대비 6%로, 푸시 알림의 레버리지가 작음 (앱 확대는 병렬 진행)
- GCP 기반 유저 행동 데이터 인프라가 아직 충분하지 않아 고수준 개인화 도입이 어려움

---

## 2. 유저 성장 프레임워크

```
New User → D1 Return User → ... → Heavy User
```

- **New User → D1 Return User**: 축적된 행동 데이터가 없어 개인화가 어려움 → 개인화에 의존하지 않는 **추천 품질 개선**이 우선
- **데이터가 쌓이는 시점부터**: 플랜 기반 보완재, 세션 이력 기반 등 개인화 점진 도입
- 현 단계 목표는 New User → D1 Return User 전환율 향상

---

## 3. GCP 데이터 노출 영역 (현행)

- **BigQuery → 어필리에이트 대시보드**: GA4 수집 데이터를 BigQuery로 적재, 매일 3AM 동기화
- **Google Cloud Retail API → 검색 모달 내 개인화 추천**: 방문자 ID 기반 predict 요청
- 기타: Google Translate(다국어 번역), Cloud TTS(광동어 오디오), Google Sheets(어필리에이트), Google Drive(영상), Google Places/Geocoding(장소/좌표)

---

## 4. 현재 추천 로직 분석

### 4-1. Frequently Booked Together (교차 구매)

- 상품 A를 구매 완료한 유저들의 다른 구매 내역을 **최신 예약순**으로 9개 노출
- fallback으로 Elasticsearch 기반 "함께 본 상품" 빈도순 보충 (MIN_PURCHASED_TOGETHER_SPOT_COUNT = 3 미만 시)
- A/B 분기: flag='A'이면 DB 기반, 그 외 ML 기반(Redis 캐시)

**문제점:**
- 시간 제한 없음 → 다른 여행의 구매가 섞임 (한복 + 스키 리조트)
- `spot_has_category` 다중 매핑으로 9개 row인데 **실질 2개 상품으로 붕괴**
- 카테고리 구분 없이 인기 상품 편중
- 보완재/대체재 무구분

### 4-2. Products Viewed by Other Customers (교차 조회)

- Redis 캐시(`spot-visitors:watched-together:spots`)에서 사전 집계 데이터 조회
- 캐시 미스 시 Elasticsearch에서 **같은 유저가 같은 날 함께 조회한 스팟** 집계
- 빈도순 정렬, 상위 N개 노출 (기본 5개)
- 부족 시 랜덤 공개 스팟으로 보충

**문제점:**
- Frequently Booked Together와 유사한 카테고리 편중, 보완재/대체재 무구분 문제 존재 가능

---

## 5. 도입 근거 분석

### 데이터 기반 분석

- **추천 탭 클릭률**: 전 세그먼트에서 가장 낮음 (~3.9%)
  - 모바일 웹: 3.91%, 데스크탑 웹: 3.36%, 모바일 앱: 3.78%
  - 데스크탑에서 탭이 한눈에 보임에도 가장 낮음 → **가시성이 아니라 워딩 매력도 문제**
- **스팟 → 스팟 전환율**: 약 13.8% (SpotProductCardClick / 전체 스팟 PV)
  - 추천 섹션 내 스팟 카드가 유일한 채널이므로, 탭은 안 눌러도 스크롤하다 카드를 클릭하는 유저가 상당수
- **탭 전체 클릭률**: 약 3.25% (Click/Impression)

### 해석

- 상품 상세를 찾는 유저는 해당 상품에 대한 관심(구매 의도, 학습 의도)이 높아 '추천'이라는 키워드가 고려 대상이 아님
- 그러나 추천 카드 클릭률(13.8%)은 낮지 않음 → 유저의 교차 탐색 수요 자체는 존재
- '상품 카드 클릭'은 D1 Retention과 구매 확률 모두에 긍정적 효과가 인사이트로 존재

### 결론

- 유저의 상품 탐색을 강화할 수 있도록 탭 워딩/섹션 타이틀 최적화 + 추천 로직 강화가 유의미한 액션

---

## 6. 액션 플랜

### 1차: 섹션 탭 'Recommend' 버튼 워딩 변경 A/B 테스트

**변경 내용:**
- 'Recommend' → **'Booked Together'** (또는 유사 워딩)
- 다른 탭들(Options, Precautions, Store Info 등)이 섹션 내용을 직접 설명하는 패턴과 일관성 유지
- 추천 영역 내부 타이틀(Frequently booked together / Products viewed by other customers)은 1차에서 변경하지 않음

**측정 지표:**
- 주요 지표: 'Recommend' 탭 클릭률 (현재 3.9%)
- 가드레일 지표:
  - 다른 탭(Options, Reviews 등) 클릭률: 추천 탭 클릭 증가가 다른 탭을 잠식하지 않는지
  - 추천 섹션 내 스팟 카드 클릭률 (현재 13.8%): 유입 증가에도 카드 클릭 품질 유지되는지
  - 구매 전환율: 워딩 변경이 구매 흐름에 부정적 영향을 주지 않는지

**1차 결과에 따른 판단:**
- 탭 클릭률 상승 → 워딩이 문제였음 확인, 2차 진행
- 변화 없음 → 워딩이 아니라 구조 자체의 문제, 위치 이동 등 다른 접근 검토
- 탭 클릭 상승 + 카드 클릭률 하락 → 기대와 콘텐츠 불일치, 2차 알고리즘 개선의 근거

### 2차: 추천 영역 알고리즘 개선 + 섹션 타이틀 변경 A/B 테스트

**변경 내용:**
- 두 추천 영역을 보완재/대체재로 분리
- 섹션 타이틀 변경:
  - Frequently booked together → **"Complete Your Trip"** (보완재)
  - Products viewed by other customers → **"More Options Like This"** (대체재)
- 알고리즘을 보완재/대체재 각각의 로직으로 변경 (아래 7, 8장 참조)

**AB 테스트 설계:**
- A군: 1차에서 변경된 탭 워딩 + 현재 알고리즘
- B군: 1차에서 변경된 탭 워딩 + 보완재/대체재 알고리즘 + 새 섹션 타이틀

**측정 지표:**
- 주요 지표: 추천 섹션 내 스팟 카드 클릭률, D1 Retention
- 가드레일 지표:
  - 구매 전환율: 보완재 추천이 현재 상품의 구매를 방해하지 않는지
  - 세션당 스팟 상세 조회 수: 교차 탐색이 실제로 늘어나는지
  - 추천 탭 클릭률: 1차에서 확보한 수준이 유지되는지

---

## 7. 보완재 추천 로직 (Complete Your Trip)

### 기존 vs 변경 비교

**추천 기준:**

| | 기존 | 변경 |
|---|---|---|
| 정렬 기준 | 최신 예약순 | 구매 수 기준 |
| 카테고리 구분 | 없음 (전체 혼합) | 카테고리별 분리 후 상위 3개 선정 |
| 추천 성격 | 보완재/대체재 무구분 | 보완재만 (자기 카테고리 제외) |

**필터링:**

| | 기존 | 변경 |
|---|---|---|
| 카테고리 레벨 | 미적용 | MIDDLE_RESERVATION만 허용 |
| 자기 카테고리 | 포함 | 제외 |
| 여행 인프라 | 포함 | 블랙리스트 19개 카테고리 제외 |
| 같은 MAIN 내 중복 | 미처리 | 구매수 1위 MIDDLE만 허용 |

**중복 처리:**

| | 기존 | 변경 |
|---|---|---|
| 카테고리 간 상품 중복 | 미처리 | 카테고리 우선순위 기반 중복 제거 + 차순위 보충 |
| `spot_has_category` 다중 매핑 | 9개 row 중 실질 2개 상품으로 붕괴 | 카테고리 단위 선정이라 영향 없음 |

**출력:**

| | 기존 | 변경 |
|---|---|---|
| 노출 수 | 최대 9개 | 최대 6개 (3카테고리 × 2상품) |
| 구조 | 상품 나열 | 카테고리별 그룹핑 |
| 다양성 | 인기 상품/카테고리 편중 | 카테고리 다양성 구조적 보장 |

### 로직 상세

```
① 구매 풀 생성
   상품 A를 구매 완료(status: COMPLETE/PARTIAL_REFUND/USED)한 모든 유저의
   다른 구매 내역을 조회

② 카테고리 집계
   구매 풀의 상품들을 카테고리별 구매 수로 내림차순 집계

③ 카테고리 필터링 (4단계)

   [a] MIDDLE_RESERVATION만 허용
       → MAIN과 혼합 시 카테고리 간 의미적 겹침 발생 방지

   [b] 상품 A의 카테고리 제외
       → 대체재가 아닌 보완재 추천을 위해

   [c] 블랙리스트 19개 카테고리 제외
       → 여행 인프라(교통/통신/배달 등) 제거, "발견 가치"가 있는 상품만 남김
       → 제외 목록:
          교통: 공항 교통(746), 기차&버스(747), 교통예약(366),
                페리(748), 자동차 대여(876), 콘서트 교통(3052)
          통신: 와이파이(904), 유심(903), 이심(905)
          배달/배송: 배달서비스(365), 배송(750), 직접수령(749)
          여행편의: 공항 서비스(751), 여행 필수(752),
                    여행편리(367), 여행필수 패키지(915)
          보험/카드: 보험(890), 선불카드(3061)
          상품권: 상품권(875)

   [d] 같은 MAIN(parent_code) 내 MIDDLE은 구매수 1위만 허용
       → 예: 염색&펌 + 헤드스파 동시 노출 방지

④ 상위 3개 카테고리 선정
   필터링 후 구매 수 기준 상위 3개

⑤ 카테고리별 상품 추출
   각 카테고리 내 구매 수 TOP 1, 2

⑥ 스팟 중복 제거 + 보충
   카테고리 우선순위(구매수 높은 카테고리 우선)에 따라 스팟 확정
   이미 확정된 spot_code가 다른 카테고리에 나오면
   다음 순위(rn=3, 4...)로 대체

   대상 상품 조건: is_reservable = 1 AND is_in_business = 1, 해당 언어 번역 존재
```

### 검증 결과 (5개 스팟)

| 테스트 스팟 | 추천 카테고리 | 겹침/중복 | 보완재 적합성 |
|---|---|---|---|
| AREX (교통) | 포토&의상대여 / 어트랙션&입장권 / 식당/맛집 | 없음 | 높음 |
| 예스한복 (포토) | 어트랙션&입장권 / 식당/맛집 / 증명사진 | 없음 | 높음 (한복→촬영) |
| 순시키헤어 (뷰티) | 피부시술 / 포토&의상대여 / 증명사진 | 없음 (dedup 동작) | 높음 (뷰티 코스) |
| 롯데월드 (어트랙션) | 포토&의상대여 / 염색&펌 / 증명사진 | 없음 | 높음 (교복대여) |
| 진미식당 (맛집) | 포토&의상대여 / 염색&펌 / 증명사진 | 없음 | 높음 |

### 테스트 반복 개선 이력

| 단계 | 변경 | 결과 |
|---|---|---|
| 1차 | 필터 없이 제안 로직 실행 | 지역/지하철 카테고리(Line 2, 강남 등)가 상위 차지, eSIM으로 수렴 |
| 2차 | 지역/지하철 type 제외 | 상품군 기반으로 개선되었으나 MAIN+MIDDLE 혼합으로 카테고리 겹침 |
| 3차 | MIDDLE_RESERVATION으로 한정 | 카테고리 겹침 해소, 상품 중복 감소 |
| 4차 | 선정 기준을 구매수 TOP 1,2로 통일 | 빈 슬롯 문제 해결, 로직 단순화 |
| 5차 | 블랙리스트 19개 카테고리 제외 | 여행 인프라 제거 → 체험/관광/식음 중심 보완재 추천 |
| 6차 | 같은 MAIN 내 MIDDLE 1개만 허용 | 헤어 계열 중복(염색&펌+헤드스파) 해소 |
| 7차 | 카테고리 우선순위 기반 spot_code 중복 제거 + 보충 | 최종 6개 모두 다른 상품 보장 |

---

## 8. 대체재 추천 로직 (More Options Like This)

### 로직 상세

```
① 교차 조회 풀 생성
   상품 A를 조회한 유저들이 같은 날 함께 조회한 스팟 집계
   → "상품 A에 관심 있는 유저의 맥락"을 반영하기 위해 필수

② MIDDLE 카테고리 일치 필터 (필수)
   상품 A와 동일한 MIDDLE_RESERVATION 카테고리에 속하는 스팟만

③ 지역 필터 (단계적 확장 + fallback)
   [a] DETAIL_LOCATION 일치 → 후보 충분하면 확정
   [b] 부족 시 CITY로 확장 → 후보 충분하면 확정
   [c] 부족 시 지역 필터 해제 (기존 로직 fallback)

④ 조회 빈도순으로 상위 N개 노출
```

### 보완재 vs 대체재 비교

| | 보완재 (Complete Your Trip) | 대체재 (More Options Like This) |
|---|---|---|
| 데이터 소스 | 교차 구매 | 교차 조회 |
| 카테고리 | 다른 카테고리 (MIDDLE) | 같은 카테고리 (MIDDLE) |
| 지역 | 미적용 | DETAIL_LOCATION → CITY → 전체 (fallback) |
| 정렬 | 구매 수 | 조회 빈도 |
| 필터링 | 블랙리스트 + MAIN dedup + spot dedup | 없음 (같은 카테고리 내이므로) |
| 출력 | 최대 6개 (3카테고리 × 2) | 상위 N개 |

### 검증 상태

- 대체재 로직은 DB 기반 프록시 테스트 쿼리를 작성 완료, **실행 대기 중**

---

## 9. UI 방향

- **보완재 영역**: 기존 가로 캐러셀 → **방사형 마인드맵** 구조 (상품 A 중심, 카테고리 3개 방사, 각 2개 상품)
- **배치**: 현재보다 상단으로 이동 검토 (New User 스크롤 깊이가 깊지 않으므로)
  - 단, 유저가 상품 평가(Options, Reviews 등)에 집중하는 중 다른 상품 안내가 노이즈가 될 가능성 고려
  - 상품 관련 콘텐츠 사이에 스팟 카드를 삽입하는 것보다 독립된 영역으로 배치하는 것이 적합

---

## 10. 잠재적 개선 포인트 (향후)

- **Time decay**: 구매 시점이 오래된 데이터의 가중치를 낮추어 계절성/트렌드 반영
  - 첫 버전 배포 후 성과 데이터 기반으로 도입 여부 판단
  - 여행 상품은 구매 빈도가 낮아 유효 데이터가 급감할 위험
- **Fallback**: 카테고리 3개 또는 상품 2개를 못 채울 때의 정책 (미정)
- **개인화 확장**: 유저 데이터가 쌓이는 시점(D1 Return User 이후)부터 플랜 기반 보완재, 세션 이력 기반 추천 도입
- **가격대 필터**: 대체재 추천에서 비슷한 가격대 상품을 우선 노출하여 비교 가능성 제고

---

## 11. 검증 쿼리 (참고)

### 보완재 최종 쿼리

```sql
SET @spotCode = ???;
SET @language = 'ko';

WITH buyer_purchases AS (
  SELECT r2.spot_code, r2.code AS reserve_code
  FROM reserve r
  INNER JOIN reserve r2 ON r2.member_code = r.member_code
    AND r2.status IN (3, 5, 6)
    AND r2.spot_code != @spotCode
  WHERE r.spot_code = @spotCode
    AND r.status IN (3, 5, 6)
),
middle_category_all AS (
  SELECT shc.category_code,
         ct.name AS category_name,
         c.parent_code,
         COUNT(*) AS purchase_count
  FROM buyer_purchases bp
  INNER JOIN spot s ON s.code = bp.spot_code AND s.is_reservable = 1 AND s.is_in_business = 1
  INNER JOIN spot_translation st ON st.spot_code = s.code AND st.language = @language
  INNER JOIN spot_has_category shc ON shc.spot_code = bp.spot_code
  INNER JOIN category c ON c.code = shc.category_code AND c.type = 'MIDDLE_RESERVATION'
  INNER JOIN category_translation ct ON ct.category_code = shc.category_code AND ct.language = @language
  WHERE shc.category_code NOT IN (
    SELECT category_code FROM spot_has_category WHERE spot_code = @spotCode
  )
  AND shc.category_code NOT IN (
    746, 747, 366, 748, 876, 3052,
    904, 903, 905,
    365, 750, 749,
    751, 752, 367, 915,
    890, 3061,
    875
  )
  GROUP BY shc.category_code
),
middle_dedup AS (
  SELECT *,
         ROW_NUMBER() OVER (PARTITION BY parent_code ORDER BY purchase_count DESC) AS parent_rn
  FROM middle_category_all
),
category_rank_all AS (
  SELECT category_code, category_name, purchase_count,
         ROW_NUMBER() OVER (ORDER BY purchase_count DESC) AS cat_rn
  FROM middle_dedup
  WHERE parent_rn = 1
),
category_rank AS (
  SELECT category_code, category_name, purchase_count, cat_rn
  FROM category_rank_all
  WHERE cat_rn <= 3
),
spot_by_purchase AS (
  SELECT shc.category_code, bp.spot_code,
         COUNT(*) AS purchase_count,
         ROW_NUMBER() OVER (PARTITION BY shc.category_code ORDER BY COUNT(*) DESC) AS rn
  FROM buyer_purchases bp
  INNER JOIN spot s ON s.code = bp.spot_code AND s.is_reservable = 1 AND s.is_in_business = 1
  INNER JOIN spot_translation st ON st.spot_code = s.code AND st.language = @language
  INNER JOIN spot_has_category shc ON shc.spot_code = bp.spot_code
  WHERE shc.category_code IN (SELECT category_code FROM category_rank)
  GROUP BY shc.category_code, bp.spot_code
),
cat1_spots AS (
  SELECT sp.category_code, sp.spot_code, sp.purchase_count, sp.rn,
         ROW_NUMBER() OVER (ORDER BY sp.rn) AS final_rn
  FROM spot_by_purchase sp
  JOIN category_rank cr ON cr.category_code = sp.category_code AND cr.cat_rn = 1
  WHERE sp.rn <= 2
),
cat2_spots AS (
  SELECT sp.category_code, sp.spot_code, sp.purchase_count, sp.rn,
         ROW_NUMBER() OVER (ORDER BY sp.rn) AS final_rn
  FROM spot_by_purchase sp
  JOIN category_rank cr ON cr.category_code = sp.category_code AND cr.cat_rn = 2
  WHERE sp.spot_code NOT IN (SELECT spot_code FROM cat1_spots)
  ORDER BY sp.rn
  LIMIT 2
),
cat3_spots AS (
  SELECT sp.category_code, sp.spot_code, sp.purchase_count, sp.rn,
         ROW_NUMBER() OVER (ORDER BY sp.rn) AS final_rn
  FROM spot_by_purchase sp
  JOIN category_rank cr ON cr.category_code = sp.category_code AND cr.cat_rn = 3
  WHERE sp.spot_code NOT IN (SELECT spot_code FROM cat1_spots)
    AND sp.spot_code NOT IN (SELECT spot_code FROM cat2_spots)
  ORDER BY sp.rn
  LIMIT 2
)
SELECT cr.category_name, cr.purchase_count AS category_purchases,
       cs.final_rn AS rank_in_category, cs.spot_code, st.title AS spot_title, cs.purchase_count AS spot_purchases
FROM cat1_spots cs
JOIN category_rank cr ON cr.category_code = cs.category_code
JOIN spot_translation st ON st.spot_code = cs.spot_code AND st.language = @language
UNION ALL
SELECT cr.category_name, cr.purchase_count, cs.final_rn, cs.spot_code, st.title, cs.purchase_count
FROM cat2_spots cs
JOIN category_rank cr ON cr.category_code = cs.category_code
JOIN spot_translation st ON st.spot_code = cs.spot_code AND st.language = @language
UNION ALL
SELECT cr.category_name, cr.purchase_count, cs.final_rn, cs.spot_code, st.title, cs.purchase_count
FROM cat3_spots cs
JOIN category_rank cr ON cr.category_code = cs.category_code
JOIN spot_translation st ON st.spot_code = cs.spot_code AND st.language = @language
ORDER BY category_purchases DESC, rank_in_category;
```

### 대체재 테스트 쿼리

```sql
SET @spotCode = ???;
SET @language = 'ko';

SET @middleCategory = (
  SELECT shc.category_code
  FROM spot_has_category shc
  JOIN category c ON c.code = shc.category_code AND c.type = 'MIDDLE_RESERVATION'
  WHERE shc.spot_code = @spotCode
  LIMIT 1
);
SET @detailLocation = (
  SELECT shc.category_code
  FROM spot_has_category shc
  JOIN category c ON c.code = shc.category_code AND c.type = 'DETAIL_LOCATION'
  WHERE shc.spot_code = @spotCode
  LIMIT 1
);
SET @city = (
  SELECT shc.category_code
  FROM spot_has_category shc
  JOIN category c ON c.code = shc.category_code AND c.type = 'CITY'
  WHERE shc.spot_code = @spotCode
  LIMIT 1
);

WITH buyer_purchases AS (
  SELECT r2.spot_code, COUNT(*) AS purchase_count
  FROM reserve r
  INNER JOIN reserve r2 ON r2.member_code = r.member_code
    AND r2.status IN (3, 5, 6)
    AND r2.spot_code != @spotCode
  WHERE r.spot_code = @spotCode
    AND r.status IN (3, 5, 6)
  GROUP BY r2.spot_code
),
detail_location_results AS (
  SELECT bp.spot_code, st.title AS spot_title, bp.purchase_count,
         'DETAIL_LOCATION' AS match_level
  FROM buyer_purchases bp
  INNER JOIN spot s ON s.code = bp.spot_code AND s.is_reservable = 1 AND s.is_in_business = 1
  INNER JOIN spot_translation st ON st.spot_code = s.code AND st.language = @language
  INNER JOIN spot_has_category shc_mid ON shc_mid.spot_code = bp.spot_code
    AND shc_mid.category_code = @middleCategory
  INNER JOIN spot_has_category shc_loc ON shc_loc.spot_code = bp.spot_code
    AND shc_loc.category_code = @detailLocation
),
city_results AS (
  SELECT bp.spot_code, st.title AS spot_title, bp.purchase_count,
         'CITY' AS match_level
  FROM buyer_purchases bp
  INNER JOIN spot s ON s.code = bp.spot_code AND s.is_reservable = 1 AND s.is_in_business = 1
  INNER JOIN spot_translation st ON st.spot_code = s.code AND st.language = @language
  INNER JOIN spot_has_category shc_mid ON shc_mid.spot_code = bp.spot_code
    AND shc_mid.category_code = @middleCategory
  INNER JOIN spot_has_category shc_city ON shc_city.spot_code = bp.spot_code
    AND shc_city.category_code = @city
  WHERE bp.spot_code NOT IN (SELECT spot_code FROM detail_location_results)
),
no_location_results AS (
  SELECT bp.spot_code, st.title AS spot_title, bp.purchase_count,
         'NO_FILTER' AS match_level
  FROM buyer_purchases bp
  INNER JOIN spot s ON s.code = bp.spot_code AND s.is_reservable = 1 AND s.is_in_business = 1
  INNER JOIN spot_translation st ON st.spot_code = s.code AND st.language = @language
  INNER JOIN spot_has_category shc_mid ON shc_mid.spot_code = bp.spot_code
    AND shc_mid.category_code = @middleCategory
  WHERE bp.spot_code NOT IN (SELECT spot_code FROM detail_location_results)
    AND bp.spot_code NOT IN (SELECT spot_code FROM city_results)
)
SELECT match_level, spot_code, spot_title, purchase_count
FROM (
  SELECT * FROM detail_location_results
  UNION ALL
  SELECT * FROM city_results
  UNION ALL
  SELECT * FROM no_location_results
) combined
ORDER BY
  CASE match_level
    WHEN 'DETAIL_LOCATION' THEN 1
    WHEN 'CITY' THEN 2
    WHEN 'NO_FILTER' THEN 3
  END,
  purchase_count DESC
LIMIT 15;
```
