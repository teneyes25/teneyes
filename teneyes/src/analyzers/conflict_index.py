from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date

from src.analyzers.diplomatic_tension import compute_diplomatic_tension
from src.analyzers.economic_anxiety import compute_economic_anxiety
from src.analyzers.military_tension import compute_military_tension
from src.analyzers.political_tension import compute_political_tension
from src.analyzers.social_emotional_anxiety import compute_social_emotional_anxiety

# 가중치 (합 = 1.0)
W_POLITICAL = 0.20
W_DIPLOMATIC = 0.25
W_MILITARY = 0.25
W_ECONOMIC = 0.15
W_SOCIAL_EMOTIONAL = 0.15


@dataclass(frozen=True)
class ConflictIndexBreakdown:
    political_tension: float
    diplomatic_tension: float
    military_tension: float
    economic_anxiety: float
    social_emotional_anxiety: float
    conflict_index: float

    def as_dict(self) -> dict[str, float]:
        return {
            "political_tension": self.political_tension,
            "diplomatic_tension": self.diplomatic_tension,
            "military_tension": self.military_tension,
            "economic_anxiety": self.economic_anxiety,
            "social_emotional_anxiety": self.social_emotional_anxiety,
            "conflict_index": self.conflict_index,
        }


def compute_conflict_index(
    target: date | None = None,
    *,
    news_lookback_days: int = 7,
    fx_lookback_days: int = 14,
    emotion_vol_window_days: int = 7,
) -> ConflictIndexBreakdown:
    """
    Conflict Index =
      (정치 긴장 × 0.20) +
      (외교 긴장 × 0.25) +
      (군사 긴장 × 0.25) +
      (경제 불안 × 0.15) +
      (사회 감정 불안 × 0.15)
    """
    d = target or date.today()

    political = compute_political_tension(d, lookback_days=news_lookback_days).score
    diplomatic = compute_diplomatic_tension(d, lookback_days=news_lookback_days).score
    military = compute_military_tension(d, lookback_days=news_lookback_days).score
    economic = compute_economic_anxiety(
        d,
        news_lookback_days=news_lookback_days,
        fx_lookback_days=fx_lookback_days,
    ).score
    social = compute_social_emotional_anxiety(
        d,
        lookback_days=news_lookback_days,
        emotion_vol_window_days=emotion_vol_window_days,
    ).score

    idx = (
        W_POLITICAL * political
        + W_DIPLOMATIC * diplomatic
        + W_MILITARY * military
        + W_ECONOMIC * economic
        + W_SOCIAL_EMOTIONAL * social
    )

    return ConflictIndexBreakdown(
        political_tension=political,
        diplomatic_tension=diplomatic,
        military_tension=military,
        economic_anxiety=economic,
        social_emotional_anxiety=social,
        conflict_index=idx,
    )


def main() -> None:
    b = compute_conflict_index()
    print(json.dumps(b.as_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
