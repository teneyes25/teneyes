from __future__ import annotations

import json
import statistics
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from src.analyzers.news_score_common import (
    keyword_presence_ratio,
    load_news,
    news_path,
    past_news_counts_and_rates,
    rate_growth_norm,
    volume_surge_index,
)

# 가중치 (합 = 1.0)
W_EXCHANGE_VOL = 0.4
W_ECON_KEYWORD_GROWTH = 0.3
W_VOLUME_SURGE = 0.3

ECON_KEYWORD_GROWTH_SATURATE = 1.5
VOLUME_SURGE_SATURATE = 2.0
# 일간 수익률 표준편차가 이 값(예: 1%)에 도달하면 변동성 지수 1.0
EXCHANGE_VOL_SATURATE = 0.01


def _data_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "data"


def _econ_path(d: date) -> Path:
    return _data_dir() / f"econ_{d.isoformat()}.json"


def _load_econ(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _extract_usd_krw(root: dict[str, Any]) -> float | None:
    """`econ_collector` 저장 형식: { \"usd_krw\": { \"rates\": { \"KRW\": ... }, ... } }"""
    block = root.get("usd_krw")
    if not isinstance(block, dict):
        return None
    if block.get("success") is False:
        return None
    rates = block.get("rates")
    if not isinstance(rates, dict):
        return None
    krw = rates.get("KRW")
    if isinstance(krw, (int, float)):
        return float(krw)
    return None


def _rates_chronological(target: date, lookback_days: int) -> list[float]:
    out: list[tuple[date, float]] = []
    for i in range(0, lookback_days + 1):
        d = target - timedelta(days=i)
        r = _extract_usd_krw(_load_econ(_econ_path(d)))
        if r is not None:
            out.append((d, r))
    out.sort(key=lambda x: x[0])
    return [rate for _, rate in out]


def exchange_rate_volatility_index(
    target: date,
    *,
    lookback_days: int = 14,
) -> float:
    """
    저장된 일별 USD/KRW 시퀀스의 일간 수익률 표준편차(표본)를 0~1로 정규화.
    관측이 2개 미만이면 0.
    """
    rates = _rates_chronological(target, lookback_days)
    if len(rates) < 2:
        return 0.0
    changes = [(rates[i] - rates[i - 1]) / rates[i - 1] for i in range(1, len(rates))]
    if len(changes) >= 2:
        vol = statistics.stdev(changes)
    else:
        vol = abs(changes[0])
    if vol <= 0:
        return 0.0
    return min(1.0, vol / EXCHANGE_VOL_SATURATE)


ECON_ANXIETY_KEYWORDS = (
    "불확실",
    "금리",
    "인하",
    "인상",
    "침체",
    "경기",
    "하락",
    "급락",
    "폭락",
    "약세",
    "경고",
    "위기",
    "유동성",
    "인플레",
    "디플레",
    "물가",
    "환율",
    "원화",
    "환율 방어",
    "순매도",
    "부채",
    "디폴트",
    "구조조정",
    "실업",
)


@dataclass(frozen=True)
class EconomicAnxietyBreakdown:
    exchange_rate_volatility: float
    economic_anxiety_keyword_growth: float
    news_volume_surge: float
    score: float

    def as_dict(self) -> dict[str, float]:
        return {
            "exchange_rate_volatility": self.exchange_rate_volatility,
            "economic_anxiety_keyword_growth": self.economic_anxiety_keyword_growth,
            "news_volume_surge": self.news_volume_surge,
            "economic_anxiety_score": self.score,
        }


def compute_economic_anxiety(
    target: date | None = None,
    *,
    news_lookback_days: int = 7,
    fx_lookback_days: int = 14,
) -> EconomicAnxietyBreakdown:
    """
    경제 불안 점수 =
      (환율 변동성 × 0.4) +
      (경제 불안 키워드 증가율 × 0.3) +
      (뉴스량 급증 지수 × 0.3)
    """
    d = target or date.today()
    fx_vol = exchange_rate_volatility_index(d, lookback_days=fx_lookback_days)

    today_items = load_news(news_path(d))
    today_count = len(today_items)
    today_econ = keyword_presence_ratio(today_items, ECON_ANXIETY_KEYWORDS)

    historical_counts, baseline_econ_rates = past_news_counts_and_rates(
        d, news_lookback_days, ECON_ANXIETY_KEYWORDS
    )

    keyword_growth = rate_growth_norm(
        today_econ,
        baseline_econ_rates,
        saturate=ECON_KEYWORD_GROWTH_SATURATE,
    )
    vol_surge = volume_surge_index(
        today_count,
        historical_counts,
        saturate=VOLUME_SURGE_SATURATE,
    )

    score = (
        W_EXCHANGE_VOL * fx_vol
        + W_ECON_KEYWORD_GROWTH * keyword_growth
        + W_VOLUME_SURGE * vol_surge
    )

    return EconomicAnxietyBreakdown(
        exchange_rate_volatility=fx_vol,
        economic_anxiety_keyword_growth=keyword_growth,
        news_volume_surge=vol_surge,
        score=score,
    )


def main() -> None:
    b = compute_economic_anxiety()
    print(json.dumps(b.as_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
