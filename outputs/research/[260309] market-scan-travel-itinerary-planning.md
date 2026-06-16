# Strategic Market Scan: 여행 일정 플래닝 프로덕트 마켓

**Date**: 2026-03-09
**Purpose**: 크리에이트립 플래너 기능 개선 전략 수립을 위한 경쟁 환경 및 거시 환경 분석
**Scope**: 글로벌 여행 일정 플래닝 시장 + 한국 인바운드 여행 시장 교차 분석

---

## Executive Summary

여행 일정 플래닝 시장은 AI 기술 접목으로 급격한 변환기에 있다. 글로벌 여행 앱 시장은 2026년 $16.23B에서 2035년 $63.87B(CAGR 15.6%)으로, AI in Travel 시장은 2025년 $165.93B에서 2026년 $222.4B(CAGR 34%)으로 성장이 예측된다. 한국은 2025년 1,873만 명의 외국인 관광객을 기록하며 팬데믹 이전 최고치를 넘어섰고, 2028년까지 3,000만 명을 목표로 AI 기반 관광 전략을 추진 중이다.

핵심 발견: **"일정 검증(Itinerary Validation)"은 시장의 미충족 니즈 중 가장 큰 기회**다. 글로벌 AI 플래너들(Layla, TripPlanner AI, Wanderlog)이 "일정 생성"에 집중하는 동안, "내가 짠 일정이 현실적인지 피드백해주는" 검증 기능은 아직 표준화되지 않았다. Klook/KKday는 예약 플랫폼이지 계획 도구가 아니므로, **"계획 + 검증 + 예약"을 통합하는 포지션은 현재 공백**이다. 크리에이트립은 한국 특화 데이터(스팟 간 이동 시간, 영업시간, 시즌 정보)를 활용해 이 공백을 선점할 수 있는 유일한 위치에 있다.

---

## SWOT Analysis

### Internal

| Strengths | Weaknesses |
|-----------|-----------|
| **한국 특화 데이터 독점**: 스팟/상품 데이터, 이동 시간, 영업시간 등 한국 여행에 특화된 1st party 데이터 보유 | **플래너 인지도 극히 낮음**: Reddit r/koreatravel 8,349건 중 크리에이트립 언급 9건(0.1%), Klook 117건의 1/13 |
| **계획→예약 통합**: 플래너에서 일정 계획 → 상품 바로 예약 가능 (Wanderlog/TripIt 불가) | **플래너 액션율 0.27%**: 여행 방문자의 99.7%가 플래너를 사용하지 않음 |
| **경쟁사 부재 기능**: Klook/KKday에 일정 계획·동선 지도 없음 | **글로벌 확장성 제한**: 한국 여행 전용 → TAM이 한국 인바운드 관광객으로 한정 |
| **검증된 리텐션 효과**: 플래너 사용자 리텐션 리프트 1.72x, 구매 전환 3.49x | **AI 플래너 대비 기술 격차**: Layla/TripPlanner AI의 자연어 기반 자동 생성 대비 수동 입력 방식 |
| **콘텐츠 자산**: 한국 여행 블로그/가이드 콘텐츠 축적 | **멀티시티/멀티데이 경험 부족**: 서울 외 지역 커버리지 부재 (Reddit 부정 피드백 공통점) |

### External

| Opportunities | Threats |
|-------------|---------|
| **한국 인바운드 관광 사상 최대**: 2025년 1,873만 명, 2028년 3,000만 목표 → TAM 급속 확대 | **AI 플래너의 범용화**: Layla, TripPlanner AI 등이 한국 여행도 커버 시작 → 차별화 약화 가능 |
| **"일정 검증" 시장 공백**: 34.3% Reddit 유저가 검증 니즈 → 아직 표준 솔루션 없음 | **Klook/KKday의 기능 확장**: 예약 플랫폼이 일정 계획 기능 추가 시 직접 경쟁 |
| **K-culture 글로벌 확산**: K-pop, K-beauty 중심 방한 여행 동기 다변화 | **구글 Travel/Maps의 기능 강화**: 구글이 AI 기반 일정 제안을 강화하면 범용 플래너 시장 잠식 |
| **한국 정부 관광 AI 전략**: 정부가 2028년까지 AI 기반 관광 인프라 투자 → 생태계 활성화 | **개인정보 보호 규제 강화**: GDPR, 한국 개인정보보호법 → 유저 데이터 활용 제약 |
| **봄 시즌 트래픽 급증**: 3~5월 벚꽃 시즌에 여행 방문자 60%+ 증가 | **대안 도구의 관성**: 구글 스프레드시트/노션/종이 노트로 일정 짜는 습관 전환 어려움 |
| **AI 이머징**: 90% 여행자가 AI 여행 계획 인지, 38%만 사용 → 나머지 52%가 전환 대기 풀 | **OTA 슈퍼앱화**: Trip.com, Booking.com의 올인원화로 독립 플래너 앱의 존재 이유 약화 |

### SWOT Action Matrix

| 전략 | 조합 | 액션 |
|------|------|------|
| **S+O: 공격** | 한국 특화 데이터 × 검증 시장 공백 | "일정 검증" 기능을 한국 특화 데이터로 구현 → 글로벌 AI 플래너가 따라올 수 없는 정확도 |
| **W+O: 개선** | 낮은 인지도 × 인바운드 관광 급증 | Reddit/SEO 오가닉 인지도 구축 + 봄 시즌 캠페인으로 TAM 확대 타이밍에 탑승 |
| **S+T: 방어** | 계획→예약 통합 × AI 플래너 범용화 | AI 플래너가 "계획"만 해주는 동안, "계획→검증→예약" 풀 플로우로 차별화 유지 |
| **W+T: 회피** | 액션율 0.27% × 대안 도구 관성 | 플래너를 "일정 짜는 도구"가 아닌 "일정 검증 도구"로 리프레이밍 → 기존 도구와의 비교 축 자체를 변경 |

---

## PESTLE Analysis

| Factor | Current State | Impact | Trend | Timeframe |
|--------|-------------|--------|-------|-----------|
| **Political** — 한국 정부 관광 목표 3,000만 명 | AI 기반 관광 인프라 투자 확대, K-culture Trail 프로그램 | **높음** (+) | 강화 | 2026~2028 |
| **Political** — 비자 정책 완화 | 동남아·중앙아 대상 무비자/간편비자 확대 | 중간 (+) | 확대 | 2025~2027 |
| **Economic** — 원화 약세 | 외국인 여행자에게 한국 여행이 가성비 높아짐 → 방한 수요 증가 | **높음** (+) | 지속 | 2025~2026 |
| **Economic** — 여행 앱 시장 성장 | 글로벌 $16.23B(2026) → $63.87B(2035), CAGR 15.6% | **높음** (+) | 강한 상승 | 2026~2035 |
| **Economic** — 높은 고객 획득 비용 | 상위 5개 플레이어가 시장 48% 장악, 신규 진입자 연 27% 증가 | 중간 (−) | 경쟁 심화 | 지속 |
| **Social** — K-culture 글로벌 확산 | K-pop, K-drama, K-beauty가 독립적 방한 여행 동기로 작용 (뷰티 4.4%) | **높음** (+) | 확대 | 지속 |
| **Social** — "검증 문화" | Reddit에서 일정 검증 요청 34.3% → "전문가/커뮤니티에 확인받고 싶다" 심리 | **높음** (+) | 강화 | 지속 |
| **Social** — 디지털 노마드 증가 | 장기 체류+원격 근무 여행자 세그먼트 성장 → 일정 플래닝 니즈 다변화 | 낮음 (+) | 상승 | 2025~2028 |
| **Technological** — AI 여행 플래너 폭발적 성장 | Layla, TripPlanner AI, iPlan AI 등 자연어 기반 자동 생성 | **최고** (+/−) | 급성장 | 2025~2027 |
| **Technological** — Agentic AI 부상 | 2026년 AI 에이전트가 end-to-end 여행 관리 시작 → 자동 리부킹, 실시간 조정 | **높음** (−) | 초기 단계 | 2026~2028 |
| **Technological** — AR/VR 통합 | 59% 여행 앱이 AR/VR 경험 통합 → 몰입형 여행 계획 | 낮음 (+) | 상승 | 2027+ |
| **Legal** — GDPR/개인정보보호법 | 여행자 데이터 수집·활용에 동의 필요, 위반 시 최대 €20M 벌금 | 중간 (−) | 규제 강화 | 지속 |
| **Legal** — 한국 위치 정보 보호법 | 위치 기반 서비스(이동 시간 계산, 동선 추천)에 위치 정보 수집 동의 필요 | 중간 (−) | 유지 | 지속 |
| **Environmental** — 지속가능 여행 트렌드 | 탄소 발자국 낮은 여행 옵션 선호, 에코 투어리즘 성장 | 낮음 (+) | 상승 | 2026~2030 |

---

## Porter's Five Forces

| Force | Intensity | Key Drivers | Implications |
|-------|----------|------------|-------------|
| **경쟁 강도** (Competitive Rivalry) | **높음** 🔴 | 상위 5개 OTA가 48% 시장 점유, 신규 진입 27%/년 증가. Wanderlog, TripIt, Sygic, Google Travel이 범용 플래너 경쟁. Klook/KKday가 한국 여행 예약 시장 장악 | 범용 플래너 시장은 레드오션. 그러나 **"한국 특화 일정 검증"은 블루오션** — 직접 경쟁자 없음 |
| **공급자 교섭력** (Supplier Power) | **중간** 🟡 | 지도 API(Google Maps, Naver Maps)에 의존. 상품 공급업체(투어, 숙소)는 다수. 콘텐츠는 자체 생산 가능 | 지도 API 비용 변동 리스크. Naver Maps API 활용 시 한국 특화 정확도 확보 가능 |
| **구매자 교섭력** (Buyer Power) | **높음** 🔴 | 무료 대안 풍부 (구글 스프레드시트, 노션, Reddit). 전환 비용 거의 0. 90%가 AI 여행 계획 인지 | 유저는 무료+편리한 도구로 즉시 이탈 가능. **Switching cost를 만드는 것(맥락 축적)이 핵심** |
| **대체재 위협** (Threat of Substitutes) | **최고** 🔴🔴 | 구글 스프레드시트/노션(무료, 익숙), Reddit itinerary check(무료, 커뮤니티), ChatGPT/Claude(범용 AI 일정 생성), 여행사 패키지(일정 고민 자체가 없음) | 가장 강력한 위협. **"크리에이트립이 아니면 안 되는 이유"를 만드는 것이 생존 조건** |
| **신규 진입자 위협** (Threat of New Entrants) | **높음** 🔴 | AI 플래너 진입 장벽 급격히 낮아짐 (LLM API + 지도 API = 최소 기능 구현 가능). Y Combinator에서 여행 AI 스타트업 다수 배출 | 기술적 진입 장벽은 낮지만, **한국 특화 1st party 데이터(스팟 DB, 이동 시간, 영업시간, 예약 연동)는 복제 어려움** |

### Industry Attractiveness: **Medium-Low** (범용 시장) / **Medium-High** (한국 특화 니치)

범용 여행 일정 플래너 시장은 5개 Force 모두 높은 레드오션이다. 그러나 **"한국 여행 특화 + 일정 검증 + 예약 통합"이라는 니치에서는 경쟁 강도가 낮고 진입 장벽이 높아** 매력도가 크게 달라진다.

---

## Ansoff Growth Matrix

| Strategy | Opportunity | Risk Level | Investment | Priority |
|----------|-----------|-----------|-----------|----------|
| **Market Penetration** — 기존 시장 깊이 파기 | 플래너 진입률 0.27%→1%+ 달성. 검색/좋아요/블로그에 진입점 확대, "일정 검증" 라이트로 리포지셔닝. 봄 시즌 캠페인 | **Low** | 프론트 1~2주 + 콘텐츠 | **최고 (H)** |
| **Product Development** — 기존 시장에 새 기능 | "일정 검증" 풀 스펙 (휴무일, 영업시간, 맥락 피드백), AI 기반 자동 일정 생성, "여행 준비도 스코어", 오프라인 캐싱 | **Medium** | 프론트+백엔드 4~8주 | **높음 (H)** |
| **Market Development** — 새 시장에 기존 제품 | 일본/대만/동남아 인바운드 여행자 타겟 확대. 다국어 플래너 UX. Reddit 외 TikTok/소홍서(小红书) 채널 | **Medium** | 마케팅 + 다국어 | **중간 (M)** |
| **Diversification** — 새 시장에 새 제품 | 한국 외 국가(일본, 대만) 여행 플래너로 확장. B2B 여행사/DMC 일정 관리 도구. 여행 보험 연동 | **High** | 대규모 투자 | **낮음 (L)** |

### 상세 분석

**Market Penetration (최우선)**
- 현재 여행 방문자 일 ~8,800명 중 플래너 사용 ~34명(0.27%) → 모수가 압도적으로 남아있음
- 진입점 확대만으로 0.5~0.8% 달성 가능 (Growth Manager 추정)
- "일정 검증" 리프레이밍으로 대안 도구(스프레드시트, 노션)와의 비교 축 자체를 변경
- **ROI가 가장 높고 리스크가 가장 낮은 전략**

**Product Development (2순위)**
- AI 일정 검증 풀 스펙이 완성되면, Reddit "itinerary check" 질문을 직접 대체 → 오가닉 인지도 구축
- 그러나 AI 기반 자동 일정 생성은 Layla/TripPlanner AI와 직접 경쟁 → 한국 특화 데이터로 차별화 필수
- "계획→검증→예약" 풀 플로우는 경쟁사가 단기간에 복제 어려움

**Market Development (3순위)**
- 한국 인바운드 상위 4국(중국 5.29M, 일본 3.65M, 미국 1.51M, 대만 1.38M)이 전체 63%
- 중국 유저는 소홍서/위챗 생태계, 일본 유저는 다른 정보 행동 패턴 → 세그먼트별 접근 필요
- 현재 Reddit 중심 인사이트는 영어권 유저에 편향 → 아시아권 유저 이해가 부족

---

## 주요 경쟁사 맵핑

### 직접 경쟁 (한국 여행 일정 관련)

| 경쟁사 | 포지셔닝 | 일정 기능 | 예약 통합 | 한국 특화 | 위협도 |
|--------|---------|----------|----------|----------|--------|
| **Klook** | 투어/티켓 예약 플랫폼 | 가이드 콘텐츠만 (일정 도구 없음) | **강력** | 중간 (아시아 전반) | 🟡 중간 — 일정 기능 추가 시 직접 경쟁 |
| **KKday** | 체험/액티비티 예약 | 가이드 콘텐츠만 | **강력** | 중간 (아시아 전반) | 🟡 중간 |
| **Trip.com** | OTA 슈퍼앱 | AI 기반 일정 제안 시작 | **최강** | 중간 (글로벌) | 🔴 높음 — AI + 예약 통합 |
| **VisitKorea** | 한국관광공사 공식 | 기본 코스 추천 | 없음 | **최고** (공식) | 🟢 낮음 — UX 열세 |

### 간접 경쟁 (범용 일정 플래너)

| 경쟁사 | 핵심 강점 | 약점 | 한국 특화 | 위협도 |
|--------|----------|------|----------|--------|
| **Wanderlog** | 협업 일정 계획, 지도 기반, 예산 관리. Y Combinator 출신 | 예약 통합 약함, 한국 데이터 부족 | 없음 | 🟡 중간 |
| **TripIt** | 이메일 포워딩 자동 일정 정리, 실시간 항공편 알림 | "정리" 도구이지 "계획" 도구가 아님 | 없음 | 🟢 낮음 |
| **Google Travel** | 구글 에코시스템 통합, 무료, 방대한 데이터 | 일정 "계획" 기능 제한적, 검증 없음 | 낮음 | 🟡 중간 |
| **Sygic Travel** | 지도 기반 관광지 탐색, 오프라인 지도 | 예약 연동 약함 | 없음 | 🟢 낮음 |

### AI 네이티브 경쟁자 (이머징)

| 경쟁사 | 핵심 강점 | 약점 | 위협도 |
|--------|----------|------|--------|
| **Layla AI** | 자연어 대화형 일정 생성, "Trusted by Millions" | 예약 통합 제한, 검증보다 생성 중심 | 🔴 높음 |
| **TripPlanner AI** | 자동 일정 생성, 교통 시간 포함 | 한국 특화 데이터 부족, 예약 연동 약함 | 🟡 중간 |
| **iPlan AI** | 분 단위 계획, 실시간 교통 반영, 자동 조정 | 범용적, 한국 특화 없음 | 🟡 중간 |
| **SupTravel AI** | **AI 일정 체커** — 기존 일정 붙여넣으면 피드백 | "검증" 기능이 크리에이트립 전략과 직접 겹침 | 🔴🔴 **최고** |
| **ChatGPT/Claude** | 범용 AI로 일정 생성+검증 모두 가능 | 실시간 데이터 없음, 예약 불가, 할루시네이션 | 🟡 중간 |

---

## Cross-Framework Synthesis

### Converging Signals (모든 프레임워크가 동의하는 것)

1. **"일정 검증"은 시장의 가장 큰 미충족 니즈**
   - SWOT: Reddit 34.3% 검증 수요가 기회
   - Porter's: 대체재(Reddit, 스프레드시트)가 검증을 못 함
   - PESTLE: AI 기술 발전으로 자동 검증이 기술적으로 가능해짐
   - Ansoff: Market Penetration의 핵심 레버

2. **한국 특화 1st party 데이터가 유일한 지속 가능 경쟁 우위**
   - SWOT: 내부 강점 1위
   - Porter's: 신규 진입자가 복제하기 가장 어려운 자산
   - PESTLE: 한국 정부의 관광 데이터 인프라 투자와 시너지
   - Ansoff: Product Development의 핵심 차별화 원천

3. **범용 플래너 시장은 레드오션, 니치 집중이 필수**
   - SWOT: 글로벌 확장성 제한은 약점이자 동시에 "니치 집중"의 정당화
   - Porter's: 범용 시장 매력도 Medium-Low vs 니치 Medium-High
   - Ansoff: Diversification(새 국가 확장)은 최하위 우선순위

4. **AI 네이티브 경쟁자가 가장 큰 위협**
   - SWOT: AI 플래너 기술 격차가 약점
   - Porter's: 진입 장벽 급격히 낮아짐
   - PESTLE: Agentic AI가 2026년부터 본격화
   - **특히 SupTravel AI의 "AI Itinerary Checker"가 크리에이트립의 "일정 검증" 전략과 직접 겹침** → 속도가 중요

### Strategic Imperatives (반드시 해야 하는 것)

1. **"일정 검증" 라이트를 최대한 빨리 출시** — SupTravel AI 등 AI 네이티브 경쟁자가 한국 특화 검증을 추가하기 전에 선점
2. **한국 특화 데이터의 깊이를 경쟁 장벽으로 강화** — 스팟별 이동 시간, 영업시간, 휴무일, 시즌 정보 등 AI가 환각 없이 제공하기 어려운 정확한 데이터
3. **"계획→검증→예약" 풀 플로우를 완성** — Wanderlog는 예약이 약하고, Klook은 계획이 없음. 이 통합이 유일한 차별화
4. **Reddit/SEO 오가닉 인지도를 최소 1%로 끌어올리기** — 0.1% 인지도는 어떤 전략도 무력화시킴

### Key Risks (최우선 대응 필요)

1. **SupTravel AI / Layla AI의 한국 특화 확장** — AI 네이티브가 한국 데이터를 크롤링해서 검증 기능을 추가하면 크리에이트립의 차별화가 약해짐
2. **Klook/KKday의 일정 기능 추가** — 예약 강자가 계획 기능을 붙이면 "계획→예약 통합" 우위가 사라짐
3. **구글의 AI Travel 강화** — 구글이 Maps + AI + 일정 검증을 통합하면 모든 독립 플래너가 위협받음
4. **플래너 진입률 0.5% 미달** — 4주 후 Go/No-Go에서 실패하면 플래너 전략 자체를 재검토해야 함

### Best Opportunities (리스크 조정된 최고 기회)

1. **봄 시즌(3~5월) × 일정 검증 라이트 출시** — 시즌 트래픽 급증 + 신기능 출시 타이밍 일치 → 최대 임팩트
2. **Reddit "itinerary check" → 크리에이트립 플래너 대체** — 34.3% 검증 니즈를 흡수하면 오가닉 유입 채널이 됨
3. **"서울+부산 3~4일" 템플릿** — Reddit 최대 수요 패턴(100건)이자 가장 높은 불안 세그먼트 → Cold Start 해소 + 검증 가치 즉시 체감
4. **메타 광고 × 플래너 랜딩 연동** — 광고가 이미 RETURN_D1을 올리고 있으니, 랜딩을 플래너 템플릿으로 변경하면 "1회성 전환 → 리텐션 파이프라인" 전환

---

## Strategic Recommendations

### 1. "일정 검증" 선점 전략 — Speed is Everything

**근거**: SWOT(S+O), Porter's(대체재 위협 대응), PESTLE(AI 기술 트렌드), Ansoff(Market Penetration)

SupTravel AI가 이미 "AI Itinerary Checker"를 출시했다. 범용 AI 검증은 한국 특화 정확도가 낮겠지만, 시간이 지나면 데이터가 축적된다. **크리에이트립은 한국 특화 1st party 데이터의 정확도 우위가 있는 지금, "일정 검증 라이트"를 최대한 빨리 출시하여 "한국 일정 검증 = 크리에이트립"이라는 인식을 선점**해야 한다.

### 2. "한국 여행의 Waze" 포지셔닝

**근거**: SWOT(차별화 필요), Porter's(니치 집중), Cross-synthesis(범용 레드오션)

Waze가 "네비게이션"이 아닌 "실시간 교통 정보"로 구글 Maps와 차별화했듯이, 크리에이트립 플래너는 "일정 짜기"가 아닌 **"한국 여행 일정이 현실적인지 즉시 확인"**으로 포지셔닝해야 한다. 이 포지셔닝이 구글 스프레드시트/노션/ChatGPT와의 비교 축 자체를 바꾼다.

### 3. AI 네이티브와 경쟁하지 말고, AI가 못하는 것에 집중

**근거**: SWOT(기술 격차 약점), Porter's(신규 진입 위협), PESTLE(Agentic AI 부상)

Layla/TripPlanner AI와 "자동 일정 생성" 경쟁은 패배가 확실하다. 대신 **AI가 환각 없이 정확하게 제공하기 어려운 것** — 실시간 영업시간, 정확한 대중교통 이동 시간, 휴무일, 시즌별 혼잡도 — 에 집중한다. **"AI가 일정을 짜주면, 크리에이트립이 검증해준다"**는 보완적 포지셔닝도 가능.

### 4. Klook/KKday와의 차별화 축 명확화

**근거**: SWOT(경쟁사 부재 기능), Porter's(경쟁 강도), Ansoff(Market Penetration)

**Klook = "뭘 살까", Creatrip = "어떻게 돌까"**. 이 포지셔닝을 모든 터치포인트에서 일관되게 강화한다. Klook이 일정 기능을 추가하더라도, "한국 특화 검증 + 동선 최적화"의 깊이에서 차별화를 유지할 수 있다.

---

## Monitoring Plan

| Signal | What to Watch | Source | Check Frequency |
|--------|-------------|--------|----------------|
| **AI 플래너 한국 진출** | Layla, SupTravel, TripPlanner가 한국 특화 기능 추가하는지 | 제품 업데이트, Product Hunt | 격주 |
| **Klook/KKday 일정 기능** | 일정 계획/플래너 기능 출시 여부 | 앱 업데이트, 보도자료 | 월 1회 |
| **구글 Travel AI** | 구글이 AI 기반 일정 제안/검증 기능 강화하는지 | Google I/O, 제품 업데이트 | 분기 |
| **한국 인바운드 관광 수치** | 월별 방문자 수, 국가별 비중 변화 | 한국관광공사, 야놀자 리서치 | 월 1회 |
| **Reddit r/koreatravel** | "itinerary check" 게시글 트렌드, 크리에이트립 언급 빈도 | Reddit | 주 1회 |
| **플래너 진입률** | 0.27% → 0.5% → 1% 추적 | 내부 대시보드 | 일 1회 |
| **AI 여행 계획 채택률** | 현재 38% 사용 → 증가 추세 | TakeUp AI 리포트, 업계 조사 | 분기 |
| **규제 변화** | GDPR 강화, 한국 개인정보보호법 개정, 위치 정보 법 변경 | 법률 뉴스 | 분기 |

---

## Sources

- [Travel Planner App Market Size, CAGR 11.9%](https://market.us/report/travel-planner-app-market/)
- [Travel Application Market Size 2025-2035](https://www.businessresearchinsights.com/market-reports/travel-application-market-116262)
- [AI in Travel Market Size, CAGR 36.2%](https://market.us/report/ai-in-travel-market/)
- [TakeUp AI — How Travelers Use AI in 2026](https://takeup.ai/new-research-shows-how-ai-is-changing-travel-planning-in-2026/)
- [AI-Planned Travel Surges in 2026](https://www.hotelmanagement.net/tech/report-ai-planned-travel-surges-2026-growth-still-ahead)
- [South Korea Welcomes Record 18.5M Tourists in 2025](https://en.tempo.co/read/2075687/south-korea-welcomes-record-18-5-million-foreign-tourists-in-2025)
- [South Korea Tourism Boom — 30M by 2028](https://www.micetraveladvisor.com/news/article/south-koreas-tourism-boom-aiming-for-30-million-visitors-by-2028/)
- [South Korea's 2025 Inbound Tourism Forecast (야놀자 리서치)](https://www.yanolja-research.com/brief/view/145?lang=en)
- [Korea's AI-Powered Tourism Revolution](https://www.travelandtourworld.com/news/article/target-thirty-million-inside-south-koreas-bold-ai-powered-tourism-revolution-by-2028/)
- [50+ Travel App Market Statistics 2025](https://hotelagio.com/travel-app-market-statistics/)
- [Wanderlog vs TripIt Comparison](https://wanderlog.com/blog/2024/11/26/wanderlog-vs-tripit/)
- [Best AI Trip Planners 2026 — 8 Tools Reviewed](https://cybernews.com/ai-tools/best-ai-trip-planner/)
- [Free AI Itinerary Checker — SupTravel](https://suptravel.ai/blog/free-ai-itinerary-checker)
- [Layla AI Trip Planner](https://layla.ai/)
- [GDPR in Tourism](https://dataprivacymanager.net/gdpr-in-tourism-through-the-eyes-of-a-privacy-geek-on-vacation/)
- [KKday vs Klook Comparison](https://www.volunteerfdip.org/comparison/kkday-vs-klook)
