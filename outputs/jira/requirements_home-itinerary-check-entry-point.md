# 메인 홈 'You might be interested in...' 영역에 Itinerary Check 진입점 추가

## 배경

### 문제 정의

- `/itinerary-check`(여행 일정 검증 MVP) 페이지의 진입 동선이 현재 `/spot`(스팟 홈)의 `SpotMainCuratedItinerarySection` carousel 첫 슬롯 하나뿐이어서, 페이지 향 진입이 제한적임
- 메인 홈(`/`)은 최근 7일 기준 **홈에서 클릭이 1회 이상 발생한 세션이 약 16,448개**로 트래픽 규모가 가장 큼에도 불구하고 `/itinerary-check` 진입점이 없음
- 메인 홈의 진입점 후보 중, **'You might be interested in...' (HomeSubMenu) 영역**은 모바일/태블릿 인게이지 세션 중 환율 아코디언 클릭율 **69%** 등 정보형 컨텐츠에 가장 강한 클릭 동선이 형성된 영역임
- 다만 HomeSubMenu의 기존 인터랙션은 "펼침 → 하위 컨텐츠 노출" 패턴이라, `/itinerary-check`처럼 페이지 이동이 적합한 진입점에는 그대로 끼우기 어려움
- 또한 `homeBottomBanners`(블로그 영역 위 롤링 배너)에 단독 배너 형태로 추가하면 **광고 노이즈에 묻혀 제품 컨텐츠로 인식되지 않을 위험**이 있음

### 가설적 임팩트

- 메인 홈은 `/spot`보다 트래픽 규모가 크고, 정보형 영역(HomeSubMenu)에 노출되면 itinerary-check의 가이드/검증 성격과 컨텍스트가 매칭되어 진입 증가 기대
- itinerary-check MVP 성공 기준(런칭 후 4주 평가): **일 10건+ 요청** 달성. 현재 진입점만으로는 도달 어려운 상황에서 메인 홈 진입점 추가가 KPI 직결
- 가설:
  - HomeSubMenu의 다른 항목(Exchange 11.01%, Beauty 1.10%, Stay 1.10% 등 분모 통일 기준) 수준의 펼침 클릭율 확보 시, 메인 홈 16,448 세션 × 1~3% = **주간 160~490 펼침 세션** 기대
  - 펼침 후 CTA 클릭 전환율을 30~50% 가정 시 주간 50~250 페이지 진입 추가 → MVP 성공 기준 충족 가능
  - 임프레션 데이터 부재로 진짜 CTR 산출은 불가하므로, 본 안 적용 후 `general_click_event` 기반 펼침/CTA 클릭 절대수로 측정

## 구현

### 유저 플로우

1. 메인 홈(`/`) 방문 시 'You might be interested in...' (HomeSubMenu) 영역에 신규 항목 **'Itinerary Check'**(가칭) 노출
2. 유저가 항목을 펼치면(모바일/태블릿: 아코디언 펼침 / 데스크톱: 탭 선택) 다음 컨텐츠가 노출됨
   - itinerary-check 가치 카피 1줄 (예: "Not sure your Korea itinerary is realistic? Get an expert review.")
   - 3단계 안내(HowItWorks 압축 버전): Submit your plan → Expert review → Email feedback in 24h (아이콘 + 한 줄 텍스트)
   - CTA 버튼 1개: "Check my itinerary →" (행동 지향 라벨, 단순 'More' 류 X)
3. 유저가 CTA 버튼을 클릭하면 `/itinerary-check` 페이지로 이동
4. 이후 `/itinerary-check` 페이지에서 폼 작성·제출은 기존 동작 유지

> 참고: 인라인 폼 임베드 방식은 MVP 단계에서는 비용/리스크가 크다고 판단하여 1차에는 페이지 이동 형태로 진행. 데이터 확인 후 임베드 방식으로 업그레이드 가능.

### 프론트엔드 요구사항

**위치**
- `frontend/apps/web/domain/common/home/HomeSubMenu.tsx` 내부의 `MobileAndTabletHomeSubMenu` 및 `DesktopHomeSubMenu` 양쪽에 항목 추가
- 노출 순서: **Exchange 항목 바로 다음(2번째 슬롯)** 추천. (Exchange가 현재 1등 동선이므로 첫 슬롯은 유지)

**신규 컴포넌트**
- 모바일/태블릿: `frontend/apps/web/domain/common/home/mobileAndTabletHomeSubMenu/SubMenuItineraryCheckCollapse.tsx`
- 데스크톱: `frontend/apps/web/domain/common/home/desktopHomeSubMenu/SubMenuItineraryCheck.tsx`
- 두 컴포넌트는 가치 카피 + 3단계 안내 + CTA 버튼 구조를 동일하게 노출 (반응형 폭 대응)

**컨텐츠 구성 (펼침 시)**
- 가치 카피: i18n 키로 관리 (예: `home.itinerary-check.value-copy`)
- 3단계 안내: `domain/common/itinerary-check/components/HowItWorks.tsx`의 압축 버전 노출 — 신규 prop 또는 별도 compact variant 추가 검토
- CTA 버튼: `Link` 컴포넌트로 `ROUTE_PATH.ITINERARY_CHECK.HOME.getURL()` 이동
- **잔여 수량 카운터(`X of 100 remaining`)는 1차 범위에 포함하지 않음** (홈에서의 데이터 의존성 추가 비용 회피, MVP는 페이지 진입 후에만 노출)

**HomeSubMenu 항목 메타**
- 라벨: i18n 키 `home.shortcut-itinerary-check`(예시), 다국어 대응 필수 (en/zh-TW/zh-HK/ja/ko 등 기존 HomeSubMenu와 동일 언어 세트)
- `useSubMenuI18nTrans` switch에 신규 case 추가
- `MobileAndTabletHomeSubMenu` / `DesktopHomeSubMenu`의 항목 리스트 정의에도 신규 항목 등록

**GA 이벤트 (신규 분리 트래킹)**
- 펼침: `HomeItineraryCheckExpand` (모바일/태블릿 아코디언 펼침 또는 데스크톱 탭 선택 시)
- CTA 클릭: `HomeItineraryCheckClick` (펼침 컨텐츠의 CTA 버튼 클릭 시)
- 페이지 도달 후 폼 제출은 기존 `/itinerary-check` 이벤트 그대로 사용 → 깔때기 분석 가능
- 자동 트래킹(`general_click_event`)도 함께 들어가지만, 명시적 GA 이벤트로 채널 분리 측정

**기존 진입점**
- `/spot`의 `SpotMainCuratedItinerarySection` carousel 첫 슬롯(`ItineraryCheckBanner`)은 그대로 유지

**i18n**
- 신규 키 추가 시 `pnpm i18n` 워크플로우 또는 `i18n-generator` 스킬 활용
- 라벨/카피/CTA 모두 다국어 대응

### 백엔드 요구사항

- **변경 없음**
- `/itinerary-check` 페이지 및 그 내부의 폼 제출/이미지 업로드/Google Sheets 적재 로직은 기존 그대로 동작

## 메트릭 / 측정 계획

- 절대 지표 (4주 평가)
  - `HomeItineraryCheckExpand` 절대수 (주간/일간)
  - `HomeItineraryCheckClick` 절대수
  - `/itinerary-check` 페이지 PV (홈 진입 vs 스팟 진입 vs 직접 진입 분리)
  - 폼 제출 건수 (기존 이벤트 활용)
- 깔때기
  - 메인 홈 클릭 세션 → HomeSubMenu 펼침 → CTA 클릭 → 페이지 도달 → 폼 제출
- 비교 가드레일
  - HomeSubMenu 내 다른 항목(특히 Exchange) 펼침/클릭 수치 변화 — 기존 항목을 가리지 않는지 확인
  - `/spot`의 `SpotMainCuratedItinerarySection`을 통한 itinerary-check 진입 수치 변화

## 미결 / 추후 결정

- CTA 버튼 정확한 라벨 (예시: "Check my itinerary", "Get expert review", "Submit my plan" 중 카피 검토 필요)
- HomeSubMenu 내 정확한 노출 순서 (Exchange 다음 권장이나 디자인 검토 시 조정 가능)
- 잔여 수량 카운터 노출은 1차 범위에서 제외하지만, 추후 데이터 확인 후 추가 검토
- 디자인 자산(아이콘/일러스트) 별도 디자인 의뢰 필요 — TBD
