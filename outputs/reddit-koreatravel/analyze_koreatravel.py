#!/usr/bin/env python3
"""
r/koreatravel 크롤링 데이터 분석
- title, description 교차 분석
- 주된 담론(토픽) 추출
- 한국 여행 관련 주된 니즈/요청 분류
출력:
  data/analysis_summary.json  (수치 요약)
  data/theme_breakdown.csv    (테마별 게시물 수/비율)
  data/top_terms.csv          (상위 키워드/바이그램)
콘솔: 핵심 지표 출력
"""
import csv
import json
import re
import sys
from collections import Counter, defaultdict

CSV_PATH = "data/koreatravel_posts.csv"
csv.field_size_limit(10_000_000)

STOPWORDS = set("""
a an the and or but if then else of to in on at for with without from by as is are was were be been being
do does did doing have has had having i you he she it we they them this that these those my your our their his her its
me us him will would can could should shall may might must not no nor so than too very just about into out up down over under
again further once here there all any both each few more most other some such only own same s t don will now what which who whom
whose when where why how been being get got go going gone went will im ive id dont doesnt cant wont thats theres youre were
also really know like want need help thanks thank pls please any anyone someone something anything ll re ve m d o
korea korean koreas
""".split())

# 한국 여행 도메인 테마 사전 (키워드 → 테마)
THEMES = {
    "Visa & Entry / K-ETA": ["visa", "k-eta", "keta", "eta", "immigration", "arrival card",
                              "passport", "entry", "customs", "e-arrival", "qcode", "q-code"],
    "Itinerary & Trip Planning": ["itinerary", "plan", "planning", "days", "day trip", "schedule",
                                   "route", "first time", "week", "weeks", "trip", "itineraries"],
    "Transport & Getting Around": ["subway", "metro", "ktx", "train", "bus", "taxi", "uber", "kakao",
                                    "t-money", "tmoney", "transport", "transportation", "airport",
                                    "incheon", "gimpo", "rail", "car", "drive", "driving", "ferry"],
    "Accommodation": ["hotel", "hostel", "airbnb", "guesthouse", "stay", "accommodation", "lodging",
                       "where to stay", "booking", "neighborhood", "area to stay", "hanok"],
    "Money / Budget / Cash & Cards": ["money", "cash", "card", "won", "krw", "exchange", "budget",
                                       "atm", "wow card", "wowpass", "wow pass", "trazel", "fee",
                                       "currency", "payment", "pay", "cost", "expensive", "cheap"],
    "SIM / eSIM / Connectivity": ["sim", "esim", "e-sim", "wifi", "wi-fi", "data", "internet",
                                   "phone", "roaming", "pocket wifi", "mobile"],
    "Food & Dining": ["food", "eat", "restaurant", "vegetarian", "vegan", "halal", "bbq", "cafe",
                       "dining", "meal", "street food", "michelin", "allergy", "gluten"],
    "Weather & Season / Packing": ["weather", "winter", "summer", "spring", "fall", "autumn",
                                    "cherry blossom", "rain", "monsoon", "snow", "cold", "hot",
                                    "pack", "packing", "clothes", "temperature", "season"],
    "K-pop / Concerts / Fan": ["kpop", "k-pop", "concert", "bts", "blackpink", "stray kids", "seventeen",
                                "fanmeeting", "fan", "album", "hybe", "sm", "twice", "music show",
                                "idol", "ticket", "lightstick"],
    "Language & Communication": ["language", "english", "speak", "translate", "papago", "korean language",
                                  "hangul", "communicate", "phrase"],
    "Shopping & Cosmetics": ["shopping", "shop", "buy", "skincare", "cosmetics", "makeup", "olive young",
                              "duty free", "souvenir", "myeongdong", "mall", "tax refund"],
    "Destinations - Seoul": ["seoul", "hongdae", "myeongdong", "gangnam", "itaewon", "insadong",
                              "dongdaemun", "namsan", "bukchon"],
    "Destinations - Jeju": ["jeju"],
    "Destinations - Busan": ["busan", "haeundae"],
    "Other Cities & Regions": ["gyeongju", "sokcho", "gangwon", "jeonju", "daegu", "incheon city",
                                "andong", "yeosu", "nami", "dmz", "everland", "lotte world"],
    "Safety / Solo / Etiquette": ["safe", "safety", "solo", "alone", "scam", "etiquette", "respectful",
                                   "culture", "tip", "tipping", "lgbt", "female"],
    "Medical / Health / Insurance": ["insurance", "hospital", "medical", "medicine", "pharmacy",
                                      "doctor", "sick", "covid", "health"],
    "Luggage / Storage": ["luggage", "storage", "locker", "suitcase", "delivery", "baggage"],
    "Tours & Activities / Experiences": ["tour", "guide", "activity", "experience", "hanbok", "templestay",
                                          "hiking", "palace", "spa", "jjimjilbang", "show", "theme park"],
}

# 요청/니즈 신호 (질문/요청형 게시물 판별)
NEED_SIGNALS = ["recommend", "recommendation", "suggest", "advice", "help", "looking for",
                "where", "how", "what", "which", "best", "should i", "any tips", "is it",
                "can i", "worth", "?"]

TOKEN_RE = re.compile(r"[a-z][a-z\-']+")


def tokenize(text):
    return [t for t in TOKEN_RE.findall(text.lower())
            if t not in STOPWORDS and len(t) > 2]


def load_rows():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def classify_themes(text):
    hits = []
    low = text.lower()
    for theme, kws in THEMES.items():
        for kw in kws:
            if kw in low:
                hits.append(theme)
                break
    return hits


def main():
    rows = load_rows()
    n = len(rows)
    if n == 0:
        print("데이터 없음", file=sys.stderr)
        sys.exit(1)

    # 기본 통계
    dates = [r["created_iso"][:10] for r in rows if r.get("created_iso")]
    dates_sorted = sorted(d for d in dates if d)
    has_desc = sum(1 for r in rows if r.get("description", "").strip()
                   and r["description"].strip().lower() not in ("[removed]", "[deleted]"))
    scores = [int(r["score"]) for r in rows if str(r.get("score", "")).lstrip("-").isdigit()]
    comments = [int(r["num_comments"]) for r in rows
                if str(r.get("num_comments", "")).isdigit()]

    # 키워드/바이그램 (title vs description 분리)
    title_tokens, desc_tokens = [], []
    title_bigrams, desc_bigrams = Counter(), Counter()
    for r in rows:
        tt = tokenize(r.get("title", ""))
        dd = tokenize(r.get("description", ""))
        title_tokens += tt
        desc_tokens += dd
        for i in range(len(tt) - 1):
            title_bigrams[tt[i] + " " + tt[i + 1]] += 1
        for i in range(len(dd) - 1):
            desc_bigrams[dd[i] + " " + dd[i + 1]] += 1
    title_freq = Counter(title_tokens)
    desc_freq = Counter(desc_tokens)

    # 테마 분류 (title+description 결합)
    theme_counts = Counter()
    theme_in_title = Counter()
    theme_in_desc = Counter()
    cooccur = Counter()
    for r in rows:
        title = r.get("title", "")
        desc = r.get("description", "")
        th_all = set(classify_themes(title + " " + desc))
        th_t = set(classify_themes(title))
        th_d = set(classify_themes(desc))
        for th in th_all:
            theme_counts[th] += 1
        for th in th_t:
            theme_in_title[th] += 1
        for th in th_d:
            theme_in_desc[th] += 1
        for a in th_all:
            for b in th_all:
                if a < b:
                    cooccur[(a, b)] += 1

    # 니즈/요청형 게시물 비율
    need_posts = 0
    for r in rows:
        blob = (r.get("title", "") + " " + r.get("description", "")).lower()
        if any(sig in blob for sig in NEED_SIGNALS):
            need_posts += 1

    # title↔description 교차: 제목에만/본문에만 강하게 나타나는 용어
    cross = []
    vocab = set(list(title_freq) + list(desc_freq))
    for w in vocab:
        tf = title_freq.get(w, 0)
        df = desc_freq.get(w, 0)
        if tf + df >= 40:
            ratio = (tf + 1) / (df + 1)
            cross.append((w, tf, df, round(ratio, 2)))
    title_skewed = sorted(cross, key=lambda x: -x[3])[:25]
    desc_skewed = sorted(cross, key=lambda x: x[3])[:25]

    # 저장: 요약 JSON
    summary = {
        "total_posts": n,
        "date_range": {"from": dates_sorted[0] if dates_sorted else None,
                       "to": dates_sorted[-1] if dates_sorted else None},
        "posts_with_description": has_desc,
        "pct_with_description": round(100 * has_desc / n, 1),
        "need_request_posts": need_posts,
        "pct_need_request": round(100 * need_posts / n, 1),
        "score_stats": {"mean": round(sum(scores) / len(scores), 1) if scores else None,
                        "max": max(scores) if scores else None},
        "comment_stats": {"mean": round(sum(comments) / len(comments), 1) if comments else None,
                          "max": max(comments) if comments else None},
        "theme_counts": theme_counts.most_common(),
        "theme_in_title": dict(theme_in_title),
        "theme_in_description": dict(theme_in_desc),
        "top_theme_cooccurrence": [
            {"pair": f"{a} + {b}", "count": c}
            for (a, b), c in cooccur.most_common(15)],
        "top_title_terms": title_freq.most_common(40),
        "top_desc_terms": desc_freq.most_common(40),
        "top_title_bigrams": title_bigrams.most_common(30),
        "top_desc_bigrams": desc_bigrams.most_common(30),
        "title_skewed_terms": title_skewed,
        "desc_skewed_terms": desc_skewed,
    }
    with open("data/analysis_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # 저장: 테마 분해 CSV
    with open("data/theme_breakdown.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["theme", "posts", "pct_of_all", "in_title", "in_description"])
        for th, c in theme_counts.most_common():
            w.writerow([th, c, round(100 * c / n, 1),
                        theme_in_title.get(th, 0), theme_in_desc.get(th, 0)])

    # 저장: 상위 용어 CSV
    with open("data/top_terms.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["scope", "term", "count"])
        for t, c in title_freq.most_common(60):
            w.writerow(["title_unigram", t, c])
        for t, c in desc_freq.most_common(60):
            w.writerow(["desc_unigram", t, c])
        for t, c in title_bigrams.most_common(40):
            w.writerow(["title_bigram", t, c])
        for t, c in desc_bigrams.most_common(40):
            w.writerow(["desc_bigram", t, c])

    # 콘솔 요약
    print(f"총 게시물: {n}")
    print(f"기간: {summary['date_range']['from']} ~ {summary['date_range']['to']}")
    print(f"본문 보유: {has_desc} ({summary['pct_with_description']}%)")
    print(f"니즈/요청형: {need_posts} ({summary['pct_need_request']}%)")
    print("\n[테마별 상위]")
    for th, c in theme_counts.most_common(12):
        print(f"  {th}: {c} ({round(100*c/n,1)}%)")
    print("\n[제목 상위 바이그램]")
    for t, c in title_bigrams.most_common(15):
        print(f"  {t}: {c}")
    print("\n[테마 동시출현 상위]")
    for (a, b), c in cooccur.most_common(8):
        print(f"  {a} + {b}: {c}")


if __name__ == "__main__":
    main()
