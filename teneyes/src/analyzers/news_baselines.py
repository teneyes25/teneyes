from __future__ import annotations

from datetime import date

# 참고: 역사적 평균 군사 뉴스 비중 (본문·제목 키워드 기준 산출 시 보정·대시보드용)
WEEKDAY_MILITARY_NEWS_SHARE = 0.08  # 평일(월~금) 평균 8%
SATURDAY_MILITARY_NEWS_SHARE = 0.05  # 토요일 평균 5%
# 일요일은 명시 없음 → 토요일과 동일 가정
SUNDAY_MILITARY_NEWS_SHARE = SATURDAY_MILITARY_NEWS_SHARE


def expected_military_news_share(d: date) -> float:
    """
    해당 요일에 대한 기대 군사 뉴스 비중(0~1).
    - 월~금: 8%
    - 토·일: 5%
    """
    wd = d.weekday()
    if wd == 5:
        return SATURDAY_MILITARY_NEWS_SHARE
    if wd == 6:
        return SUNDAY_MILITARY_NEWS_SHARE
    return WEEKDAY_MILITARY_NEWS_SHARE


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
