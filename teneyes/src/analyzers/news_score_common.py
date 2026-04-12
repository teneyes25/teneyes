from __future__ import annotations

import html
import json
from datetime import date, timedelta
from pathlib import Path
from collections.abc import Sequence
from typing import Any, Iterable


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    return project_root() / "data"


def news_path(d: date) -> Path:
    return data_dir() / f"news_{d.isoformat()}.json"


def load_news(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    return data if isinstance(data, list) else []


def item_text(item: dict[str, Any]) -> str:
    title = str(item.get("title", ""))
    summary = str(item.get("summary", ""))
    return html.unescape(f"{title} {summary}")


def count_hits(text: str, keywords: Iterable[str]) -> int:
    t = text.lower()
    n = 0
    for kw in keywords:
        if kw.lower() in t:
            n += 1
    return n


def keyword_presence_ratio(items: list[dict[str, Any]], keywords: Iterable[str]) -> float:
    if not items:
        return 0.0
    hit = 0
    for it in items:
        if count_hits(item_text(it), keywords) > 0:
            hit += 1
    return hit / len(items)


def moving_average(values: Sequence[float], window: int = 3) -> float:
    """
    마지막 `window`개 평균. 길이가 `window`보다 짧으면 전체 평균.
    """
    if not values:
        return 0.0
    if window < 1:
        raise ValueError("window must be >= 1")
    n = len(values)
    if n < window:
        return sum(values) / n
    return sum(values[-window:]) / window


def last_weekday_on_or_before(d: date) -> date:
    """`d` 이하에서 가장 최근 월~금(토·일이면 역으로 당김)."""
    cur = d
    while cur.weekday() >= 5:
        cur -= timedelta(days=1)
    return cur


def previous_weekday(d: date) -> date:
    """직전 영업일(공휴일 미반영, 주말만 건너뜀)."""
    cur = d - timedelta(days=1)
    while cur.weekday() >= 5:
        cur -= timedelta(days=1)
    return cur


def three_business_days_ending_at(end: date) -> list[date]:
    """
    `end` 기준 이하 최근 영업일 3일, 최신 → 과거 순.
    예: end가 일요일이면 금·목·수.
    """
    d0 = last_weekday_on_or_before(end)
    d1 = previous_weekday(d0)
    d2 = previous_weekday(d1)
    return [d0, d1, d2]


def rate_growth_norm(
    today_rate: float,
    baseline_rates: list[float],
    *,
    saturate: float,
) -> float:
    if not baseline_rates:
        return 0.0
    base = sum(baseline_rates) / len(baseline_rates)
    if base <= 0 and today_rate <= 0:
        return 0.0
    denom = base + 1e-6
    raw = (today_rate - base) / denom
    if raw <= 0:
        return 0.0
    return min(1.0, raw / saturate)


def volume_surge_index(
    today_count: int,
    historical_counts: list[int],
    *,
    saturate: float,
) -> float:
    if today_count <= 0:
        return 0.0
    hist = [c for c in historical_counts if c >= 0]
    if not hist:
        return 0.0
    mean_h = sum(hist) / len(hist)
    if mean_h <= 0:
        return 0.0
    raw = (today_count - mean_h) / mean_h
    if raw <= 0:
        return 0.0
    return min(1.0, raw / saturate)


def past_news_counts_and_rates(
    target: date,
    lookback_days: int,
    keywords: Iterable[str],
) -> tuple[list[int], list[float]]:
    counts: list[int] = []
    rates: list[float] = []
    for i in range(1, lookback_days + 1):
        past = target - timedelta(days=i)
        items = load_news(news_path(past))
        counts.append(len(items))
        rates.append(keyword_presence_ratio(items, keywords))
    return counts, rates
