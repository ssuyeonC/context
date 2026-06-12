#!/usr/bin/env python3
"""
'지역(목적지)' 테마 게시물 심층 분석
- 목적지 테마(서울/부산/제주/기타 도시·지역)로 분류된 게시물만 필터링
- 그 안에서: 세부 지명 빈도, 동반 주제(니즈), 요청 유형, title vs description
출력:
  data/region_summary.json
  data/region_place_freq.csv
  data/region_subtopic.csv
콘솔: 핵심 지표
"""
import csv
import json
import re
from collections import Counter, defaultdict

CSV_PATH = "data/koreatravel_posts.csv"
csv.field_size_limit(10_000_000)

# --- 목적지 테마 판별용 (원 분석과 동일 기준) ---
DESTINATION_KWS = [
    # Seoul cluster
    "seoul", "hongdae", "myeongdong", "gangnam", "itaewon", "insadong",
    "dongdaemun", "namsan", "bukchon",
    # Jeju
    "jeju",
    # Busan
    "busan", "haeundae",
    # Other cities & regions
    "gyeongju", "sokcho", "gangwon", "jeonju", "daegu", "andong", "yeosu",
    "nami", "dmz", "everland", "lotte world",
]

# --- 세부 지명 사전 (region/도시/동네/명소) → 표준 라벨 ---
PLACES = {
    # --- 광역/도시 ---
    "Seoul": ["seoul"],
    "Busan": ["busan"],
    "Jeju": ["jeju"],
    "Incheon (city)": ["incheon city", "songdo"],
    "Daegu": ["daegu"],
    "Gyeongju": ["gyeongju"],
    "Jeonju": ["jeonju"],
    "Sokcho": ["sokcho"],
    "Gangneung": ["gangneung", "gangwon"],
    "Andong": ["andong"],
    "Yeosu": ["yeosu"],
    "Suwon": ["suwon"],
    "Chuncheon/Nami": ["chuncheon", "nami island", "nami"],
    "Pyeongchang": ["pyeongchang"],
    "Tongyeong": ["tongyeong"],
    # --- 서울 내 동네/명소 ---
    "Myeongdong": ["myeongdong"],
    "Hongdae": ["hongdae"],
    "Gangnam": ["gangnam"],
    "Itaewon": ["itaewon"],
    "Insadong": ["insadong"],
    "Dongdaemun": ["dongdaemun"],
    "Bukchon Hanok": ["bukchon"],
    "Namsan/N Seoul Tower": ["namsan", "n seoul tower", "seoul tower"],
    "Gyeongbokgung/Palaces": ["gyeongbokgung", "changdeokgung", "palace"],
    "Seongsu": ["seongsu"],
    "Ikseondong": ["ikseondong"],
    "Gwangjang Market": ["gwangjang"],
    # --- 부산 내 ---
    "Haeundae": ["haeundae"],
    "Gamcheon Village": ["gamcheon"],
    "Gwangalli": ["gwangalli", "gwangan"],
    # --- 명소/테마 ---
    "DMZ/JSA": ["dmz", "jsa", "panmunjom"],
    "Everland": ["everland"],
    "Lotte World": ["lotte world"],
    "Nami Island": ["nami island"],
    "Jeju Olle/Hallasan": ["hallasan", "olle", "seongsan", "udo"],
}

# --- 동반 주제(서브토픽) 사전 — 지역 게시물이 '무엇을 묻는가' ---
SUBTOPICS = {
    "일정/동선(Itinerary)": ["itinerary", "plan", "days", "day trip", "route", "schedule",
                          "first time", "worth", "how many days"],
    "이동/교통(Transport)": ["subway", "metro", "ktx", "train", "bus", "taxi", "from seoul",
                         "to busan", "get to", "getting to", "transport", "airport",
                         "rent", "drive", "ferry"],
    "숙소/입지(Stay)": ["hotel", "stay", "accommodation", "where to stay", "hostel", "airbnb",
                     "neighborhood", "area to stay", "hanok stay"],
    "볼거리/명소(Things to do)": ["see", "do", "visit", "attraction", "spot", "view", "sightseeing",
                            "things to do", "must see", "must visit"],
    "음식/맛집(Food)": ["food", "eat", "restaurant", "cafe", "market", "street food", "bbq",
                    "where to eat", "vegetarian", "vegan", "halal"],
    "체험/액티비티(Activity)": ["hanbok", "tour", "hike", "hiking", "templestay", "experience",
                          "show", "festival", "spa", "jjimjilbang", "theme park"],
    "쇼핑(Shopping)": ["shopping", "shop", "buy", "olive young", "market", "mall", "duty free",
                     "souvenir"],
    "날씨/시기(Season)": ["weather", "winter", "summer", "spring", "fall", "autumn",
                      "cherry blossom", "foliage", "snow", "rain", "best time", "when to"],
    "당일치기/근교(Day trip)": ["day trip", "from seoul", "near seoul", "side trip", "outside seoul"],
    "추천 요청(Recommend)": ["recommend", "recommendation", "suggest", "best", "tips", "advice",
                         "looking for", "help"],
}

NEED_SIGNALS = ["recommend", "recommendation", "suggest", "advice", "help", "looking for",
                "where", "how", "what", "which", "best", "should i", "any tips", "is it",
                "can i", "worth", "?"]

TOKEN_RE = re.compile(r"[a-z][a-z\-']+")
STOPWORDS = set("""
a an the and or but if then else of to in on at for with without from by as is are was were be been being
do does did doing have has had having i you he she it we they them this that these those my your our their his her its
me us him will would can could should shall may might must not no nor so than too very just about into out up down over under
again further once here there all any both each few more most other some such only own same don will now what which who whom
when where why how get got go going will im dont thats youre also really know like want need help thanks korea korean south
""".split())


def is_destination(text):
    low = text.lower()
    return any(kw in low for kw in DESTINATION_KWS)


def main():
    rows = list(csv.DictReader(open(CSV_PATH, encoding="utf-8")))
    n_all = len(rows)
    region_rows = [r for r in rows
                   if is_destination(r.get("title", "") + " " + r.get("description", ""))]
    n = len(region_rows)

    # 세부 지명 빈도
    place_freq = Counter()
    place_in_title = Counter()
    for r in region_rows:
        blob = (r.get("title", "") + " " + r.get("description", "")).lower()
        title_low = r.get("title", "").lower()
        for label, kws in PLACES.items():
            if any(k in blob for k in kws):
                place_freq[label] += 1
                if any(k in title_low for k in kws):
                    place_in_title[label] += 1

    # 서브토픽(동반 주제) — 지역 게시물 내부
    sub_freq = Counter()
    for r in region_rows:
        blob = (r.get("title", "") + " " + r.get("description", "")).lower()
        for st, kws in SUBTOPICS.items():
            if any(k in blob for k in kws):
                sub_freq[st] += 1

    # 도시별 × 서브토픽 (서울/부산/제주 한정)
    city_sub = {c: Counter() for c in ["Seoul", "Busan", "Jeju"]}
    city_kw = {"Seoul": "seoul", "Busan": "busan", "Jeju": "jeju"}
    for r in region_rows:
        blob = (r.get("title", "") + " " + r.get("description", "")).lower()
        for city, ck in city_kw.items():
            if ck in blob:
                for st, kws in SUBTOPICS.items():
                    if any(k in blob for k in kws):
                        city_sub[city][st] += 1

    # 다도시 비교 게시물 (한 글에 2개 이상 광역 도시)
    multi_city = 0
    for r in region_rows:
        blob = (r.get("title", "") + " " + r.get("description", "")).lower()
        c = sum(1 for ck in ["seoul", "busan", "jeju", "daegu", "gyeongju",
                             "jeonju", "incheon"] if ck in blob)
        if c >= 2:
            multi_city += 1

    # 니즈/요청형 비율
    need = sum(1 for r in region_rows
               if any(s in (r.get("title", "") + " " + r.get("description", "")).lower()
                      for s in NEED_SIGNALS))

    # 키워드/바이그램 (지역 게시물 한정)
    toks, bigrams = [], Counter()
    for r in region_rows:
        ws = [t for t in TOKEN_RE.findall(
            (r.get("title", "") + " " + r.get("description", "")).lower())
            if t not in STOPWORDS and len(t) > 2]
        toks += ws
        for i in range(len(ws) - 1):
            bigrams[ws[i] + " " + ws[i + 1]] += 1
    uni = Counter(toks)

    summary = {
        "region_posts": n,
        "pct_of_all": round(100 * n / n_all, 1),
        "need_request_pct": round(100 * need / n, 1),
        "multi_city_compare_posts": multi_city,
        "multi_city_pct": round(100 * multi_city / n, 1),
        "place_frequency": place_freq.most_common(),
        "subtopic_within_region": sub_freq.most_common(),
        "city_x_subtopic": {c: cnt.most_common() for c, cnt in city_sub.items()},
        "top_bigrams": bigrams.most_common(40),
        "top_unigrams": uni.most_common(40),
    }
    json.dump(summary, open("data/region_summary.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    with open("data/region_place_freq.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["place", "posts", "pct_of_region", "in_title"])
        for p, c in place_freq.most_common():
            w.writerow([p, c, round(100 * c / n, 1), place_in_title.get(p, 0)])

    with open("data/region_subtopic.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["subtopic", "posts", "pct_of_region"])
        for st, c in sub_freq.most_common():
            w.writerow([st, c, round(100 * c / n, 1)])

    # 콘솔
    print(f"전체 {n_all} 중 지역 테마 게시물: {n} ({summary['pct_of_all']}%)")
    print(f"  요청형 비율: {summary['need_request_pct']}%")
    print(f"  다도시 비교 게시물: {multi_city} ({summary['multi_city_pct']}%)")
    print("\n[세부 지명 Top 20]")
    for p, c in place_freq.most_common(20):
        print(f"  {p}: {c} ({round(100*c/n,1)}%, 제목노출 {place_in_title.get(p,0)})")
    print("\n[지역 게시물 내부 동반 주제(서브토픽)]")
    for st, c in sub_freq.most_common():
        print(f"  {st}: {c} ({round(100*c/n,1)}%)")
    print("\n[도시별 × 서브토픽 Top5]")
    for city in ["Seoul", "Busan", "Jeju"]:
        top = city_sub[city].most_common(5)
        print(f"  {city}: " + ", ".join(f"{s}={c}" for s, c in top))
    print("\n[지역 게시물 상위 바이그램]")
    for t, c in bigrams.most_common(20):
        print(f"  {t}: {c}")


if __name__ == "__main__":
    main()
