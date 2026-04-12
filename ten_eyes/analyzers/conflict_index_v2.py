from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from utils.keyword_extract import extract_keywords
from utils.moving_average import moving_average, three_business_days_ending_at

from .keywords.conflict_keywords import CONFLICT_KEYWORDS
from .relevance_score import get_relevance_score
from .sentiment.analyzer import SentimentAnalyzer
from .weekday_baseline import get_weekday_baseline


def _data_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "data"


HAPPINESS_AXIS_WEIGHTS: dict[str, float] = {
    "political": 0.20,
    "diplomatic": 0.25,
    "military": 0.25,
    "economic": 0.15,
    "social": 0.15,
}


def weighted_happiness_index(scores: dict[str, float]) -> float:
    return sum(scores[axis] * w for axis, w in HAPPINESS_AXIS_WEIGHTS.items())


class ConflictIndexCalculatorV2:
    def __init__(self, sentiment_mode: str = "opensource") -> None:
        self.sentiment = SentimentAnalyzer(mode=sentiment_mode)

    def load_news(self, date_str: str) -> list[dict[str, Any]]:
        path = _data_dir() / f"news_{date_str}.json"
        if not path.is_file():
            raise FileNotFoundError(f"No news file for {date_str}")
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError(f"Expected list in news file, got {type(data)}")
        return data

    def analyze_article(self, article: dict[str, Any]) -> dict[str, Any]:
        text = article.get("title", "") + " " + article.get("summary", "")
        sentiment = self.sentiment.analyze(text)
        relevance = float(get_relevance_score(article))
        return {
            "text": text,
            "sentiment": sentiment,
            "relevance": relevance,
        }

    def compute_category_score(
        self,
        analyzed_articles: list[dict[str, Any]],
        category_keywords: list[str],
        date_str: str,
    ) -> float:
        total_articles = len(analyzed_articles)
        if total_articles == 0:
            return 0.0

        total_news = total_articles

        positive_sum = 0.0
        relevance_sum = 0.0
        positive_keywords = 0

        for a in analyzed_articles:
            text = a["text"]
            sentiment = a["sentiment"]
            positive_ratio = float(sentiment["positive"])
            positive_sum += positive_ratio
            relevance_sum += float(a["relevance"])

            for kw in category_keywords:
                if kw in text:
                    positive_keywords += 1

        positive_ratio = positive_sum / total_articles
        emotion_score = positive_ratio * 100.0

        keyword_score = (positive_keywords / total_articles) * 100.0
        volume_ratio = (positive_keywords / total_news) * 100.0

        relevance_score = relevance_sum / total_articles
        relevance_adjusted = (
            emotion_score * 0.5 + keyword_score * 0.3 + volume_ratio * 0.2
        ) * relevance_score

        weekday_baseline = get_weekday_baseline(date_str)
        weekday_adjusted = relevance_adjusted * weekday_baseline

        return weekday_adjusted

    def _run_one_day(self, date_str: str) -> dict[str, Any]:
        articles = self.load_news(date_str)
        analyzed = [self.analyze_article(a) for a in articles]
        keywords = extract_keywords(articles, CONFLICT_KEYWORDS)

        scores = {
            category: self.compute_category_score(analyzed, kws, date_str)
            for category, kws in CONFLICT_KEYWORDS.items()
        }

        happiness_index = weighted_happiness_index(scores)

        return {
            "date": date_str,
            "scores": scores,
            "happiness_index": happiness_index,
            "conflict_index_raw": happiness_index,
            "keywords": keywords,
        }

    def _happiness_index_or_zero(self, date_str: str) -> float:
        try:
            return float(self._run_one_day(date_str)["happiness_index"])
        except (FileNotFoundError, ValueError):
            return 0.0

    def run(self, date_str: str, *, ma_window: int = 3) -> dict[str, Any]:
        out = self._run_one_day(date_str)
        end = date.fromisoformat(date_str)
        biz_days = three_business_days_ending_at(end)
        values = [
            self._happiness_index_or_zero(d.isoformat()) for d in biz_days
        ]
        dates_iso = [d.isoformat() for d in biz_days]
        final_ma = moving_average(values, window=ma_window)

        out["happiness_index_3d"] = values
        out["happiness_index_3d_dates"] = dates_iso
        out["final_happiness_index"] = final_ma

        out["conflict_index_3d"] = values
        out["conflict_index_3d_dates"] = dates_iso
        out["final_conflict_index"] = final_ma
        return out
