from __future__ import annotations

from .base import BaseSentimentEngine, SentimentScores
from .gpt_engine import GPTSentimentEngine
from .opensource_engine import OpenSourceSentimentEngine


class SentimentAnalyzer:
    def __init__(self, mode: str = "opensource", api_key: str | None = None) -> None:
        self.engine: BaseSentimentEngine
        if mode == "gpt":
            self.engine = GPTSentimentEngine(api_key)
        else:
            self.engine = OpenSourceSentimentEngine()

    def analyze(self, text: str) -> SentimentScores:
        return self.engine.analyze(text)
