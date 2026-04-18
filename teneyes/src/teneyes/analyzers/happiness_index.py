from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..paths import repo_root
from ..utils.keyword_extract import extract_keywords

from .keywords.happiness_keywords import HAPPINESS_KEYWORDS
from .relevance_score import get_relevance_score
from .sentiment.analyzer import SentimentAnalyzer
from .weekday_baseline import get_weekday_baseline


def _data_dir() -> Path:
    return repo_root() / "data"


HAPPINESS_INDEX_WEIGHTS: dict[str, float] = {
    "social_emotion": 0.25,
    "economic": 0.25,
    "culture_life": 0.20,
    "public_service": 0.15,
    "safety": 0.15,
}


class HappinessIndexCalculator:
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

        total_news_count = total_articles

        weighted_positive_sum = 0.0
        weighted_keyword_hits = 0.0

        for a in analyzed_articles:
            text = a["text"]
            sentiment = a["sentiment"]
            relevance = float(a["relevance"])

            weighted_positive_sum += float(sentiment["positive"]) * relevance

            for kw in category_keywords:
                if kw in text:
                    weighted_keyword_hits += relevance

        emotion_score = (weighted_positive_sum / total_articles) * 100.0
        keyword_score = (weighted_keyword_hits / total_articles) * 100.0
        volume_ratio = (weighted_keyword_hits / total_news_count) * 100.0

        baseline = get_weekday_baseline(date_str)
        baseline_adjusted = (
            emotion_score * 0.5 + keyword_score * 0.3 + volume_ratio * 0.2
        ) * baseline

        return baseline_adjusted

    def run(self, date_str: str) -> dict[str, Any]:
        articles = self.load_news(date_str)
        analyzed = [self.analyze_article(a) for a in articles]
        keywords = extract_keywords(articles, HAPPINESS_KEYWORDS)

        scores = {
            category: self.compute_category_score(analyzed, kws, date_str)
            for category, kws in HAPPINESS_KEYWORDS.items()
        }

        happiness_index_raw = sum(
            scores[axis] * w for axis, w in HAPPINESS_INDEX_WEIGHTS.items()
        )

        return {
            "date": date_str,
            "scores": scores,
            "happiness_index_raw": happiness_index_raw,
            "keywords": keywords,
        }
