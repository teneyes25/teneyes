from __future__ import annotations

from .base import BaseSentimentEngine, SentimentScores


class GPTSentimentEngine(BaseSentimentEngine):
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or ""

    def analyze(self, text: str) -> SentimentScores:
        # TODO: call GPT API
        _ = text
        return {
            "positive": 0.1,
            "neutral": 0.2,
            "negative": 0.7,
        }
