# 데이터 분석 — 스팟 카드 '온라인 쿠폰' 태그

스팟 리스트/검색 결과 카드에 **온라인 쿠폰** 태그를 노출하는 기능의 효과를 판단하기 위한 분석 모음.

> **성격**: 참고용. 출시 전 반드시 측정해야 하는 것은 아니며, 태그 노출 **전/후** 변화를 사후에 확인하고 싶을 때 쓰는 분석 명세다. 각 파일은 "무엇을, 어떤 데이터로, 어떻게 보는지"를 정의하며, 실제 수치는 비워 두었다(돌릴 때 채움).

관련 기획 문서:
- 제안서: `.context/outputs/proposals/proposal_online-coupon-spot-card-tag.md`
- 요구사항: `.context/outputs/jira/requirements_online-coupon-spot-card-tag.md`

## 분석 목록

| # | 파일 | 한 줄 요약 | 우선순위 |
|---|------|-----------|---------|
| 01 | [spot-card-ctr.md](./01-spot-card-ctr.md) | 스팟 카드 CTR — 태그 노출 전/후, 쿠폰 보유 vs 비보유 비교 (핵심) | 높음 |
| 02 | [coupon-spot-coverage.md](./02-coupon-spot-coverage.md) | 태그 노출 대상 스팟 규모·분포·추이 | 중간 |
| 03 | [tag-conversion-funnel.md](./03-tag-conversion-funnel.md) | 태그 → 상세 진입 → 쿠폰 적용 결제 퍼널 + 카니발리제이션 | 중간 |
| 04 | [beauty-cashback-benchmark.md](./04-beauty-cashback-benchmark.md) | 뷰티 캐시백 태그를 벤치마크로 기대 증분 추정 | 낮음(참고) |

## 공통 전제 — 알려진 사실 (확인 완료)

데이터 기준: prod, 조사 시점 2026-06-01.

- **뷰티 캐시백 ON 스팟**: 90개
- **온라인 쿠폰 연결 스팟(활성, `is_active=1`)**: 1,001개
- **온라인 쿠폰 연결 스팟(활성+노출, `is_active=1 AND is_exposed=1`)** = **태그 노출 대상**: **8개**
- **둘 다(뷰티 캐시백 + 활성+노출 쿠폰)**: 0개 / 둘 다(뷰티 캐시백 + 활성 쿠폰): 1개(스팟 14840, 연결 쿠폰 3건 모두 미노출)
- 태그 노출 조건 = 스팟-쿠폰 연결 + 쿠폰 활성(`is_active`) + 쿠폰 자동 노출(`is_exposed`), **그리고** 해당 스팟 뷰티 캐시백 OFF (겹치면 뷰티 캐시백 우선)

### 대상 8개 스팟 = 단일 캠페인 (확인됨)

현재 태그 노출 대상 8개는 모두 **"부산 PICK! 웰니스 할인 쿠폰"** 단일 캠페인에 묶여 있다. (유저 가설 — "특정 캠페인 스팟" — 확인)

- 쿠폰: 정액 할인 **$35 USD / ¥5,500 JPY / NT$1,100 TWD / HK$260 HKD** (언어별 4개 변형, 쿠폰 id 1876–1879)
- 발급 기간: **2026-05-26 ~ 2026-10-31**, 쿠폰 생성·노출 시작 ≈ 2026-05-19
- 대상 스팟(8): 14485 부산 클럽디오아시스 스파&워터파크 / 14487 서프홀릭 / 15208 크레이지서퍼스 / 15224 SMB Wellness / 15455 부산BGN밝은눈안과병원(메디컬) / 15539 빛으로 힐링 에콜 / 15554 하버요가 / 15558 힐스파
- 카테고리: 7개 '체험' + 1개 '메디컬', 전부 부산 웰니스 테마
- **함의**: 향후 보고는 "온라인 쿠폰 태그가 붙은 스팟(=캠페인 스팟)"만 대상으로, 캠페인 단위 전/후로 본다. (대조군/DiD 불필요)

## 공통 — 데이터 소스 & 이벤트

- **스팟 카드 클릭**: GA4 이벤트 `SpotProductCardClick`
  - 주요 파라미터: `code`(스팟 코드), `type`, `categoryid`, `location`(노출 면 — 리스트/검색 등), `keyword`(검색어), `embedding`
  - 발화 위치: `SpotThumbnailCardVertical` / `SpotThumbnailCardHorizontal`의 카드 클릭(Link onClick)
- **DB(쿠폰/스팟)**: `spot`(`is_beauty_cash_back`), `online_coupon`(`is_active`, `is_exposed`), `online_coupon_has_linked_domain`(`linked_domain_type='SPOT'`, `linked_domain_id`=스팟 code)
- 조회 도구: GA(`GA_runAnalyticsReport`), BigQuery(GA4 export), DBA(`select`)

## ⚠️ 공통 주의 — '진짜 CTR'의 분모 문제 & 가용 데이터

데이터 가용성을 확인한 결과(2026-06-01):

- **GA4 raw export(`analytics_*`) 데이터셋은 접근 목록에 없다.** 대신 큐레이션된 `dashboard_ga4.*` 테이블을 쓴다.
- **스팟 카드 단위 '노출(impression)' 이벤트가 없다.** 클릭 이벤트 `SpotProductCardClick`은 GA4로만 가고, 큐레이션 테이블/`general_click_event`(스팟코드 컬럼 없음)에서 **스팟별 카드 클릭 수를 바로 집계할 수 없다.**
- 따라서 `클릭수 / 카드 노출수` 형태의 정확한 카드 CTR은 **지금 데이터로 계산 불가.** 실측에는 아래를 쓴다.
  - **`dashboard_ga4.SpotDetailPV`** — 스팟별 상세 PV(`event_name='SpotDetailPV'`) + 예약정보 진입(`event_name='ReservationInfoEnter'`). 컬럼: `spot_code`, `event_date`, `language`, `last_click_session_source/medium`, 카테고리 등.
  - 이것을 **"카드 클릭으로 도달한 트래픽의 프록시(상세 PV)"**로 사용한다. 단, 상세 PV는 리스트/검색뿐 아니라 외부유입·직접 등 **모든 경로의 도달**을 포함한다(리스트 카드 클릭만 분리되지 않음).
- 정확 CTR이 필요하면(권장, 개발 필요): 카드 노출 이벤트(예: `SpotProductCardImpression`) + 내부 referrer(리스트/검색) 구분을 추가해야 한다. 그 전까지는 **상세 PV 전/후 추이**로 방향성만 본다.
