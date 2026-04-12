from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date

from src.analyzers.news_score_common import (
    keyword_presence_ratio,
    load_news,
    news_path,
    past_news_counts_and_rates,
    rate_growth_norm,
    volume_surge_index,
)

# 가중치 (합 = 1.0)
W_NEGATIVE = 0.4
W_CONFLICT_GROWTH = 0.4
W_VOLUME_SURGE = 0.2

CONFLICT_GROWTH_SATURATE = 1.5
VOLUME_SURGE_SATURATE = 2.0

NEGATIVE_KEYWORDS = (
    "불안",
    "우려",
    "비판",
    "심각",
    "위기",
    "논란",
    "파장",
    "충격",
    "하락",
    "악화",
    "실패",
    "혼란",
    "긴급",
    "우려된다",
    "우려가",
)

CONFLICT_KEYWORDS = (
    "갈등",
    "대립",
    "충돌",
    "긴장",
    "무력",
    "도발",
    "비난",
    "맞불",
    "신경전",
    "대치",
    "전쟁",
    "교전",
    "협상 결렬",
    "결렬",
    "탄핵",
    "정쟁",
)


@dataclass(frozen=True)
class PoliticalTensionBreakdown:
    negative_emotion_ratio: float
    conflict_keyword_growth: float
    news_volume_surge: float
    score: float

    def as_dict(self) -> dict[str, float]:
        return {
            "negative_emotion_ratio": self.negative_emotion_ratio,
            "conflict_keyword_growth": self.conflict_keyword_growth,
            "news_volume_surge": self.news_volume_surge,
            "political_tension_score": self.score,
        }


def compute_political_tension(
    target: date | None = None,
    *,
    lookback_days: int = 7,
) -> PoliticalTensionBreakdown:
    """
    정치 긴장 점수 =
      (부정 감정 비율 × 0.4) +
      (갈등 키워드 증가율 × 0.4) +
      (뉴스량 급증 지수 × 0.2)
    """
    d = target or date.today()
    today_items = load_news(news_path(d))
    today_count = len(today_items)
    today_conflict = keyword_presence_ratio(today_items, CONFLICT_KEYWORDS)
    neg_ratio = keyword_presence_ratio(today_items, NEGATIVE_KEYWORDS)

    historical_counts, baseline_conflict_rates = past_news_counts_and_rates(
        d, lookback_days, CONFLICT_KEYWORDS
    )

    conflict_growth = rate_growth_norm(
        today_conflict,
        baseline_conflict_rates,
        saturate=CONFLICT_GROWTH_SATURATE,
    )
    vol_surge = volume_surge_index(
        today_count,
        historical_counts,
        saturate=VOLUME_SURGE_SATURATE,
    )

    score = (
        W_NEGATIVE * neg_ratio
        + W_CONFLICT_GROWTH * conflict_growth
        + W_VOLUME_SURGE * vol_surge
    )

    return PoliticalTensionBreakdown(
        negative_emotion_ratio=neg_ratio,
        conflict_keyword_growth=conflict_growth,
        news_volume_surge=vol_surge,
        score=score,
    )


def main() -> None:
    b = compute_political_tension()
    print(json.dumps(b.as_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
