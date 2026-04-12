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
W_EVENT_RISK = 0.5
W_MILITARY_GROWTH = 0.3
W_VOLUME_SURGE = 0.2

MILITARY_GROWTH_SATURATE = 1.5
VOLUME_SURGE_SATURATE = 2.0

# 군사 이벤트 위험도: 훈련·배치·발사 등 ‘사건성’ 키워드
MILITARY_EVENT_RISK_KEYWORDS = (
    "연합훈련",
    "군사훈련",
    "사격훈련",
    "기동훈련",
    "출격",
    "배치",
    "전개",
    "발사",
    "도발",
    "침범",
    "침공",
    "월경",
    "순찰",
    "요격",
    "방공",
    "비상대기",
    "동원훈련",
    "무력시위",
    "무력 도발",
    "NLL",
    "북방한계선",
)

# 군사 키워드 증가율: 군사 보도 전반
MILITARY_KEYWORDS = (
    "국방",
    "합참",
    "군",
    "군부대",
    "북한",
    "한미",
    "미군",
    "주한미군",
    "군사",
    "훈련",
    "미사일",
    "핵",
    "잠수함",
    "전투기",
    "군함",
    "무력",
    "전쟁",
    "교전",
    "휴전",
    "무기",
)


@dataclass(frozen=True)
class MilitaryTensionBreakdown:
    military_event_risk: float
    military_keyword_growth: float
    news_volume_surge: float
    score: float

    def as_dict(self) -> dict[str, float]:
        return {
            "military_event_risk": self.military_event_risk,
            "military_keyword_growth": self.military_keyword_growth,
            "news_volume_surge": self.news_volume_surge,
            "military_tension_score": self.score,
        }


def compute_military_tension(
    target: date | None = None,
    *,
    lookback_days: int = 7,
) -> MilitaryTensionBreakdown:
    """
    군사 긴장 점수 =
      (군사 이벤트 위험도 × 0.5) +
      (군사 키워드 증가율 × 0.3) +
      (뉴스량 급증 지수 × 0.2)
    """
    d = target or date.today()
    today_items = load_news(news_path(d))
    today_count = len(today_items)
    event_risk = keyword_presence_ratio(today_items, MILITARY_EVENT_RISK_KEYWORDS)
    today_mil = keyword_presence_ratio(today_items, MILITARY_KEYWORDS)

    historical_counts, baseline_military_rates = past_news_counts_and_rates(
        d, lookback_days, MILITARY_KEYWORDS
    )

    military_growth = rate_growth_norm(
        today_mil,
        baseline_military_rates,
        saturate=MILITARY_GROWTH_SATURATE,
    )
    vol_surge = volume_surge_index(
        today_count,
        historical_counts,
        saturate=VOLUME_SURGE_SATURATE,
    )

    score = (
        W_EVENT_RISK * event_risk
        + W_MILITARY_GROWTH * military_growth
        + W_VOLUME_SURGE * vol_surge
    )

    return MilitaryTensionBreakdown(
        military_event_risk=event_risk,
        military_keyword_growth=military_growth,
        news_volume_surge=vol_surge,
        score=score,
    )


def main() -> None:
    b = compute_military_tension()
    print(json.dumps(b.as_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
