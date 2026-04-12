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
W_HARDLINE = 0.5
W_TENSION_GROWTH = 0.3
W_VOLUME_SURGE = 0.2

TENSION_GROWTH_SATURATE = 1.5
VOLUME_SURGE_SATURATE = 2.0

HARDLINE_KEYWORDS = (
    "강경",
    "엄중",
    "단호",
    "용납할 수 없",
    "보복",
    "즉각",
    "경고",
    "강력 대응",
    "무력 대응",
    "무력침해",
    "자위권",
    "재앙",
    "결사반대",
    "이대로는",
    "안 된다",
)

TENSION_KEYWORDS = (
    "외교",
    "외교장관",
    "대사",
    "영공",
    "영해",
    "영토",
    "군사",
    "휴전",
    "분쟁",
    "제재",
    "협상",
    "정상회담",
    "국제",
    "유엔",
    "NATO",
    "긴장",
    "대치",
    "무력",
    "핵",
    "미사일",
)


@dataclass(frozen=True)
class DiplomaticTensionBreakdown:
    hardline_rhetoric_index: float
    tension_keyword_growth: float
    news_volume_surge: float
    score: float

    def as_dict(self) -> dict[str, float]:
        return {
            "hardline_rhetoric_index": self.hardline_rhetoric_index,
            "tension_keyword_growth": self.tension_keyword_growth,
            "news_volume_surge": self.news_volume_surge,
            "diplomatic_tension_score": self.score,
        }


def compute_diplomatic_tension(
    target: date | None = None,
    *,
    lookback_days: int = 7,
) -> DiplomaticTensionBreakdown:
    """
    외교 긴장 점수 =
      (강경 발언 지수 × 0.5) +
      (긴장 키워드 증가율 × 0.3) +
      (뉴스량 급증 지수 × 0.2)
    """
    d = target or date.today()
    today_items = load_news(news_path(d))
    today_count = len(today_items)
    hardline = keyword_presence_ratio(today_items, HARDLINE_KEYWORDS)
    today_tension = keyword_presence_ratio(today_items, TENSION_KEYWORDS)

    historical_counts, baseline_tension_rates = past_news_counts_and_rates(
        d, lookback_days, TENSION_KEYWORDS
    )

    tension_growth = rate_growth_norm(
        today_tension,
        baseline_tension_rates,
        saturate=TENSION_GROWTH_SATURATE,
    )
    vol_surge = volume_surge_index(
        today_count,
        historical_counts,
        saturate=VOLUME_SURGE_SATURATE,
    )

    score = (
        W_HARDLINE * hardline
        + W_TENSION_GROWTH * tension_growth
        + W_VOLUME_SURGE * vol_surge
    )

    return DiplomaticTensionBreakdown(
        hardline_rhetoric_index=hardline,
        tension_keyword_growth=tension_growth,
        news_volume_surge=vol_surge,
        score=score,
    )


def main() -> None:
    b = compute_diplomatic_tension()
    print(json.dumps(b.as_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
