# Google TTD 모수 확장 검토 자료

작성일: 2026-05-28
담당: 정수연 (모수 확장) / 강병준 (기술 대응)
마감: 2026-05-29 (1차 공유)

---

## 1. 배경

Google Actions Center의 **Things To Do (TTD)** 피드에 Creatrip 스팟을 내보내 입장권·투어·체험 상품을 광고/무료 노출하는 채널.

2026-05-27 슬랙(`#product-core`)에서 역할 분담:
- **강병준**: 기술 대응 (코드/데이터 모델 수정)
- **정수연**: **모수 확장 검토** (이 문서)

---

## 2. 현재 연동 현황

### 2.1 DB 기준 (production)

- **활성 TTD 스팟 (`is_ttd = 1`)**: **89개**
- `spot_google_ttd` 메타데이터 행: **402개** (비활성화된 이력 포함)
- relation_type 분포:
  - `RELATION_TYPE_ADMISSION_TICKET` (입장권): **49개**
  - `RELATION_TYPE_RELATED_NO_ADMISSION` (투어/체험): **40개**

### 2.2 Google Actions Center 기준 (report.tsv)

- 등록 모수: **87개**
- **유효 노출 효율 낮음**: 28일 Search Referrals 0건이 약 60개 (절반 이상)
- 상위 유입: 롯데월드(41), 전쟁기념관(6), 부산 해변열차(5), 블루라인파크 등
- 3개 채널(Ads/Admission/Experience) 전부 Not Approved인 무효 모수: **약 16개**

---

## 3. report.tsv 컬럼 정의

| 컬럼 | 의미 |
|---|---|
| **Product Id** | Creatrip 스팟 코드 (`spot.code`) |
| **Title** | 상품 제목. 150바이트(UTF-8) 제한 |
| **Locations** | 연결된 POI(관광지) 이름. 빈값이면 `Missing related POI` |
| **Languages** | 피드 포함 번역 언어 (표준 14개: de/en/es/fr/id/it/ja/ko/mn/ru/th/vi/zh-CN/zh-HK/zh-TW) |
| **Ads Status** | Google Ads 유료 광고 노출 자격 |
| **Admission Free Listing Status** | 입장권(Attractions Booking) 무료 노출 자격 — `ADMISSION_TICKET`용 |
| **Experience Free Listing Status** | 체험/투어(Experiences Module) 무료 노출 자격 — `RELATED_NO_ADMISSION`용 |
| **Tour Operator Free Listing Status** | 오퍼레이터 직접 노출. **중개사는 영구 Not Approved 정상** |
| **Brand** | Actions Center 브랜드 (Creatrip Inc.) |
| **Maps Referrals (28d)** | Google Maps에서 들어온 클릭 수 |
| **Search Referrals (28d)** | Google Search에서 들어온 클릭 수 |

**Status 값**: `Eligible` (노출) / `Not Approved` (거부)

**정상 상태 정의**: Admission ↔ Experience 중 **1개 이상 Eligible** + Tour Operator는 Not Approved

---

## 4. TTD 연동 정책 정리

### 4.1 계정·브랜드

- **단일 계정 = 단일 트랙 원칙**: Appointments Redirect + Reservations(Dining) 동시 운영 불가
- Creatrip은 **TTD 전용 별도 계정** 운영 (권한도 별도 부여 필요)
- 식당은 Appointments 계정에서 분리 → 별도 처리

### 4.2 4개 노출 채널

| 채널 | 비용 | 분류 | 자격 |
|---|---|---|---|
| Ads | 유료 | 모든 종류 | Google Ads allowlist |
| Admission Free Listing | 무료 | 입장권 | `relation_type=ADMISSION_TICKET` + POI eligible |
| Experience Free Listing | 무료 | 투어/체험 | `relation_type=RELATED_NO_ADMISSION` + POI eligible |
| Tour Operator | 무료 | 사업자 직접 | GBP 직접 보유 (중개사 제외) |

→ Admission ↔ Experience는 **상호배타적**. 둘 다 Eligible 드묾.

### 4.3 relation_type

| 값 | 정의 | 용도 |
|---|---|---|
| `ADMISSION_TICKET` | 관광지 입장권 | 놀이공원·아쿠아리움·전망대 |
| `RELATED_NO_ADMISSION` | 입장권 없는 관련 활동 | 투어·체험·클래스 |

오분류 → `Overtagged admission` 에러 → 전체 거부

### 4.4 POI 요구사항

- 모든 상품은 최소 1개 POI 연결 필수
- POI는 TTD 프로그램 자격 보유 + Google Place ID 정확 매칭
- 현재 `google_place_id`를 리뷰 수집/TTD 공용 → **TTD 전용 `related_google_place_id` 분리됨** (5/12)

### 4.5 가격 정책

- 표준 성인 가격(standard adult price) 명시 필수
- 30일 내 예약 가능 가격 1개 이상 필수
- 계절 상품/이벤트 종료 시 즉시 제거
- 노출 금액 = 옵션 중 최고가 (5/12 람다 수정)

### 4.6 데이터 품질

| 요구사항 | 제한 |
|---|---|
| title 길이 | 150바이트 UTF-8 |
| option title | 동일 |
| option 번역 | 빈 문자열 금지, 모든 언어 채움 |

### 4.7 카테고리 정책

**TTD 미지원** (영구 제외): 식당·헤어·카페 → Appointments/Dining 트랙으로

**TTD 지원** (Creatrip 어드민 필터 기준 18개, 5/12 최종):
- 명소&입장권(3071), Concert(902), 프라이빗투어(882), 서울근교투어(933), 자연명소투어(934), 도시투어(935), 전통체험투어(937), K-POP클래스(3053), 푸드클래스(3056), 원데이클래스(885), 놀이공원(884), 액티비티&레저(3087), 스키투어(939), 한복&스냅 사진(3081)
- **추가 4개**: 투어(354), 체험(352), K-뷰티(403), 전문헤어(3028) — 정책상 애매하나 광고 노출 실적 있어 추가

### 4.8 운영 진입 조건 (`is_ttd = 1` 유지 게이트, 5/12 확정)

- 영업 중 (미운영 제외)
- 예약 가능 상태
- 예약 가능 시간대 존재
- 어권(다국어) 공개됨
- TTD 메타데이터 + Option Categories 설정 완료

→ 5/12에 위반 스팟 **90+개 `is_ttd=0` 일괄 회수**

---

## 5. 모수 확장을 가로막는 5대 제약

### 5.1 카테고리 미커버
- TTD 미지원 카테고리(식당·헤어·카페) 7개 회수: `11438, 11766, 12810, 12885, 12910, 12980, 13122`
- 5/12 카테고리 4개 추가로 일부 회복 가능 (투어·체험·K-뷰티·전문헤어)

### 5.2 relation_type 오분류
- 투어인데 ADMISSION_TICKET 태깅 → Not Approved
- 5/12에 18개 정정 완료: `2, 10941, 11519, 11522, 11583, 12850, 12872, 12957, 12986, 12998, 13000, 13064, 13115, 13167, 13468, 13879, 14491, 14542`
- Google 재승인 대기

### 5.3 Google Place ID 매칭 실패
- TTD 전용 필드 분리 결정 (5/11)
- **23개 스팟이 매칭 실패 상태**: `11370, 12873, 12984, 13039, 13133, 13135, 13168, 13173, 13176, 13177, 13207, 13471, 13472, 13490, 13566, 13630, 13631, 13728, 13730, 13755, 13760, 13765, 14581`

### 5.4 데이터 품질 (코드 수정 완료)
- option 번역 누락 19개, title 길이 초과 48개, 가격 정책 위반 → 람다 패치 완료

### 5.5 운영 부적격
- 5/12 90+개 일괄 회수 (시간대/어권/예약 가능성 미충족)

---

## 6. TTD 전용 Place ID — 진행 상황

### 6.1 완료 (development 머지됨)

| 커밋 | 내용 |
|---|---|
| `4c9974b6694` | DB migration: `spot_google_ttd.related_google_place_id VARCHAR(255) NULL` |
| `e943bd39503` | 어드민 편집 폼 추가 |
| `09ec5465fec` | TTD Drawer Google Map 링크 변경 |
| `592ecc3580a` | Fallback: NULL이면 `spot.google_place_id` 사용 |
| `d65504c457f` / `f6469f4aa90` / `8c2c2dbb389` / `a3a3ae5ec93` | 편집 UI 안내·검증·일관성 보완 |

### 6.2 미완료

- **데이터 백필 0건**: 402개 행 전부 `related_google_place_id IS NULL`
- **람다 레포(`google-ttd`)의 fallback PR 머지/배포 여부 미확인** — 이 워크스페이스에서 확인 불가, 별도 레포

---

## 7. "조치 필요" 모수 (Admission AND Experience 둘 다 Not Approved)

report.tsv 기준 16개:

| Spot ID | 제목 | 추정 원인 |
|---|---|---|
| 13455 | 부산 블루라인파크 스카이캡슐 일일투어 | relation_type / place_id |
| 12986 | 대구 템플스테이 1박2일 | 5/12 정정됨, 재승인 대기 |
| 13730 | 딸기체험 + 비발디 + 어비얼음계곡 | place_id 매칭 실패 |
| 14254 | 남이섬 입장권 + 셔틀버스 | Locations 빈값 |
| 12925 | 서울 나이트투어 북악~낙산 | 조사 필요 |
| 13135 | 부산 퍼블릭 요트 투어 | place_id 매칭 실패 |
| 12850 | SCENT M.O.M.O 향수 만들기 | 5/12 정정됨 |
| 13414 | 강원여행 (제이드/남이/쁘띠) | 언어 누락 (th 없음) |
| 13064 | 청양 알프스마을 얼음분수축제 | 5/12 정정됨 + 계절상품 |
| 11239 | N서울타워 전망대 | 조사 필요 (입장권인데 거부) |
| 12984 | 평화곤돌라 + 감악산 출렁다리 | place_id 매칭 실패 |
| 13760 | 춘천 레고랜드 프라이빗 | place_id 매칭 실패 |
| 13566 | 서울 시즌 핫스팟 | place_id 매칭 실패 |
| 11240 | 남이섬+쁘띠+이탈리아+아침고요 | 조사 필요 |
| 11561 | 양평 패러글라이딩 | 조사 필요 |
| 11934 | 대구 컴뱃 태권도 | 조사 필요 |

---

## 8. 다음 액션 (우선순위)

### Priority 1 — 즉시 회복 가능
1. **람다 레포 `google-ttd` 의 Place ID fallback PR 배포 상태 확인**
2. **TTD 전용 Place ID 23개 백필** (어드민 편집 폼으로)
   - 대상: 5/11 명단의 매칭 실패 23개
   - 예상 효과: 가장 큰 모수 회복

### Priority 2 — 모니터링
3. 5/12 relation_type 정정 18개의 Google 재승인 추적
4. 5/12 람다 코드 수정 후 데이터 품질 에러 감소 확인

### Priority 3 — 신규 후보 발굴
5. DB에서 후보 풀 추출: `is_ttd=0` AND TTD 지원 카테고리 매칭 AND 예약 가능 시간대 존재 AND 어권 공개됨
6. report에서 Eligible인데 referral 0인 스팟의 컨텐츠/가격 점검

### Priority 4 — 운영 정책 정착
7. `spot_google_ttd` 잔여 데이터 정리 (313개 비활성 행)
8. `is_ttd` 자동 토글 룰 도입 (4.8 진입 조건 기반)

---

## 9. 참고 슬랙 스레드

`#product-core` (`C05999AP2UU`)

- 2026-03-20: [구글 액션 인수인계 + Reservations Redirect 정책](https://creatrip.slack.com/archives/C05999AP2UU/p1773986706980909)
- 2026-04-08: [구글 액션 식당 연동](https://creatrip.slack.com/archives/C05999AP2UU/p1775638232321039)
- 2026-04-10: [TTD 접근 권한](https://creatrip.slack.com/archives/C05999AP2UU/p1775797978296499)
- 2026-04-15: [google ttd 어드민 관리 위치 확인](https://creatrip.slack.com/archives/C05999AP2UU/p1776240202426479)
- 2026-04-16: [Google TTD 이슈 요약 정리](https://creatrip.slack.com/archives/C05999AP2UU/p1776333986340309) — **에러 카탈로그 5종**
- 2026-04-20: [어드민 Google Actions 페이지](https://creatrip.slack.com/archives/C05999AP2UU/p1776671922878559)
- 2026-04-28: [Google Actions TTD 메인 스레드](https://creatrip.slack.com/archives/C05999AP2UU/p1777353716535709) — **모수/카테고리/relation_type 논의**
- 2026-05-27: [Google TTD 역할 분담](https://creatrip.slack.com/archives/C05999AP2UU/p1779852887682179)
