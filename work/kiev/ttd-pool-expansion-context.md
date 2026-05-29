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

## 8. 모수 확보 액션 플랜 (임팩트순)

> 전제: 모수 확장 경로는 **(A) 내부 정상화** (DB에 있는 상품 켜기) + **(B) 신규 입점** 두 갈래. (A)부터 처리.
> POI(Google Maps 카테고리) ≠ Tour Operator GBP(파트너 직접 노출 채널, 우리 모수 아님). 혼동 금지.

### Action 1. Tier 1 32개 relation_type 정정 후 토글 — **+25~30**
- 대상: `is_ttd=0` + 운영 진입 조건 5개 + `spot_google_ttd` 메타까지 보유한 32개
- 작업: 어드민 `Google Actions → TTD → 상세 Drawer → TtdMetadataSection`에서 relation_type 정정 후 `is_ttd=1` 토글
- 검수: 투어/택시투어/워킹투어/명상투어/원데이클래스의 ADMISSION_TICKET 오분류 → RELATED_NO_ADMISSION 정정 (오분류 시 `Overtagged admission` → 전체 거부)
- 제외: 헤어/리조트/렌트카는 카테고리 부적격 — 토글 금지
- 소요: 운영팀 1~2시간

### Action 2. Tier 2 보수 175개 메타데이터 일괄 입력 — **+150**
- 대상: TTD 공식 지원 12개 카테고리 + 운영 진입 조건 5개 충족 + `spot_google_ttd` row 없음
- 카테고리 batch (relation_type + option_categories 매핑):
  - 원데이클래스 66 / K-POP클래스 6 / 푸드클래스 10 / 한복&스냅 18 / 액티비티&레저 12 / 투어계열(서울근교 11 + 자연 8 + 도시 7 + 전통체험 6 + 프라이빗 5) → `RELATED_NO_ADMISSION`
  - 명소&입장권 25 → `ADMISSION_TICKET`
  - Concert 1 → 케이스별
- 선행 확인: Tier 2처럼 `spot_google_ttd` row 없는 케이스의 "신규 생성" UI 진입점 존재 여부
- 소요: 운영팀 1~2일

### Action 3. Place ID 매칭 실패 23개 백필 — **+15~20**
- 대상: §5.3 명단 23개 (TTD 전용 `related_google_place_id`)
- 분기:
  - Place ID가 틀린 곳 → 올바른 ID 교체
  - Place가 일반 사업장 분류 → Google Maps 관광지 카테고리 정정 요청
  - Place 없음 → 신규 Place 등록 후 ID 발급
- 선행: 람다 레포 `google-ttd`의 Place ID fallback PR 배포 상태 확인 **필수**

### Action 4. Tier 2 애매 4개 카테고리 314개 단계적 적용 — **+200~250**
- 진행 순서:
  1. 투어 26 → RELATED_NO_ADMISSION (안전)
  2. 체험 148 → RELATED_NO_ADMISSION (안전)
  3. K-뷰티 160 → 시범 30개 → 승인률 확인 → 확대
  4. 전문헤어 180 → 보류 (§4.7과 충돌 가능성 가장 큼)
- 소요: 1~2주 (Google 승인 모니터링 포함)

### Action 5. relation_type 자동 추천 + 어드민 부정합 가드 — **누적 모수 유지**
- 카테고리 ↔ relation_type 매핑 테이블 정책화
- 어드민 저장 시 부정합 경고로 신규 오분류 사전 차단

### Action 6. `is_ttd` 자동 토글 룰 — **운영 정착**
- §4.8 진입 조건 위반 시 자동 `is_ttd=0`, 회복 시 자동 `is_ttd=1`
- 시즌 상품 자동 회수/재가입

---

### 누적 임팩트

| 단계 | 누적 활성 모수 | 비고 |
|---|---:|---|
| 현재 | 89 | 무효 16개 포함 |
| + Action 1 | ~115 | 운영 1~2시간 |
| + Action 2 | ~265 | 운영 1~2일 |
| + Action 3 | ~280 | 람다 배포 선행 |
| + Action 4 | **~500** | 1~2주 단계적 |

### 의존성

| 작업 | 선행 |
|---|---|
| Action 1 | 어드민 편집 폼 (배포 완료) |
| Action 2 | 신규 row 생성 UI 진입점 확인 |
| Action 3 | 람다 `google-ttd` Place ID fallback 배포 |
| Action 4 | Google 정책 재확인 + 시범 결과 |
| Action 5,6 | 카테고리-relation_type 매핑 정책 합의 |

---

## 9. relation_type 분류 가이드 (어드민 정정용)

`TtdRelationType` 3종 — Google TTD `related_locations.relation_type`:

| 값 | 정의 | 노출 채널 |
|---|---|---|
| `ADMISSION_TICKET` | 상품 = POI 입장권 자체 | Admission Free Listing |
| `RELATED_NO_ADMISSION` | POI에서/근처 활동·체험·투어 (입장권 미포함) | Experience Free Listing |
| `SUPPLEMENTARY_ADDON` | POI 방문 보조 (셔틀/오디오가이드/픽업) | 보조 슬롯 (Eligible 카운트 미포함이 정상) |

**결정 트리**
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

---

## 10. 후보 풀 추출 결과 (2026-05-29 production)

§4.8 운영 진입 조건 + POI 매칭 기준 SQL 추출:

| 구분 | 수 | 정의 | 필요 작업 |
|---|---:|---|---|
| Tier 1 | **32** | `spot_google_ttd` 메타까지 보유, `is_ttd=0` | 어드민에서 토글만 (relation_type 검수 후) |
| Tier 2 (보수) | **175** | 공식 지원 12개 카테고리, 메타 없음 | 메타데이터 신규 입력 |
| Tier 2 (애매) | **314** | 5/12 추가 4개 카테고리 | 단계적 진행 (헤어 제외) |
| **합계** | **521** | 즉시~단기간 내 활성화 가능 후보 | |

추출 조건:
- `is_ttd=0` AND `is_in_business=1` AND `is_reservable=1`
- `google_place_id` 보유
- TTD 지원 18개 카테고리 중 하나
- `spot_translation.is_publish=1`인 표준 14언어 중 ≥12개
- 향후 30일 내 예약 가능 time slot 존재

---

## 11. 참고 슬랙 스레드

`#product-core` (`C05999AP2UU`)

- 2026-03-20: [구글 액션 인수인계 + Reservations Redirect 정책](https://creatrip.slack.com/archives/C05999AP2UU/p1773986706980909)
- 2026-04-08: [구글 액션 식당 연동](https://creatrip.slack.com/archives/C05999AP2UU/p1775638232321039)
- 2026-04-10: [TTD 접근 권한](https://creatrip.slack.com/archives/C05999AP2UU/p1775797978296499)
- 2026-04-15: [google ttd 어드민 관리 위치 확인](https://creatrip.slack.com/archives/C05999AP2UU/p1776240202426479)
- 2026-04-16: [Google TTD 이슈 요약 정리](https://creatrip.slack.com/archives/C05999AP2UU/p1776333986340309) — **에러 카탈로그 5종**
- 2026-04-20: [어드민 Google Actions 페이지](https://creatrip.slack.com/archives/C05999AP2UU/p1776671922878559)
- 2026-04-28: [Google Actions TTD 메인 스레드](https://creatrip.slack.com/archives/C05999AP2UU/p1777353716535709) — **모수/카테고리/relation_type 논의**
- 2026-05-27: [Google TTD 역할 분담](https://creatrip.slack.com/archives/C05999AP2UU/p1779852887682179)
