from __future__ import annotations

import json
import statistics
from dataclasses import dataclass
from datetime import date, timedelta

from src.analyzers.news_score_common import (
    keyword_presence_ratio,
    load_news,
    news_path,
    past_news_counts_and_rates,
    rate_growth_norm,
)
from src.analyzers.political_tension import CONFLICT_KEYWORDS, NEGATIVE_KEYWORDS

# 가중치 (합 = 1.0)
W_NEGATIVE = 0.5
W_EMOTION_VOL = 0.3
W_CONFLICT_GROWTH = 0.2

CONFLICT_GROWTH_SATURATE = 1.5
# 일별 부정 비율(0~1)의 표준편차 상한 — 이 값이면 변동성 지수 1.0
EMOTION_VOL_STDDEV_SATURATE = 0.35


def _daily_negative_ratios(target: date, window_days: int) -> list[float]:
    out: list[float] = []
    for i in range(window_days):
        d = target - timedelta(days=i)
        items = load_news(news_path(d))
        out.append(keyword_presence_ratio(items, NEGATIVE_KEYWORDS))
    return out


def social_emotion_volatility_index(target: date, *, window_days: int = 7) -> float:
    """
    당일 포함 최근 `window_days`일의 '부정 감정 비율' 시계열 표준편차를 0~1로 정규화.
    여론 톤이 날짜마다 들쭉날쭉할수록 값이 커짐.
    """
    ratios = _daily_negative_ratios(target, window_days)
    if len(ratios) < 2:
        return 0.0
    s = statistics.stdev(ratios)
    if s <= 0:
        return 0.0
    return min(1.0, s / EMOTION_VOL_STDDEV_SATURATE)


@dataclass(frozen=True)
class SocialEmotionalAnxietyBreakdown:
    negative_emotion_ratio: float
    emotion_volatility: float
    conflict_keyword_growth: float
    score: float

    def as_dict(self) -> dict[str, float]:
        return {
            "negative_emotion_ratio": self.negative_emotion_ratio,
            "emotion_volatility": self.emotion_volatility,
            "conflict_keyword_growth": self.conflict_keyword_growth,
            "social_emotional_anxiety_score": self.score,
        }


def compute_social_emotional_anxiety(
    target: date | None = None,
    *,
    lookback_days: int = 7,
    emotion_vol_window_days: int = 7,
) -> SocialEmotionalAnxietyBreakdown:
    """
    사회 감정 불안 점수 =
      (부정 감정 비율 × 0.5) +
      (감정 변동성 × 0.3) +
      (갈등 키워드 증가율 × 0.2)

    부정/갈등 키워드는 `political_tension`과 동일 목록을 사용합니다.
    """
    d = target or date.today()
    today_items = load_news(news_path(d))
    neg_ratio = keyword_presence_ratio(today_items, NEGATIVE_KEYWORDS)
    today_conflict = keyword_presence_ratio(today_items, CONFLICT_KEYWORDS)

    _, baseline_conflict_rates = past_news_counts_and_rates(
        d, lookback_days, CONFLICT_KEYWORDS
    )
    conflict_growth = rate_growth_norm(
        today_conflict,
        baseline_conflict_rates,
        saturate=CONFLICT_GROWTH_SATURATE,
    )

    emotion_vol = social_emotion_volatility_index(
        d, window_days=emotion_vol_window_days
    )

    score = (
        W_NEGATIVE * neg_ratio
        + W_EMOTION_VOL * emotion_vol
        + W_CONFLICT_GROWTH * conflict_growth
    )

    return SocialEmotionalAnxietyBreakdown(
        negative_emotion_ratio=neg_ratio,
        emotion_volatility=emotion_vol,
        conflict_keyword_growth=conflict_growth,
        score=score,
    )


def main() -> None:
    b = compute_social_emotional_anxiety()
    print(json.dumps(b.as_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
