from __future__ import annotations

import json
import time
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import feedparser
import requests

from teneyes.paths import repo_root

NEWS_FEEDS = {
    "naver_politics": "https://news.naver.com/rss/politics.xml",
    "naver_economy": "https://news.naver.com/rss/economy.xml",
    "yonhap_all": "https://www.yonhapnewstv.co.kr/browse/feed/",
}

RSS_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36 TenEyes/0.1"
)
RSS_MAX_ATTEMPTS = 5
RSS_RETRY_DELAY_SEC = 2.0


def _project_root() -> Path:
    return repo_root()


def _failure_log_path() -> Path:
    return _project_root() / "data" / f"news_failures_{date.today().isoformat()}.jsonl"


def _append_failure_log(
    source: str,
    url: str,
    event: str,
    detail: str,
    *,
    attempt: int | None = None,
) -> None:
    path = _failure_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    record: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "url": url,
        "event": event,
        "detail": detail,
    }
    if attempt is not None:
        record["attempt"] = attempt
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _fetch_feed_entries(name: str, url: str) -> list[Any]:
    headers = {"User-Agent": RSS_USER_AGENT}
    last_detail = ""

    for attempt in range(1, RSS_MAX_ATTEMPTS + 1):
        try:
            r = requests.get(url, headers=headers, timeout=30)
            r.raise_for_status()
            feed = feedparser.parse(r.content)
            if feed.bozo and feed.bozo_exception:
                last_detail = f"bozo: {feed.bozo_exception!r}"
            elif not feed.entries:
                last_detail = "empty_feed"
            else:
                return list(feed.entries)
        except requests.RequestException as e:
            last_detail = str(e)

        if attempt < RSS_MAX_ATTEMPTS:
            time.sleep(RSS_RETRY_DELAY_SEC)

    _append_failure_log(
        name,
        url,
        "rss_unavailable_after_retries",
        last_detail or "unknown",
        attempt=RSS_MAX_ATTEMPTS,
    )
    return []


def collect_news() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for name, url in NEWS_FEEDS.items():
        entries = _fetch_feed_entries(name, url)
        for entry in entries:
            results.append(
                {
                    "source": name,
                    "title": entry.title,
                    "summary": entry.get("summary", ""),
                    "link": entry.link,
                    "published": entry.get("published", ""),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
    return results


def save_news(data: list[dict[str, Any]]) -> Path:
    today = date.today().isoformat()
    path = _project_root() / "data" / f"news_{today}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


class NewsCollector:
    """뉴스 RSS 수집 (v0.1)."""

    feeds: dict[str, str] = NEWS_FEEDS

    def collect(self) -> list[dict[str, Any]]:
        return collect_news()

    def save_news(self, data: list[dict[str, Any]]) -> Path:
        return save_news(data)


if __name__ == "__main__":
    items = collect_news()
    save_news(items)
    print(f"Collected {len(items)} news items.")
