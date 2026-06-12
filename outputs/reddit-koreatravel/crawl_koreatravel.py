#!/usr/bin/env python3
"""
r/koreatravel 서브레딧 게시물 크롤러
- 데이터 소스: pullpush.io (Pushshift 후속 공개 API)
  Reddit 공식 API가 비인증 접근을 차단(403)하므로 공개 아카이브 API를 사용.
- 최근 게시물부터 과거 방향으로 `before`(epoch) 페이지네이션하며 수집.
- 수집 필드: id, created_utc(+ISO), title, description(selftext),
             score, num_comments, author, url, permalink, link_flair_text
- 출력: data/koreatravel_posts.csv
"""
import csv
import sys
import time
import datetime as dt
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

SUBREDDIT = "koreatravel"
TARGET = 10000
PAGE_SIZE = 100
BASE = "https://api.pullpush.io/reddit/search/submission/"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36")
OUT_CSV = "data/koreatravel_posts.csv"

FIELDS = ["id", "created_utc", "created_iso", "title", "description",
          "score", "num_comments", "author", "link_flair_text",
          "url", "permalink"]


def fetch_page(before=None, retries=5):
    params = {"subreddit": SUBREDDIT, "size": PAGE_SIZE, "sort": "desc",
              "sort_type": "created_utc"}
    if before is not None:
        params["before"] = before
    url = BASE + "?" + urlencode(params)
    delay = 2.0
    for attempt in range(1, retries + 1):
        try:
            req = Request(url, headers={"User-Agent": UA,
                                        "Accept": "application/json"})
            with urlopen(req, timeout=60) as resp:
                import json
                payload = json.loads(resp.read().decode("utf-8"))
                return payload.get("data", [])
        except (HTTPError, URLError) as e:
            code = getattr(e, "code", "n/a")
            print(f"  [retry {attempt}/{retries}] HTTP/URL error "
                  f"({code}); waiting {delay:.1f}s", file=sys.stderr)
            time.sleep(delay)
            delay = min(delay * 2, 30)
        except Exception as e:  # noqa
            print(f"  [retry {attempt}/{retries}] {type(e).__name__}: {e}; "
                  f"waiting {delay:.1f}s", file=sys.stderr)
            time.sleep(delay)
            delay = min(delay * 2, 30)
    return None  # all retries failed


def clean(text):
    if text is None:
        return ""
    # CSV 안전성 위해 개행/탭 정규화 (정보 손실 최소화)
    return (str(text).replace("\r\n", " ").replace("\n", " ")
            .replace("\r", " ").replace("\t", " ").strip())


def main():
    seen = set()
    rows = []
    before = None
    empty_streak = 0
    page = 0

    print(f"수집 시작: r/{SUBREDDIT} (목표 {TARGET}개)")
    while len(rows) < TARGET:
        page += 1
        data = fetch_page(before=before)
        if data is None:
            print("연속 재시도 실패 — 수집 중단", file=sys.stderr)
            break
        if not data:
            empty_streak += 1
            print(f"  page {page}: 빈 응답 ({empty_streak})")
            if empty_streak >= 3:
                print("빈 응답 연속 — 더 이상 과거 데이터 없음. 종료.")
                break
            # before를 조금 더 과거로 밀어 재시도
            if before is not None:
                before -= 1
            time.sleep(1.5)
            continue
        empty_streak = 0

        oldest = before
        new_count = 0
        for p in data:
            pid = p.get("id")
            cu = p.get("created_utc")
            if oldest is None or (cu is not None and cu < oldest):
                oldest = cu
            if not pid or pid in seen:
                continue
            seen.add(pid)
            iso = ""
            if cu is not None:
                try:
                    iso = dt.datetime.utcfromtimestamp(int(cu)).strftime(
                        "%Y-%m-%d %H:%M:%S")
                except Exception:  # noqa
                    iso = ""
            rows.append({
                "id": pid,
                "created_utc": cu,
                "created_iso": iso,
                "title": clean(p.get("title")),
                "description": clean(p.get("selftext")),
                "score": p.get("score", ""),
                "num_comments": p.get("num_comments", ""),
                "author": clean(p.get("author")),
                "link_flair_text": clean(p.get("link_flair_text")),
                "url": clean(p.get("url")),
                "permalink": clean(p.get("permalink")),
            })
            new_count += 1

        # 다음 페이지: 가장 오래된 게시물 시각 이전
        if oldest is not None and oldest != before:
            before = int(oldest)
        else:
            before = (int(before) - 1) if before else None

        print(f"  page {page}: +{new_count}개 (누적 {len(rows)}) "
              f"| before={before} "
              f"({dt.datetime.utcfromtimestamp(before).date() if before else '-'})")

        if new_count == 0:
            empty_streak += 1
            if empty_streak >= 3:
                print("신규 데이터 없음 연속 — 종료.")
                break

        time.sleep(1.2)  # rate-limit 예의

    # CSV 저장
    rows = rows[:TARGET]
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    print(f"\n완료: {len(rows)}개 게시물 -> {OUT_CSV}")
    if rows:
        print(f"기간: {rows[-1]['created_iso']} ~ {rows[0]['created_iso']} (UTC)")


if __name__ == "__main__":
    main()
