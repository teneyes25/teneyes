from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from .keywords.conflict_keywords import CONFLICT_KEYWORDS
from .news_score_common import moving_average, three_business_days_ending_at
from .relevance import get_relevance_score
from .sentiment.analyzer import SentimentAnalyzer


def _data_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "data"


class ConflictIndexCalculator:
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
        return {
            "text": text,
            "sentiment": sentiment,
            "geo_relevance": float(get_relevance_score(article)),
        }

    def compute_category_score(
        self,
        analyzed_articles: list[dict[str, Any]],
        category_keywords: list[str],
    ) -> float:
        """
        geo_relevance(기사별)로 가중합합니다. 모든 기사의 geo_relevance가 1이면
        기존 공식과 동일합니다.

        relevance_score = 해당 축 가중 기사 비중(0~1),
        keyword_score = (키워드 가중합 * relevance_score) / 가중합 * 100,
        volume_score = (해당 축 가중합 / 전체 가중합) * 100,
        raw_score = 감성·키워드·volume 가중합,
        final_score = raw_score * relevance_score.
        """
        total_articles = len(analyzed_articles)
        if total_articles == 0:
            return 0.0

        w_sum = sum(float(a["geo_relevance"]) for a in analyzed_articles)
        if w_sum <= 0:
            return 0.0

        keyword_weighted = 0.0
        negative_weighted = 0.0
        axis_weighted = 0.0

        for a in analyzed_articles:
            text = a["text"]
            sentiment = a["sentiment"]
            w = float(a["geo_relevance"])
            negative_weighted += float(sentiment["negative"]) * w

            hit_in_article = False
            for kw in category_keywords:
                if kw in text:
                    keyword_weighted += w
                    hit_in_article = True
            if hit_in_article:
                axis_weighted += w

        emotion_score = (negative_weighted / w_sum) * 100.0
        relevance_score = axis_weighted / w_sum
        keyword_score = (
            (keyword_weighted * relevance_score) / w_sum * 100.0
        )
        volume_score = (axis_weighted / w_sum) * 100.0

        raw_score = (
            emotion_score * 0.5
            + keyword_score * 0.3
            + volume_score * 0.2
        )

        return raw_score * relevance_score

    def _run_one_day(self, date_str: str) -> dict[str, Any]:
        articles = self.load_news(date_str)
        analyzed = [self.analyze_article(a) for a in articles]

        scores = {
            category: self.compute_category_score(analyzed, keywords)
            for category, keywords in CONFLICT_KEYWORDS.items()
        }

        conflict_index = (
            scores["political"] * 0.20
            + scores["diplomatic"] * 0.25
            + scores["military"] * 0.25
            + scores["economic"] * 0.15
            + scores["social"] * 0.15
        )

        return {
            "date": date_str,
            "scores": scores,
            "conflict_index": conflict_index,
        }

    def _conflict_index_or_zero(self, date_str: str) -> float:
        try:
            return float(self._run_one_day(date_str)["conflict_index"])
        except (FileNotFoundError, ValueError):
            return 0.0

    def run(self, date_str: str, *, ma_window: int = 3) -> dict[str, Any]:
        """
        당일 `conflict_index` + 최근 `ma_window`개 **영업일**(월~금) 지수의 이동평균.
        주말은 건너뜀(공휴일 미반영). 뉴스 파일 없는 영업일은 0.
        """
        out = self._run_one_day(date_str)
        end = date.fromisoformat(date_str)
        biz_days = three_business_days_ending_at(end)
        values = [
            self._conflict_index_or_zero(d.isoformat()) for d in biz_days
        ]
        dates_iso = [d.isoformat() for d in biz_days]
        out["conflict_index_3d"] = values
        out["conflict_index_3d_dates"] = dates_iso
        out["final_conflict_index"] = moving_average(values, window=ma_window)
        return out
