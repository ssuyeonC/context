# 세부 기획안 요구사항 문서

## 배경

### 문제 정의

- 스팟 리스트 페이지(`/spot/list`)는 지역·카테고리 조합으로 사실상 수많은 랜딩 URL이 생성되지만, 어권별 SEO 메타 정보(타이틀·설명)와 페이지 대표 URL(캐노니컬), 문서 구조를 대표하는 `H1` 태그가 정비되어 있지 않은 상태
- 어권별 정적 메타만 있거나 값이 없어, 검색엔진이 "서울 즐길거리", "부산 한복 대여"처럼 지역·카테고리 조합 키워드로 페이지를 색인·평가하기 어려운 구조
- 지역·카테고리 필터가 URL 파라미터(`region` / `category` / `middleCategory`)로 갈라지는데도, 그 조합에 맞춰 타이틀·설명·`H1`이 바뀌지 않아 조합별 페이지가 검색 결과에서 변별력을 갖지 못함
- 캐노니컬 부재로 정렬(`order` / `direction`)·페이지네이션(`page`) 파라미터만 다른 동일 콘텐츠 URL이 중복 색인될 여지
- 동일 페이지가 17개 어권으로 존재하나 어권 간 대체 관계(`hreflang`) 신호가 없어, 번역만 다른 페이지끼리 중복 콘텐츠로 평가되거나 유저 언어와 다른 어권 페이지가 검색결과에 노출될 여지

### 가설적 임팩트

- 지역·카테고리 조합별로 어권에 맞는 타이틀·설명·`H1`을 동적 노출하여, 조합 키워드 색인 커버리지와 검색 결과 클릭률(CTR) 개선 기대
- 캐노니컬 정비로 정렬·페이지 파라미터 변형 URL의 중복 색인을 정리하여, 대표 URL로 색인 신호 집중
- `hreflang` 정비로 유저 언어에 맞는 어권 페이지가 검색결과에 노출되도록 유도, 어권 간 중복 콘텐츠 평가 리스크 완화
- 정량 지표(조합 랜딩 URL 색인 수, 오가닉 노출·유입, CTR)는 도입 후 사후 측정 — TBD

## 구현

### 유저 플로우

- 유저가 어떤 어권(예: 영어·일본어·번체 등)으로 `/spot/list`에 진입하면, 그 어권의 템플릿으로 타이틀·설명·`H1`이 채워져 노출
- 유저가 지역·카테고리 필터를 적용하면, 적용된 조합에 맞춰 타이틀·설명·`H1`의 변수 자리(`지역`·`카테고리`)가 그 값으로 치환되어 갱신
- 지역·카테고리를 아무것도 고르지 않은 기본 상태에서는, 각 변수의 어권별 기본값(예: 지역=`Korea`/`한국`, 카테고리=`Activities`/`즐길거리`)으로 치환
- `H1`은 검색엔진·접근성용으로 문서에는 존재하되, 유저에게 보이는 화면에서는 시각적으로 숨김 처리(레이아웃에 영향 없이 화면 밖으로 밀어냄) — 화면 노출 문구가 아니라 문서 구조 신호 목적

### 프론트엔드 요구사항

**어권별 동적 메타 렌더링**

- `/spot/list` 진입 시 현재 어권에 해당하는 템플릿으로 `<title>`, `<meta name="description">`, `<link rel="canonical">`, `H1`을 서버 사이드 렌더링 단계에서 생성하여, 크롤러가 최초 응답에서 완성된 메타를 읽도록 구성
- 타이틀·설명·`H1` 템플릿의 변수는 아래 규칙으로 치환
  - `{ 지역 | 기본값 }` → 선택된 지역명, 미선택 시 어권 기본값
  - `{ 카테고리 | 기본값 }` → **선택된 카테고리 중 가장 하위 단계**의 카테고리명, 미선택 시 어권 기본값
    - 대·중카테고리 모두 선택 시 → 중카테고리명
    - 대카테고리만 선택 시 → 대카테고리명
    - 미선택 시 → 어권 기본값

**어권별 템플릿 정본 (17개 어권)**

| 어권 | 타이틀(`<title>`) | 설명(`description`) | H1 |
|------|------|------|-----|
| 한국 | `{ 지역 \| 한국 } { 카테고리 \| 즐길거리 } 추천 \| creatrip` | 크리에이트립에서 { 지역 \| 한국 } {카테고리} 상품과 리뷰를 한 눈에 비교하고 예약하세요! 한국 여행은 크리에이트립과 함께 준비하기 | `{ 지역 \| 한국 } { 카테고리 } 추천` |
| 영어 | `Best { 카테고리 \| Activities } In { 지역 \| Korea } \| creatrip` | Compare { 카테고리 \| Activities } in { 지역 \| Korea } along with real user reviews on creatrip, the leading Korea travel platform, and book easily today! | `{ 카테고리 \| Activities } in { 지역 \| Korea }` |
| 일본 | `{ 지역 \| 韓国 } { 카테고리 \| アクティビティ } 人気（おすすめ）\| creatrip` | 韓国旅行プラットフォーム「creatrip」で、{ 지역 \| 韓国 }の{ 카테고리 \| アクティビティ }商品と口コミを一目で比較して、簡単かつスピーディーに予約しましょう！ | `{ 지역 \| 韓国 } { 카테고리 \| アクティビティ }` |
| 대만(번체) | `{ 지역 \| 韓國 } { 카테고리 \| 玩樂體驗 } 推薦 \| creatrip` | 在韓國旅遊平台 creatrip 一目了然地比較 { 지역 \| 韓國 } { 카테고리 \| 玩樂體驗 } 商品與評價，輕鬆快速完成預訂！ | `{ 지역 \| 韓國 } { 카테고리 \| 玩樂體驗 }` |
| 홍콩(번체) | `{ 지역 \| 韓國 } { 카테고리 \| 玩樂體驗 } 推薦 \| creatrip` | 在韓國旅遊平台 creatrip 一目了然地比較 { 지역 \| 韓國 } { 카테고리 \| 玩樂體驗 } 商品與評價，輕鬆快速完成預訂！ | `{ 지역 \| 韓國 } { 카테고리 \| 玩樂體驗 }` |
| 중국(간체) | `{ 지역 \| 韩国 } { 카테고리 \| 玩乐体验 } 推荐 \| creatrip` | 在韩国旅游平台 creatrip 一目了然地比较 { 지역 \| 韩国 } { 카테고리 \| 玩乐体验 } 商品与评价，轻松快速完成预订！ | `{ 지역 \| 韩国 } { 카테고리 \| 玩乐体验 }` |
| 베트남 | `Top { 카테고리 \| Hoạt động } tại { 지역 \| Hàn Quốc } \| creatrip` | So sánh sản phẩm và đánh giá { 카테고리 \| Hoạt động } tại { 지역 \| Hàn Quốc } trong một nháy mắt trên nền tảng du lịch Hàn Quốc Creatrip và đặt chỗ dễ dàng, nhanh chóng! | `{ 지역 \| Hàn Quốc } { 카테고리 \| Hoạt động }` |
| 태국 | `{ 카테고리 \| กิจกรรม } { 지역 \| เกาหลี } แนะนำ \| creatrip` | เปรียบเทียบสินค้าและรีวิว { 카테고리 \| กิจกรรม } ใน { 지역 \| เกาหลี } ได้ในพริบตาบน Creatrip แพลตฟอร์มท่องเที่ยวเกาหลี พร้อมจองได้อย่างง่ายดายและรวดเร็ว! | `{ 지역 \| เกาหลี } { 카테고리 \| กิจกรรม }` |
| 프랑스 | `Réserver { 카테고리 \| Activités } à { 지역 \| Corée } \| creatrip` | Comparez les produits et les avis pour { 카테고리 \| Activités } à { 지역 \| Corée } en un coup d'œil sur Creatrip, la plateforme de voyage en Corée, et réservez facilement ! | `{ 카테고리 \| Activités } à { 지역 \| Corée }` |
| 스페인 | `Los mejores { 카테고리 \| Actividades } en { 지역 \| Corea } \| creatrip` | ¡Compare los mejores productos y reseñas de { 카테고리 \| Actividades } en { 지역 \| Corea } de un vistazo en Creatrip, la plataforma de viajes de Corea, y reserve de forma fácil! | `{ 카테고리 \| Actividades } en { 지역 \| Corea }` |
| 독일 | `Die besten { 카테고리 \| Aktivitäten } in { 지역 \| Korea } \| creatrip` | Vergleichen Sie Produkte und echte Bewertungen für { 카테고리 \| Aktivitäten } in { 지역 \| Korea } auf einen Blick auf Creatrip, der Korea-Reiseplattform, und buchen Sie jetzt einfach! | `{ 카테고리 \| Aktivitäten } in { 지역 \| Korea }` |
| 이탈리아 | `I migliori { 카테고리 \| Attività } a { 지역 \| Corea } \| creatrip` | Scopri e confronta i migliori prodotti e le recensioni per { 카테고리 \| Attività } a { 지역 \| Corea } in un colpo d'occhio su Creatrip, la piattaforma di viaggio in Corea, e prenota! | `{ 카테고리 \| Attività } a { 지역 \| Corea }` |
| 러시아 | `Лучшие { 카테고리 \| Развлечения } в { 지역 \| Корея } \| creatrip` | Сравнивайте товары и отзывы о { 카테고리 \| Развлечения } в { 지역 \| Корея } с первого взгляда на корейской туристической платформе Creatrip и бронируйте легко и быстро! | `{ 카테고리 \| Развлечения } в { 지역 \| Корея }` |
| 몽골 | `{ 지역 \| Солонгос }-ын шилдэг { 카테고리 \| Аяллын бүтээгдэхүүн } \| creatrip` | Солонгосын аяллын Creatrip платформоос { 지역 \| Солонгос }-ын { 카테고리 \| Аяллын бүтээгдэхүүн } бараа бүтээгдэхүүн, сэтгэгдлийг нэг дороос харьцуулж, хялбар бөгөөд хурдан захиалаарай! | `{ 지역 \| Солонгос }-ын { 카테고리 \| Аяллын бүтээгдэхүүн }` |
| 인도네시아 | `{ 카테고리 \| Aktivitas } Terbaik di { 지역 \| Korea } \| creatrip` | Bandingkan produk dan ulasan { 카테고리 \| Aktivitas } di { 지역 \| Korea } dalam sekejap di Creatrip, platform perjalanan Korea, lalu pesan dengan mudah dan cepat! | `{ 지역 \| Korea } { 카테고리 \| Aktivitas }` |

> 📌 원본 시트 정합성 처리 결과
> - **인도네시아 설명·H1 (확정)**: 원본의 카테고리 기본값 누락(`{ 카테고리 }`)과 `{ 지역 | korea}` 표기 불일치를 다른 어권과 통일해 `{ 카테고리 \| Aktivitas }`, `{ 지역 \| Korea }`로 보정 완료
> - **영어 카테고리 기본값 (확정)**: SEO 타이틀 예시 문구에만 `Travel Activities`로 적혀 있던 불일치를, 타이틀·H1·설명 전체 `Activities`로 통일 확정 (기본값 = `Activities`)
> - **설명 길이**: 어권별 설명 길이가 68~178자로 편차가 크고 일부는 검색결과 권장 노출 길이(약 150~160자)를 초과 → 초과분은 검색결과에서 말줄임 노출될 수 있음. 이번 건에서는 원본 유지, 카피 검수는 후속 처리

**조합별 치환 예시 (영어 어권 기준, 대카테고리=`Experiences`(352) / 중카테고리=`Outfit Rental`(359) / 지역=`Seoul`(22) 가정)**

| 대 | 중 | 지역 | 타이틀 예시 | H1 예시 | 필터 파라미터 |
|:--:|:--:|:--:|------|-----|------|
| X | X | X | Best Activities In Korea | Activities In Korea | (없음) |
| X | X | O | Best Activities In Seoul | Activities In Seoul | `region=22` |
| O | X | X | Best Experiences In Korea | Experiences In Korea | `category=352` |
| O | X | O | Best Experiences In Seoul | Experiences In Seoul | `category=352&region=22` |
| O | O | X | Best Outfit Rental In Korea | Outfit Rental In Korea | `category=352&middleCategory=359` |
| O | O | O | Best Outfit Rental In Seoul | Outfit Rental In Seoul | `category=352&middleCategory=359&region=22` |

- 중카테고리는 대카테고리가 선택된 경우에만 성립 → 유효 조합은 위 6가지 (지역 유무 2 × 카테고리 단계 3)
- `카테고리` 변수는 가장 하위 선택 단계값으로 치환 → 중 있으면 중, 없고 대만 있으면 대, 둘 다 없으면 기본값

**H1 노출 처리**

- `H1`은 페이지 최상위 문서 제목으로 마크업에 포함하되, 유저 화면에는 노출하지 않음(시각적 숨김) — 접근성 도구·크롤러는 인식, 시각 레이아웃에는 미표시
- 페이지당 `H1`은 1개만 존재하도록 보장, 기존에 다른 `H1`이 있으면 중복 방지

**캐노니컬(`<link rel="canonical">`)**

- 각 페이지의 캐노니컬은 **현재 어권 경로를 유지한 자기참조형 절대 URL**로 지정 (예: `https://creatrip.com/en/spot/list?...`)
- 캐노니컬 URL에는 **콘텐츠 정체성을 정의하는 필터 파라미터만 포함**하고, 정렬·페이지네이션 등 표현 파라미터는 제외
  - 포함: `category`, `middleCategory`, `region`
  - 제외: `order`, `direction`, `page` 및 기타 임시·추적 파라미터
- 파라미터 순서를 고정하여 동일 조합이 항상 동일 캐노니컬을 갖도록 정규화 (권장 순서: `category` → `middleCategory` → `region`)
  - 예: `/en/spot/list?page=2&order=MOST_VIEWED_IN_A_MONTH&direction=DESC&category=352&region=22` → 캐노니컬 `/en/spot/list?category=352&region=22`
- 지역·카테고리 미선택(기본) 페이지의 캐노니컬은 파라미터 없는 `/{locale}/spot/list`
- **페이지네이션 처리 (확정)**: `page`는 캐노니컬에서 제외하여, 2페이지 이후는 해당 필터 조합의 1페이지 대표 URL로 색인 신호를 통합. 정렬(`order`/`direction`)도 제외

**어권 간 대체 관계(`hreflang`)**

- 각 페이지 `<head>`에, 동일 필터 조합의 **모든 어권 버전을 서로 가리키는 `<link rel="alternate" hreflang="...">` 태그를 나열** — 17개 어권 전부 + `x-default` 1개
- `hreflang` 값은 어권별 언어 코드로 지정 (예: 한국=`ko`, 영어=`en`, 일본=`ja`, 간체=`zh-CN`, 태국=`th` 등). **대만·홍콩은 동일 번체(`zh-TW`) 페이지를 공유**하므로 하나의 번체 대체로 처리
  - 어권별 언어 코드는 사이트의 기존 다국어 라우팅(로케일 경로) 규칙을 그대로 따름 — 실제 코드 매핑은 라우팅 정의 기준으로 확정 (TBD 확인)
- `x-default`는 언어 미지정 유저용 기본 버전을 가리킴 (기본 = 영어 페이지, 최종 확정 필요 TBD)
- `alternate` 대상 URL은 **캐노니컬과 동일한 정규화 규칙**을 적용 — 어권 경로만 다르고 필터 파라미터(`category`/`middleCategory`/`region`)·순서는 동일, 정렬·페이지 파라미터는 제외
- 어권 간 링크는 **상호(양방향)로 일치**해야 하며(A가 B를 가리키면 B도 A를 가리킴), 한 조합의 대체 목록에는 자기 자신을 포함한 전 어권이 빠짐없이 들어가도록 보장
- 특정 어권 페이지가 존재하지 않는 조합에서는 그 어권을 대체 목록에서 제외 (없는 URL을 가리키지 않음)

### 백엔드 요구사항

- 변수 치환에 필요한 **어권별 표시명 데이터 제공**
  - 지역명: 선택된 `region` 값에 대응하는 어권별 지역 표시명 (지역 도메인 데이터 연동)
  - 카테고리명: 선택된 대/중카테고리(`category`/`middleCategory`)에 대응하는 어권별 표시명
- 표시명 누락 시 처리 규칙 (TBD): 특정 어권 표시명이 없을 때 기본값 또는 대체 어권으로 폴백할지 정의
- 메타·캐노니컬 생성 로직 자체는 렌더링 단계에서 처리 가능하여, 스팟 리스트 조회 API의 엔드포인트·응답 스키마 변경은 원칙적으로 없음 (표시명 데이터가 기존 응답에 포함되어 있지 않은 경우에 한해 필드 보강 필요)
