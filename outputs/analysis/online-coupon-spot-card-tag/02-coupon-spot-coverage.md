# 02. 태그 노출 대상 스팟 규모·분포·추이

## 목적

태그가 실제로 **몇 개 스팟·어떤 상품군에 붙는지**, 그리고 시간이 지나며(관공서 수주 확대) **얼마나 늘어나는지**를 파악한다. 효과(01)를 해석할 때 "모수가 8개뿐이라 작다 / 점점 커진다" 같은 맥락을 제공한다.

## 핵심 질문

1. 현재 태그 노출 대상 스팟은 몇 개이고, 어떤 카테고리/지역에 몰려 있는가?
2. 노출 대상이 시간에 따라 증가하는가? (신규 온라인 쿠폰 연결·노출 추이)
3. '활성 쿠폰 연결(1,001개)' 대비 '활성+노출(8개)' 격차 — 노출 OFF로 빠지는 쿠폰이 얼마나 되나?

## 지표 정의

- 태그 노출 대상 스팟 수 = 활성+노출 쿠폰이 1개 이상 연결 + 뷰티 캐시백 OFF
- 노출 누락분 = 활성 쿠폰 연결 스팟 − 활성+노출 쿠폰 연결 스팟 (자동 노출만 켜면 태그가 붙을 잠재 대상)

## 방법 (DB 집계, 시점별 스냅샷)

### 현재 규모 (3종)

```sql
-- 활성 쿠폰 연결 스팟
SELECT COUNT(DISTINCT d.linked_domain_id)
FROM online_coupon_has_linked_domain d
JOIN online_coupon c ON c.id = d.online_coupon_id
WHERE d.linked_domain_type='SPOT' AND c.is_active=1;

-- 활성+노출(=태그 잠재 대상, 뷰티캐시백 무시)
SELECT COUNT(DISTINCT d.linked_domain_id)
FROM online_coupon_has_linked_domain d
JOIN online_coupon c ON c.id = d.online_coupon_id
WHERE d.linked_domain_type='SPOT' AND c.is_active=1 AND c.is_exposed=1;

-- 최종 태그 노출 대상(뷰티 캐시백 OFF까지)
SELECT COUNT(DISTINCT s.code)
FROM spot s
JOIN online_coupon_has_linked_domain d ON d.linked_domain_id=s.code AND d.linked_domain_type='SPOT'
JOIN online_coupon c ON c.id=d.online_coupon_id AND c.is_active=1 AND c.is_exposed=1
WHERE s.is_beauty_cash_back=0;
```

### 카테고리/지역 분포

- 위 대상 스팟을 스팟의 카테고리·지역 속성으로 group by 하여 쏠림 확인.

### 추이

- `online_coupon.created_at` / `online_coupon_has_linked_domain` 생성 시점 기준으로, 월별 신규 노출 쿠폰·연결 스팟 증가 추이.
- 관공서 수주 배치가 있으면 배치 단위(쿠폰명·매니저)로도 끊어 본다. (예: 현재 14840에 연결된 `EPOS会員様限定クーポン` 류처럼 묶음으로 들어오는 패턴)

## 산출물

- 규모 3종 스냅샷 표 (활성 / 활성+노출 / 최종 대상)
- 카테고리·지역 분포 표
- 월별 증가 추이 라인

## 주의

- 현재 알려진 값(2026-06-01): 활성 1,001 / 활성+노출 8 / 최종 대상 ≈ 8. **노출 OFF로 빠지는 양이 매우 큼** → "자동 노출을 켜는 운영 동작"이 태그 노출의 실질 병목일 수 있음(어드민 안내 문구가 여기에 기여).

---

## 측정 결과 (2026-06-01 기준)

### 규모 3종 (DB)

| 구분 | 스팟 수 |
|---|---|
| 활성 쿠폰 연결 (`is_active=1`) | **1,001** |
| 활성+노출 (`is_active=1 AND is_exposed=1`) | **8** |
| 최종 태그 노출 대상 (위 + 뷰티캐시백 OFF) | **8** |

- **활성 1,001 → 노출 8**의 격차가 핵심. 연결은 많지만 '자동 노출'이 켜진 건 극소수 → 태그가 실제로 붙으려면 운영이 자동 노출을 켜야 한다. (어드민 안내 문구의 의의)

### 분포 — 현재 대상은 단일 캠페인

- 8개 전부 **"부산 PICK! 웰니스 할인 쿠폰"**(쿠폰 id 1876–1879, 정액 $35 USD 등 언어별 변형) 1건에 묶임.
- 카테고리: **체험 7 / 메디컬 1**, 전부 부산 웰니스 테마.
- 즉 현재 "온라인 쿠폰 태그 대상"은 **사실상 1개 캠페인 = 8개 스팟**. 분포 분석은 캠페인이 늘어난 뒤 의미가 커진다.

### 추이 — 캠페인 도입 시점

- 쿠폰 생성·노출: **2026-05-19**, 발급기간 2026-05-26 ~ 10-31.
- 8개 스팟에 쿠폰(1876–1879) 연결: 대부분 **2026-05-19 ~ 05-30**에 집중(일부 스팟은 과거 다른 쿠폰 연결 이력 있으나, 현재 활성+노출 쿠폰은 이 캠페인이 유일).
- 결론: **노출 대상 스팟의 추이 = 캠페인 추가 추이**. 다음 관공서/지자체 수주가 들어오면 같은 쿼리로 재집계해 증가를 추적한다.
