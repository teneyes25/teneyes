from __future__ import annotations

from collections import Counter
from typing import Any

from utils.news_summary import generate_advanced_summary, generate_daily_news_summary


def explain_conflict(
    conflict: float, conf_kw: Counter[str], articles: list[dict[str, Any]]
) -> str:
    top_conf = [kw for kw, _ in conf_kw.most_common(3)]
    c = float(conflict)
    if c > 20:
        level = "높은 수준의 갈등 신호가 감지되었습니다."
    elif c > 10:
        level = "중간 수준의 갈등 신호가 나타났습니다."
    else:
        level = "갈등 신호는 낮은 편입니다."
    top_join = ", ".join(top_conf) if top_conf else "(해당 없음)"
    return f"{level} 주요 갈등 요인은 {top_join}입니다."


def explain_happiness(
    happiness: float, happy_kw: Counter[str], articles: list[dict[str, Any]]
) -> str:
    top_happy = [kw for kw, _ in happy_kw.most_common(3)]
    h = float(happiness)
    if h > 20:
        level = "긍정 신호가 강하게 나타난 하루입니다."
    elif h > 10:
        level = "긍정 신호가 일정 수준 감지되었습니다."
    else:
        level = "긍정 신호는 다소 약한 편입니다."
    top_join = ", ".join(top_happy) if top_happy else "(해당 없음)"
    return f"{level} 주요 긍정 키워드는 {top_join}입니다."


def explain_ten_eyes(conflict: float, happiness: float, ten_eyes: float) -> str:
    c = float(conflict)
    h = float(happiness)
    te = float(ten_eyes)
    diff = h - c
    if diff > 5:
        mood = "전반적으로 긍정 흐름이 우세한 날입니다."
    elif diff < -5:
        mood = "전반적으로 갈등 신호가 강한 날입니다."
    else:
        mood = "긍정과 부정 신호가 균형을 이루는 중립적인 날입니다."
    return f"{mood} TEN EYES Score는 {te:.1f}입니다."


def generate_daily_briefing(
    conflict: float,
    happiness: float,
    ten_eyes: float,
    conf_kw: Counter[str],
    happy_kw: Counter[str],
    articles: list[dict[str, Any]],
    sentiment_analyzer: Any,
) -> str:
    c = float(conflict)
    h = float(happiness)
    te = float(ten_eyes)

    diff = h - c
    if diff > 5:
        mood = "오늘은 긍정 흐름이 우세한 안정적인 하루였습니다."
    elif diff < -5:
        mood = "오늘은 갈등 신호가 강하게 나타난 불안정한 하루였습니다."
    else:
        mood = "긍정과 부정 신호가 균형을 이루는 중립적인 하루였습니다."

    conf_expl = explain_conflict(c, conf_kw, articles)
    happy_expl = explain_happiness(h, happy_kw, articles)
    ten_expl = explain_ten_eyes(c, h, te)

    advanced_summary = generate_advanced_summary(articles, sentiment_analyzer)
    news_summary = generate_daily_news_summary(articles, sentiment_analyzer)

    if diff > 3:
        outlook = "긍정 흐름이 이어질 가능성이 있습니다."
    elif diff < -3:
        outlook = "갈등 신호가 내일도 영향을 줄 수 있습니다."
    else:
        outlook = "내일은 큰 변동 없이 비슷한 정서 흐름이 예상됩니다."

    conf_top = ", ".join(kw for kw, _ in conf_kw.most_common(3))
    happy_top = ", ".join(kw for kw, _ in happy_kw.most_common(3))
    if not conf_top:
        conf_top = "(해당 없음)"
    if not happy_top:
        happy_top = "(해당 없음)"

    briefing = f"""
📰 **TEN EYES 일일 브리핑**

**1) 오늘의 핵심 지수**
- TEN EYES Score: {te:.1f}
- 갈등지수: {c:.1f}
- 행복지수: {h:.1f}
- 분위기 요약: {mood}

**2) 지수 변동 원인 분석**
- 갈등지수 분석: {conf_expl}
- 행복지수 분석: {happy_expl}
- 종합 해석: {ten_expl}

**3) 오늘의 핵심 사건**
{advanced_summary}

**4) 정서 흐름 분석**
- 긍정/부정 감정이 강하게 반응한 사건 중심으로 정서가 형성되었습니다.
- 갈등 키워드: {conf_top}
- 행복 키워드: {happy_top}

**5) 주요 뉴스 요약**
{news_summary}

**6) 내일 전망**
{outlook}
"""
    return briefing
