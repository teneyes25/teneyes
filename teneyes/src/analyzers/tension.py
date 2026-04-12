from __future__ import annotations

from typing import Any, TypedDict

from .conflict_index_calculator import ConflictIndexCalculator
from .happiness_index_calculator import HappinessIndexCalculator


class TenEyesBundle(TypedDict):
    tension: float
    stability: float
    ten_eyes_score: float


def compute_tension(conflict_index: float, happiness_index: float) -> float:
    """Tension = max(0, ConflictIndex - HappinessIndex)."""
    return max(0.0, float(conflict_index) - float(happiness_index))


def compute_stability(happiness_index: float, conflict_index: float) -> float:
    """Stability = max(0, HappinessIndex - ConflictIndex)."""
    return max(0.0, float(happiness_index) - float(conflict_index))


def compute_ten_eyes(conflict: float, happiness: float) -> TenEyesBundle:
    tension = max(0.0, float(conflict) - float(happiness))
    stability = max(0.0, float(happiness) - float(conflict))

    ten_eyes = 50.0 + float(happiness) - float(conflict)
    ten_eyes = max(0.0, min(100.0, ten_eyes))

    return {
        "tension": tension,
        "stability": stability,
        "ten_eyes_score": ten_eyes,
    }


def tension_for_date(
    date_str: str,
    *,
    sentiment_mode: str = "opensource",
) -> dict[str, Any]:
    """
    당일 `conflict_index`·`happiness_index_raw`로 Tension·Stability·ten_eyes_score를 산출합니다.
    """
    conflict_calc = ConflictIndexCalculator(sentiment_mode=sentiment_mode)
    happy_calc = HappinessIndexCalculator(sentiment_mode=sentiment_mode)

    conflict_out = conflict_calc.run(date_str)
    happy_out = happy_calc.run(date_str)

    conflict_index = float(conflict_out["conflict_index"])
    happiness_index = float(happy_out["happiness_index_raw"])
    bundle = compute_ten_eyes(conflict_index, happiness_index)

    return {
        "date": date_str,
        "conflict_index": conflict_index,
        "final_conflict_index": float(conflict_out["final_conflict_index"]),
        "happiness_index": happiness_index,
        **bundle,
    }
