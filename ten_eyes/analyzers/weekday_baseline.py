from __future__ import annotations

from datetime import date

# 뉴스량·이슈 강도 등 요일 보정용 배수 (월~금 정상, 주말 축소)
WEEKDAY_BASELINE: dict[int, float] = {
    0: 1.0,  # 월
    1: 1.0,  # 화
    2: 1.0,  # 수
    3: 1.0,  # 목
    4: 1.0,  # 금
    5: 0.7,  # 토
    6: 0.6,  # 일
}


def get_weekday_baseline(date_str: str) -> float:
    """`YYYY-MM-DD` 문자열 → 해당 요일 베이스라인 배수."""
    d = date.fromisoformat(date_str)
    return WEEKDAY_BASELINE[d.weekday()]
