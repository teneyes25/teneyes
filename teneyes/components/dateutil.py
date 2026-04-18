"""날짜를 API용 `YYYY-MM-DD` 문자열로 통일."""

from __future__ import annotations

import datetime


def to_date_str(date: str | datetime.date) -> str:
    if isinstance(date, datetime.date):
        return date.strftime("%Y-%m-%d")
    return str(date)
