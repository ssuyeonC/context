# Google Actions Center — 쿠폰 연동 랜딩페이지 정합성 커뮤니케이션

작성일: 2026-08-19
상대: Momo (Google Actions Center)
담당: Suyeon (Creatrip)
주제: Actions Center Offers 연동 — 랜딩페이지 이용 조건(최소 주문금액 등) 노출 정책 준수

---

## 배경 / 쟁점

- 구글 Actions Center Offers 연동 진행 중. 온/오프라인 쿠폰 플로우 영상 공유 완료.
- 구글 통합 정책상 랜딩페이지는 각 오퍼의 **이용 자격/조건**(user segment, 결제수단, 요일·시간, **최소 주문금액**, 사용 횟수, 식사 종류(런치/디너), 코스 제한, 구독 요건 등)을 **명확·전면적으로(clearly and comprehensively)** 노출해야 함.
  - 정책 링크: https://developers.google.com/actions-center/verticals/offers/policies/integration-policies
- Momo 측 지적: **최소 주문금액(min spend)이 랜딩페이지에 노출되지 않는다.** 상세페이지엔 있으나 랜딩페이지엔 없음.
- Creatrip 입장: 조건은 랜딩페이지 **설명 텍스트 안에** 이미 기술돼 있음(예: "…and free tea or coffee with coupon on orders over 20,000 won"). 다만 별도 전용 영역으로 부각돼 있진 않음.
- **미해결 쟁점**: 설명 텍스트 내 기술로 충분한지, 아니면 별도 전용 영역으로 가시성을 강화해야 통과되는지. + 조건이 아예 없는 오퍼는 "조건 없음"을 명시해야 하는지 생략 가능한지.

## 현재 상태 (2026-09-04)

- 7/31 발신 → Momo 무응답(약 3주) → 8/19 Suyeon 후속(명확화) 메일 발송. **위치/포맷/조건 없음 케이스 확정 요청.**
- 8/19 발송 직후 Momo **OOO 자동응답**(8/24 복귀 예정, 복귀 후 순차 대응) 수신.
- 2026-09-02, Momo 복귀(8/24) 후 9일 무응답 → Suyeon **팔로업(bump) 메일 발송.**
- 2026-09-04, Momo 회신 — 랜딩페이지 3종엔 답 없이 **화제 전환: "deal 부서가 food/appointment와 siloed냐"** 질의. → **계정 프로비저닝(신규 Offers 계정 생성 중) 맥락으로 해석.**
  - Creatrip 측 사실: Actions Center 계정이 버티컬별로 분리(**Creatrip TTD / Creatrip Appointments / Creatrip Inc.**), action별 role-based 접근. 조직상 제휴팀 내 카테고리 담당자 분리(뷰티=A, 식당=B).
  - **미확정 쟁점**: Offers가 별도 계정이어야 하는지 vs 기존 버티컬(예: Dining Reserve)에 붙일 수 있는지. 공식 문서상 Offers는 Dining/Food/Shopping 버티컬의 "옵션"으로 등장 → 별도 silo가 아닐 가능성. **Momo에게 계정 구조 역질문 발송 완료(9/4), 회신 대기 중.**

---

## 메일 스레드 (시간순)

### 1. Suyeon → Momo (담당자 인계, 서면 소통 요청)

> Hi Momo,
>
> Welcome back — I hope you had a great break.
> I'm Suyeon from Creatrip and I'll be your point of contact on our side going forward.
>
> Thank you for suggesting a call.
> If it's alright with you, I'd prefer to keep our communication in writing — it helps us keep a clear record on both sides and makes it easier to loop in the relevant people internally.
>
> To that end, would you mind sharing in writing whatever you'd planned to cover on the call? In particular, it would help to know:
>
> - Whether you were able to access the online and offline coupon flow videos we shared
> - The remaining steps needed to complete the integration, and what you need from our side for each
>
> I'll respond promptly so we can keep this moving. Looking forward to hearing from you.
>
> Best regards,
> Suyeon

### 2. Momo → Suyeon (최소 주문금액 랜딩 미노출 지적)

> Hi Suyeon,
>
> I have consulted with our tech team regarding your landing pages.
> They said that overall looks good. The main problem they see is:
>
> https://developers.google.com/actions-center/verticals/offers/policies/integration-policies
>
> Landing pages must clearly and comprehensively outline the eligibility requirements for each offer. This includes restrictions related to user segments, payment methods, specific days or times, minimum spending amounts, the number of times the offer can be used, type of meals (lunch/dinner), limitation to certain courses, and requirement for any subscription.
>
> The problem is that right now there is no minimum spending amounts on the landing page.
>
> (image.png)
>
> Could you please confirm if this understanding is correct?
>
> Best,
> Momo

### 3. Suyeon → Momo (2026-07-29, 조건 노출 방식 설명 + 조건 없는 오퍼 질의)

> Hi Momo,
>
> Thank you for the detailed feedback on our landing pages.
>
> I'd like to clarify how we currently handle coupon usage restrictions:
>
> When an offer has specific restrictions (e.g., a minimum spending amount), those conditions are clearly displayed on the coupon's detail page. For example, the attached landing page shows "a Free Americano for Creatrip members who spend over ₩10,000" — the minimum spend requirement is stated directly on the page. (Image attached; live URL to follow: https://creatrip.com/en/spot/8211)
>
> (스크린샷 2026-07-29 오후 4.35.16.png)
>
> When an offer has no restrictions, the "coupon usage restrictions" section is simply not shown, since there are no conditions to communicate.
>
> Our question: Even when an offer has no restrictions, is a "coupon usage restrictions" section still required to appear on the landing page (e.g., explicitly stating that there are none)? Or is it acceptable to omit the section entirely when there are no applicable conditions?
>
> We want to make sure our implementation fully complies with the integration policies.
>
> Thank you,
> Suyeon

### 4. Momo → Suyeon (특정 딜 재지적 — 랜딩에 보이게 해달라)

> Hi Suyeon,
>
> Could you please check the deal below? It does not have the minimum spend on the landing page but we see it in the details page. We need these condition to be visible on the landing page.
>
> (image.png / image.png)
>
> Best,
> Momo

### 5. Suyeon → Momo (2026-07-31, 설명 텍스트 내 기술돼 있음 + 위치/포맷 역질의)

> Hi Momo,
>
> Thanks for flagging this — I looked into the deal you mentioned.
>
> The minimum spend condition is actually shown on the landing page too. You can see it in the deal description text ("…and free tea or coffee with coupon on orders over 20,000 won"). I've attached a screenshot with the relevant part highlighted so it's easy to spot.
>
> That said, I want to make sure we're aligned on where you'd like this to appear. If you need the minimum spend to be surfaced in a more prominent/dedicated spot on the landing page (rather than within the description text), just let me know the exact position and format you have in mind, and I'll get it adjusted on our side.
>
> Best,
> Suyeon
>
> (스크린샷 2026-07-31 오후 2.35.12.png)

### 6. Suyeon → Momo (2026-08-19, 후속 — 발송 완료)

> Subject: Re: Coupon integration — confirming landing page eligibility display
>
> Dear Momo,
>
> I hope you're doing well. I'm writing to follow up on my note from July 31.
>
> I'd like to make sure I understand the requirement correctly. The condition is already stated on the landing page (within the description text), so my question is whether it needs to be reworked into a **more visible, dedicated format** in order to pass review — would that be the right understanding?
>
> If so, we're planning to add a dedicated, clearly-labeled "Coupon conditions" section that lists each applicable restriction (minimum spend, valid days/times, usage limit, and so on) as its own line, independent of the description text. Before we implement, it would help to confirm a few points: whether there's a required position on the page (e.g. near the offer CTA) or anywhere clearly visible is fine; which restriction types we should always render when applicable; and how to handle offers with no conditions — should the section still appear with a "no conditions apply" note, or may we omit it entirely?
>
> If you happen to have an approved landing page example or a checklist we could model against, that would be the most reliable way for us to match your expectations. Once you confirm the above, we'll implement the changes and share the updated pages for your review.
>
> Thank you very much for your help.
>
> Best regards,
> Suyeon

### 7. Momo → Suyeon (OOO 자동응답, 8/19 발송 직후)

> Hi,
>
> I'm out of office. I will have limited access to email during this time. (Returning on the 24th of August)
>
> 2026年8月24日まで不在にしております。その期間いただいたメールは、出社次第順次対応させて頂きます。
>
> For enquiries on Hotel Ads and free booking links, please use the "Contact Us" form in the Help Center.
>
> Cheers,
> Momo

- 자동응답 하단 Hotel Ads/free booking links 안내는 범용 서명 푸터 → Offers 건과 무관.

### 8. Suyeon → Momo (2026-09-02, 팔로업 bump — 발송 완료)

> Subject: Re: Coupon integration — confirming landing page eligibility display
>
> Hi Momo,
>
> Following up on my note from August 19. Could you confirm three points so we can implement the dedicated "Coupon conditions" section and share the updated pages for review?
>
> 1. **Position** — a required placement (e.g. near the offer CTA), or anywhere clearly visible?
> 2. **Fields** — which restrictions should we always render (minimum spend, valid days/times, usage limit, etc.)?
> 3. **No-condition offers** — show the section with a "no conditions apply" note, or omit it entirely?
>
> An approved example or checklist would help too, if you have one.
>
> Best,
> Suyeon

### 9. Momo → Suyeon (2026-09-04, 부서 siloing 질의 — 화제 전환)

> Sorry for the delay.
>
> Could you please confirm
> - Is your deal departement siloed from the food/appointment departement ?
> - Is your food departement siloed from the appointment departement ?
>
> Best,
> Momo

- 랜딩페이지 3종(위치/항목/조건없음)엔 **미답변**. 화제를 계정/부서 구조로 전환.
- 첨부(Actions Center 계정 스위처): **Creatrip (TTD) / Creatrip Appointments / Creatrip Inc.** 3개 계정 확인 → 버티컬별 계정 분리 상태.
- 해석: 신규 Offers 계정 생성 절차 중 발생한 질의 → Offers를 별도 silo로 팔지, 기존 버티컬에 묶을지 확인 목적으로 추정.

### 10. Suyeon → Momo (2026-09-04, 우리 구조 전달 + 계정 구조 역질문 — 발송 완료)

> Hi Momo,
>
> No worries, and thanks for getting back to me.
>
> To give you the picture on our side: each of our existing verticals runs under its own separate Actions Center account — **Creatrip (TTD)**, **Creatrip Appointments**, and our Dining Reserve setup — with role-based access per action, so food and appointments are managed independently.
>
> For the deal/Offers integration, we're still in the process of setting up the account, so this is a good moment to align on structure. Our understanding was that each action typically requires its own account — but could you confirm how Offers should be set up? Specifically:
> - Should Offers have its own dedicated account, or can/should it be attached to an existing vertical (e.g. our Dining Reserve account)?
> - If it shares an account, is that what you mean by the deal/food/appointment departments being "siloed" — i.e. are you checking whether they can be combined or must stay separate?
>
> Once we're aligned on the account structure, I'd also like to close out the landing-page eligibility point from my earlier notes (position, required fields, and how to handle no-condition offers) so we can implement. Happy to proceed however you recommend.
>
> Best,
> Suyeon

### 11. Momo → Suyeon (2026-09-09, 예약 계정에 Offers 부착 제안)

> Hi Suyeon,
>
> We are trying to determine how to set up your deals account. Can we add this deals and promotions features to the account that handles the reservation?
>
> Best,
> Momo

- 9/4 계정 구조 역질문에 대한 답 → **구글도 별도 silo 안 만들고 기존 예약 계정(Dining Reserve)에 Offers 부착하는 방향 제안.** 우리 추정("Offers는 Dining/Food/Shopping의 옵션 → 별도 silo 아닐 가능성")과 일치. 신규 계정 프로비저닝 불필요 → 진행 간소화.

### 12. Suyeon → Momo (2026-09-09, 부착 동의 + 카테고리 범위 1점 확인 — 발송 완료)

> Hi Momo,
>
> Thanks — that works for us, and it's simpler than spinning up a separate account.
>
> One quick check before we confirm, since our Offers aren't limited to dining: if deals & promotions are added to our reservation (Dining Reserve) account, can we register offers across all our categories (e.g. beauty as well as restaurants), or would offers on that account be scoped to dining only?
>
> If it covers all categories, please go ahead and add it to the reservation account.
>
> Best,
> Suyeon

- 접근 권한(role-based) 건은 **우리 내부에서 Dining Reserve 계정에 인원 추가로 해결 가능** → 구글에 안 물음.
- 랜딩페이지 3문항은 **이번 메일에서 의도적으로 제외**(저쪽이 현재 문제 삼지 않음, 계정 건에 집중해 빠른 회신 유도). 단 "해결"이 아니라 "미답변·잠복" 상태 → 검수 단계 전 우리가 먼저 클로징하도록 트래킹 유지.

### 13. Momo → Suyeon (2026-09-09, 계정 셋업 착수 + 단계적 런칭 + 오퍼 전체 공유 요청)

> Thank you! I have forwarded your account details to our setup team.
>
> We plan to launch Food and Local Shopping first, but we will also support Beauty and other offer categories in the future. It would be great if you could share all of your available offers so we are ready to launch as additional categories become available.
>
> The relevant team will reach out to you once the account setup is complete, which usually takes 1 to 2 weeks.
>
> Best,
> Momo

- **계정 구조 트랙 마무리** — 우리 계정 정보 셋업팀 전달. **셋업 1~2주 소요**, 완료 시 담당팀이 연락.
- **카테고리 답 = 전 카테고리 지원(단계적)** — 런칭 순서 **Food + Local Shopping 먼저**, **Beauty 등 나머지 이후 순차**. dining 한정 우려 해소.
- **요청**: 카테고리 오픈 시 즉시 런칭 가능하도록 **가용 오퍼 전체 미리 공유**.

### 14. Suyeon → Momo (2026-09-09, 단계적 런칭 확인 + 오퍼 공유 포맷/채널 역질의 — 발송 완료)

> Hi Momo,
>
> Thanks for the update — good to hear the setup is underway.
>
> Understood on the phased rollout: Food and Local Shopping first, with Beauty and other categories to follow. We'll prepare our full offer inventory across all categories so we're ready as each one becomes available.
>
> Could you let us know how you'd like us to share the offers — a specific feed/template format, or directly through the account once access is provisioned? And if there's anything category-specific you need for the Food and Local Shopping launch, happy to line that up.
>
> Best,
> Suyeon

---

## 다음 액션

- [ ] **계정 셋업 대기 (~1~2주, ≈2026-09-23 전후)** — 완료 시 구글 담당팀이 연락 예정. 별도 계정 생성 불필요 / 예약(Dining Reserve) 계정에 deals & promotions 부착으로 확정.
- [ ] **Momo 회신 대기 (9/9 오퍼 공유 포맷/채널 질의 발송 완료)** — 확정 목표:
  1. 오퍼 공유 방식 = 별도 피드/템플릿 vs 계정 프로비저닝 후 계정 직접 업로드
  2. Food/Local Shopping 런칭에 카테고리별 별도 요구사항 유무
- [ ] **우리 쪽 준비: 전 카테고리 오퍼 인벤토리 정리** (Food/Local Shopping 우선, Beauty 등 순차 대비 전체 포함) → 포맷 확정 시 공유
- [ ] (부착 후, 필요 시 뷰티 등 담당자 role-based 접근 권한 우리 쪽에서 추가)
- [ ] **랜딩페이지 3종 — 여전히 미해결(잠복), 검수 전 우리가 먼저 클로징**:
  1. 노출 위치 (CTA 인근 / 상단 등 지정 여부)
  2. 항상 렌더해야 하는 조건 항목 범위
  3. 조건 없는 오퍼 처리 ("조건 없음" 명시 vs 생략)
- [ ] 확정 시 랜딩페이지 전용 "Coupon conditions" 영역 구현 → 구글 검수용 페이지 공유
