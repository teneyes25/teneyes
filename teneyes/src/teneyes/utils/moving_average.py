from __future__ import annotations

from collections.abc import Sequence
from datetime import date, timedelta


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
    """
    d0 = last_weekday_on_or_before(end)
    d1 = previous_weekday(d0)
    d2 = previous_weekday(d1)
    return [d0, d1, d2]
