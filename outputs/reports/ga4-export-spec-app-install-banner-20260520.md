# GA4 수동 추출 사양 — AppInstallBanner 세그먼트별 CTR

> **목적**: 여행 블로그 방식 B 세그먼트(killer/hidden/passing/low)별 AppInstallBanner 노출·클릭·CTR 산출
> **기간**: 2026-03-22 ~ 2026-05-20 (최근 60일)
> **방법**: GA4 콘솔 "탐색(Explore)" → 자유 형식 보고서 → CSV 내보내기
> **사유**: MCP `GA_runAnalyticsReport`는 `invalid_grant` (서버 OAuth 만료), 원시 `analytics_*` 데이터셋은 권한 없음, `dashboard_ga4` 집계 테이블에 본 이벤트 미수록

---

## 1. 사전 확인 — 이벤트 사양 (코드 기준)

`frontend/apps/web/domain/shared/AppInstallBanner/AppInstallBanner.tsx`

| 항목 | 값 |
|---|---|
| Impression 이벤트명 | `AppInstallBannerImpression` |
| Click 이벤트명 | `AppInstallBannerClick` |
| 이벤트 파라미터(payload) | **없음** (page_location으로만 블로그 식별 가능) |
| 노출 디바이스 | `Display mobileAndTablet` (모바일·태블릿 웹 한정) |
| 노출 path 5종 | HOME, SPOT.HOME, SPOT.LIST, SPOT.DETAIL, **BLOG.DETAIL**, USER_BLOG.DETAIL |
| dismiss 시 | 노출 자체 안 됨 (이미 닫은 사용자 제외) |
| 네이티브 앱 | 노출/이벤트 없음 (이벤트는 mobile web만) |

→ **블로그 단위 분석은 `page_location`이 `/blog/{code}` 패턴인 경우만 필터**.
→ URL 패턴: `https://creatrip.com[/{locale}]/blog/{code}` — locale은 `de|en|es|fr|id|it|ja|mn|ru|th|vi|zh-CN|zh-HK|zh-TW` 또는 생략(=zh-TW 기본).

---

## 2. GA4 탐색 보고서 설정

### 위치
GA4 콘솔 → 좌측 메뉴 "**탐색(Explore)**" → "**+ 빈 탐색 분석**" (자유 형식)

### 설정값

| 항목 | 값 |
|---|---|
| **이름** | `AppInstallBanner CTR by blog (60d)` |
| **기간** | `2026-03-22 ~ 2026-05-20` |
| **세분화 (Segments)** | 만들지 않음 (전체) |
| **측정기준 (Dimensions)** | `이벤트 이름 (eventName)`, `페이지 위치 (pageLocation)` |
| **측정항목 (Metrics)** | `이벤트 수 (eventCount)` |
| **시각화** | 자유 형식 표 |
| **행 (Rows)** | 페이지 위치 (pageLocation) |
| **열 (Columns)** | 이벤트 이름 (eventName) |
| **값 (Values)** | 이벤트 수 (eventCount) |
| **행 표시 수** | 최대값 (보통 500. 부족하면 분할 추출) |

### 필터 (Filter — 측정기준)

```
조건 1 (필수): 이벤트 이름 (eventName) — "정확히 일치 (one of)"
   값: AppInstallBannerImpression
        AppInstallBannerClick

조건 2 (필수): 페이지 위치 (pageLocation) — "포함 (contains)"
   값: /blog/
```

(`/userblog/` 패턴은 사용자 블로그라 별도 풀이므로 본 분석에선 제외)

### 검증 팁
- 우상단 디바이스 카테고리(device category) 필터를 `mobile` + `tablet`으로 좁히면 코드 동작과 일치하는 모수로 수렴
- desktop 트래픽은 코드상 노출 자체가 없으므로 0이어야 함 (있다면 deep_link/redirect 유입 등 노이즈)

---

## 3. CSV 내보내기

표 우상단 다운로드 → **CSV** 선택. 파일을 다음 경로로 저장:

```
.context/outputs/raw/ga4-app-install-banner-by-page-60d-20260520.csv
```

기대 컬럼(GA4 한국어 콘솔 기준):

| 페이지 위치 | AppInstallBannerImpression | AppInstallBannerClick |
|---|---:|---:|
| https://creatrip.com/ja/blog/1491 | 12,345 | 234 |
| https://creatrip.com/en/blog/2528 | 8,901 | 156 |
| ... | ... | ... |

영문 콘솔이라면 컬럼명이 `Page location` / `Event count`로 표시될 수 있음. 어떤 형태든 그대로 저장.

---

## 4. 산출 시 제가 처리할 내용 (CSV 전달 후)

1. `page_location` URL에서 정규식 `/blog/(\d+)` 으로 `blog_code` 추출
2. **locale 합산**: 같은 블로그의 14개 locale URL을 sum (블로그 자체 성과를 보는 게 목적이므로)
3. `.context/outputs/reports/blog-segment-lookup-travel-pool-20260520.csv` (이번 세션에서 생성, 2,229행)와 LEFT JOIN
4. 세그먼트별 집계:
   ```
   CTR = SUM(click) / SUM(impression)
   ```
5. 출력 형식:

   | segment | blogs (분석포함) | impressions | clicks | CTR | 블로그당 평균 imp | 블로그당 평균 click |
   |---|---:|---:|---:|---:|---:|---:|
   | killer | … | … | … | …% | … | … |
   | hidden | … | … | … | …% | … | … |
   | passing | … | … | … | …% | … | … |
   | low | … | … | … | …% | … | … |
   | (unmatched) | … | … | … | …% | – | – |

6. 추가 cuts (요청 시):
   - 블로그별 top/bottom 10 CTR (세그먼트 내)
   - locale별 CTR 차이 (한·중·일·영어권)
   - 블로그당 노출 1회 이상 비율 (커버리지)

---

## 5. 사용자 액션 체크리스트

- [ ] GA4 콘솔 접속 (Creatrip 속성)
- [ ] 위 설정대로 탐색 보고서 생성
- [ ] CSV 다운로드
- [ ] `.context/outputs/raw/ga4-app-install-banner-by-page-60d-20260520.csv`로 저장
- [ ] "CSV 저장 완료" 알려주기 → 제가 즉시 후처리 진행

---

## 6. 후처리 의사코드 (참고용)

```python
import pandas as pd, re

ga = pd.read_csv('.context/outputs/raw/ga4-app-install-banner-by-page-60d-20260520.csv')
ga.columns = ['page_location', 'impression', 'click']  # 컬럼명 정규화

ga['blog_code'] = ga['page_location'].str.extract(r'/blog/(\d+)').astype('Int64')
ga = ga.dropna(subset=['blog_code'])

by_blog = ga.groupby('blog_code', as_index=False)[['impression','click']].sum()

seg = pd.read_csv('.context/outputs/reports/blog-segment-lookup-travel-pool-20260520.csv')
m = by_blog.merge(seg, on='blog_code', how='left')

agg = (m.assign(segment=m['segment'].fillna('(unmatched)'))
        .groupby('segment')
        .agg(blogs=('blog_code','nunique'),
             impressions=('impression','sum'),
             clicks=('click','sum'))
        .assign(ctr=lambda d: d['clicks']/d['impressions']))
print(agg)
```
